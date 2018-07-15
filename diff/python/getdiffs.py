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

class PrintManager:

  should_print = True
  
  @staticmethod
  def print(*args, **kwargs):
    if PrintManager.should_print:
      print(' '.join(map(str,args)), **kwargs)

  @staticmethod
  def print_diff_summary(diff_summary, pretty):
    for diff_data in diff_summary:
      diff_data.print(pretty)
  
  @staticmethod
  def print_relevant_diff(diff_summary, only_fn):
    if diff_summary:
      PrintManager.print('Displaying patch information:\n')

      if bool(only_fn):
        PrintManager.print_diff_summary(diff_summary, pretty=False)
      else:
        PrintManager.print_diff_summary(diff_summary, pretty=True)
      PrintManager.print()
    else:
      PrintManager.print('No relevant changes detected.')

class ChangedLinesManager:

  def __init__(self, added_lines, removed_lines):
    self.added_lines = added_lines
    self.removed_lines = removed_lines

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
      print(']')

class FnAttributes:

  def __init__(self, fn_name, start, end, prototype):
    
    def trim_prototype(prototype):
      proto = prototype[:prototype.rfind('{') - 1]
      return proto[proto.find('^') + 1:]

    self.fn_name = fn_name
    self.start_line = start
    self.end_line = end
    self.prototype = trim_prototype(prototype)

class FileDifferences:
  
  def __init__(self, filename):
    self.filename = filename
    self.file_extension = filename[filename.rfind('.'):]
    self.current_fn_map = self.get_fn_names(prev=False)
    self.prev_fn_map = self.get_fn_names(prev=True)
    self.fn_to_changed_lines = {}

  def get_fn_names(self, prev):
    target = os.getcwd() + '/repo/' + self.filename if not prev else os.getcwd() + '/repo_prev/' + self.filename
    fn_table = subprocess.check_output(['ctags', '-x', '--c-kinds=fp', '--fields=+ne', '--output-format=json', target]).decode('utf-8').strip().split('\n')
    fn_map = {}

    for obj in fn_table:
      fn_data = json.loads(obj)
      fn_map[fn_data['name']] = FnAttributes(fn_data['name'], fn_data['line'], fn_data['end'] if 'end' in fn_data else fn_data['line'], fn_data['pattern'])

    return fn_map

  def match_lines_to_fn(self, new_lines, old_lines):
    for fn_name in self.current_fn_map.keys():

      added, removed = [], []

      if fn_name in self.current_fn_map:
        new_fn_attr = self.current_fn_map[fn_name]

        for new_line_no in new_lines:
          if new_line_no >= new_fn_attr.start_line and new_line_no <= new_fn_attr.end_line:
            added.append(new_line_no)

      if fn_name in self.prev_fn_map:
        old_fn_attr = self.prev_fn_map[fn_name]

        for old_line_no in old_lines:
          if old_line_no >= old_fn_attr.start_line and old_line_no <= old_fn_attr.end_line:
            removed.append(old_line_no)
      
      if fn_name in self.fn_to_changed_lines:
        self.fn_to_changed_lines[fn_name].added_lines.extend(added)
        self.fn_to_changed_lines[fn_name].removed_lines.extend(removed)
      elif added or removed:
        self.fn_to_changed_lines[fn_name] = ChangedLinesManager(added, removed)
        

  # Prints all the data that this object has
  def print(self, pretty):
    fn_list_file = None

    if not pretty:
      PrintManager.print('Updated functions:')
      fn_list_file = open('../updated_functions', 'w')

    for fn_name, lines in self.fn_to_changed_lines.items():
      if pretty and lines:
        print('%s: In function %s' % (colored(self.filename, 'blue'), colored(fn_name, 'green')), end='')
        self.fn_to_changed_lines[fn_name].print_added_lines()
        self.fn_to_changed_lines[fn_name].print_removed_lines()
      elif lines:
        print('  %s' % colored(fn_name, 'green'))
        fn_list_file.write('%s\n' % fn_name)

class RepoManager:

  cloned_repos_paths = []

  def __init__(self, repo_url, cwd, cache, extensions):
    self.repo_url = repo_url
    self.cwd = cwd
    self.cache = cache
    self.allowed_extensions = extensions

  # Handles the cloning of a repo
  def clone_repo(self, repo_path, hash):
    repo = None

    try:
      repo = pygit2.clone_repository(self.repo_url, repo_path)
    except pygit2.GitError:
      username = input('Enter git username: ')
      password = getpass.getpass('Enter git password: ')
      cred = pygit2.UserPass(username, password)
      try:
        repo = pygit2.clone_repository(self.repo_url, repo_path, callbacks=pygit2.RemoteCallbacks(credentials=cred))
      except ValueError:
        PrintManager.print("Invalid URL!")
        sys.exit(1)
    except ValueError:
      PrintManager.print("Invalid URL!")
      sys.exit(1)

    hash_oid = pygit2.Oid(hex=hash)
    repo.reset(hash_oid, pygit2.GIT_RESET_HARD)

    return repo

  def get_repo(self, repo_path, repo_hash):
    # Keep track of paths of cloned repos
    RepoManager.cloned_repos_paths.append(repo_path)

    # Do not look outside this path
    ceil_dir = dirname(abspath(repo_path))

    # Check if we have a repo
    discover_repo_path = pygit2.discover_repository(repo_path, 0, dirname(self.cwd))

    repo = None

    if discover_repo_path is None:
      PrintManager.print("No repo found. Cloning...")
      repo = self.clone_repo(repo_path, repo_hash)
      PrintManager.print("Cloned repo.")
      current_hash = repo.revparse_single('HEAD')
      PrintManager.print('Current commit (patch): ' + current_hash.hex)

    else:
      repo = pygit2.Repository(discover_repo_path)

      if repo.remotes['origin'].url != self.repo_url:
        PrintManager.print("Found repo is incorrect. Cloning required repo...")

        # Remove existing contents
        shutil.rmtree(repo_path)

        # Clone
        repo = self.clone_repo(repo_path, repo_hash)

        PrintManager.print("Cloned repo.")
        current_hash = repo.revparse_single('HEAD')
        PrintManager.print('Current commit (patch): ' + current_hash.hex)
      else:
        PrintManager.print('Found required repo.')
        
        # Check that commits match
        current_hash = repo.revparse_single('HEAD')
        PrintManager.print('Current commit (patch): ' + current_hash.hex)
        if current_hash.hex != repo_hash:
          PrintManager.print('Changing to desired commit...')
          hash_oid = pygit2.Oid(hex=repo_hash)
          repo.reset(hash_oid, pygit2.GIT_RESET_HARD)
          PrintManager.print('Changed to %s.' % (repo_hash,))
    
    PrintManager.print()
    return repo

  def compute_diffs(self, diff):
    diff_summary = []
    patches = list(diff.__iter__())

    for patch in patches:
      filename = patch.delta.new_file.path

      extension = filename[filename.rfind('.'):]
      if extension not in self.allowed_extensions:
        continue

      diff_data = FileDifferences(filename)

      for hunk in patch.hunks:
        new_fn_lines = []
        old_fn_lines = []

        for diff_line in hunk.lines:
          if diff_line.content.strip():
            if diff_line.new_lineno > -1:
              new_fn_lines.append(diff_line.new_lineno)
            else:
              old_fn_lines.append(diff_line.old_lineno)

        diff_data.match_lines_to_fn(new_fn_lines, old_fn_lines)
      
      diff_summary.append(diff_data)
    
    return diff_summary
  
  def cleanup(self):
    if not self.cache:
      for path in RepoManager.cloned_repos_paths:
        shutil.rmtree(path)

##### Main program #####
def main(main_args):
  # Initialize argparse
  parser = argparse.ArgumentParser(description='Outputs a list of patched functions and the corresponding source code lines.')

  parser.add_argument('gitrepo', metavar='repo', help='git repo url')
  parser.add_argument('patchhash', help='patch hash')
  parser.add_argument('--only-function-names', dest='fn_names', action='store_true', help='display only a list of function names')
  parser.add_argument('--cache', action='store_true', help='do not delete cloned repos after finishing')
  parser.add_argument('--verbose', action='store_true', help='display helpful progress messages')

  # Dictionary of arguments
  args_orig = parser.parse_args(main_args)
  args = vars(args_orig)

  # Handle printing
  PrintManager.should_print = bool(args['verbose'])

  # Path where repo is supposed to be
  cwd = os.getcwd()
  curr_repo_path = cwd + '/repo'
  prev_repo_path = cwd + '/repo_prev'

  # Allowed file extensions
  extensions = ['.c', '.h']

  repo_manager = RepoManager(args['gitrepo'], cwd, args['cache'], extensions)
  curr_repo = repo_manager.get_repo(curr_repo_path, args['patchhash'])

  # Get diff between patch commit and previous commit
  prev = curr_repo.revparse_single('HEAD~')
  curr = curr_repo.revparse_single('HEAD')
  PrintManager.print("Comparing with previous commit: " + prev.hex)
  PrintManager.print()
  diff = curr_repo.diff(prev, curr, context_lines=0)

  # Also get previous version of repo
  prev_repo = repo_manager.get_repo(prev_repo_path, prev.hex)

  # Write diff file
  diff_file = open('diffs', 'w')
  diff_file.write(diff.patch)
  diff_file.close() 

  diff_summary = repo_manager.compute_diffs(diff)
  PrintManager.print_relevant_diff(diff_summary, args['fn_names'])  

  repo_manager.cleanup()

if __name__ == '__main__':
  main(sys.argv[1:])