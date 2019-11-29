#!/bin/sh

echo 'Checking for conda...'
command -v conda >/dev/null 2>&1 \
    || { echo >&2 "conda is required, but not installed (or not in path). Aborting."; exit 1; }
echo 'Conda is available'
conda --version
echo

echo 'Available conda environments'
conda env list