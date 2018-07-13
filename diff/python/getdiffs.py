#!/usr/bin/env python
import argparse
import os
import shutil
import getpass
import pygit2

from os.path import dirname, abspath
from termcolor import colored

class DiffData:
  
  def __init__(self, filename, restrict):
    self.filename = filename
    self.fn_to_lines = {}
    self.restrict_extensions = restrict
    self.file_extension = filename[filename.rfind('.'):]

  # Extract function name from header. Might be empty if no function is provided in the source.
  @staticmethod
  def fn_name_from_header(header):
    begin_delimitator = '@@'
    end_delimitator = ')'

    first_extract = header[header.rfind(begin_delimitator) + len(begin_delimitator) + 1:].rstrip()
    second_extract = first_extract[:first_extract.rfind(end_delimitator) + 1].rstrip()

    return second_extract if second_extract else 'Global'
  
  # Add to dictionary
  def add_fn_lines(self, fn_name, lines):
    if fn_name in self.fn_to_lines:
      self.fn_to_lines[fn_name].extend(lines)
    else:
      self.fn_to_lines[fn_name] = lines

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
      if pretty:
        self.print_fn_pretty(fn_name)
        DiffData.print_lines(lines)
      else:
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
    repo = pygit2.clone_repository(args['gitrepo'], repo_path, callbacks=pygit2.RemoteCallbacks(credentials=cred))

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

# Get diff between patch commit and previous commit
prev = repo.revparse_single(args['patchhash'] + '~1')
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
  diff_data = DiffData(filename, args_orig.exts is not None)

  for hunk in patch.hunks:
    fn_lines = []
    for diff_line in hunk.lines:
      if diff_line.new_lineno > -1:
        fn_lines.append(diff_line.new_lineno)

    diff_data.add_fn_lines(DiffData.fn_name_from_header(hunk.header), fn_lines)
  
  diff_summary.append(diff_data) 

if bool(args['fn_names']):
  print_diff_summary(diff_summary, pretty=False)
else:
  print_diff_summary(diff_summary, pretty=True)