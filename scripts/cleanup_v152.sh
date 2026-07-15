#!/usr/bin/env bash
set -euo pipefail

rm -f \
  opsready_lab/services/assessment_agent.py \
  tests/test_assessment_agent.py \
  docs/ASSESSMENT_AGENT_SETUP.md

echo "Legacy assessment-generator files removed."
