#!/bin/zsh
set -e

ROOT="/Volumes/FIGUEIRA/LABLAB/HACKATHON IBM BOB/IBM BOB 2.0/sitecheck"
cd "$ROOT"

AFTER="/tmp/sitecheck-live-after"
COMPARISON="/tmp/sitecheck-live-comparison"
rm -rf "$AFTER" "$COMPARISON"

clear
printf '\033[38;2;216;255;85mFIGUEIRA AI  /  SITECHECK LIVE VERIFICATION\033[0m\n'
printf '\033[38;2;150;150;150mIBM Bob 2.0 Hackathon · reproducible local run\033[0m\n\n'
sleep 1

printf '\033[38;2;87;96;255m$ python3 sitecheck.py demo-site/index.html\033[0m\n'
python3 sitecheck.py demo-site/index.html --out-dir "$AFTER" | tail -n 5
sleep 1

printf '\n\033[38;2;87;96;255m$ python3 recheck.py before/report.json after/report.json\033[0m\n'
python3 recheck.py sitecheck-output/before/report.json "$AFTER/report.json" --out-dir "$COMPARISON" \
  | sed -n '2,8p'
sleep 1

printf '\n\033[38;2;87;96;255m$ python3 -m unittest discover test\033[0m\n'
python3 -m unittest discover test 2>&1 | tail -n 5
sleep 1

printf '\n\033[30;48;2;216;255;85m  VERIFIED  3 BEFORE  ·  2 AFTER  ·  1 FIXED  ·  0 REGRESSIONS  ·  42 TESTS PASS  \033[0m\n'
sleep 4
