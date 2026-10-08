---
title: What I learned and what went wrong
description: The bugs I wrote, the promise I withdrew, the weeks nothing merged, and what I do differently after a summer on omegaUp.
---

<p class="lede">This is the part of a project report that usually gets one polite paragraph. I think it is
the most useful part, so it gets its own page.</p>

## I break my code before I trust a test {#break-it-first}

The single biggest change is how I write tests. I used to write the test after the fix and move on the
moment it went green. Now I break the code on purpose first and check that the test fails, because a test
that passes against broken code is decoration.

It costs about a minute. It caught two real bugs in my own work this summer, both in code I had written
minutes earlier and was certain was correct.

The first was in the [health checks](health-checks.html#two-bugs). The step that closes findings which are
no longer detected was reading the clock after writing the new findings. On a slow run, a finding written
moments earlier could be judged as "not seen this run" and closed, so the job would report a problem as
fixed at the instant it discovered it. I found it because I wrote the test. I trusted the fix because I put
the bug back and watched the test go red.

The second I nearly shipped without noticing. Three of the four health checks fired on their first real run
and one found nothing. My first reaction was relief. It found nothing because the development database
contained no data that could trigger it, so the check had never run once against a real case. I seeded the
failure and watched it fire before I trusted it.

No results and not working look identical from the outside. I now treat an empty result from a new check as
unproven.

## My tests agreed with my code, and both were wrong {#agreeing-tests}

Twice this summer a reviewer found something my own testing could not have found, because my tests encoded
the same wrong idea as my code.

Ankit found that the fake database cursor I had built for the cron tests never advanced, so reading two rows
returned the first row twice. Every test standing on it was passing for a reason unrelated to the code under
test. That is on [Tests and query fixes](groundwork.html#the-fake).

Juan Pablo found that the score my model guardrail recorded as MAP was not MAP, and that it left out every
user the model had no answer for. I had run the guardrail both ways in Docker and watched it refuse a weak
model and publish a good one. It worked. It was working on the wrong number. That is on
[Model training](model-training.html#the-review).

What I took from both: testing tells you whether the code does what you meant. It cannot tell you whether
what you meant was right. That second question needs another person.

## I withdrew a promise from my own proposal {#the-promise}

I had committed to rebuilding the rankings in a second table and swapping it in. When I researched it
properly I found five reasons it was a bad idea, and then found that the problem it was meant to solve had
been fixed by someone else while I was writing the proposal.

I wrote that up and posted it. The alternative was building something smaller and hoping nobody compared it
with the document. It felt bad to do, and it was the easiest decision of the summer once I had the facts in
front of me. The detail is on [Tests and query fixes](groundwork.html#the-promise-i-took-back).

## Nothing merged for weeks {#waiting}

The hardest part of the summer had nothing to do with code. At the midterm, one of my pull requests for the
main project had merged. Every other one had green checks and was sitting in the queue, and there was no
version of working harder that would change that.

Up to then every problem I had hit was one I could solve by putting in more hours. My mentors were
straightforward that review time was the constraint and told me to keep building, so I kept building.
Seventeen of my pull requests merged in August.

{{chart waiting | The same chart as on the summary page, because it is the most honest picture I have of the summer. The long bars are pull requests waiting in a queue.}}

What I took from it is that on a project maintained by volunteers, how reviewable your work is matters as
much as whether it is correct. A large correct change and a small correct change are not worth the same to
the person who has to read them. I used to think a bigger pull request showed more work. It mostly shows
less consideration for the reviewer.

## Small pull requests have a cost, and I pay it on purpose {#small-prs}

Keeping pull requests small and ordered is right for reviewers and expensive for me. Every time one merges I
rebase the next so its diff stands alone. When the first tables merged, the migration number had changed
underneath me, so every later database change had to shift with it. That happened twice more. At one point a change to a shared file had to be carried across seventeen branches, because all of
them descended from it.

I would work the same way again. I would plan for the rebasing instead of treating it as something that
happens to me.

I also got the granularity wrong before I got it right. In late August I split the rerun feature into five
pull requests and the same day folded three back, because a chain of drafts that could not be reviewed yet
felt like clutter. In October the maintainer asked for it in six pieces. A draft that waits its turn is
cheaper for a reviewer than one large pull request, and I should have left the split alone.

## Stacks merge in whatever order they are approved {#stacks}

Twice a pull request of mine was squash merged while the one underneath it was still open, which carried the
lower one's changes into main and left it with nothing to merge. Both times the cause was the same. The
upper one was not marked as a draft, so nothing about it said "not yet".

Now every stacked pull request is a draft until its parent lands, and its description opens with which
number it is in the stack and what has to merge first.

## When two checks contradict each other {#contradicting-checks}

One problem was purely mechanical and taught me something anyway. After the first tables merged, one
required check insisted that a generated schema file match the main schema byte for byte, and another
required check crashed trying to read that same file. Both were mandatory, so satisfying one broke the
other.

The crash was at one specific table, caused by a full text index clause another contributor had added that
the schema parser did not understand. Nobody had hit it because main's copy of the generated file was out of
date and did not contain that line yet. Mine was the first change to regenerate it. The fix was one line in
the parser.

When two automated checks contradict each other, the contradiction is usually pointing at something real.

## Skipped is not passed {#skipped}

On one pull request the PHP job showed as skipped, because it depends on another job that had died. The PHP
tests for that change had never run. Nothing was red and nothing had been tested. I read the job list now
instead of the summary.

## Checking before building {#checking-first}

Several things I built before the summer are still open and unreviewed: an online code tester of nine
hundred lines, a three part feature for saving code templates, a redesigned verification email. I opened
them without first agreeing with a maintainer that the project wanted them.

The pull requests of mine that merged quickly were either small or had been asked for. The fourteen ideas I
sent Juan Pablo at the midterm, asking which one the organisation needed, were the same lesson applied on
purpose. Asking first would have cost me a day on each of those.

## Three claims I will not round up {#claims}

There are three things about this project I could phrase so they sound better than they are.

The system can tell you a job ran and failed. It cannot tell you a job never started, which is the one
failure that a run history cannot catch.

The lock lives in the database, so it is only as available as the database is. It prevents wasted work. The
correctness comes from the transaction underneath it.

The model guardrail shows that a new model is not much worse than the last one on an offline number. It does
not show that the model is better for the students using it.

All three are fine for what they are, and none of them is more than that.
