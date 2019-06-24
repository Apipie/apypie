#!/bin/sh

FAM_DIR=$(mktemp -d)
git clone --depth=1 https://github.com/theforeman/foreman-ansible-modules.git ${FAM_DIR}
make -C ${FAM_DIR} test-setup test
