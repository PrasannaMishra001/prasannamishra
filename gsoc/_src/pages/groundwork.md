---
title: Tests, query fixes, and the proposal I started with
description: The first half of GSoC 2026 at omegaUp: unit tests for the cron scripts, safer SQL, the midterm feedback, and the shadow table swap that was promised and withdrawn.
---

<p class="lede">The first half of the summer was the project I had proposed: make four Python scripts safer
and give them tests. It is also where the project changed direction, and where I took back something I had
promised.</p>

## The proposal {#the-proposal}

The project was called Cronjob Optimization. My proposal covered four scripts in `stuff/cron/`: the ranking
job, the badge job, the feedback job and the recommendation model trainer. The plan was unit tests, safer
and faster queries, proper exception handling, names for magic numbers, structured logging, and in week five
a new way to rebuild the rankings table.

By the time coding started on 26 May, a good part of that list was already done. omegaUp had a busy spring,
and other contributors had merged the query rewrites, the batch inserts, the atomic transactions and the
timing logs I had planned to write. So my first week was checking each proposal item against main and
crossing out what no longer needed doing. What was left was the tests, three queries, the bare excepts, the
constants, and the rankings rebuild.

## Tests for scripts that had none {#tests}

Two of the four scripts had no unit tests at all. The difficulty is that they are almost entirely SQL, so
there is little to test without a database.

I built two things. The first is a scripted cursor: you tell it "when you see a query containing this text,
answer with these rows", and afterwards you can ask it what it was sent. That is enough to test the logic
around a query.

```python stuff/cron/tests/fixtures/mock_cursor.py
def fetchone(self) -> Optional[Row]:
    '''Return the next scripted row and advance, or None when drained.'''
    if self._position >= len(self._current):
        return None
    row = self._current[self._position]
    self._position += 1
    return row
```

The second came out of a review comment. Juan Pablo pointed out that one of my tests only checked that an
`UPDATE` had been sent, so a malformed query would pass. To test what a statement does, it has to run. So the
later tests run the job's real SQL against an in memory SQLite database, translating the three
MySQL only constructs those queries use, and then read the table back.

```python stuff/cron/tests/fixtures/sqlite_cursor.py
def _translate(sql: str) -> str:
    '''Rewrite the MySQL-only constructs the cron queries use.'''
    sql = sql.replace('%s', '?').replace('UNION DISTINCT', 'UNION')
    return _UPDATE_ALIAS_RE.sub(r'UPDATE \1 AS \2', sql)
```

These tests check what the SQL means, not whether MySQL accepts it. I say so in the pull request, because a
reader should know what a green tick here does and does not cover.

### The fake that was subtly wrong {#the-fake}

That `fetchone` above is the fixed version. The one I first wrote never advanced. It returned the first row
every time you called it.

Ankit reviewed the test infrastructure two days after I opened it and left thirteen comments. This was one:

> `fetchone()` does not consume the row — repeated calls always return `_current[0]`. The real
> `MySQLCursor.fetchone()` advances the cursor position. Any future test that calls `fetchone()` twice on the
> same scripted cursor will silently get the same row both times.

Every test built on that helper would have passed for a reason that had nothing to do with the code under
test. He also found that an uppercase key in the script silently matched nothing, and a real crash in the
feedback job when a problem had no tag votes.

I now write a test for the test helper before I trust anything built on it.

## Safer queries {#queries}

Three queries in the coder of the month code were assembled by pasting values into SQL strings. They now
bind their values as parameters. For each of these I ran the job before and after against the same database
and compared the tables it writes, because "no behaviour change" is a claim and I wanted it to be a checked
one.

The badge job had a stranger version of the same problem. It supported "pretend today is this date" by
finding `NOW()` in each badge's query and replacing it with a formatted string. I could not turn that into a
normal parameter without editing every badge's query file, so the job now sets a session variable and the
replacement points at that. I ran old and new code over all 23 badges, at eight fixed timestamps and once
with none, and the set of people who would earn each badge matched in all 207 comparisons.

## The promise I took back {#the-promise-i-took-back}

My proposal said I would rebuild the rankings in a second table and swap it in with a rename, so that
readers would never see a half built leaderboard. When I sat down to research it properly I found five
problems.

A rename is a schema change, so it forces a commit and breaks the single transaction that phase depends on.
Copying a table does not bring its foreign keys with it, so the swapped table would lose three of them. It
needs privileges the production database user may not have. The coder of the month calculation reads the
rankings through a separate connection while they are being rebuilt, and would start seeing the new ones.
And it still rewrites every row every day, so the write load is not reduced, only moved.

Then I found the part that settled it. The problem the swap was meant to solve had already been fixed by
somebody else while I was writing the proposal. The phase had become a single transaction, so readers
already saw the complete old ranking the whole way through. The empty leaderboard I had written the proposal
against no longer existed.

I wrote all of that up and posted it. The alternative was quietly building something smaller and hoping
nobody compared it against the proposal. It felt bad to do and it was obviously right. Nobody is served by a
contributor who ships something they know does not work in order to match a document.

What merged in its place updates the rankings in place and then removes only the users who dropped out. Even
that changed once in review. My first version staged rows in a temporary table, Juan Pablo asked whether the
production user was allowed to create one, I could not find out, and so I rewrote it to need no such
permission.

```python stuff/cron/update_ranks.py
cur.execute('SELECT NOW() AS `now`;')
run_start = cur.fetchone()['now']
# Usernames are unique in `User_Rank`, so a username that moved to another
# user would make the upsert below match the wrong row.
cur.execute('''
                DELETE `ur`
                FROM `User_Rank` AS `ur`
                INNER JOIN `Identities` AS `i`
                    ON `i`.`username` = `ur`.`username`
                WHERE `i`.`user_id` IS NOT NULL
                    AND `i`.`user_id` != `ur`.`user_id`;''')
```

## The midterm {#the-midterm}

At the midterm, on 5 July, exactly one of these pull requests had merged, two days earlier. The rest had
green checks and were waiting.

I passed. The feedback was to go bigger. The work so far was many small improvements spread across existing
scripts, and what the mentors wanted for the second half was one connected project that an admin could see
and use, with the database, the backend, the jobs, the interface and the tests all building on each other.

I had been reading omegaUp's production deployment to prepare, which is how I knew that only three jobs
were scheduled. I wrote up fourteen ideas, from a control panel for the cron jobs to contest ratings and
weekly leagues, said which two I would pick, and said I would rather build what the organisation needed.
Juan Pablo picked the control panel first, and named problem health checks and scheduled model training to
follow.

One thing from the first half carried straight over. I had a pull request open that timed every phase of
every job and logged it. Once the [shared runner](control-plane.html#one-runner) existed, it did the same
thing and stored it in a table, so I cut that pull request down from a new helper used everywhere to
eighteen lines.

## When each one merged {#when}

{{prtable groundwork}}

The three test pull requests were open for eleven weeks and merged on 24, 25 and 26 August, the last days of
the coding period. Nothing was wrong with them. They were stacked on each other and waiting for a first
maintainer review, which came on 19 August. I have more to say about waiting on
[What I learned](lessons.html#waiting).

## The pull requests {#pull-requests}

{{records groundwork}}
