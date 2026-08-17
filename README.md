# Effects Cookbook: Understanding Digital Audio Effects

### Ed Norris and Bart Massey 2026

## Overview

See [the site](https://pdx-cs-sound.github.io/effects-cookbook/) for an introduction to the content.

For simple updates, edit a markdown file and push to `main` - this will re-publish the site through GitHub Actions.


### Where things are

| Path                            | Contents                                                                                       |
|---------------------------------|------------------------------------------------------------------------------------------------|
| `prototype/`                    | The book contents, the `docs_dir` for MkDocs.                                                  |
| `prototype/img/`                | Generated SVG figures                                                                          |
| `prototype/audio/`              | Generated WAV demos (currently not used)                                                       |
| `prototype/visualization/`      | AudioExplorer widgets and the compressor decision map.                                         |
| `code/`                         | Reference implementations, their unit tests, and the figure, demo, and embed-check scripts.    |
| `mkdocs.yml`                    | Site config. The `nav` block is the chapter order.                                             |
| `.github/workflows/publish.yml` | The publish gate: tests, build, embed check, deploy.                                           |
| `DESIGN.md`                     | Purpose, scope, page template, and the decision log (§8).                                      |
| `STYLE.md`                      | Prose rules for the pages. Rule 12 requires an adversarial pass on new prose.                  |
| `TODO.md`                       | The task list, including completed items                                                       |
| `research/`                     | Source notes, feedback logs, and voice samples. Not published.                                 |
| `site/`                         | This is a local build artifact and is gitignored. Nothing in it should be edited or committed. |

### How the pieces connect

Each effect is defined once, in a module under `code/`, and everything related to that effect is 
generated from it.  The code shown on a page is included at build time
from a module in `code/` with a `pymdownx.snippets` directive, the figures are drawn by
`code/make_figures.py` running those same modules, the WAV demos come from
`code/make_demos.py`, and the JavaScript kernels behind the interactive widgets are held to
the Python by golden tests in `code/test_worklet_ports.py`. 

Editing one function in `code/` can therefore change a page, a figure, a sound, and a test at once. Run the full local
sequence below after any change under `code/`.

### Where the work stands

All twelve chapters have drafted content in the book's flat register, but maintenance of
the flat register is a continuing process.
Despite admonitions to avoid default AI speech in `STYLE.md` and the requirement of an
adversarial pass to detect AI speech, it will creep back in.

The reader-facing status page is the [Status & scope](prototype/status.md) appendix which will be updated before handoff.

Thirty figures are embedded, which is every SVG in `prototype/img/`. Three AudioExplorers are
embedded, on the Waveforms, Tremolo, and Vibrato pages.

Four things are unfinished and are not visible from the code:

1. Citations are unverified. `prototype/status.md` carries a notice telling readers to treat
   references as leads, and the Attribution section of `TODO.md` lists what remains, including
   the Woodgate and IEC citation details and the borrowed figure that has to be redrawn.
2. The project has no license. Content and code may need different ones (DESIGN §7).
3. Audio demos for chapters 7 through 11 were deferred pending a read-through. The WAV files
   in `prototype/audio/` are no longer referenced by any page, and whether to keep them as an
   archive or delete them along with the WAV writer's tests is an open call.
4. `requirements.txt` is unpinned. It names `mkdocs-material` and nothing else, so the CI
   build tracks whatever version is current.

### Picking the work up

`TODO.md` is the working list, and its "Now" section is ordered. `DESIGN.md` §8 records why
past decisions went the way they did. The original version of this book used Claude but the AI guidance is the same for any model.  Fable was excellent at creating reusable code, like the Plot library and AudioExplorer widgets, both of which call the example code shown in the book.  The graphs themselves were usually based on a good idea and needed some tweaks from a reviewer to bring those out.  Text voice has been a consistent problem and requires vigilance - specific tics have been identified and eliminated and rules have been established to run an adversarial scan for AI-voice but it continues to creep back in.

## Updating

Run the commands below from the repository root.

**Read a page as the reader will see it, and keep editing.** The dev server rebuilds on
save, so a page open at `localhost:8000` will automatically reload.

```sh
./env/bin/mkdocs serve
```

**Confirm a change under `code/` did not break a page's code, a figure, or a widget.** The
suite is 85 tests and takes about half a second. It is standard library only, so any modern
Python 3 will run it.

```sh
./env/bin/python3 -m unittest discover -s code
```

**Find out whether a push will publish or fail.** The workflow runs these three steps in
this order and stops at the first failure. Running the same three locally reproduces the
gate.

```sh
./env/bin/python3 -m unittest discover -s code && ./env/bin/mkdocs build && ./env/bin/python3 code/check_embeds.py
```

**Check that the interactive widgets still match the Python.** The golden tests run the
JavaScript kernels under Node and compare their samples against the Python originals. They
skip silently when Node is absent, so a passing suite on a machine without Node says nothing
about the kernels. Confirm Node is installed first.

```sh
node -v
```

**Update a figure after changing the code that draws it, or the DSP behind it.** The script
writes every SVG in `prototype/img/`, and the output is deterministic. A clean `git status`
afterward means nothing moved. Any file that does show up in the diff changed because the
code changed, and the new SVG gets committed with it.

```sh
./env/bin/python3 code/make_figures.py
```

**Regenerate the WAV demos.** The script rewrites `prototype/audio/`. Nothing in the book
currently plays these files, so this is only needed if the demos are put back into use.

```sh
./env/bin/python3 code/make_demos.py
```

**Verify a hand-written HTML embed points at a file that exists.** MkDocs validates the
links it generates from Markdown, but a raw `<iframe>`, `<img>`, `<a>`, `<script>`,
`<audio>`, or `<source>` in a page is opaque to it, and a wrong relative path builds without
error and publishes a broken embed. The check walks the built site, so run `mkdocs build`
first. It prints the count it checked, names each missing target with the page holding it,
and exits 1 if there are any.

```sh
./env/bin/python3 code/check_embeds.py
```

**Work out why an included code snippet is wrong or missing.** Snippet paths in a page are
relative to the repository root, as in `--8<-- "code/delays.py:chorus"`, and the name after
the colon is a section marker in the Python file. `check_paths` is on, so a bad path fails
the build with the offending file named instead of publishing an empty code block. A path
that resolves but a marker that does not also produces an empty block, so check the marker
comments in the module when the build passes and the page is still blank.


**See whether the last push published.** Pushing to `main` triggers the workflow, which
deploys with `mkdocs gh-deploy --force` to the `gh-pages` branch. A failure in the tests, the
build, or the embed check blocks the deploy and leaves the published site at its previous
state.

```sh
gh run list --workflow publish.yml --limit 5
```

**Read the log of a failed publish.** The run ID comes from the listing above.

```sh
gh run view <run-id> --log-failed
```
