SHELL = /bin/bash
VIRTUALENV ?= /usr/bin/env virtualenv

ACTIVATE = source virtualenv/bin/activate
REQUIREMENTS = $(shell cat requirements.txt)
TESTS = $(wildcard test/test_*.py)
VERSION = $(shell python setup.py --version)
MODULE_FILES = $(wildcard fzsl/*.py) bin/fzsl etc/fzsl.bash etc/fzsl.conf

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

dist/fzsl-$(VERSION).tar.gz: virtualenv $(MODULE_FILES)
	python setup.py sdist

dev-install: dist/fzsl-$(VERSION).tar.gz
	$(ACTIVATE); pip install --no-index dist/fzsl-$(VERSION).tar.gz

clean:
	rm -rf virtualenv
	rm -rf build
