# Project Makefile

PYTEST=./scripts/run_tests.sh

.PHONY: test clean

default: test

# Run the Python test suite
test:
	$(PYTEST)

clean:
	rm -rf build *.vvp cpu64_tb
