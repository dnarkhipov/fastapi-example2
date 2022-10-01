#!/bin/bash

set -ex

psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" <<-EOSQL
  -- accounts
	create role accounts login password 'dev2022';
	create database accounts owner accounts;
	\c accounts
	create extension if not exists "uuid-ossp";

  -- accounts_test
	create role accounts_tester login password 'test2022';
	create database accounts_test owner accounts_tester;
	\c accounts_test
	create extension if not exists "uuid-ossp";
EOSQL
