#!/usr/bin/env python
import argparse
import os
import shutil
import getpass
import pygit2

from os.path import dirname, abspath
from termcolor import colored

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

# Extract function name from header. Might be empty if no function is provided in the source.
def fn_name_from_header(header):
  begin_delimitator = '@@'
  end_delimitator = ')'

  extract = header[header.rfind(begin_delimitator) + len(begin_delimitator) + 1:].rstrip()
  return extract[:extract.rfind(end_delimitator) + 1].rstrip()

def color_string(str, color_code):
  return str + color_code

def print_fn_info(filename, fn_name):
  if fn_name:
    print(colored(filename, 'blue') + ": " + colored(fn_name, 'green'))

##### Main program #####

# Initialize argparse
parser = argparse.ArgumentParser(description='Outputs a list of patched functions and the corresponding source code lines.')

parser.add_argument('gitrepo', metavar='repo', help='git repo url')
parser.add_argument('patchhash', help='patch hash')
parser.add_argument('--file-extensions', dest="exts", default=['.c', '.h'], metavar='ext', nargs='+', help="data about these file extensions (default .c, .h)" )

# Dictionary of arguments
args_orig = parser.parse_args()
args = vars(args_orig)

restrict_extensions = args_orig.exts is not None

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

patches = list(diff.__iter__())
for patch in patches:
  filename = patch.delta.new_file.path
  extension = filename[filename.rfind('.'):]

  for hunk in patch.hunks:
    # Print only information regarding provided extensions
    fn_name = fn_name_from_header(hunk.header)
    if restrict_extensions:
      if extension in args_orig.exts:
        print_fn_info(filename, fn_name)
    else:
      print_fn_info(filename, fn_name)
      