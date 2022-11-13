#!/bin/bash
python3 -m pip install virtualenv
if [ -d .venv ] ; then
    rm -rf .venv
fi

if [ ! -f .venv/bin/python ] ; then
    python3 -m virtualenv -p python3 .venv
fi

.venv/bin/pip install --requirement=requirements.txt --upgrade --exists-action=w
