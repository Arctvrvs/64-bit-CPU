#!/bin/sh
# Run the Python unit tests with optional coverage output
if python - <<'PY'
import importlib.util
import sys
sys.exit(0 if importlib.util.find_spec('pytest_cov') else 1)
PY
then
    pytest --cov=rtl --cov=tb --cov-report=term-missing -q "$@"
else
    pytest -q "$@"
fi

