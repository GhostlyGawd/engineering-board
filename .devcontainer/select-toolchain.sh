#!/bin/sh
set -eu

runtime_root=/opt/engineering-board-runtime
selected=linux-x86_64
native_path=

if grep -Eq '(^|[[:space:]])asimd([[:space:]]|$)' /proc/cpuinfo; then
  selected=linux-arm64
  native_path=/opt/engineering-board-native/usr/bin
  GIT_EXEC_PATH=/opt/engineering-board-native/usr/lib/git-core
  export GIT_EXEC_PATH
fi

ln -sfn "${runtime_root}/${selected}" "${runtime_root}/current"
PATH="${runtime_root}/current/bin:${runtime_root}/current/python-tools/bin:${runtime_root}/current/node/bin:${runtime_root}/current/node-tools/node_modules/.bin${native_path:+:${native_path}}:${PATH}"
export PATH
exec "$@"
