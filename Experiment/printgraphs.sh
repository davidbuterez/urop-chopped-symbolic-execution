#!/usr/bin/env zsh

LLVM_DIS="/home/davidb/llvm-3.4/llvm-cmake/bin/llvm-dis"
OPT="/home/davidb/llvm-3.4/llvm-cmake/bin/opt"
CLANG="/home/davidb/llvm-3.4/llvm-cmake/bin/clang"

SOURCE=$1
FILENAME="${SOURCE%%.*}"

# Generate bitcode and human readable IR
"$CLANG" -emit-llvm src/"$SOURCE" -c -o out/"$FILENAME".bc
"$LLVM_DIS" out/"$FILENAME".bc -o assembly/"$FILENAME".ll

# Generate CFG .dot files and viewable .ps (images)
cd cfg; "$OPT" -dot-cfg ../out/"$FILENAME".bc >/dev/null
for dotfile in *;do dot -Tps "$dotfile" -o "img/$dotfile.ps" >/dev/null;done
cd ..

# Generate Call Graph .dot files and viewable .ps (images)
cd call-graph; "$OPT" -dot-callgraph ../out/"$FILENAME".bc >/dev/null
for dotfile in *;do dot -Tps "$dotfile" -o "img/$dotfile.ps" >/dev/null;done
cd ..