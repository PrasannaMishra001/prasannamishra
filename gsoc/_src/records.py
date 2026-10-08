"""One entry per pull request: what it changed and what review changed about it.

`name` is the short label used in charts, `title` replaces the GitHub title
where that one is hard to read, `text` is the body, and `review` is a list of
(reviewer, what they asked and what came of it).
"""

from build_media import fig, vid

R = {}


def add(number, name, text, review=None, title=None, media='', hide_size=False):
    R[number] = {'name': name, 'text': text, 'review': review or [], 'title': title, 'media': media,
                 'hide_size': hide_size}


JP = 'Juan Pablo'
ANKIT = 'Ankit'

# ------------------------------------------------------------------ 2025

add(8412, 'contest dates', '''
My first pull request, and for a long time my oldest open one. The contest list printed raw date strings.
Now each tab says what a person would say: "Ends in 3 hours", "Starts in 5 days", or the full date with the
month spelled out once it is more than fifteen days away. The exact time stays available as a tooltip.

It took six months to merge, and most of that was my own doing. I stepped away, the branch was deleted,
and in January I rebuilt the change on top of current main.
''', [
    (JP, 'pointed out that my first version built the sentences in English inside the component, which '
         '<q>would work fine if we only displayed information in English</q>. Every string went into the '
         'translation files, and the logic moved into <code>time.ts</code> where the rest of the date code lives.'),
    (JP, 'later asked for a days format between two and fifteen days, with singular forms, and sent the '
         'wording he wanted in English, Spanish and Portuguese along with test contests for the bootstrap data.'),
], title='Human readable and relative contest dates', media=vid('contest-dates', 'The three tabs after the final review round.', 'm'))

add(8426, 'contest buttons', '''
The first one to merge, five days after I opened it. The icon and label on the contest card buttons sat at
different heights because the text was wrapped in paragraph tags. I removed the wrappers and gave every button
the same alignment classes.
''', [
    (JP, 'asked for two more things while I was in there: white hover text on the green Scoreboard button, '
         'and both buttons the same size.'),
], title='Fix contest button alignment', media=fig('shot/contest-buttons.png', 'The buttons after the review changes.', 's'))

add(8599, 'navbar hover', '''
Hover effects for the navbar, dropdowns that open on hover on desktop, and the profile completion percentage
printed inside its progress bar. It went through four rounds of review over six weeks.

My first two attempts used JavaScript listeners, and each one had a state bug: two menus open at once, or a
menu that would not close. The version that merged is CSS only. A <code>:has(.dropdown.show)</code> rule
switches hover off while a menu is clicked open, and an invisible strip under each toggle covers the gap the
pointer has to cross.
''', [
    (JP, 'listed what was wrong with the listener approach and asked <q>What do you think about removing this '
         'block of code and using a different approach based on a pure CSS?</q>'),
], title='Navbar hover effects, hover dropdowns and profile progress',
    media=vid('navbar-hover', 'Hover dropdowns closing when the pointer moves to another menu.', 'm'))

add(8743, 'navbar draft', '''
A draft I opened by mistake from the wrong branch and closed about ninety seconds later. The same work went
onto #8599.
''', title='Navbar hover fixes, opened by mistake')

# ------------------------------------------------------------------ January 2026

add(8736, 'filters toggle', '''
Problem collection pages always showed the filter sidebar. This adds a button that slides it away so the
problem table takes the full width.

I had tested the first version against an empty collection, which hid the fact that my button was taking
space from the table. Juan Pablo showed me how to fill a local collection, and getting that set up by hand
is what later became #8894.
''', [
    (JP, 'asked for the labels to go through the translation files, for the button to sit exactly where the '
         'sidebar collapses, and <q>for extra points</q> a sliding animation.'),
], title='Toggle to hide the problem filters',
    media=vid('filters-toggle', 'The final version on a populated collection.', 'm'))

add(8737, 'issue link check', '''
The workflow that checks a pull request is linked to an issue only accepted closing keywords, so a pull
request that fixed part of an issue could not pass. Now, when GitHub reports no linked issue, the check reads
the description for issue references and passes if one of them is assigned to the author.
''', title='Let the issue link check accept non closing references')

add(8744, 'translation typos', '''
Fixes for the translation errors listed in #8717. Another contributor's pull request for the same issue
merged first, so I closed mine. The extra errors I had found while doing it went into #8746.
''', title='Fix translation typos in the Spanish and Portuguese files')

add(8746, 'portuguese strings', '''
While fixing the listed typos I kept finding more in the Portuguese file: Spanish words inside Portuguese
strings, whole Spanish sentences, missing accents. This corrects sixteen of them.
''', [
    (JP, 'caught that I had changed the support address to a Portuguese spelling that does not exist as a '
         'mailbox. I reverted it everywhere.'),
], title='Correct Portuguese strings that were still Spanish')

add(8775, 'printable statements', '''
Adds a printable statement type and blocks it for contestants while their contest is still running, plus a
print button on the problem page. It has not been reviewed.
''', title='Printable problem statements for contestants')

add(8794, 'GitHub sign in', '''
omegaUp had Google and Facebook sign in and no GitHub. This adds the whole flow: the OAuth exchange on the
server, a state value in a cookie that the callback must match so a forged callback is rejected, matching by
primary verified email so an existing account is reused, the button, a setup guide and tests.

It was my first change that touched the backend, the frontend, configuration and documentation together, and
the review read like a checklist I now run myself before asking for one.
''', [
    (JP, 'asked me to replace <code>Math.random()</code> with <code>crypto.getRandomValues()</code> for the '
         'state value, to drop inline styles <q>to keep our CSP effective</q>, to add an '
         '<code>aria-label</code> and then to translate it, and to document the credentials in '
         '<code>config.php</code>, which is not versioned and so cannot be committed by accident.'),
], title='GitHub sign in', media=vid('github-signin', 'Signing in with GitHub on a local instance.', 'm'))

add(8819, 'safe drafts', '''
In the problem creator a saved draft did not come back after a reload, and nothing guarded the browser
storage calls. This adds wrappers that catch a full or unavailable store, loads the draft back into the
editor, and extends drafts to cover test cases. It has not been reviewed.
''', title='Keep problem creator drafts across a reload',
    media=vid('draft-persist', 'Test cases surviving a save and a reload.', 'm'))

add(8843, 'assign own issues', '''
The assignment bot limits how many issues one person can hold, which also stopped contributors from taking
issues they had reported themselves. This lets someone with ten merged pull requests take an issue they
created, and leaves every other case to the existing bot.
''', [
    (JP, 'asked me to count only merged pull requests, lower the threshold from fifteen to ten, and cap the '
         'query at two hundred. He also caught that my documentation described two existing rules with the '
         'wrong numbers.'),
], title='Let experienced contributors take the issues they report')

add(8846, '3D badges', '''
Badges were flat images. This wraps them in a small component that tilts with the pointer, drawn as four
stacked layers to fake thickness. No library, and the badge artwork is untouched.
''', title='A tilt effect for badges', media=vid('badge-3d', '', 's'))

add(8851, 'verdict names', '''
The profile charts showed verdict codes such as AC and TLE in their tooltips. They now show the full
translated name.
''', title='Full verdict names in the profile chart tooltips', media=vid('verdict-tooltip', '', 's'))

add(8874, 'merge Fidélitas', '''
One university had been entered eighteen times under different spellings. This migration points every
reference at the official record and then removes the duplicates.

The review turned a script that would probably have worked into one that could not do damage.
''', [
    (JP, 'pointed out that my verification queries at the end did not stop the delete from running, and '
         'proposed a delete that only removes a school no table still refers to. He also explained why summing '
         'the monthly solved counts into the surviving school would double count, and asked for everything to '
         'run in one transaction.'),
], title='Merge eighteen duplicates of one school')

add(8891, 'settings, first try', '''
My first attempt at letting an admin switch the embedded IDE off: a table, its data access classes, two
endpoints, an admin page and the checks, in one pull request of 994 lines across 36 files. It was too much
to review and I was asked to split it, which became #8905, #8918, #8906 and #8938.
''', [
    (JP, '<q>Can you split this PR into smaller changes?</q> The same day I opened the first two pieces.'),
], title='System settings, as one large pull request')

add(8894, 'bootstrap data', '''
A fresh local install has empty problem collections until you set a flag by hand and run a cron script.
I had lost an afternoon to that on #8736, so this makes the bootstrap script do it. It has not been reviewed.
''', title='Fill the problem collections during local setup')

add(8905, 'settings table', '''
Part one of the split. The <code>System_Settings</code> table and its first row, and nothing else, because
omegaUp deploys a schema change before the code that reads it. Approved the day I opened it.
''', title='System settings table')

add(8906, 'settings api', '''
The endpoints for reading and updating settings. My first version ran SQL from a helper class, and it was put
on hold until that moved into a data access class, which became #8918.

This one never merged under its own number. The admin page in #8938 was built on top of this branch, and
when that was squash merged it carried this code into main with it. I closed this afterwards. The lesson was
mine: a pull request that depends on another should be a draft, and should say so in its first line.
''', [
    (JP, '<q>All database-related changes must live in the DAOs</q>. Later he suggested caching the value, '
         'since it is read on every page and changed almost never, and exposing it once through the payload '
         'every view already receives.'),
], title='System settings endpoints')

add(8918, 'settings dao', '''
The data access layer for the settings table, with typed getters and setters. It waited four months for a
first review, and was then fixed, approved and merged in a day.
''', [
    (JP, 'explained why <code>SELECT *</code> is avoided: during a deploy the code and the schema can be out '
         'of step for a moment, and an explicit column list survives that.'),
], title='System settings data access layer')

add(8938, 'settings page', '''
The admin page with the switch, and the checks that hide the IDE when it is off. This closed the feature that
#8891 had started in January.

Juan Pablo wanted the "this is switched off" message to be a component the whole site could use, which I
built separately in #9919 before finishing this one.
''', [
    (JP, 'asked for the component to only emit the change and leave the request to the page script, for a '
         'computed property in place of an inline condition, and on approving noted <q>For future changes, '
         'let\'s try to keep each PR focused on a single issue</q>.'),
], title='System settings admin page',
    media=vid('system-settings', 'Switching the IDE off as an admin, and what a user then sees.', 'm'))

# ------------------------------------------------------------------ February 2026

add(8959, 'add case form', '''
In the embedded IDE, the form for adding your own test case sat at the bottom of the list with two unlabelled
inputs and a button that said "+". It moved to the top and got labels.
''', [
    (JP, 'reviewed it three times in two days. Two of the rounds were about what to call the translation '
         "keys, after I renamed them to something with <q>less context ='(</q>."),
], title='Make adding a custom test case easier to find',
    media=fig('shot/case-selector.png', 'The form after review.', 's'))

add(8983, 'verification email', '''
Replaces the plain text account verification email with an HTML one in the reader's language. It has not
been reviewed.
''', title='A designed verification email', media=fig('shot/email-verify.png', 'As rendered in a local mail catcher.', 's'))

add(9038, 'code tester', '''
A page for writing, compiling and running code to see its time and memory, built on the endpoint the embedded
IDE already uses. It is 909 lines in one piece, I opened it without agreeing the approach first, and it has
not been reviewed. I would not open it this way today.
''', title='An online code tester page', media=vid('code-tester', '', 'm'))

add(9070, 'language detection', '''
If you paste Python into the editor while C++ is selected, a small banner now offers to switch. Detection is
a table of patterns per language, grouped into families so that C++11 against C++20 does not count as a
difference. Each language keeps its own code for the session, so switching back loses nothing.
''', [
    (JP, 'asked for the listeners to be removed in <code>beforeDestroy</code>, because the hook I had used may '
         'never run in this kind of component, then approved with <q>This feature is awesome!</q>'),
], title='Detect the language of pasted code', media=vid('language-detect', 'Pasting code in a different language from the one selected.', 'm'))

add(9087, 'templates table', '''
Opened with an unfinished description and closed the same day. #9088 is the same change described properly.
''', title='Code templates table, first attempt')

add(9088, 'templates table', '''
Part one of three for saved code templates in the editor: the table. The three parts have not been reviewed.
''', title='Code templates table')

add(9089, 'templates dao', '''
Part two: the data access layer for code templates.
''', title='Code templates data access layer', hide_size=True)

add(9090, 'templates ui', '''
Part three: the endpoints and a dialog in the editor for saving, loading, renaming and deleting templates.
''', title='Code templates endpoints and editor dialog', hide_size=True,
    media=vid('code-templates', '', 'm'))

add(9103, 'stray it.only', '''
One end to end test file had a stray <code>it.only()</code>, so for five months that file ran one test and
skipped the other eleven: registration, login, creating a course, creating a problem. Removing it exposed one
test that had broken in the meantime, which I fixed here.
''', [
    (JP, '<q>It seems that in these 5 months only one test may have broken.</q>'),
], title='Remove a stray it.only() that was skipping eleven tests')

add(9105, 'https links', '''
Six external links still used http. Juan Pablo wondered whether the file that already held the blog links
should hold every external link, and I built that before he had answered whether it belonged in this pull
request. He approved it and said it could have been its own issue, which was fair.
''', title='Use https for external links')

add(9108, 'CI credentials', '''
The teaching assistant step in CI passed a password and an API key as command line flags, where they show up
in process listings and logs. They now travel through environment variables.
''', title='Keep CI credentials out of command lines')

add(9127, 'babel polyfill', '''
The build still loaded a deprecated polyfill package that pulled in an older core library than the one the
project was configured for. Replaced with the supported entry points.
''', title='Replace a deprecated polyfill')

add(9143, 'birth date', '''
On the profile page the date of birth moved back a day after saving, for anyone west of UTC. The date was
being built from a string with the timezone stripped. It is now built from the UTC parts.

Juan Pablo could not reproduce the report at first, so I recorded it happening.
''', title='Fix the date of birth shifting by a day', media=vid('dob-bug', 'The bug, before the fix.', 'm'))

add(9212, 'pin alpine', '''
The frontend image was built from <code>alpine:latest</code>, so it could change underneath us without a
commit. Pinned to a version.
''', title='Pin the Alpine version')

add(9214, 'cypress flags', '''
Removes two experimental Cypress flags that have no effect in headless CI.
''', title='Remove experimental Cypress flags')

add(9215, 'badges query', '''
One query in the badge job was built with an f-string. Juan Pablo approved this, and then found the same fix
had just merged from another contributor's pull request, so it was closed.
''', title='Parameterize a query in assign_badges')

add(9216, 'pin redis, rabbitmq', '''
Pins the Redis and RabbitMQ images in the development compose file.
''', title='Pin Redis and RabbitMQ versions')

add(9217, 'release comment', '''
A workflow comment said "every day" above a schedule that runs on Sundays, and intentional skips were logged
as warnings. Corrected both.
''', title='Correct the release workflow comment and annotations')

add(9218, 'lazy boto3', '''
The migration script imported an AWS library at the top, so it failed even for <code>--help</code> on a
machine without it. The import moves into the one function that uses it.
''', title='Import boto3 only where it is used')

add(9219, 'mysql timeouts', '''
Raises two very short MySQL timeouts in the development compose file that caused dropped connections locally.
''', title='Relax the MySQL timeouts for development')

add(9220, 'restart policy', '''
Every service restarted forever on failure, so a container crashing on start still showed as up. Changes the
policy so a broken service stays down and visible.
''', title='Stop crashed services restarting forever')

add(9222, 'slow query log', '''
Turns on the MySQL slow query log in development, so a slow query is visible before it ships.
''', title='Enable the slow query log in development')

add(9224, 'IN clause', '''
The coder of the month queries built their <code>IN (...)</code> lists by joining ids into the SQL string.
This binds them as parameters. It was never reviewed, and during the summer I redid the same fix as #9900,
which merged.
''', title='Parameterize the coder of the month queries, first attempt')

add(9248, 'grader directory', '''
Every fresh <code>docker compose up</code> logged a permission error from the grader because one directory
was never created. One line in the entrypoint creates it.
''', title='Create the grader directory on startup')

add(9249, 'pin kustomize', '''
A deploy workflow installed a tool by piping a script from a moving branch into a shell. This downloads a
fixed release and checks its checksum first.
''', title='Pin kustomize and verify its checksum')

add(9250, 'school matching', '''
Creating a school looked for an existing one with the autocomplete search, which matches any part of the
name, so creating "Fidelitas" could hand back "Universidad de Fidelitas". This adds an exact match.

It sat untouched for seven months and merged in a week once the maintainers picked the school cleanup back up.
''', [
    (JP, 'opened with <q>Sorry for the late review. We\'re now picking up the Schools de-duplication project '
         'again, so this PR is a good first step</q>, and asked whether country and state should be part of '
         'the match, since two schools can share a name in different places. They are now, and a school '
         'created without a location only ever matches another one without a location.'),
], title='Match schools by exact name and location')

add(9298, 'tab filters', '''
The three tabs of the contest list shared one filter, so choosing "only recommended" on Past applied to
Current as well. Each tab now keeps its own.
''', title='Keep a filter and sort order per contest tab', media=vid('tab-filters', '', 'm'))

add(9301, 'show more', '''
"Show more contests" replaced the whole list with loading placeholders while the next page arrived. The
existing cards now stay and the new ones are appended.
''', title='Append on "show more" without clearing the list', media=vid('show-more', '', 'm'))

add(9303, 'button alignment', '''
Two small alignment fixes: the clear button in the contest search, and the GitHub sign in button losing its
label while pressed.
''', title='Button and input alignment fixes')

# ------------------------------------------------------------------ March to May 2026

add(9411, 'block GET, backfill', '''
The same gap as #9429, on a bulk mailing list endpoint. Not reviewed yet, and it now needs rebasing onto the
one that merged.
''', title='Block GET on the mailing list backfill endpoint')

add(9412, 'group roles', '''
A system role granted through a group worked, but the admin and support views did not list it, because they
only read roles granted to the user directly. Both sources are now merged.
''', title='Show system roles inherited from a group')

add(9428, 'page lower bound', '''
Endpoints with a <code>page</code> parameter accepted zero and negative numbers and answered as if you had
asked for page one. They now reject them, as <code>page_size</code> already did.
''', title='Reject page numbers below one', media=fig('shot/page-param-after.png', 'A negative page number after the change.', 'm'))

add(9429, 'block GET, clone', '''
While reading how the API routes requests I found that omegaUp decides whether an endpoint may be called
with GET by looking for words such as "create" or "update" in its name. Anything named differently was
reachable with a plain link. <code>GET /api/contest/clone/</code> created a real contest, the course
equivalent created a course, and one more recorded a user's consent to the privacy policy.

The fix adds the missing words, and an exception so that a read only endpoint with "accepted" in its name
keeps working.
''', [
    (JP, '<q>Great catch! Thank you</q>'),
], title='Block GET on endpoints that change data')

add(9432, 'clarification alias', '''
One endpoint always returned <code>contest_alias: null</code> because the value was hardcoded. I made it
return the real value. Juan Pablo looked at the history, saw nobody had needed that field in four years, and
asked me to remove it. So what merged is the opposite of the title.
''', title='Remove a field that was always null',
    media=vid('clarification', 'The response before and after.', 'm'))

add(9801, 'help menu icons', '''
The Help menu was a list of plain links. Each entry now has an icon, a title and a line saying what it is.
In approving it Juan Pablo listed what should come next: a reusable item component, the same style on the
other menus, and the menus built from a configuration file. Those became #9871 and #9968.
''', [
    (JP, 'suggested the two book entries use the authors\' names as the second line, to keep the menu compact.'),
], title='Icons and descriptions for the Help menu')

# ------------------------------------------------------------------ GSoC: groundwork

add(9883, 'cron test infrastructure', '''
The cron scripts had no shared way to be tested without a database. This adds one: a scripted cursor that
answers queries from a table of expected results and records every statement it was given, shared sample
data, and the first thirty four tests on top of it.

It is also the pull request where I learned to test my test helpers. See the review.
''', [
    (ANKIT, 'left thirteen comments. The one that mattered most: <q><code>fetchone()</code> does not consume '
            'the row — repeated calls always return <code>_current[0]</code>. The real '
            '<code>MySQLCursor.fetchone()</code> advances the cursor position.</q> Any test that read two '
            'rows would have passed while reading the same row twice. He also found that an uppercase key in '
            'the script matched nothing, and a real crash in the job when a problem had no tag votes.'),
    (JP, 'found that my path setup exposed the cron <code>database</code> package under a name another part of '
         'the repository already used, which would break those tests depending on collection order.'),
], title='Test infrastructure for the cron scripts')

add(9889, 'update_ranks tests', '''
Tests for the ranking job: how points are computed for users and schools, where the percentile cutoffs fall,
and which rank name each band gets. The later tests run the job's real SQL against an in memory SQLite
database, so they check what ends up in the table.
''', [
    (JP, 'pointed out that one of my tests only checked that an <code>UPDATE</code> had been issued: '
         '<q>A malformed query could currently pass this test</q>. I replaced it with tests that run the '
         'statement and read the result back, and unmocked a helper whose filtering rules I had been skipping.'),
], title='Tests for update_ranks')

add(9900, 'parameterized queries', '''
Three queries in the coder of the month code were assembled by pasting values into SQL. All of them now bind
their values as parameters. I ran the ranking job before and after against the same database and compared
four tables to confirm nothing else had changed.
''', title='Parameterize the coder of the month queries')

add(9901, 'typed excepts', '''
Sixteen bare <code>except:</code> blocks across the cron scripts, which also swallow a keyboard interrupt or
a deliberate exit. Each now catches <code>Exception</code>. An older attempt at this issue had been failing
checks for months, so I asked to take it over.
''', title='Replace bare except blocks')

add(9903, 'rank upsert', '''
Every night the ranking job deleted every row of the user ranking and inserted them all again. It now updates
rows in place and afterwards removes only the users who dropped out.

This replaced the "shadow table swap" I had promised in my proposal. Why I took that promise back is on the
<a href="groundwork.html#the-promise-i-took-back">groundwork page</a>.
''', [
    (JP, 'asked whether the production cron user was allowed to create temporary tables, which my first '
         'version needed. I could not see production grants, so I rewrote it to need none.'),
], title='Update the ranking in place')

add(9914, 'structured logs', '''
The jobs logged their totals inside sentences. They now also attach them as fields, so something can chart
them without parsing text. This began as a much larger change that timed every phase of every job, and
shrank to eighteen lines once the runner in #9998 did that part properly.
''', title='Structured end of run fields in the cron logs')

add(9920, 'assign_badges tests', '''
Tests for the badge job, and one fix. The job supported "pretend it is this date" by replacing
<code>NOW()</code> in each badge's query with a formatted string. It now sets a session variable. I ran the
old and new code over all 23 badges, at eight fixed timestamps and once with none, and compared who would
have earned each one. They matched in all 207 comparisons.
''', title='Tests for assign_badges')

add(9940, 'named constants', '''
The scripts excluded site admins with a bare <code>1</code> in two places. Those numbers now have the same
names they carry on the PHP side. The first of my cron pull requests to merge, on 3 July.
''', title='Name the magic numbers')

# ------------------------------------------------------------------ GSoC: alongside

add(9871, 'NavbarItem', '''
Eight entries in the Help menu were eight copies of the same markup. This extracts one component and renders
the menu from a list.
''', [
    (JP, 'asked for a marker on links that leave the site, and a Storybook story for each kind of icon the '
         'component accepts. I derive the marker from the address, so nobody has to remember to set a flag.'),
], title='A reusable navbar item',
    media='<div class="gallery reveal">' + ''.join(
        fig(f'shot/navitem-{i}.png', cap, 'l').replace('zoomable reveal', 'zoomable')
        for i, cap in ((1, 'an external link'), (3, 'a named icon'), (4, 'an icon from a set'))) + '</div>')

add(9919, 'view unavailable', '''
A single component for "this part of the site is switched off", with an icon, a title and an optional
message, in every language the site supports.
''', [
    (JP, 'asked for it to sit inside a card and be centred vertically.'),
], title='A generic "view unavailable" component')

add(9967, 'other menus', '''
The Help menu's new style applied to Contests, Courses, Problems and Ranking. It was never reviewed on its
own. #9968 was stacked on top of it and merged first, carrying this with it, so I closed this one.
''', title='The same style on the other menus')

add(9968, 'menus from config', '''
Every menu entry now lives in one configuration file with a rule for who sees it. The template filters the
list once and renders what is left.
''', [
    (JP, 'asked whether the "create" submenus could go, to keep the configuration simple, and then for '
         'clearer names on the two ways to create a problem: <q>Something like "Create Problem from ZIP" and '
         '"Create Problem from Scratch"</q>.'),
], title='Build the menus from one configuration')

add(10025, 'generic entrypoint', '''
The disabled IDE page had its own entry file with its message written into it, so the next page to be
disabled would have needed a copy. The file is now generic and takes its message from the server. Merged
seven hours after I opened it.
''', title='Make the view unavailable page reusable')

# ------------------------------------------------------------------ GSoC: control plane

add(9995, 'tables', '''
Two tables. <code>Cron_Jobs</code> lists the jobs that exist, with a schedule and a switch.
<code>Cron_Runs</code> holds one row for every execution.
''', [
    (JP, 'asked whether a run should point at its job by id. I kept the name, because a run has to be '
         'recordable for a script that is not in the registry, and history should outlive a job being renamed. '
         'He asked me to write that reasoning into the schema, which I did.'),
], title='The registry and run history tables')

add(9996, 'data access', '''
The data access layer for both tables, including "the last successful run of this job", which is what lets
the page say how fresh a job's data is. Most of its 1,345 lines are generated.
''', title='Data access for the cron tables')

add(9998, 'runner', '''
The piece everything else stands on. One context manager that a job wraps around itself. It checks the job is
switched on, takes a database lock so two copies cannot overlap, writes a "running" row, times each phase,
and on the way out records what happened and lets go of the lock.
''', [
    (JP, 'found two ways the lock could be left held: if writing the first row failed after the lock was '
         'taken, and if writing the final status failed. Both are now covered by <code>finally</code> blocks. '
         'He also noticed my description mentioned a method that was not in the diff.'),
], title='The shared runner')

add(10000, 'admin api', '''
Two endpoints for system admins: the registry with the fifty most recent runs, and one run with its phases.
''', [
    (JP, 'asked for a test that a non admin is refused on the second endpoint too, since it has its own check, '
         'and one with phases present, since the endpoint decodes them.'),
], title='The admin API')

add(10003, 'update_ranks', '''
The ranking job, wrapped in the runner. It deletes more lines than it adds, because the hand written timing
code comes out. Merged twenty minutes after the runner.
''', title='Put update_ranks through the runner')

add(10008, 'dashboard', '''
The page at <code>/admin/crons</code>: one row per job with its schedule and latest result, and one row per
recent run that opens to show the timing of each phase and the error if there was one.
''', [
    (JP, 'asked for the schedule to be shown in words next to the raw expression, for the page and the API to '
         'share one helper, and for job names and statuses to be enums. On approving: <q>I\'m sorry the '
         'human-readable date suggestion ended up requiring more work and complexity than I initially '
         'expected.</q>'),
], title='The admin page')

add(10009, 'badges, feedback', '''
The badge and feedback jobs through the runner. The badge job reports a failed badge through its return value
and carries on, so the runner gained a way to mark a run as failed without an exception.
''', title='Put assign_badges and aggregate_feedback through the runner')

add(10011, 'ranking audit', '''
Before the new ranking is committed, the job checks it. If it is empty, has a negative score, or has lost
more than half of the users who were ranked yesterday, the job raises and the transaction rolls back.
''', [
    (JP, 'noticed the table also holds rows for people ranked only as problem authors, which would have '
         'inflated yesterday\'s count and caused false alarms. Both sides now count the same people.'),
], title='Check the ranking before publishing it')

add(10021, 'dispatcher', '''
The worker that runs rerun requests. It claims one request at a time, starts the job as a child process with
a time limit, links the run that produced, and notifies whoever asked.

This pull request has had three shapes. It began as the whole rerun feature. Juan Pablo asked for it in six
pieces, and it is now the dispatcher alone.
''', [
    (JP, '<q>The dispatcher in particular contains concurrency, timeout, transaction, and failure-handling '
         'behavior that deserves to be reviewed independently from the UI and API changes.</q>'),
], title='Run queued rerun requests', hide_size=True)

add(10022, 'other jobs', '''
The two remaining scripts, model training and plagiarism detection, through the runner. With this every cron
job on omegaUp records its runs.
''', title='Put the remaining jobs through the runner')

add(10023, 'dashboard e2e', '''
An end to end test for the page. It stayed a draft behind the rerun work, I folded it into #10021, and after
the split it came back as #10277.
''', title='End to end test, first attempt', hide_size=True)

add(10048, 'dashboard v2', '''
A second pass on the page: a health card per job with its success rate and average duration, filters,
relative times, refresh every fifteen seconds, and a switch to turn a job off. It is last in the queue behind
the rerun pieces.
''', title='Health cards, filters and a switch per job', hide_size=True)

add(10155, 'request table', '''
The queue a rerun request goes into.
''', [
    (JP, 'asked for a foreign key from a request to the run it produced.'),
], title='The rerun request table')

add(10156, 'request dao', '''
Data access for the request queue. Main had gained a table without generated classes in the meantime, so
regenerating brought those in too.
''', [
    (JP, 'asked why "the active request for a job" needed an <code>ORDER BY</code> when there should only ever '
         'be one. It did not, so it went.'),
], title='Data access for rerun requests')

add(10157, 'rerun api', '''
The rerun endpoint as its own pull request. I folded it back into #10021 the same day, and it returned in
October as #10275.
''', title='Rerun endpoint, first attempt', hide_size=True)

add(10158, 'dispatcher', '''
The dispatcher as its own pull request, folded back into #10021 the same day.
''', title='Dispatcher, first attempt', hide_size=True)

add(10159, 'enable api', '''
The endpoint behind the on and off switch, split out of #10048 and folded back the same day.
''', title='Enable and disable endpoint, first attempt')

add(10275, 'rerun api', '''
The endpoint an admin's click reaches. It checks the caller, the job name, that the job is switched on and
that nothing is already queued for it, and then writes one row. It does not start anything.
''', title='An endpoint to request a rerun', hide_size=True)

add(10276, 'rerun button', '''
A button on each job row. About forty lines of its own.
''', title='The rerun button', hide_size=True)

add(10277, 'cypress', '''
One file: sign in as an admin, open the page, check the jobs are listed, press rerun, check it was queued.
''', title='End to end test for the page', hide_size=True)

# ------------------------------------------------------------------ GSoC: model training

add(10050, 'model runs table', '''
One row per training run: the score, the size of the data, the parameters, whether the model was published
and why not if it was not. It also registers the job with a weekly schedule.
''', [
    (JP, 'noticed the random seed that decides the train and test split was not stored: <q>Without it, '
         'training runs cannot be reproduced reliably or compared accurately</q>.'),
], title='The model runs table')

add(10051, 'guarded training', '''
The training job now records every run and refuses to publish a model that is too weak or clearly worse than
the one it would replace.

The review of this one changed what the number means. It is the most useful review I received all summer.
''', [
    (JP, 'found four things. A refused model still exited with success, so anything watching the process saw '
         'nothing wrong. The comparison used any published model, so a test run to a temporary file could set '
         'the bar for production. The score I was storing as MAP was not MAP. And users the model could not '
         'answer for were being left out of the average: <q>a model covering only 1% of the test cases could '
         'still report perfect scores if it gets that 1% right</q>.'),
], title='Record and guard model training')

add(10052, 'model quality view', '''
A table on the admin page showing each training run, its score, and the reason if it was held back. Open, and
the last piece before the parent issue can close.
''', title='Show model quality to admins', hide_size=True)

add(10150, 'model runs dao', '''
Data access for the model runs table, newest first.
''', title='Data access for model runs')

add(10154, 'model api', '''
The server half of #10052, split out and folded back the same day.
''', title='Model quality endpoint, first attempt', hide_size=True)

# ------------------------------------------------------------------ GSoC: health checks

add(10065, 'findings table', '''
Where findings are stored. One row per problem and check, which is what lets a finding keep the date it was
first seen.
''', title='The findings table')

add(10066, 'health check job', '''
The nightly job and its four checks. It reads the clock once at the start and uses that one timestamp for
everything, and if any single check fails the whole run fails, because skipping a check would mark its
findings as fixed.
''', [
    (JP, 'asked whether submissions made by a problem setter testing their own problem should count as judge '
         'errors. They should not, and now only normal submissions do. He also asked that a mistyped '
         'threshold be rejected before the job runs, since a nonsense value makes a check find nothing and '
         '<q>an operator typo</q> would then rewrite the history.'),
], title='The nightly health check')

add(10069, 'findings view', '''
A "problems needing attention" table on the admin page, worst first, with the newest findings at the top of
each group so a problem that broke last night is not buried under ones nobody has dealt with.
''', [
    (JP, 'asked for the labels to live in one place, since they mirror enums on the server. They are now a '
         'typed map, so adding a check without giving it a label fails the build.'),
], title='Show findings to admins')

add(10149, 'findings dao', '''
Data access for findings, split out of #10069 when Juan Pablo asked. It merged thirty four minutes after I
opened it.
''', title='Data access for findings')

add(10153, 'findings api', '''
The server half of #10069, split out and folded back the same day.
''', title='Findings endpoint, first attempt')


# ------------------------------------------------------------------ groupings

GROUPS = {
    'control': [9995, 9996, 9998, 10000, 10003, 10009, 10022, 10011, 10008],
    'rerun': [10155, 10156, 10275, 10021, 10276, 10277, 10048],
    'rerun-closed': [10023, 10157, 10158, 10159],
    'model': [10050, 10150, 10051, 10052, 10154],
    'health': [10065, 10149, 10066, 10069, 10153],
    'groundwork': [9940, 9901, 9900, 9903, 9883, 9889, 9920, 9914],
    'navbar': [9801, 9871, 9967, 9968],
    'unavailable': [9919, 10025],
    'settings': [8891, 8905, 8918, 8906, 8938],
    'b-first': [8412, 8426, 8599, 8743],
    'b-ui': [8736, 8846, 8851, 9143, 9105],
    'b-signin': [8794],
    'b-grader': [8959, 9070, 9248],
    'b-chores': [8737, 8843, 8744, 8746, 9103, 9108, 9127, 9217],
    'b-data': [8874, 9250, 9432],
    'b-security': [9429, 9411, 9412, 9428, 9215, 9224],
    'b-infra': [9212, 9214, 9216, 9218, 9219, 9220, 9222, 9249],
    'b-open': [8775, 8819, 8894, 8983, 9038, 9087, 9088, 9089, 9090, 9298, 9301, 9303],
    'after-merged': [9889, 9914, 9920, 10011, 10008, 10050, 10149, 10150, 10155, 10066, 10051, 10156,
                     10069, 9250],
    'after-open': [10275, 10021, 10276, 10277, 10048, 10052],
}

ERAS = [
    ('Before the summer: August 2025 to January 2026',
     [8412, 8426, 8599, 8736, 8737, 8743, 8744, 8746, 8775, 8794, 8819, 8843, 8846, 8851, 8874, 8891, 8894,
      8905, 8906, 8918, 8938]),
    ('Before the summer: February to May 2026',
     [8959, 8983, 9038, 9070, 9087, 9088, 9089, 9090, 9103, 9105, 9108, 9127, 9143, 9212, 9214, 9215, 9216,
      9217, 9218, 9219, 9220, 9222, 9224, 9248, 9249, 9250, 9298, 9301, 9303, 9411, 9412, 9428, 9429, 9432,
      9801]),
    ('GSoC: tests, queries and reliability', [9883, 9889, 9900, 9901, 9903, 9914, 9920, 9940]),
    ('GSoC: alongside the project', [9871, 9919, 9967, 9968, 10025]),
    ('GSoC: the cron control plane', [9995, 9996, 9998, 10000, 10003, 10008, 10009, 10011, 10022, 10023]),
    ('Rerun, and the second pass on the page',
     [10021, 10048, 10155, 10156, 10157, 10158, 10159, 10275, 10276, 10277]),
    ('GSoC: recommendation model training', [10050, 10051, 10052, 10150, 10154]),
    ('GSoC: problem health checks', [10065, 10066, 10069, 10149, 10153]),
]

ISSUE_GROUPS = {
    'control': [9992, 9993, 9994, 9997, 9999, 10002, 10004, 10007, 10010, 10018, 10019, 10020, 10047],
    'model': [10049],
    'health': [10064],
}

GROUPS['b-all'] = ERAS[0][1] + ERAS[1][1]

# What I said on threads that were not mine, in my own words.
COMMENT_NOTES = {
    7563: 'Linked an older request for language detection on paste to the issue where I was already building it.',
    7927: 'Asked to take the date of birth bug, and described what I was seeing. It became #9143.',
    8207: 'Reviewed the linked pull request and offered to help. Months later, when a newcomer asked for the '
          'issue, I summarised which parts had merged and which were stuck, and suggested agreeing a plan first.',
    8280: 'My first comment on anything to do with the cron scripts, in August 2025: a proposal to split up the '
          'school of the month query the way coder of the month had been.',
    8302: 'Asked to take a stale issue about clearer errors when uploading a problem zip.',
    8319: 'Proposed how an admin could switch the embedded IDE off. This became the system settings work.',
    8321: 'Benchmarked a slow contest query locally, reported what an index bought and what it did not, and asked '
          'which direction the maintainer preferred.',
    8381: 'Asked for the contest date bug after setting up the project for the first time. It became #8412.',
    8393: 'Offered to build the online tester and laid out two ways to do it.',
    8417: 'Asked to take the school merge request and pointed out it duplicated an older issue.',
    8514: 'Asked to take a stale documentation issue.',
    8551: 'Diagnosed a bug in converting problem zips and suggested where the fix belonged.',
    8679: 'Linked a pull request to the issue it belonged to.',
    8681: 'Asked to be reassigned a feature if its author had moved on.',
    8683: 'Closed my own duplicate issue, and stepped back when another contributor said theirs was nearly done.',
    8712: 'Pointed out that a chart design was very close to another platform\'s and suggested alternatives.',
    8717: 'Asked for the translation bug, then filed the extra errors I found as their own issue.',
    8728: 'Linked my filter toggle, and filed a separate issue for it when the original requester objected.',
    8729: 'Suggested a short recorded setup walkthrough to go with the written contributing guide.',
    8735: 'Proposed a fix for the issue link workflow and stepped back when told it was being handled.',
    8750: 'Reviewed a workflow change: a fixed page size without pagination would miss pull requests on busy '
          'issues and unassign people wrongly.',
    8847: 'Cleared up a misunderstanding about a comment I had deleted.',
    8958: 'Opened the matching change in the lint tooling repository and asked who maintains it.',
    9000: 'Reviewed a pull request from its CI logs: lint errors, missing translations and a migration problem.',
    9085: 'Pointed out that a community blog had been discussed and declined before, and asked if that still held.',
    9293: 'Asked to take over the bare except cleanup, since the existing attempt had been failing for months. '
          'It became #9901.',
    9308: 'On a fix for an issue I had filed: explained where the scroll jump came from, tested the new version, '
          'and reported a second bug with a recording.',
    9340: 'Explained that sixty two thousand extra lines in a diff came from a lock file generated by the wrong '
          'package manager, and how to undo it.',
    9351: 'Reviewed a search change and noted that prefix matching had been dropped along the way.',
    9357: 'Confirmed a validation bug and named the two other places that needed changing with it.',
    9460: 'Tried to reproduce an urgent error, could not, and pointed at a recently added catch block as the '
          'likely cause.',
    9694: 'Explained a lint failure: the file is generated, and here is the command that regenerates it.',
    9713: 'Gave the lint fix command and suggested applying the maintainer\'s review first.',
    9716: 'Explained why the linter rejects an id in that file and showed a way to do it without one.',
    9719: 'On a proposal to catch slow SQL in CI: the test data has too few rows for a query plan to mean '
          'anything, and here is one way round that.',
    9721: 'Explained that a schema file has to be regenerated after adding a migration, and gave the command.',
    9731: 'Pointed out that a diff of 162 thousand lines was line endings, which made the real change unreadable.',
    10203: 'Asked by the maintainer for context on the recommendation pipeline, I described what exists and what '
           'does not: a trained model, no scheduled training in production yet, and nothing that serves it.',
    10215: 'Corrected a proposed design for a recommendations feed. Syncing only the top few suggestions per '
           'problem can leave a user with an empty feed, because problems they have solved are filtered out '
           'first. The plan was revised and accepted.',
}
