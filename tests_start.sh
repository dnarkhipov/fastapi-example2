#!/usr/bin/env bash

set -xe

export TESTING=True

pytest --cov=app --cov-report=term-missing tests "${@}"
