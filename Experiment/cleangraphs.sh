#!/usr/bin/env zsh

cd assembly; rm *; cd ..
cd call-graph; rm * >/dev/null 2>&1; cd img; rm *; cd ../..
cd cfg; rm * >/dev/null 2>&1; cd img; rm *; cd ../..
cd out; rm *; cd ..