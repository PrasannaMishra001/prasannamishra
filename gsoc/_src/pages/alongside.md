---
title: Work alongside the main project
description: Three frontend pieces that merged during GSoC 2026 at omegaUp: navigation menus built from one configuration, a reusable view unavailable page, and a system settings feature.
---

<p class="lede">Three pieces of work ran next to the cron project during the summer. None of them was in my
proposal. Each started as a small request in a review and turned into something the rest of the site can
reuse.</p>

## The navigation menus {#navbar}

This began in April as an issue about the Help menu, which was a list of plain links. I gave each entry an
icon, a title, and one line saying what it is.

{{pair shot/help-before.jpg | before | shot/help-after.png | after | The Help menu. The second line under each title was the point: it lets the menu stay short and still say where a link goes.}}

When Juan Pablo approved that, he listed what he would like next: a reusable component for one menu entry,
the same treatment for the other menus, and eventually the menus built from a configuration file. I did them
in that order.

**One component.** Eight menu entries were eight copies of the same markup. I extracted one component and
rendered the menu from a list. In review I was asked to mark links that leave the site. I derive that from
the address, so a new entry gets the marker without anyone remembering to ask for it. Doing that turned up a
small inconsistency: some external links were missing the attributes that stop the new page reaching back
into the old one, and some internal links had them. The component now decides.

**One configuration.** Every entry in every menu now lives in one file, with an optional rule for who sees
it.

```ts frontend/www/js/omegaup/components/common/navbarMenus.ts
export function visibleEntries(
  entries: NavbarMenuEntry[],
  access: NavbarAccess,
): NavbarMenuEntry[] {
  return entries.filter((entry) => !entry.visible || entry.visible(access));
}
```

That is the whole of the visibility logic. The template used to be full of conditions. Now it filters once
and renders what is left.

{{gallery shot/menu-contests.png :: Contests ;; shot/menu-courses.png :: Courses ;; shot/menu-ranking.png :: Ranking ;; shot/menu-help.png :: Help || Four of the five menus, all rendered from the same file. Click any of them to look closer.}}

### What review changed {#navbar-review}

The clearest example of what a review is for is the Problems menu. I had kept a collapsed "Create problem"
submenu, and inside it two entries reading "Create zip file" and "I have a zip file". Those names make sense
only if you already know what they do.

{{pair shot/menu-problems-submenu.png | with the submenu | shot/problems-after.png | what merged | Juan Pablo first asked whether the submenus could go, to keep the configuration simple. Then, once titles had a second line to explain them, he asked for names that tell the two ways of creating a problem apart.}}

### A lesson about stacks {#navbar-stack}

These were three pull requests stacked on each other. The middle one never got a review of its own. The top
one was reviewed and squash merged first, which carried the middle one's changes into main with it, so I
closed the middle one as having nothing left to merge.

Nothing was lost. But it was the second time a stack of mine had merged out of order, and it is why every
stacked pull request I open now starts with a note saying where it sits and what has to land first.

## A page for "this is switched off" {#view-unavailable}

During the system settings review, Juan Pablo wrote that he would like a generic "view unavailable"
component that the server could control, so that every disabled feature looked the same. The easy version
would have been to write that message into the one page that needed it. I built the component.

{{pair shot/unavailable-in-page.png | with its own message and icon | shot/unavailable-es.png | the default, in Spanish | The heading and the message come from the translation files, so the page arrives in whatever language the reader is already using.}}

After it merged he noticed something I had missed. The way I had wired it in, with an entry file specific to
the IDE and its message written inside, meant the next disabled page would need a copy of that file. A
follow up made the entry generic and moved the message to the server. It merged seven hours after I opened
it.

## System settings {#system-settings}

This is the oldest thread on the page. In January I asked to work on an issue: let an admin switch the
embedded IDE off without a redeploy.

My first attempt was one pull request with a new table, its data access classes, two endpoints, an admin
page and all the checks: 994 lines across 36 files. I was asked to split it, and it became four.

{{video system-settings | Switching the IDE off as an admin, and what a user sees afterwards. | l}}

The table merged in two days. The data access layer waited four months for a first review and then merged
within a day of getting one. The admin page merged in July, during the coding period, five and a half months
after I opened it.

### The one that merged without merging {#out-of-order}

The endpoints were the third piece. The admin page was built on top of that branch. I did not mark the page
as a draft, so from the outside it looked ready on its own, and when it was approved and squash merged it
carried the endpoints into main with it. The endpoint pull request was left open with nothing in it that
main did not already have.

That was my mistake and I said so on the pull request. A change that depends on another one should be a
draft, and should say so in its first line. Everything I have stacked since does both.

### What I took from the reviews {#settings-review}

Three things from this thread shaped how I wrote the cron project a few weeks later.

Database access goes in the data access layer, with no exceptions, and a table merges before the code that
reads it. That is why every table in the control plane is its own pull request.

A value that is read on every page and changed almost never should be cached and exposed once, in the
payload every view already receives, not fetched by each page that wants it.

And a component should only announce what happened. The page script that owns the data makes the request.

## The pull requests {#pull-requests}

### Navigation {#navbar-prs}

{{records navbar}}

### View unavailable {#unavailable-prs}

{{records unavailable}}

### System settings {#settings-prs}

{{records settings}}
