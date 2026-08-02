#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPOSITORY_ROOT=$(CDPATH= cd -- "$PROJECT_DIR/../.." && pwd)
ELAN_HOME="$PROJECT_DIR/.elan"
export ELAN_HOME
PATH="$ELAN_HOME/bin:$PATH"
export PATH

if [ ! -x "$ELAN_HOME/bin/lake" ]; then
  echo "Pinned local Lean toolchain is missing at $ELAN_HOME" >&2
  exit 2
fi

cd "$PROJECT_DIR"
lake build
exec .lake/build/bin/sft-verify \
  "$REPOSITORY_ROOT" \
  "$PROJECT_DIR/reports/whole_model_validation.json"
