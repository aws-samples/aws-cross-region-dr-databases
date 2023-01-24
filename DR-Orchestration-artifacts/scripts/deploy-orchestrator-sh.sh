#!/bin/bash

# To PACKAGE the lambda functions with requirements use this script
# Run from the root (DR-Orchestration-artifacts) directory:
# bash scripts/deploy-orchestrator-sh.sh
echo `date` starting

mkdir build
for path in lambda_function/*; do
  echo `date` path
  if [ -d "$path" ]; then
    dir=$(basename "$path")
    echo "Packaging: ${dir}"
    mkdir -p build/$dir
    cp -r $path/* build/$dir/
    pushd build/$dir
    zip $dir.zip *.py
    if [ -f "requirements.txt" ]; then
      pip3 install -r requirements.txt -t packages --no-cache-dir
      pushd packages
      zip -r ../$dir.zip .
      popd
    fi
    popd
    cp build/$dir/$dir.zip lambda_function
  fi
done
rm -rf build
