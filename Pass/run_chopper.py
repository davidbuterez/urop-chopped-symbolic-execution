#!/usr/bin/env python
import subprocess
import argparse
import sys

def main(main_args):
  # Initialize argparse
  parser = argparse.ArgumentParser(description='Runs chopper on the given file')

  parser.add_argument('bcfile', help='target bitcode file')
  parser.add_argument('target', help='target function')

  # Dictionary of arguments
  args_orig = parser.parse_args(main_args)
  args = vars(args_orig)

  cmd = ['/home/davidb/llvm-3.4/llvm-cmake/bin/opt', '-load', 'ShortestPathPass/ShortestPathPass.so', '-shortestPath', '-target', args['target'], '-disable-output', args['bcfile']]
  fn_to_skip = subprocess.check_output(cmd).decode('utf-8').strip().replace(' ', ',')

  chopper_cmd = ['/home/davidb/chopper/klee_build/bin/klee', '-libc=klee', '--posix-runtime', '-search=dfs', '-skip-functions=' + fn_to_skip, args['bcfile']]
  subprocess.Popen(chopper_cmd)

if __name__ == '__main__':
  main(sys.argv[1:])