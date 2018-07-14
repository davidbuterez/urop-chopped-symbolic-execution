#!/usr/bin/env python
import sys
import argparse
import os
import subprocess
import shlex
import shutil
import getpass
import pygit2
import json

from os.path import dirname, abspath
from termcolor import colored

class FnData:

  def __init__(self, fn_name, start, end, prototype):
    
    def trim_prototype(prototype):
      proto = prototype[:prototype.rfind('{') - 1]
      return proto[proto.find('^') + 1:]

    self.fn_name = fn_name
    self.start_line = start
    self.end_line = end
    self.prototype = trim_prototype(prototype)

class FileDiff:
  
  def __init__(self, filename, restrict):
    self.filename = filename
    self.restrict_extensions = restrict
    self.file_extension = filename[filename.rfind('.'):]
    self.fn_map = self.get_fn_names()
    self.fn_to_lines = {key: [] for key in self.fn_map.keys()}

  def get_fn_names(self):
    fn_table = subprocess.check_output(['ctags', '-x', '--c-kinds=fp', '--fields=+ne', '--output-format=json', self.filename]).decode('utf-8').strip().split('\n')
    fn_map = {}

    for obj in fn_table:
      fn_data = json.loads(obj)
      fn_map[fn_data['name']] = FnData(fn_data['name'], fn_data['line'], fn_data['end'] if 'end' in fn_data else fn_data['line'], fn_data['pattern'])

    return fn_map

  def match_lines_to_fn(self, lines):
    # matched_fn_name = None

    start, end = 0, 0

    for fn_name, fn_data in self.fn_map.items():
      for line_no in lines:
        if line_no >= fn_data.start_line and line_no <= fn_data.end_line:
          self.fn_to_lines[fn_name].append(line_no)

  # Full function information
  def print_fn_pretty(self, fn_name):
    if fn_name:
      print(colored(self.filename, 'blue') + ": " + colored(fn_name, 'green'), end='')

  # Just function name
  def print_fn_simple(self, fn_name):    
    if fn_name and fn_name != 'Global':
      first_extract = fn_name[fn_name.find(' ') + 1:]
      second_extract = first_extract[:first_extract.rfind('(')]
      print(colored(second_extract, 'green'))

  @staticmethod
  def print_lines(lines):
    print(' changed lines [', end='')
    print(*lines, end='')
    print(']')

  # Prints all the data that this object has
  def print(self, pretty):

    def select_print(pretty, fn_name, lines):
      if pretty and lines:
        self.print_fn_pretty(fn_name)
        FileDiff.print_lines(lines)
      elif lines:
        self.print_fn_simple(fn_name)

    for fn_name, lines in self.fn_to_lines.items():
      if self.restrict_extensions:
        if self.file_extension in args_orig.exts:
          select_print(pretty, fn_name, lines)   
      else:
        select_print(pretty, fn_name, lines)

# Handle the cloning of a repo
def clone_repo(repo_url, repo_path):
  repo = None

  try:
    repo = pygit2.clone_repository(repo_url, repo_path)
  except pygit2.GitError:
    username = input('Enter git username: ')
    password = getpass.getpass('Enter git password: ')
    cred = pygit2.UserPass(username, password)
    try:
      repo = pygit2.clone_repository(args['gitrepo'], repo_path, callbacks=pygit2.RemoteCallbacks(credentials=cred))
    except ValueError:
      print("Invalid URL!")
      sys.exit(1)
  except ValueError:
    print("Invalid URL!")
    sys.exit(1)

  hash_oid = pygit2.Oid(hex=args['patchhash'])
  repo.reset(hash_oid, pygit2.GIT_RESET_HARD)

  return repo

# Print collected data
def print_diff_summary(diff_summary, pretty):
  for diff_data in diff_summary:
    diff_data.print(pretty)

##### Main program #####

# Initialize argparse
parser = argparse.ArgumentParser(description='Outputs a list of patched functions and the corresponding source code lines.')

parser.add_argument('gitrepo', metavar='repo', help='git repo url')
parser.add_argument('patchhash', help='patch hash')
parser.add_argument('--file-extensions', dest="exts", default=['.c', '.h'], metavar='ext', nargs='+', help='data about these file extensions (default .c, .h)' )
parser.add_argument('--only-function-names', dest='fn_names', action='store_true', help='display only a list of function names')

# Dictionary of arguments
args_orig = parser.parse_args()
args = vars(args_orig)

# Path where repo is supposed to be
cwd = os.getcwd()
repo_path = cwd + '/repo'

# Do not look outside this path
ceil_dir = dirname(abspath(repo_path))

# Check if we have a repo
discover_repo_path = pygit2.discover_repository(repo_path, 0, dirname(cwd))

repo = None

if discover_repo_path is None:
  print("No repo found. Cloning...")
  repo = clone_repo(args['gitrepo'], repo_path)
  print("Cloned repo.")

else:
  repo = pygit2.Repository(discover_repo_path)

  if repo.remotes['origin'].url != args['gitrepo']:
    print("Found repo is incorrect. Cloning required repo...")

    # Remove existing contents
    shutil.rmtree(repo_path)

    # Clone
    repo = clone_repo(args['gitrepo'], repo_path)

    print("Cloned repo.")
  else:
    print('Found required repo.')
    
    # Check that commits match
    current_hash = repo.revparse_single('HEAD')
    print('Current commit: ' + current_hash.hex)
    if current_hash.hex != args['patchhash']:
      print('Changing to desired commit...')
      hash_oid = pygit2.Oid(hex=args['patchhash'])
      repo.reset(hash_oid, pygit2.GIT_RESET_HARD)
      print('Changed to %s.' % (args['patchhash'],))


os.chdir(repo_path)

# Get diff between patch commit and previous commit
prev = repo.revparse_single('HEAD~')
diff = repo.diff(prev, context_lines=0)

# Write diff file
diff_file = open('diffs', 'w')
diff_file.write(diff.patch)
diff_file.close()

print('Displaying patch information:\n')

diff_summary = []
patches = list(diff.__iter__())

for patch in patches:
  filename = patch.delta.new_file.path
  diff_data = FileDiff(filename, args_orig.exts is not None)

  for hunk in patch.hunks:
    fn_lines = []
    for diff_line in hunk.lines:
      if diff_line.new_lineno > -1 and diff_line.content.strip():
        fn_lines.append(diff_line.new_lineno)

    diff_data.match_lines_to_fn(fn_lines)
  
  diff_summary.append(diff_data) 

if bool(args['fn_names']):
  print_diff_summary(diff_summary, pretty=False)
else:
  print_diff_summary(diff_summary, pretty=True)