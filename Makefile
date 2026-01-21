SHELL := /bin/bash

PYDV_ENV := $(if $(PYDV_ENV),$(PYDV_ENV),/usr/workspace/$(USER)/pydv_env)

PKG_REGISTRY_URL = $(CI_API_V4_URL)/projects/$(CI_PROJECT_ID)/packages/generic/archive
DEPLOY_PATH = /usr/gapps/pydv
PYTHON_PATH = /usr/apps/weave/weave-prod-cpu/bin/python3
CI_UTILS = /usr/workspace/weave/ci_utils

RZ_GITLAB = "ssh://git@rzgitlab.llnl.gov:7999"
PROJECT = "weave/pydv.git"

RZ_TESTS_WORKDIR = /usr/gapps/pydv/wsc_tests_workdir

WHEELS_PATH = /usr/workspace/weaveci/weave/wheels/develop/public

define do_create_env
    echo "Creating venv $(PYDV_ENV)"
	if [ -d $(PYDV_ENV) ]; then rm -Rf $(PYDV_ENV); fi
	/usr/apps/weave/tools/create_venv.sh -p cpu -e $(PYDV_ENV) -v latest-develop
	source $(PYDV_ENV)/bin/activate && \
	pip install . && \
	which pytest && \
	pip list
endef

define run_pydv_tests
	# call from the top repository directory
	# arg1: full path to venv
	source $(PYDV_ENV)/bin/activate && which pip && which pytest && \
	if [ -z $(DISPLAY) ]; then \
	  xvfb-run --auto-servernum pytest --capture=tee-sys -v tests/; \
	else \
	  pytest --capture=tee-sys -v tests/; \
	fi
endef

define do_run_rz_tests
	# arg1: full path to venv
	source $(PYDV_ENV)/bin/activate && pip list && pwd
	cd tests && ln -s /usr/gapps/pydv/dev/tests/wsc_tests . && cd ..
	if [ -z $(DISPLAY) ]; then \
		xvfb-run --auto-servernum python3 -m pytest tests/wsc_tests/test_*py; \
	else \
		python3 -m pytest -v tests/wsc_tests/test_*py; \
	fi
endef

.PHONY: create_env
create_env:
	$(call do_create_env,$(PYDV_ENV))


.PHONY: run_tests
run_tests:
	@echo "Run tests...";
	$(call run_pydv_tests,$(PYDV_ENV))


.PHONY: run_rz_tests
.ONESHELL:
run_rz_tests:
	echo "Run RZ tests...RZ_TESTS_WORKDIR: $(RZ_TESTS_WORKDIR)"
	$(call do_run_rz_tests,$(PYDV_ENV))


.PHONY: release
release:
	@echo "...create a release....TAG: $(CI_COMMIT_TAG), PKG_REGISTRY_URL: $(PKG_REGISTRY_URL)"; \
	$(eval TAG=$(shell  echo $(CI_COMMIT_TAG) | sed -e "s/^pydv-//")) \
	env; \
	$(CI_UTILS)/bin/release-cli create --name "PyDV $(CI_COMMIT_TAG)" --tag-name $(CI_COMMIT_TAG); \
	tar -cvf $(TAG).tar pydv docs; \
	ls; \
	gzip $(TAG).tar; \
	curl --header "JOB-TOKEN: $(CI_JOB_TOKEN)" --upload-file $(TAG).tar.gz $(PKG_REGISTRY_URL)/$(CI_COMMIT_TAG)/$(TAG).tar.gz

.PHONY: deploy
.ONESHELL:
deploy:
	@echo "...deploy...only run from CI... ";
	$(eval TAG=$(shell  echo $(CI_COMMIT_TAG) | sed -e "s/^pydv-//"))
	wget --header="JOB-TOKEN:$(CI_JOB_TOKEN)" $(PKG_REGISTRY_URL)/$(CI_COMMIT_TAG)/$(TAG).tar.gz -O $(TAG).tar.gz
	give weaveci $(TAG).tar.gz
	$(eval GIVE_USER=$(shell echo ${USER}))
	xsu weaveci -c "sg us_cit" <<AS_WEAVECI_USER
		mkdir -p $(DEPLOY_PATH)
		cd $(DEPLOY_PATH)
		take $(GIVE_USER) -f
		chmod 750 $(TAG).tar.gz
		gunzip $(TAG).tar.gz
		tar -xvf $(TAG).tar
		rm $(TAG).tar
		mv pydv $(TAG)
		mv docs $(TAG)
		chmod -R 750 $(TAG)
		rm -f current
		ln -s $(TAG) current
		cd $(TAG)
		sed -i "s,/usr/apps/weave/weave-prod-cpu/bin/python3,$(PYTHON_PATH)," pdv
	AS_WEAVECI_USER


.PHONY: deploy_to_develop
.ONESHELL:
deploy_to_develop:
	$(eval VERSION=`cat $(CI_PROJECT_DIR)/pydv/scripts/version.txt`)
	echo "...deploy_to_develop...VERSION: $(VERSION)"
	cd pydv && rm -rf __pycache__
	rm -f $(VERSION).tar.gz
	tar -cvf $(VERSION).tar * ../docs && gzip $(VERSION).tar
	give --force weaveci $(VERSION).tar.gz
	$(eval GIVE_USER=$(shell echo ${USER}))
	xsu weaveci -c "sg us_cit" <<AS_WEAVECI_USER
		umask 027
		mkdir -p $(DEPLOY_PATH)/develop
		cd $(DEPLOY_PATH)/develop
		take $(GIVE_USER) -f
		gunzip $(VERSION).tar.gz
		tar -xvf $(VERSION).tar && rm $(VERSION).tar
		sed -i "s,/usr/apps/weave/weave-prod-cpu/bin/python3,$(PYTHON_PATH)," pdv
		cd .. && chmod -R 750 develop
	AS_WEAVECI_USER

#
# create_and_upload_wheels creates wheels and uploads to /usr/workspace/weaveci/weave...
# so that /usr/apps/weave/tools/create_venv.sh can install it from the wheels
# This is meant to be run when CI_COMMIT_BRANCH == develop.
# Temporarily updated the name since PyDV is already taken in pypi
#
.ONESHELL:
create_and_upload_wheels:
	$(eval GIVE_USER = $(USER))
	cp pyproject.toml pyproject.toml.ORIG
	sed -i 's/name = "PyDV"/name = "LLNL-PyDV"/g' pyproject.toml
	source $(PYDV_ENV)/bin/activate && \
	python3 -m build && \
	deactivate
	cp pyproject.toml.ORIG pyproject.toml
	give -f weaveci $(CI_PROJECT_DIR)/dist/*
	export TERM=xterm && export DISPLAY=:0. && \
	xsu weaveci -c "sg weaveci" <<AS_WEAVECI_USER
		umask 027
		mkdir -p $(WHEELS_PATH)
		cd $(WHEELS_PATH)
		take -f $(GIVE_USER)
		chmod -R go+rX $(WHEELS_PATH)
	AS_WEAVECI_USER
