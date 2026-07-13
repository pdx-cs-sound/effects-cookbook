Effects Cookbook: Understanding Digital Audio Effects
Ed Norris and Bart Massey 2026

## Python

The project targets Python 3.14 (see `.python-version`). The teaching code in `code/` is
standard library only and runs on any modern Python 3; the pinned version is for
reproducibility of the docs build and tests, not because the code needs it.

Never rely on a bare `python3` — it means whatever is first on PATH today. Use the project
virtualenv by path instead:

```sh
./env/bin/python3 ...
./env/bin/mkdocs serve
```

To see what any terminal's bare `python3` actually is:

```sh
which -a python3
python3 -c 'import sys; print(sys.executable, sys.version)'
```

### Recreate the environment

The virtualenv (`env/`, gitignored) symlinks to the Python it was created from, so a
Homebrew upgrade can break it. Recreating it is cheap:

```sh
rm -rf env
/opt/homebrew/bin/python3 -m venv env
./env/bin/pip install -r requirements.txt
```

## Build and test

```sh
./env/bin/mkdocs serve                      # live-preview the site at localhost:8000
python3 -m unittest discover -s code        # run the code tests (stdlib only)
./env/bin/mkdocs build                      # build the static site into site/
python3 code/check_embeds.py                # verify raw-HTML embeds in site/ resolve
python3 code/make_figures.py                # regenerate the SVG figures
python3 code/make_demos.py                  # regenerate the audio demos
```

Pushing to `main` publishes the site via GitHub Actions. The workflow runs the tests and
the embed check first; a failure in either blocks the deploy.
