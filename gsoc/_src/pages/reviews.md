---
title: Reviews
description: What reviewers asked for on Prasanna Mishra's omegaUp pull requests and what changed as a result, and the threads where he reviewed or helped on other contributors' work.
---

<p class="lede">Almost everything good about this work was improved by somebody else reading it. This page
collects what reviewers asked for, grouped by the lesson, and then the threads where I was the one
reading.</p>

## Who reviewed {#who}

[Juan Pablo Gómez Aguilar](https://github.com/pabo99) reviewed and merged every pull request of mine that
has merged. That is <span data-count="all-merged">57</span> so far, on a project he maintains as a volunteer.

[Ankit Sisodya](https://github.com/Ankitsinghsisodya), my other mentor, reviewed the test infrastructure for
the cron scripts in the first week of June, which is the review that found my fake cursor was broken.

## What I was told, by theme {#themes}

### Say it in every language {#theme-language}

My first review comment on omegaUp, in September 2025, was about a sentence I had built in English inside a
component:

> This would work fine if we only displayed information in English.

omegaUp is used mostly in Spanish. Every string goes through the translation files, in four languages. I
was told this again about a loading message, and again about an `aria-label`. I have not been told since.

Names of translation keys got their own round. I renamed three keys to something shorter and was told they
now had "less context ='(".

### Put it where that kind of thing already lives {#theme-place}

Date logic goes in the date module. Database access goes in the data access layer, and a pull request of
mine was put on hold until it did. A value every page needs goes in the payload every page already
receives. A component announces what happened and the page script makes the request.

On the admin page for cron jobs, the same idea came up as "do not call one endpoint from another". The page
and the API now share one helper, so they cannot drift apart.

```php frontend/server/src/Controllers/Admin.php
private static function cronsPayload(): array {
    return [
        'jobs' => self::cronJobsPayload(),
        'runs' => self::cronRunsPayload(
            \OmegaUp\DAO\CronRuns::getRecent(self::CRON_RUNS_LIMIT)
        ),
    ];
}
```

### Known sets of values are enums {#theme-enums}

Job names and run statuses in PHP. Check types and severities in Python. And when the same values had to be
known in TypeScript, a typed map keyed on a mirror of the enum, so that adding a value on the server without
giving it a label fails the build.

### A test has to be able to fail {#theme-tests}

> A malformed query could currently pass this test

That was about a test of mine that checked an `UPDATE` had been sent and not what it did. I rewrote it to
run the statement and read the result. On the admin API I was asked for a test that a non admin is refused
on each endpoint separately, since each has its own check. On the model training job, every one of the four
findings came with a request for a named regression test.

### Release what you took, on every path {#theme-cleanup}

The shared runner takes a database lock. Review found two ways it could stay held: if the first write after
taking it failed, and if the last write before releasing it failed. Both are easy to miss, because both
only happen when something else has already gone wrong.

### Count the same thing on both sides {#theme-counting}

The ranking audit compares how many users are ranked today against yesterday. Juan Pablo noticed the table
also holds rows for people ranked only as problem authors, and my "yesterday" was counting them while my
"today" was not.

The same shape of mistake was in the model score: users the model had no answer for were left out of the
average, so the number described only the cases it could handle.

### Make failure visible to whoever is watching {#theme-visible}

A model that is refused now exits with a failure status, because marking it as failed in a table is no use
to something that only watches exit codes. A health check that raises fails the whole run, because a
skipped check looks the same as a clean one.

### Smaller {#theme-smaller}

> Can you split this PR into smaller changes?

January, about system settings. I heard versions of it in July about the admin page and in October about
rerun. The October one came with the best explanation of why:

> The dispatcher in particular contains concurrency, timeout, transaction, and failure-handling behavior that
> deserves to be reviewed independently from the UI and API changes.

### Sometimes the fix is to delete {#theme-delete}

I fixed an endpoint that always returned `null` for one field by making it return the real value. Juan
Pablo looked at the history, saw the field had been null for four years without anyone asking for it, and
suggested removing it. So the pull request titled "return contest_alias" removed `contest_alias`.

## Where I disagreed {#disagreed}

Not often, and I tried to give a reason each time.

On the run history table I was asked whether a run should refer to its job by id. I kept the name and
explained why: a script outside the registry should still be recordable, and history should survive a
rename. The reasoning went into the schema as a comment.

On the settings data access layer I was asked whether the table should store each setting's type. I argued
that the only setting was a boolean and the function name already said so, and offered to raise it
separately if a second kind of setting appeared.

On the test fixtures Ankit suggested that asking the fake cursor for dictionary rows should either work or
raise. I kept it accepting the flag, because the tests coming next needed to call it that way, and
documented that the scripted rows decide the shape.

And once I was simply wrong. I folded a set of split pull requests back together in August because the
chain felt like clutter, and in October was asked to split them again.

## On other people's work {#on-other-work}

I have commented on thirty nine issues and pull requests that were not mine. Early on these were mostly me
asking to take an issue. From late February they are mostly me helping someone get a pull request through:
explaining why CI failed, which file is generated and how to regenerate it, why a diff had sixty thousand
unexpected lines in it.

A few were reviews. On a workflow change I pointed out that reading a fixed number of results without paging
would miss pull requests on busy issues and unassign people who had done nothing wrong. On a search change I
noticed prefix matching had been dropped between two versions. On a proposal to catch slow SQL in CI I
pointed out that the test database has ten rows per table, which is too few for a query plan to mean
anything.

{{comments}}
