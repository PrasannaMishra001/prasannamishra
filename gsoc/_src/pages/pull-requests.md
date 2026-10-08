---
title: Pull requests
description: Every pull request Prasanna Mishra has opened on omegaUp, with its current status, refreshed from GitHub when the page loads.
wide: yes
---

<p class="lede">Every pull request I have opened on omegaUp, oldest first within each group. The status
column is refreshed from GitHub when this page loads, and a pull request I open after this page was built is
added at the bottom.</p>

{{stats all}}

Type in the box to filter by number or by words, or use the buttons. The number links to GitHub. The detail
of each one, and what review changed about it, is on the page for its part of the work:
[control plane](control-plane.html#pull-requests), [model training](model-training.html#pull-requests),
[health checks](health-checks.html#pull-requests), [tests and query fixes](groundwork.html#pull-requests),
[alongside the project](alongside.html#pull-requests) and [before the summer](before-gsoc.html).

{{prtable all}}

## By month {#by-month}

{{chart monthly | Opened and merged, by month.}}

## A note on the closed ones {#closed}

Thirteen of these were closed without merging. I counted why.

Six were pieces I had split out of a larger pull request and then folded back the same day, in late
August, before anyone had reviewed them. Their code merged, or is in review, under another number.

Two were absorbed: the pull request stacked on top of each was squash merged first and carried their
changes into main.

Two were overtaken by another contributor fixing the same thing first.

One was the original system settings pull request, which was split into four. One I closed and reopened
with a proper description. And one I opened from the wrong branch and closed ninety seconds later.

None of them was rejected for what it did.
