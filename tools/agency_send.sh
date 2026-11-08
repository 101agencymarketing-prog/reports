#!/usr/bin/env bash
# usage: agency_send.sh <telegram.txt> <REPORT_KEY>
set -euo pipefail
ENC=$(openssl enc -aes-256-cbc -pbkdf2 -iter 100000 -salt -a -A -pass "pass:$2" < "$1")
gh api -X POST repos/101agencymarketing-prog/reports/actions/workflows/agency.yml/dispatches -f ref=main -f "inputs[enc]=$ENC"
echo "dispatched"
