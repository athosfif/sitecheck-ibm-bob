#!/bin/zsh
set -eu
cd "$(dirname "$0")/.."
python3 tools/reproduce_demo.py
python3 -m unittest discover test
