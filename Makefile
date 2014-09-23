VIRTUALENV ?= /usr/bin/env virtualenv

ACTIVATE = source virtualenv/bin/activate
TESTS = $(wildcard test/*.py)

.PHONY: test

all: virtualenv

virtualenv/bin/python:
	$(VIRTUALENV) virtualenv

virtualenv: requirements.txt virtualenv/bin/python
	$(ACTIVATE); pip install $$(<requirements.txt)

test: virtualenv
	@failed="";
	@for test in $(TESTS); do \
		echo "Testing $${test%_*}"; \
		$(ACTIVATE); python $${test} --verbose; \
		if [ $$? -ne 0 ]; then \
			failed+=" $${test%_*}"; \
		fi; \
		echo;echo; \
	done
	@if [ -n "$${failed}" ]; then \
		echo "Failed tests: $${failed}"; \
	else \
		echo "All tests passed."; \
	fi




