import unittest
import subprocess
import os
import sys
import shutil
import pygit2

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import diffanalyze

url = 'https://git.savannah.gnu.org/git/findutils.git'

class DiffsTest(unittest.TestCase):

  @staticmethod
  def git_log_output(ext, full_history):
    
    def fst_pattern(ext):
      if ext is 'none':
        return '\":/*\"'
      else:
        return '\":/*%s\"' % ext

    def snd_pattern(ext):
      if ext is 'none':
        return '\":^/*.*\"'
      else:
        return '\":/**/*%s\"' % ext

    path = os.getcwd()
    cmd = []

    os.chdir('findutils')

    if full_history:
      cmd = ['git', 'log', '--full-history', '--format=%H', fst_pattern(ext), snd_pattern(ext)]
    else:
      cmd = ['git', 'log', '--format=%H', fst_pattern(ext), snd_pattern(ext)]

    output = subprocess.check_output(' '.join(cmd), shell=True)
    list_of_commits = output.decode('utf-8').strip().split('\n')

    os.chdir(path)

    return int(len(list_of_commits))

  def setUp(self):
    diffanalyze.PrintManager.should_print = False
    pygit2.clone_repository(url, os.getcwd() + '/findutils')

  def test_output_matches_git_log(self):
    repo_manager = diffanalyze.RepoManager(url, cache=False, print_mode='only-fn')
    repo_manager.get_updated_fn_per_commit()

    for ext, commits in repo_manager.other_changed.items():
      # Don't want to check .c files, as the git output would include all .c files, w
      # hile we track only the .c files where no functions were changed
      if ext == '.c':
        continue

      git_output1 = DiffsTest.git_log_output(ext, full_history=True)
      git_output2 = DiffsTest.git_log_output(ext, full_history=False)

      # print('diffanalyze says %s; git full history says %s; git no history says: %s' % (len(commits), git_output1, git_output2))

      self.assertTrue(len(commits) == git_output1 or len(commits) == git_output2)

    repo_manager.cleanup()
    
  def tearDown(self):
    if os.path.isdir('findutils'):
      shutil.rmtree(os.getcwd() + '/findutils')
    if os.path.isdir('repo'):
      shutil.rmtree(os.getcwd() + '/repo')
    if os.path.isdir('repo_prev'):
      shutil.rmtree(os.getcwd() + '/repo_prev')

if __name__ == '__main__': 
  unittest.main()