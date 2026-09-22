#!/usr/bin/env bash
# Exit 0 when a pull request is the day's briefing and safe to merge into main.
# Usage: REPORT_DATE=YYYY-MM-DD briefing_pr_eligible.sh "PR title" file [file...]
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "usage: REPORT_DATE=YYYY-MM-DD $0 TITLE FILE [FILE...]" >&2
  exit 2
fi

title="$1"
shift
date="${REPORT_DATE:-}"

if ! printf '%s' "$date" | grep -Eq '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'; then
  echo "skip: REPORT_DATE missing"
  exit 1
fi

if ! printf '%s' "$title" | grep -Fq "$date"; then
  echo "skip: title has no report date $date"
  exit 1
fi

if ! printf '%s' "$title" | grep -Eq '早报|preopen briefing'; then
  echo "skip: title is not a briefing"
  exit 1
fi

for file in "$@"; do
  case "$file" in
    archive/*.html|r/*.html|index.html|latest.html) ;;
    *)
      echo "skip: $file is outside the briefing allowlist"
      exit 1
      ;;
  esac
done

echo "eligible"
exit 0
