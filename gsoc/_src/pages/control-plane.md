---
title: The cron control plane
description: How omegaUp's background jobs got a run history, a lock, an admin page and a safe way to rerun them, and the pull requests that built it.
---

<p class="lede">omegaUp's background jobs ran every night and left nothing behind. This is the project that
gave them a history, stopped them overlapping, and put them on a page an admin can read. It was the first of
the three projects Juan Pablo asked for, and the other two are built on it.</p>

## What was wrong {#what-was-wrong}

There were five things, and I wrote them into the [parent issue](https://github.com/omegaup/omegaup/issues/9992)
before writing any code.

There was no record that a job had run. No row saying it started, finished, took a while or fell over. When a
job died halfway through, the evidence was a missing badge or a stale leaderboard, noticed days later.

Nothing stopped two copies overlapping. That matters most for the ranking job, which at the time deleted
every row of the rankings table before writing fresh ones. Two copies overlapping does not raise an error.
It leaves half a leaderboard and carries on.

Nobody could see how long a job took, or which step inside it was slow.

Rerunning a job needed a shell on a production pod.

And when I read the production schedule I found only three jobs on it. The model trainer and the plagiarism
detector were scripts somebody had to remember to run.

## The design {#the-design}

{{diagram architecture | The whole thing on one drawing. Jobs on the left, the page on the right, and everything in between exists so that the two never talk to each other directly.}}

### Two tables {#two-tables}

`Cron_Jobs` is the registry: one row per job, with its schedule and a switch.

`Cron_Runs` is the history: one row per execution, with a status, when it started and finished, how long it
took, how many rows it touched, a JSON list of its phases, and the error text if it failed.

The registry, as it merged:

```sql frontend/database/00277_cron_control_plane.sql
CREATE TABLE `Cron_Jobs` (
  `job_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `description` text,
  `schedule` varchar(64) DEFAULT NULL,
  `enabled` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`job_id`),
  UNIQUE KEY `unique_cron_job_name` (`name`)
)
```

A run stores the job's name, not an id pointing at the registry. Juan Pablo asked about that in review, and it
is a fair question, because an id would avoid repeating the name and the database would enforce the link. I
kept the name for two reasons. A script that is not in the registry should still be able to record that it
ran. And if a job is renamed or removed, its history should stay readable. He asked me to write that reasoning
into the schema itself, so it is in the column comment.

### One runner {#one-runner}

Each job wraps its work in a context manager from `stuff/lib/runner.py`.

{{diagram runner | Steps one and two can end the run early, and when they do nothing is recorded, because nothing happened.}}

The lock is MySQL's `GET_LOCK`, a named lock held by a connection.

```python stuff/lib/runner.py
def _acquire_lock(self) -> bool:
    assert self._connection is not None
    timeout = getattr(self._args, 'lock_timeout', 0)
    with self._connection.cursor() as cur:
        cur.execute(
            'SELECT GET_LOCK(%s, %s)', (self._lock_name, timeout))
        row = cur.fetchone()
    return bool(row is not None and row[0] == 1)
```

I chose it over a lock file because these jobs can run on different machines. And because the database ties
the lock to the connection, a job that crashes while holding it releases it by dying. The default timeout is
zero: a second copy does not queue up behind the first, it logs "already running" and leaves.

The review of the runner found two ways I could still have left the lock held. If writing the "running" row
failed after the lock was taken, the cleanup never ran, because Python does not call `__exit__` when
`__enter__` raises. And if writing the final status failed, the release after it was skipped. Both paths now
release the lock in a `finally`. Neither would have shown up in normal use, which is the kind of bug a
reviewer is for.

Adopting it in a job is a small change. The ranking job's pull request deletes more lines than it adds,
because its hand written timing code comes out.

```python stuff/cron/update_ranks.py
with cron_run.phase('update_problem_accepted_stats'):
    update_problem_accepted_stats(cur, dbconn.conn)
with cron_run.phase('update_users_stats'):
    update_users_stats(cur, cur_readonly, dbconn.conn, args)
with cron_run.phase('update_schools_stats'):
    update_schools_stats(cur, cur_readonly, dbconn.conn,
                         args.date,
                         args.update_school_of_the_month)
```

### The page {#the-page}

`/admin/crons` is for system admins only. It lists each job with its schedule and how its last run went, and
below that the fifty most recent runs across all jobs. A run opens to show each phase with its own timing,
and the error text if it failed.

{{fig shot/dash-overview.png | The page on a local branch with everything applied. The cards at the top and the rerun buttons are from pull requests still in review. The two tables under them are what is on main today. | l}}

{{fig shot/dash-failed-run.png | A failed run of the ranking job, opened. The audit refused a ranking that had shrunk from 1500 rows to 400, and you can see which phase raised and how long each one took. This is from a local branch with the second dashboard pass applied. | l}}

Juan Pablo asked for the schedule to be shown in words next to the raw cron expression. That sounded small
and was not, because cron expressions are a small language. I describe the shapes the registry uses, such as
daily, weekly, monthly, hourly and every few minutes, and for anything else the page shows only the
expression. I would rather show nothing than a confident wrong sentence.

### A guardrail on the ranking job {#a-guardrail-on-the-ranking-job}

Before the new ranking is committed, the job checks it. If it is empty, has negative scores, or has lost more
than half of yesterday's ranked users, it raises and the transaction rolls back. I would rather have
yesterday's rankings than today's broken ones.

I tested that the rollback does what I claim. On a forced failure the job exits non zero and the checksum of
the rankings table is identical before and after.

## Rerunning a job safely {#rerun}

The obvious design is that the button sends a request and the server runs the job. I did not build that,
because a web request that can start a program on your servers is a door, and I did not want to be the person
who built it.

{{diagram rerun | The request and the run are separate steps, done by separate programs. The web server can only write a row.}}

The endpoint checks four things and then writes one row with the status `pending`. It never starts anything.

A separate worker, the dispatcher, is the only thing that launches a job. A name is launchable only if it is
on a list compiled into the dispatcher, is present in the registry, is a bare filename and exists in the cron
directory. There is a test that fails if the list in Python and the list in PHP ever drift apart.

```python stuff/cron/cron_dispatcher.py
cur.execute(
    '''
    UPDATE Cron_Run_Requests
    SET status = %s, picked_at = NOW()
    WHERE request_id = %s AND status = %s;''',
    (RequestStatus.PICKED.value, request_id, RequestStatus.PENDING.value))
claimed = cur.rowcount == 1
dbconn.conn.commit()
return claimed
```

That one statement is the whole concurrency story. Two dispatchers can read the same pending row, but only
one of them can change it, and the other sees that it changed nothing and moves on.

Two things fall out of this design without extra work. Every rerun is recorded, including who asked. And the
person pressing the button needs no server access, which was the point.

{{fig shot/dash-rerun.png | After pressing rerun. The page says the request was made, not that the job ran, because that is all the page knows. | l}}

### How it got split, twice {#how-it-got-split}

I opened the rerun feature in July as one pull request. In August I split it into five, and the same day
folded three of them back, because a chain of drafts that could not be reviewed until their parents merged
felt like noise. That was the wrong call. In October Juan Pablo reviewed it and asked for it in pieces, with
a reason I could not argue with:

> The dispatcher in particular contains concurrency, timeout, transaction, and failure-handling behavior that
> deserves to be reviewed independently from the UI and API changes.

So it is now a stack, and each pull request says at the top which number it is and what has to merge first.

## The order it merged in {#merge-order}

{{diagram stack | Each box is a pull request and links to it. An arrow means "has to merge first". As of 8 October 2026, the first two rows are on main and the third is in review.}}

The repository's schema check does not allow a table definition and its generated data access classes in the
same pull request. So every table has to merge before the code that reads it can even pass CI, and every
stacked pull request stays red on one check until its parent lands. I spent a lot of the summer explaining a
red check that was correct.

The tables waited fifteen days, the page forty six. Then the runner merged on 19 August and the three pull
requests behind it landed in the next three days.

## What this does not do {#limits}

Three things I could phrase so they sound better than they are.

The system can tell you a job ran and failed. It cannot tell you a job never started, which is the one
failure that a run history cannot catch by itself. The schedule is stored, so this can be built, and it is next.

The lock lives in the database, so it is only as available as the database. It is also there to stop wasted
work, not to guarantee correctness. Correctness comes from the transaction underneath.

And the lock is held on a connection that sits idle for the whole job. A server side timeout could drop that
connection on a long run. I have not seen it happen, and I have not ruled it out.

## The pull requests {#pull-requests}

### The foundation {#foundation-prs}

{{records control}}

### Rerun, and the second pass on the page {#rerun-prs}

{{records rerun}}

### Closed without merging {#closed-prs}

These four are the pieces I split out and folded back on 29 August. I am listing them because the list is
meant to be complete.

{{records rerun-closed}}

## The issues {#issues}

{{issuerows control}}
