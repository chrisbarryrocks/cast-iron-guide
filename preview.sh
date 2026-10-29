#!/bin/sh
# Serves the built site at http://localhost:8000/cast-iron-guide/ (mirrors GitHub Pages project path)
cd "$(dirname "$0")" && .venv/bin/python build.py >/dev/null && rm -rf .preview && mkdir .preview && ln -s ../_site .preview/cast-iron-guide && cd .preview && python3 -m http.server 8000
