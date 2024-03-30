
build:
	(cd boptest-service && docker-compose build)

build-nocache:
	(cd boptest-service && docker-compose build --no-cache)

remove-image:
	docker-compose rm -sf

run-many :
	$(MAKE) run-many-detached
	$(MAKE) provision
	(cd boptest-service && docker-compose logs -f web worker)

run :
	$(MAKE) run-detached
	$(MAKE) provision
	(cd boptest-service && docker-compose logs -f web worker)

bash:
	$(COMMAND_RUN) --detach=false ${IMG_NAME} /bin/bash -c "bash"

run-detached:
	(cd boptest-service && docker-compose up -d web worker)

run-many-detached:
	(cd boptest-service && docker-compose up -d --scale worker=${NUM} web)

provision:
	(cd boptest-service/provision && docker-compose run --no-deps provision python3 -m boptest_submit ../boptest/testcases/${TESTCASE})

stop:
	(cd boptest-service && docker-compose down)

compile_testcase:
	(cd boptest-service/boptest/testing && make compile_testcase_model TESTCASE=${TESTCASE})

.PHONY: build run run-detached remove-image stop provision
