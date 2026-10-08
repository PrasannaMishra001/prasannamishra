---
title: Timeline
description: Every month of Prasanna Mishra's work on omegaUp since the first pull request in August 2025, through Google Summer of Code 2026 and after.
---

<p class="lede">Everything since August 2025, in order. The chart shows how uneven it was, and the list underneath says
what was happening.</p>

{{stats all}}

{{chart monthly | Pull requests I opened and pull requests of mine that merged, by month. Hover a month for the numbers. February is the tallest bar, and less than a third of it merged that month.}}

## Month by month {#month-by-month}

<ul class="timeline">
<li class="era"><span>2025</span></li>
<li class="major reveal"><time>31 Aug 2025</time><div><h4>First pull request</h4><p>Human readable contest dates. Opened the day I finished setting the project up. It took six months to merge, mostly because I walked away from it. The same day I left my first comment on a cron script.</p></div></li>
<li class="reveal"><time>9 Sep 2025</time><div><h4>First merge</h4><p>A button alignment fix, five days after I opened it.</p></div></li>
<li class="reveal"><time>Dec 2025</time><div><h4>Back after three months</h4><p>Navbar hover effects. Four rounds of review, and the version that merged threw away my JavaScript for a few lines of CSS.</p></div></li>
<li class="era"><span>2026, before the summer</span></li>
<li class="major reveal"><time>Jan 2026</time><div><h4>Seventeen pull requests</h4><p>GitHub sign in, the first attempt at system settings, a migration merging eighteen duplicate schools, and a long list of things I was told once and did not need telling twice. Nine merged the same month.</p></div></li>
<li class="reveal"><time>29 Jan 2026</time><div><h4>"Can you split this PR into smaller changes?"</h4><p>System settings, 994 lines in one piece, became four pull requests. The last of them merged in July.</p></div></li>
<li class="reveal"><time>9 Feb 2026</time><div><h4>GitHub sign in merges</h4><p>Three review rounds on security, accessibility and translation.</p></div></li>
<li class="major reveal"><time>Feb 2026</time><div><h4>Thirty pull requests, and a lesson about volume</h4><p>The busiest month by a distance. Small focused fixes merged within days. A batch of thirteen infrastructure changes opened in two days mostly never got a reply, and neither did three large features nobody had asked for.</p></div></li>
<li class="reveal"><time>5 Mar 2026</time><div><h4>Endpoints that changed data on a GET</h4><p>Found by reading how the API routes requests. Merged on 9 May with "Great catch!".</p></div></li>
<li class="reveal"><time>Apr 2026</time><div><h4>The Help menu, and a proposal</h4><p>One pull request this month, which turned into the summer's navigation work.</p></div></li>
<li class="era"><span>Google Summer of Code</span></li>
<li class="major reveal"><time>26 May 2026</time><div><h4>Coding period begins</h4><p>The first week went on checking my proposal against main. Other contributors had already merged a good part of it.</p></div></li>
<li class="reveal"><time>4 Jun 2026</time><div><h4>Ankit reviews my test infrastructure</h4><p>Thirteen comments. The fake cursor I had built returned the first row forever.</p></div></li>
<li class="reveal"><time>12 Jun 2026</time><div><h4>I withdraw the shadow table swap</h4><p>Five reasons it was a bad idea, and a sixth: the problem it solved had already been fixed.</p></div></li>
<li class="reveal"><time>3 Jul 2026</time><div><h4>The first cron pull request merges</h4><p>Named constants. Thirty eight days into the coding period.</p></div></li>
<li class="major reveal"><time>5 Jul 2026</time><div><h4>Midterm: passed, and "go bigger"</h4><p>I sent fourteen project ideas and asked which one omegaUp needed. Juan Pablo picked the cron control plane, then health checks and model training.</p></div></li>
<li class="major reveal"><time>13 Jul 2026</time><div><h4>The control plane starts</h4><p>A parent issue, then tables, data access, the runner and the admin API opened in one day, each as its own pull request.</p></div></li>
<li class="reveal"><time>14 Jul 2026</time><div><h4>System settings finally closes</h4><p>The admin page merges, five and a half months after I opened it, and carries an unmerged pull request into main with it. I start marking stacked pull requests as drafts.</p></div></li>
<li class="reveal"><time>28 Jul 2026</time><div><h4>The tables merge</h4><p>Fifteen days after opening. Everything else in the project was waiting on this.</p></div></li>
<li class="reveal"><time>27 Jul to 3 Aug</time><div><h4>Projects two and three</h4><p>Model training and problem health checks, opened as stacks behind the control plane.</p></div></li>
<li class="major reveal"><time>19 Aug 2026</time><div><h4>The runner merges</h4><p>The keystone. The ranking job went through it twenty minutes later, and the other jobs over the next three days. From 22 August every cron job on omegaUp records its runs.</p></div></li>
<li class="reveal"><time>24 Aug 2026</time><div><h4>Coding period ends</h4><p>Twenty two pull requests merged inside it, ten of them in the last two weeks.</p></div></li>
<li class="era"><span>after</span></li>
<li class="major reveal"><time>29 Aug 2026</time><div><h4>The admin page merges</h4><p>Forty six days after I opened it. Three pull requests merged that day.</p></div></li>
<li class="reveal"><time>2 Sep 2026</time><div><h4>The review that changed the number</h4><p>Juan Pablo finds that the model score I record as MAP is not MAP. Four findings, four fixes, a test for each.</p></div></li>
<li class="reveal"><time>17 Sep 2026</time><div><h4>The health check job merges</h4><p>And the next day, guarded model training.</p></div></li>
<li class="reveal"><time>2 Oct 2026</time><div><h4>Rerun gets split</h4><p>One pull request becomes a stack of small ones at the maintainer's request.</p></div></li>
<li class="major reveal"><time>7 Oct 2026</time><div><h4>Health checks done</h4><p>The findings view merges and closes the issue. A school matching fix from February merges the same day, after seven months.</p></div></li>
<li class="reveal"><time>now</time><div><h4>Still going</h4><p>Rerun is in review. What comes after it is on <a href="after-gsoc.html#next">After the summer</a>.</p></div></li>
</ul>

## The same thing as a chart {#waiting}

{{chart waiting | Every pull request from the coding period onwards. The shaded band is the coding period.}}
