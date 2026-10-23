---
title: GSoC 2026 with omegaUp: Cronjob Optimization
description: What Prasanna Mishra built for omegaUp during Google Summer of Code 2026: a control plane for background jobs, scheduled recommendation model training and nightly problem health checks, with every pull request and issue.
---

<div class="factsheet">
<div><span>contributor</span> Prasanna Mishra</div>
<div><span>organisation</span> omegaUp</div>
<div><span>project</span> Cronjob Optimization</div>
<div><span>mentors</span> <a href="https://github.com/pabo99">Juan Pablo G&oacute;mez Aguilar</a>, <a href="https://github.com/Ankitsinghsisodya">Ankit Sisodya</a></div>
<div><span>project size</span> large, 350 hours</div>
<div><span>coding period</span> 26 May 2026 to 24 August 2026</div>
<div><span>result</span> passed both evaluations &middot; <a href="https://drive.google.com/file/d/1nUSmF8SteqWiQusMwfKkd1URJqCJ-4nx/view?usp=sharing">certificate</a> &middot; <a href="https://drive.google.com/file/d/1IvU8CoLtiptRZC3_CsNsfoSoWTJHl9D_/view?usp=sharing">verification letter</a></div>
</div>

<p class="lede">This is my summer with omegaUp: what was wrong with its background jobs, what I built, where
each piece stands today, and what I got wrong along the way. This page is the summary. Each part has its own
page with the detail, and the work from before and after the summer is here too, because it did not start in
May and it has not stopped.</p>

## Summary {#summary}

omegaUp is an open source competitive programming platform, used mostly by students and teachers across
Latin America. You submit a solution to a problem, it gets judged automatically, and your result feeds into
rankings, badges and the suggestions the site makes about what to solve next.

Behind the site a handful of Python scripts run on a schedule overnight. They recompute the rankings, hand
out badges, aggregate the feedback students leave on problems, and train the model that decides what to
recommend. None of that is visible from the website, and none of it was visible to the people running the
website either.

That was the problem. There was no record that a job had run at all, so when one died halfway through, the
first sign would be a student noticing days later that a problem they had solved had never counted. Nothing
stopped two copies of the same job running at once. And an admin who wanted to rerun a job needed shell
access to a production server to do it.

While reading omegaUp's production deployment repository I found a commit from December 2021 saying "Make
update-ranks only run once a day for now". The "for now" had been holding for five years. In the same
afternoon I found that the recommendation model was never trained in production at all, because that job had
never been added to the schedule.

So I built three things that share one foundation.

{{stats gsoc}}

The first is a **control plane for the cron jobs**. Two tables record every job the platform has and every
time one of them ran. A shared runner wraps each job so it writes itself into that history and takes a lock,
so two copies can never overlap. An admin page at `/admin/crons` shows all of it. A rerun button, still in
review, lets an admin run a job again without touching a server.

The second is **scheduled training for the recommendation model**. Every run records how good the model it
produced was, and a guardrail refuses to publish one that is below a floor or measurably worse than the model
it would replace.

The third is a **nightly job that looks for problems which silently stopped working**. It needed no admin
page of its own. It runs through the same runner, so it appeared on the page by itself.

In one paragraph: before this summer, if a background job on omegaUp failed at three in the morning, nobody
found out until a student complained. Now the run is written down, it cannot collide with itself, an admin
can see it from a web page, and the two jobs most likely to publish bad data check their own work before
they publish it.

## About me {#about-me}

I am a third year Integrated B.Tech and M.Tech student in Information Technology at IIITM Gwalior. My first
pull request to omegaUp was on 31 August 2025, nine months before this project started, and by the time the
coding period began twenty one of them had merged, including GitHub sign in and a fix for endpoints that
changed data on a plain GET request. That mattered mostly because I did not spend the first month of the
summer finding my way around the codebase.

That earlier work is on [Before the summer](before-gsoc.html).

## How the project changed shape {#how-the-project-changed-shape}

My original proposal was narrow. It was about cleaning up four Python scripts: unsafe SQL, the near total
absence of unit tests, bare except blocks, magic numbers. By the time coding started, other contributors had
already merged several of the items I had proposed, so the first thing I did was check each one against main
and cut the plan down to what was left.

At the midterm I passed, and the feedback was that the work so far did not add up to one thing you could
point at. It was many small improvements spread thinly across existing scripts. What was wanted was
something vertical: a single project cutting through the database, the backend, the jobs, the interface and
the tests, where the result is a feature somebody can see.

Rather than choose the next project alone, I read the production deployment repository so I would be arguing
from facts, wrote up fourteen candidate projects, and sent them to my mentor saying I was not attached to
any of them and would rather know what the organisation needed. Juan Pablo chose one and named the two that
should follow it:

> the highest priority is building a Cron Control Plane. Today our cron infrastructure lacks visibility and
> operational tooling. After that, automated problem health checks and scheduled training for the
> recommendation model.

So the second half became three projects sharing one foundation. The first half, including the promise from
my proposal that I took back, is on [Tests and query fixes](groundwork.html).

## The shared foundation {#architecture}

{{diagram architecture | Every job goes through one runner, which is the only thing that writes run history. The dashed line is the rerun path: the page writes a request, and a separate worker is what starts the job.}}

### How the shared runner works {#how-the-shared-runner-works}

Every job now wraps its `main()` in one small helper:

```python
with lib.runner.run(parser.prog, args) as cron_run:
    with cron_run.phase('update_users_stats'):
        update_users_stats(...)
    cron_run.set_rows_affected(rows)
```

{{diagram runner | The six things the runner does. A job that is switched off, or already running, exits cleanly without leaving a row.}}

The lock lives in the database, not on disk, because these jobs can run on different machines and a lock
file on one machine means nothing to a job on another. It also solves the failure I was most worried about.
The database ties the lock to the connection, so if a job dies while holding it, the lock releases by itself.
A crash cannot jam the door shut.

## Project one: the cron control plane {#project-1-the-cron-control-plane}

Two tables, the runner, an admin API and a page. The page shows the health of each job, how long each run
took, the timing of every step inside a run, and the error if there was one.

{{video cron-dashboard | The page on a local branch with the whole stack applied, including the rerun button and the health cards that are still in review. | l}}

The rerun button is the piece I thought hardest about. The obvious version is that the button sends a
request and the server runs the job. I did not do that, because the moment a web page can cause a program to
run on your servers you have built a door. The button writes down a request, and a separate worker that is
already running on the inside picks it up, and only for jobs on a fixed list it knows about.

{{cards control-plane}}

## Project two: scheduled recommendation model training {#project-2-scheduled-recommendation-model-training}

omegaUp has a model that answers "this student just solved problem X, what should they try next". It was a
script somebody had to remember to run. Nothing recorded what past training produced, and a bad run would
silently overwrite the good model file.

It is now in the registry with a weekly schedule. Every run records a score for the model it produced, and
two rules decide whether that model is published. Juan Pablo's review of this one found that the score I was
recording was not the metric its name claimed, which is the most useful thing a reviewer told me all summer.

{{cards model-training}}

## Project three: automated problem health checks {#project-3-automated-problem-health-checks}

A problem on omegaUp can stop working after it is published, and nothing errors loudly. Students hit a wall,
and the only signal was somebody filing a report, which means the platform found out about broken problems
from the people it had already failed. A nightly job now looks for four kinds of breakage and keeps a record
of when each was first seen.

{{fig shot/health-findings.png | The findings table on the admin page, from a local database seeded with one case of each check. | l}}

{{cards health-checks}}

## Work alongside the main project {#work-outside-the-main-project}

Three other pieces ran alongside the cron work and all three are merged: the navigation menus rebuilt from
one configuration file, a reusable "this view is unavailable" page, and a system settings feature that lets
an admin switch the embedded IDE off without a deploy.

{{pair shot/problems-before.png | what I shipped first | shot/problems-after.png | after review | "Create zip file" and "I have a zip file" only make sense if you already know what they do. Juan Pablo asked for something more descriptive.}}

{{cards alongside}}

## Current status {#current-status}

This is where things stood on 8 October 2026. The status columns on this site refresh from GitHub when a page
loads, so if something has moved since, the tables will say so and this paragraph is the part that will be
out of date.

**On main and done.** The registry and run history tables, the runner, the admin API and the admin page.
Every cron job on omegaUp runs through the runner, so each one writes itself into the history, takes a lock
that stops a second copy starting, and times each of its phases. The ranking job checks its own result
before it publishes. The recommendation model records and guards every training run. The health check job
runs nightly, its production schedule was added on 6 October, and its findings are on the admin page.

**In review.** The rerun feature, which Juan Pablo asked me to split into small stacked pull requests in
October. Its table and data access layer are merged. The other four are open in the order they need to land:
the endpoint, the worker, the button and the end to end test. Behind them are the second pass on the admin
page and the model quality table.

**Not done.** The model trainer has a weekly schedule in the registry, but the matching entry in the
production deployment has not been added yet, so it is not running in production. That needs the open pieces
to land first.

What sets the pace now is review time, on a project maintained by volunteers. Nothing is half built and
nothing is waiting on me. What has merged since the coding period ended is on
[After the summer](after-gsoc.html).

## Pull requests {#pull-requests}

I opened <span data-count="opened">31</span> pull requests during the coding period and
<span data-count="merged-of-opened">26</span> of them have merged. Counting by merge date instead,
<span data-count="merged-in-period">22</span> landed between 26 May and 24 August, because some had been
waiting since before it began. Each one had an issue written before it, so the reason for a change existed in
writing before the change did.

{{chart waiting | Every pull request I opened from the first day of the coding period, from the day it was opened to the day it merged. Hover a bar for the dates. Most of the summer's work merged in the last three weeks of August, which is what waiting for review looks like from the inside.}}

The full list, including everything before the summer, is on [Pull requests](pull-requests.html). The detail
of each one is on the page for its project.

## Issues {#issues}

I have filed <span data-count="issues-all">93</span> issues on omegaUp. The ones behind this project are a
parent issue for each of the three parts and one sub issue per pull request under them. All of them are on
[Issues](issues.html).

## What I learned and what went wrong {#what-i-learned}

The single biggest change is how I write tests. I used to write the test after the fix and move on the
moment it went green. Now I break the code on purpose first and check that the test fails, because a test
that passes against broken code is decoration. It costs about a minute and it caught two real bugs in my own
work this summer, both in code I had written minutes earlier and was certain was correct.

The hardest thing I did was withdraw a promise from my own funded proposal, after I found the problem it
solved had already been fixed by somebody else. And the hardest part of the summer had nothing to do with
code: at the midterm, not one of my pull requests for the main project had merged, and there was no version
of working harder that would change it.

The whole of it is on [What I learned](lessons.html).

## What is left to do next {#future-work}

The gap I care most about is that the system can tell you a job ran and failed, but it cannot tell you a job
never started. The schedule is already stored in the registry, so the pieces are there, and it is the next
thing I want to build. After that, failure alerting through the notification path the rerun worker already
uses, which is what turns history into monitoring. Then retention, because nothing deletes from the run
history. That is fine today and will not be in two years.

Smaller things: pagination past the fifty run cap, a duration sparkline per job, and a "next run" column
computed from the schedule that is already stored. I left model versioning and rollback alone on purpose,
because the model file layout and the serving side live in omegaUp's production repository and building it
blind risked doing it wrong.

Before any of that, the work that is already written has to finish landing, and I am staying for it.

## Acknowledgments {#acknowledgments}

Thanks to [Juan Pablo](https://github.com/pabo99) for reviews that were specific and for pushing back on the
parts that deserved it. The question about storing a name instead of an id made the schema better, the
review of the model training job changed what its score means, and the request to split a large pull request
changed how I work.

Thanks to [Ankit](https://github.com/Ankitsinghsisodya) for the review of my test infrastructure that found
real bugs in it. Being told early and precisely that my fake database was subtly wrong was worth more than
an approval.

And thanks to omegaUp for letting a contributor propose a direction, argue for it with evidence, and then
build it.

## The rest of it {#the-rest}

{{cards before-gsoc, after-gsoc, journey, pull-requests, issues, reviews}}
