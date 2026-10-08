---
title: Before the summer
description: Prasanna Mishra's contributions to omegaUp from August 2025 to May 2026, before Google Summer of Code: GitHub sign in, endpoints that changed data on GET, language detection, and the pull requests that never got reviewed.
---

<p class="lede">My first pull request to omegaUp was on 31 August 2025. Between then and the first day of
the coding period I opened fifty six, of which twenty seven have merged. This page is those nine months,
including the part that did not go well.</p>

## How it started {#how-it-started}

I set up the project in late August 2025 and asked for a bug about how contest dates were shown. That became
my first pull request. Four days later I opened a second, a small alignment fix, and that one merged first.

{{records b-first}}

Then I disappeared for three months. I came back in December with the navbar change above and from January
I was contributing most days.

## January and February: being told how things are done here {#january}

Eighteen pull requests in the first three and a half weeks of January. Looking back, this was the month I learned the project's
rules by breaking them one at a time, and Juan Pablo was patient about it.

Every string goes through the translation files. Logic goes where the codebase already keeps that kind of
logic. Prefer a few lines of CSS to a clever script. Test against real data, not an empty page. Split large
changes. I was told each of these at least once.

{{records b-ui}}

### GitHub sign in {#github-sign-in}

The first thing I built that crossed the whole stack.

{{records b-signin}}

```php frontend/server/src/Controllers/Session.php
$sessionManager = self::getSessionManagerInstance();
$storedState = $sessionManager->getCookie('github_oauth_state');
if (is_null($storedState) || $storedState !== $state) {
    self::$log->error('Invalid GitHub CSRF token');
    throw new \OmegaUp\Exceptions\InvalidParameterException(
        'loginGitHubInvalidCSRFToken',
        'state'
    );
}
```

The check that rejects a forged callback. The server sets a random value in a cookie when it renders the
login page, GitHub hands the same value back, and if the two differ the login stops.

### Fixing data {#fidelitas}

{{records b-data}}

## The embedded IDE {#the-ide}

omegaUp has an editor where you can run code against your own test cases. Three of my changes to it merged.

{{records b-grader}}

## Workflows, translations and small repairs {#chores}

{{records b-chores}}

## Reading the API for holes {#security}

In early March I spent a few days reading how omegaUp routes API requests, to see what could go wrong.

Requests that change data are supposed to be rejected when they arrive as a GET, because a GET can be
triggered by a link or an image tag on another site. omegaUp decides which endpoints those are by looking
for words such as "create", "update" or "delete" in the endpoint's name. Anything that changes data under a
different name is missed.

I tried the ones whose names did not match. `GET /api/contest/clone/` returned 200 and created a contest.
The course version created a course. Another recorded a user's acceptance of the privacy policy.

```php frontend/server/src/ApiCaller.php
'accept', 'add', 'arbitrate', 'archive', 'associate',
'bulkcreate', 'change', 'clone', 'confirm', 'create',
'delete', 'disqualify', 'execute', 'expire', 'forfeit',
'generate', 'invalidate', 'login', 'logout', 'open',
'read', 'refresh', 'register', 'rejudge', 'remove',
'requalify', 'resolve', 'revoke', 'select', 'set',
'toggle', 'update', 'verify',
```

The list after my fix, with `accept`, `clone` and `open` added. Adding `accept` would also have blocked a
read only endpoint with "accepted" in its name, so that one is on an allow list, with a test.

I should say what this fix is and is not. It closes the holes I found. It does not change the approach, and
a list of words will miss the next endpoint somebody names differently. One more of the same kind, which I
found at the same time, is still open.

{{records b-security}}

{{pair shot/page-param-before.png | before | shot/page-param-after.png | after | Asking for page minus five. It used to answer as if you had asked for page one.}}

## The batch that mostly went nowhere {#the-batch}

On 20 and 21 February I filed fifteen issues about the development environment and CI in one go, and opened
thirteen pull requests for them: unpinned Docker images, timeouts, restart policies, a tool installed by
piping a script into a shell.

Three merged. One was approved and then turned out to duplicate another contributor's fix. Nine have never
had a reply from a maintainer.

Each one is small and I still think each one is correct. But thirteen pull requests arriving in two days
that nobody asked for is a lot to put in front of a volunteer, and four of them edit the same file, so they
cannot all merge as they are. If I were doing it again I would open one issue listing all of it and ask
which parts were wanted.

{{records b-infra}}

## Built, and never reviewed {#never-reviewed}

These are larger things I built in the same period. They work, they have recordings, and nobody has reviewed
them. In most cases I had not agreed with a maintainer beforehand that the project wanted them, and I think
that is the reason.

I am leaving them listed because they are part of what I did, and because the pattern taught me more than
the merged ones. What I do now is on [What I learned](lessons.html#checking-first).

{{records b-open}}

## What these months were for {#what-it-was-for}

Twenty one merged pull requests is what I had when the coding period started. More useful than the number
was knowing how a change gets into omegaUp: a table before the code that reads it, strings in four language
files, generated types regenerated, an issue first.

It is also where the summer's side projects came from. The Help menu change in April led to the
[navigation work](alongside.html#navbar), and the system settings feature I started in January was finished
in July, as described on [Alongside the project](alongside.html#system-settings).

And my first comment on a cron script was in August 2025, on the day I opened my first pull request. I
proposed splitting up one of the ranking queries. Nine months later that directory was my project.

## Everything from this period {#all}

{{prtable b-all}}
