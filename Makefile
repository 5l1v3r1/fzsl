SHELL = /bin/bash

PYTHON_VERSION ?= $(shell python -c 'import sys;print("%d.%d" % (sys.version_info[0], sys.version_info[1]))')
VIRTUALENV ?= /usr/bin/env virtualenv

ACTIVATE = source virtualenv$(PYTHON_VERSION)/bin/activate
REQUIREMENTS = $(shell cat requirements.txt)
TESTS = $(wildcard test/test_*.py)
VERSION = $(shell python setup.py --version)
MODULE_FILES = $(wildcard fzsl/*.py) bin/fzsl etc/fzsl.bash etc/fzsl.conf

.PHONY: test dist

all: virtualenv$(PYTHON_VERSION)

dist: dist/fzsl-$(VERSION).tar.gz


virtualenv$(PYTHON_VERSION): requirements.txt
	@$(VIRTUALENV) --python=python$(PYTHON_VERSION) virtualenv$(PYTHON_VERSION)
	@if [ -n "$(REQUIREMENTS)" ]; then \
		$(ACTIVATE); pip install $(REQUIREMENTS); \
	fi

test: virtualenv$(PYTHON_VERSION)
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

dist/fzsl-$(VERSION).tar.gz: virtualenv$(PYTHON_VERSION) $(MODULE_FILES) setup.py
	python setup.py sdist

dev-install: dist/fzsl-$(VERSION).tar.gz
	$(ACTIVATE); pip install --no-deps \
		--upgrade --force-reinstall --no-index dist/fzsl-$(VERSION).tar.gz

clean:
	rm -rf virtualenv[23]*
	rm -rf build
	rm -rf dist
	rm -rf fzsl.egg-info
