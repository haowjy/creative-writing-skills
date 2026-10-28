# Cold Read

A reader who wasn't part of the work checks durable prose for what its
writer can't see: the labels, links, and reasons that only make sense with
the work's context. Commission one for new or rewritten prose that
outlives the work (KB pages, `AGENTS.md` and `.context/`, `docs/`, PR
bodies); deletions and link fixes don't need one.

## Commissioning

Spawn `@cold-reader`, one per tree you changed. Pass only the paths and
each page's reader, as text: no summary of the work, no reasons for the
changes, no labels from the work even as examples of what to flag, and no
attached file content. Anything more leaks the context the check depends
on.

## Acting on Findings

You hold the context the reader lacks, so you judge each finding. In page
prose, rewrite every work-local label, every link into a work directory,
and every reason only the originating conversation explains, without
changing the settled meaning. A cold reader also asks for detail the page
doesn't owe; that is a rejection, not a rewrite. List rejections in your
report, one line each, grouped by reason.
