# This path is a permanent link

`https://prasannamishra001.github.io/prasannamishra/gsoc/` was submitted to
Google Summer of Code 2026 as the permanent record of that work, on
24 August 2026. The submission cannot be edited afterwards, and GSoC archives
the link publicly.

So this directory has to keep working for as long as possible.

## Do not

- rename this repository (`prasannamishra`)
- rename the GitHub account (`PrasannaMishra001`)
- rename or move the `gsoc/` directory
- delete or make this repository private
- turn off GitHub Pages
- rename `index.html`, or remove the section ids inside it. Old links point at
  `index.html#summary`, `#architecture`, `#pull-requests` and the rest, and
  `report.html` redirects to them.

## If the portfolio is ever rebuilt

Redesign everything else freely, but leave `gsoc/index.html` reachable at this
exact path. If the new site cannot keep the files here, put a redirect at
`gsoc/index.html` pointing at wherever the content moved, rather than deleting
it.

The content is also published at
`https://prasannamishra001.github.io/gsoc-2026-omegaup/`, so if this copy is
ever lost that repository still has an older version of it.

## How the pages are made

The pages are generated. Do not edit the `.html` files by hand, because the next
build overwrites them.

    python3 gsoc/_src/build.py

- `_src/pages/*.md` is the writing, one file per page.
- `_src/records.py` has one entry per pull request: what it changed and what
  review changed about it. A new pull request needs an entry here and a place in
  `GROUPS` and `ERAS`, or the build stops and says which number is missing.
- `_src/data/*.json` is the list of pull requests and issues with their dates.
- `_src/diagrams.py` draws every diagram and chart as SVG.
- `quartz.css` and `quartz.js` are the look and the behaviour, and
  `pr-status.js` refreshes statuses and counts from the GitHub API in the
  browser, so merged pull requests show as merged without a rebuild.

The build needs Python 3 with `markdown` and `pygments`.
