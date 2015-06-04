#!/bin/bash
# Automatically install all the necessary packages to run the pipeline
#
source $(dirname $0)/env.sh

pkgs=("apputils" "denoiser" "pipeline")

for pkg in ${pkgs[@]}
do
    if [ `pip list | grep ${pkg} | wc -l` -eq 1 ]
    then
        pip uninstall -y ${pkg}
    fi

    cd ${ROOT}/packages/${pkg}
    rm -r dist
    python2 setup.py sdist
    pip install dist/*.tar.gz
done