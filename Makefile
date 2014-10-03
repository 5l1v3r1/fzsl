SHELL = /bin/bash
VIRTUALENV ?= /usr/bin/env virtualenv

ACTIVATE = source virtualenv/bin/activate
REQUIREMENTS = $(shell cat requirements.txt)
TESTS = $(wildcard test/*.py)

.PHONY: test

all: virtualenv

virtualenv/bin/python:
	$(VIRTUALENV) virtualenv

virtualenv: requirements.txt virtualenv/bin/python
	@if [ -n "$(REQUIREMENTS)" ]; then \
		$(ACTIVATE); pip install $(REQUIREMENTS); \
	fi

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

clean:
	rm -rf virtualenv
	rm -rf build
