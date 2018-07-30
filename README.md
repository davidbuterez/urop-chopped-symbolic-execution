There is a Git repository which contains a single C source file: https://github.com/davidbuterez/password-example
This repo is to be used to get example diffs.

In the 'Experiment' folder there is currently a simple C source file, 'password.c'. There is a script to generate CFG and Call Graphs (saved as images). See 'Description.txt' for more details.

Experiments for a shortest path pass and similar ideas should use the files in 'Experiment'.

Current format to run chopper with the output from the pass:

```
chopper --max-time=900 --max-memory=8192 --output-dir=out-chopper -libc=uclibc --posix-runtime -simplify-sym-indices -search=nurs:covnew -split-search -skip-functions=$(opt -load ../../../Pass/ShortestPathPass/ShortestPathPass.so -shortestPath -target get_fts_info_name -file assembly.bc -disable-output LINKED.bc | sed -e 'H;${x;s/\n/,/g;s/^,//;p;};d') LINKED.bc -sym-args 0 8 10
```

