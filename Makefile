.PHONY: check-codestyle codestyle

check-codestyle:
	bash ./bin/codestyle/_check_codestyle.sh -s

codestyle:
	pre-commit run
