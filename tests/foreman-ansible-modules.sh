#!/bin/sh

FAM_DIR=$(mktemp -d)
git clone --depth=1 https://github.com/theforeman/foreman-ansible-modules.git ${FAM_DIR}
pip install ansible
python ${FAM_DIR}/vendor.py ./apypie/*.py > ${FAM_DIR}/plugins/module_utils/_apypie.py
make -C ${FAM_DIR} test-setup test-crud
