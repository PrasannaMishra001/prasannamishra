---
title: After the summer
description: What has merged on omegaUp since the GSoC 2026 coding period ended on 24 August, what is still in review, and what comes next.
---

<p class="lede">The coding period ended on 24 August 2026 and the work did not. More of this project has
merged since that date than some people would guess from the word "final" on a report. This page is kept up
to date as things land.</p>

{{stats all}}

## What has merged since 24 August {#merged-since}

Fourteen pull requests, as of 8 October.

{{prtable after-merged}}

In the first week, the remaining test suites for the cron scripts, the ranking audit, the admin page itself and
the model runs table all landed. September brought the health check job, the guarded model training and the
rerun request table. October brought the findings view, which closed the health checks issue, and a school
matching fix I had opened in February.

Three of these changed in ways worth writing down.

**The model score was not what I said it was.** The review of the training job on 2 September found that
the number I was storing as MAP was a different, older measure, and that users the model could not answer
for were being left out of the average. Fixing that changed the meaning of the project's central number.
The story is on [Model training](model-training.html#the-review).

**A typo could have rewritten the health history.** The review of the health check job asked for thresholds
to be validated before the job runs, because a nonsense value makes a check find nothing and the job then
closes every open finding of that kind. That is on [Health checks](health-checks.html#what-review-changed).

**A seven month old pull request merged in a week.** I opened a fix for how schools are matched on
21 February. Nobody looked at it until 30 September, when Juan Pablo wrote that the school cleanup project
was being picked up again and this was a good first step. He asked for country and state to be part of the
match. I pushed that on 3 October and it merged on the 7th.

## What is in review {#in-review}

{{prtable after-open}}

These have to merge in the order shown. Each is stacked on the one above it and says so in its first line.

On 2 October Juan Pablo reviewed the rerun feature and asked for it in smaller pieces. I split it the next
day. The same day, CI went red on six branches at once. Main had gained a new table that had no generated
classes yet, and omegaUp's schema check requires the generated schema file to match the real one exactly, so
every branch of mine that touched that file failed a check for a table that was not mine. I rebased the
whole stack onto current main and regenerated, which is how one of my pull requests came to include the
generated classes for somebody else's table.

## Helping on other people's work {#helping}

Twice since the summer a maintainer has tagged me on someone else's issue as the person who knows the
recommendation pipeline.

In September another contributor proposed a personalised "recommended for you" feed. I described what
already exists: a trained model and a function that returns suggestions, a training job that is recorded
and guarded but not yet scheduled in production, and nothing that serves the model to users. That got the
issue marked as blocked until a serving path was designed, which was the right outcome and saved someone
building on something that was not there.

On the revised proposal I corrected one design decision. The plan was to copy only the top few suggestions
per problem into a table. But the model filters out problems a user has already solved before it picks the
top few, so for an active user a short list can come back empty. The fix was to store more per problem and
keep the score. The plan was revised and accepted on 2 October.

I also answered a newcomer who asked to take an old issue about omegaUp's GSoC pages, with a summary of
which parts had already merged and which pull requests were stuck, so they would not start from zero.

All of the threads where I commented on someone else's work are on [Reviews](reviews.html#on-other-work).

## What comes next {#next}

In order:

1. Get the four rerun pull requests and the two views behind them merged.
2. Add the model trainer to the production schedule, once the pieces it needs are on main.
3. Detect a job that never started. The run history can show a failure, but it cannot show an absence, and
   the schedule needed to work that out is already stored.
4. Send a notification when a job fails, through the path the rerun worker already uses.
5. Decide how long run history is kept. Nothing deletes from it today.

I was contributing to omegaUp before this project started and I have not stopped at the end of it.
