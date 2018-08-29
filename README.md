# urop-chopped-symbolic-execution
### Idea
Chopped symbolic execution, described in the [Chopped Symbolic Execution (ICSE 2018) paper](https://srg.doc.ic.ac.uk/publications/18-chopper-icse.html), 
is a technique that allows irrelevant parts of the code to be skipped during symbolic execution. 
Excluded portions of code are lazily executed, when needed. The tool which allows skipping function invocations is an extension of KLEE, and 
it is named [Chopper](https://github.com/davidtr1037/chopper).

For this project, we want to apply Chopper in the context of patch testing. For this purpose, I have written some tools, some of which were eventually moved to their own repositories:
- [diffanalyze](https://github.com/davidbuterez/diffanalyze) - a Python script to extract useful patch testing information from git repositories
- [patchbb](https://github.com/davidbuterez/patchbb) - a tool (scripts and an LLVM Pass) for counting updated basic blocks in git repositories
- (Current repo) - an LLVM Pass, which given some bitcode will output a list of functions to skip for Chopper

In theory, we want to reach code which is uncoverable just by KLEE. The current implementation is a result of some of the experiments that I 
managed to run during the time of the UROP. Currently, there are two strategies:
- *excludeAll* - Given a target function, we compute the shortest path from the `main` function to the target. Then, we try to exclude 
every function that is not on the shortest path. While this strategy works in theory, currently it is not very effective, as the output list is large 
and the analysis in Chopper takes too long.
- *excludeSelective* - We look at the shortest path, as before, but we try to exclude only functions that might be called from the functions on the 
path. The output set of functions is now smaller, and the time problem is avoided. The current downside is that unless the patches are cherry-picked, 
we do not observe improvements in the code coverage (not genereal enough).

## Installation
After cloning, in the main directory run:

`cmake CMakeLists.txt`

`make`

This will build the `.so` file that can then be invoked with `opt`.

## Notes
This was built and tested on LLVM 3.4, as this is the stable version that is used by KLEE.

## Usage
This pass is intended to be used with targets provided by [diffanalyze](https://github.com/davidbuterez/diffanalyze). A typical use scenario looks like this:

`opt -load <path-to-pass> -shortestPath -target <target-function-name> -file <assembly.bc> -disable-output <bitcode>`

The arguments are:
- `target` - the name of the target function
- `file` - to avoid some errors in Chopper, we require information from a previous run of KLEE or Chopper. Simply run KLEE/Chopper on the 
desired bitcode, and in the `klee-last` directory, KLEE will output an `assembly.ll` file, which can be turned to `.bc` with `llvm-as`. Alternatively, 
KLEE can output directly a bitcode file. Provide the `.bc` file as the argument.
- `bitcode` - this is the bitcode file on which you intend to run KLEE/Chopper.

If you want to format the output so that it can be directly fed into Chopper, you can run it like this (note the additional redirection to `sed`):

`opt -load ~/ShortestPathPass.so -shortestPath -target get_fts_info_name -file assembly.bc -disable-output LINKED.bc | sed -e 'H;${x;s/\n/,/g;s/^,//;p;};d'`



