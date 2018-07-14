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

class DiffLines:

  def __init__(self, added_lines, removed_lines):
    self.added_lines = added_lines
    self.removed_lines = [-ln for ln in removed_lines]

  def print_added_lines(self):
    print()
    if self.added_lines:
      print('Patch has added lines (new file indices): [', end='')
      print(*self.added_lines, end='')
      print(']', end='')

  def print_removed_lines(self):
    print()
    if self.removed_lines:
      print('Patch has removed lines (old file indices): [', end='')
      print(*self.removed_lines, end='')
      print(']', end='')

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
  
  def __init__(self, filename):
    self.filename = filename
    self.file_extension = filename[filename.rfind('.'):]
    self.fn_map = self.get_fn_names()
    self.fn_to_lines = {}

  def get_fn_names(self):
    fn_table = subprocess.check_output(['ctags', '-x', '--c-kinds=fp', '--fields=+ne', '--output-format=json', self.filename]).decode('utf-8').strip().split('\n')
    fn_map = {}

    for obj in fn_table:
      fn_data = json.loads(obj)
      fn_map[fn_data['name']] = FnData(fn_data['name'], fn_data['line'], fn_data['end'] if 'end' in fn_data else fn_data['line'], fn_data['pattern'])

    return fn_map

  def match_lines_to_fn(self, lines):
    for fn_name, fn_data in self.fn_map.items():
      added, removed = [], []
      for line_no in lines:
        if abs(line_no) >= fn_data.start_line and abs(line_no) <= fn_data.end_line:
          if line_no > 0:
            added.append(line_no)
          else:
            removed.append(line_no)

      if fn_name in self.fn_to_lines:
        self.fn_to_lines[fn_name].added_lines.extend(added)
        self.fn_to_lines[fn_name].removed_lines.extend(removed)
      elif added or removed:
        self.fn_to_lines[fn_name] = DiffLines(added, removed)

  # Prints all the data that this object has
  def print(self, pretty):
    if not pretty:
      print('Updated functions:')

    for fn_name, lines in self.fn_to_lines.items():
      if pretty and lines:
        print('%s: In function %s' % (colored(self.filename, 'blue'), colored(fn_name, 'green')), end='')
        self.fn_to_lines[fn_name].print_added_lines()
        self.fn_to_lines[fn_name].print_removed_lines()
      elif lines:
        print('  %s' % colored(fn_name, 'green'))

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

# Allowed file extensions
extensions = ['.c', '.h']

repo = None

if discover_repo_path is None:
  print("No repo found. Cloning...")
  repo = clone_repo(args['gitrepo'], repo_path)
  print("Cloned repo.")
  current_hash = repo.revparse_single('HEAD')
  print('Current commit (patch): ' + current_hash.hex)

else:
  repo = pygit2.Repository(discover_repo_path)

  if repo.remotes['origin'].url != args['gitrepo']:
    print("Found repo is incorrect. Cloning required repo...")

    # Remove existing contents
    shutil.rmtree(repo_path)

    # Clone
    repo = clone_repo(args['gitrepo'], repo_path)

    print("Cloned repo.")
    current_hash = repo.revparse_single('HEAD')
    print('Current commit (patch): ' + current_hash.hex)
  else:
    print('Found required repo.')
    
    # Check that commits match
    current_hash = repo.revparse_single('HEAD')
    print('Current commit (patch): ' + current_hash.hex)
    if current_hash.hex != args['patchhash']:
      print('Changing to desired commit...')
      hash_oid = pygit2.Oid(hex=args['patchhash'])
      repo.reset(hash_oid, pygit2.GIT_RESET_HARD)
      print('Changed to %s.' % (args['patchhash'],))


os.chdir(repo_path)

# Get diff between patch commit and previous commit
prev = repo.revparse_single('HEAD~')
curr = repo.revparse_single('HEAD')
print("Comparing with previous commit: " + prev.hex)
diff = repo.diff(prev, curr, context_lines=0)

# Write diff file
diff_file = open('diffs', 'w')
diff_file.write(diff.patch)
diff_file.close()

diff_summary = []
patches = list(diff.__iter__())

for patch in patches:
  filename = patch.delta.new_file.path

  extension = filename[filename.rfind('.'):]
  if extension not in extensions:
    continue

  diff_data = FileDiff(filename)

  for hunk in patch.hunks:
    fn_lines = []
    for diff_line in hunk.lines:
      if diff_line.content.strip():
        if diff_line.new_lineno > -1:
          fn_lines.append(diff_line.new_lineno)
        else:
          fn_lines.append(-diff_line.old_lineno)

    diff_data.match_lines_to_fn(fn_lines)
  
  diff_summary.append(diff_data) 

if diff_summary:
  print('Displaying patch information:\n')

  if bool(args['fn_names']):
    print_diff_summary(diff_summary, pretty=False)
  else:
    print_diff_summary(diff_summary, pretty=True)
  print()
else:
  print('No relevant changes detected.')