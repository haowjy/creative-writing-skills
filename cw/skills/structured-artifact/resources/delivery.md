# HTML Delivery

Deliver ready-to-open static output with its required assets. A build step is
fine; the reader should not need to run it. Use relative links and verify the
entry HTML works from `file://`. If the brief requires a server, provide the
command that starts it and the URL; a server started during your session may
stop when the session ends.

Under `file://`, browsers can block external module scripts, `fetch` of local
files, and workers. Inline data and scripts or choose a file-compatible build
rather than assuming any static build will work locally.

Embed or include assets needed offline. CDN scripts, remote fonts, images,
and runtime imports are network dependencies, even in a single HTML file;
disclose any that remain. Check library APIs against their current docs.

## Verify the delivered artifact

Check the delivered output in a browser, not just the development preview.

- Names, claims, figures, and relationships match the source material.
- The initial view communicates the main point without requiring clicks.
- At a narrow viewport (around 375px), text is readable and visuals remain
  usable. Large diagrams can have their own navigable viewport.
- Text, images, diagrams, and links render correctly, and the console shows no
  errors. Exercise any controls, including keyboard access and visible focus.
- Check contrast in every supported theme, including embedded content, and
  reduced-motion behavior when motion is used.
- If offline use is promised, test with networking disabled.

Report checks you could not perform.
