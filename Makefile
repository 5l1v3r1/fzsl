SHELL = /bin/bash
VIRTUALENV ?= /usr/bin/env virtualenv

ACTIVATE = source virtualenv/bin/activate
REQUIREMENTS = $(shell cat requirements.txt)
TESTS = $(wildcard test/test_*.py)
VERSION = $(shell python setup.py --version)
MODULE_FILES = $(wildcard fzsl/*.py) bin/fzsl etc/fzsl.bash etc/fzsl.conf

.PHONY: test

all: virtualenv

virtualenv: requirements.txt
	@$(VIRTUALENV) virtualenv
	@if [ -n "$(REQUIREMENTS)" ]; then \
		$(ACTIVATE); pip install $(REQUIREMENTS); \
	fi

test: virtualenv
	@failed=""; \
	for test in $(TESTS); do \
		echo "Testing $${test#*_}"; \
		$(ACTIVATE); \
		python $${test} --verbose; \
		if [ $$? -ne 0 ]; then \
			failed+=" $${test}"; \
		fi; \
		echo;echo; \
	done; \
	if [ -n "$${failed}" ]; then \
		echo "Failed tests: $${failed}"; \
		exit 1; \
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
	rm -rf dist
	rm -rf fzsl.egg-info
