#!/usr/bin/env bash
# Convenience launcher for environments without pip installed globally.
# Usage: ./run.sh --help  |  ./run.sh probe --model gpt-6-luna
set -euo pipefail
cd "$(dirname "$0")"
exec python3 -c "import sys; sys.path.insert(0, 'src'); from ai_cost_monitor.cli import main; sys.exit(main())" "$@"
