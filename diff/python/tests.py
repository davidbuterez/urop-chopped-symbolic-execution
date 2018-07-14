import unittest
import subprocess
import sys
import os
import shutil

# These tests aim to check the connection and commands (e.g. clone, reset) and that the generated output matches the expected one.
# Mock objects would be nice, but would take too much code for these simple sanity checks
# Checking that the found function names and lines are correct still needs to be done manually
# The way the unittests are run seems to mess up the clone/delete operations, so instead of having separate methods for each test,
# they are all clumped into one single method 'test'

test_url = 'https://github.com/davidbuterez/password-example'
incorrect_url = 'https://git.savannah.gnu.org/git/findutils.git'
sha1 = '4d7add621bf6f54b520a02dd50c3aaf69a43b4f4'

class DiffsTest(unittest.TestCase):
  curr_path = os.getcwd()

  def set_up_correct_repo_right_hash(self):
    subprocess.check_call(['git', 'clone', test_url, 'repo'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.chdir(DiffsTest.curr_path + '/repo')
    subprocess.check_call(['git', 'reset', '--hard', sha1], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.chdir(DiffsTest.curr_path)

  def set_up_correct_repo_wrong_hash(self):
    subprocess.check_call(['git', 'clone', test_url, 'repo'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.chdir(DiffsTest.curr_path + '/repo')
    subprocess.check_call(['git', 'reset', '--hard', '65eea916396822dc4963c597063742b74e995ff9'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.chdir(DiffsTest.curr_path)

  def set_up_no_repo(self):
    repo_path = DiffsTest.curr_path + '/repo'
    if os.path.isdir('repo'):
      shutil.rmtree(repo_path, ignore_errors=True)

  def set_up_incorrect_repo(self):
    subprocess.check_call(['git', 'clone', incorrect_url, 'repo'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

  def test(self):
    # Found repo right hash all output
    self.set_up_correct_repo_right_hash()

    correct = 'Found required repo.\nCurrent commit (patch): 4d7add621bf6f54b520a02dd50c3aaf69a43b4f4\nComparing with previous commit: 3335d2691ceba843960d2b0b63c0c72f4dc1a5bc\nDisplaying patch information:\n\n\x1b[34mpassword.c\x1b[0m: In function \x1b[32mappend_string\x1b[0m\nPatch has added lines (new file indices): [8 9 10]\n\x1b[34mpassword.c\x1b[0m: In function \x1b[32mget_length\x1b[0m\nPatch has added lines (new file indices): [4 5 6]\n\x1b[34mpassword.c\x1b[0m: In function \x1b[32mcheck_password\x1b[0m\nPatch has added lines (new file indices): [13 20]\n\x1b[34mpassword.c\x1b[0m: In function \x1b[32mmain\x1b[0m\nPatch has added lines (new file indices): [29]\n\n'
    output = subprocess.check_output([sys.executable, 'getdiffs.py', test_url, sha1])
    
    self.assertEqual(correct, output.decode('utf-8'))

    # Found repo right hash only fn output    
    correct = 'Found required repo.\nCurrent commit (patch): 4d7add621bf6f54b520a02dd50c3aaf69a43b4f4\nComparing with previous commit: 3335d2691ceba843960d2b0b63c0c72f4dc1a5bc\nDisplaying patch information:\n\nUpdated functions:\n  \x1b[32mappend_string\x1b[0m\n  \x1b[32mget_length\x1b[0m\n  \x1b[32mcheck_password\x1b[0m\n  \x1b[32mmain\x1b[0m\n\n'
    output = subprocess.check_output([sys.executable, 'getdiffs.py', test_url, sha1, '--only-function-names'])
    
    self.assertEqual(correct, output.decode('utf-8'))

    # No repo right hash all output
    self.set_up_no_repo()

    correct = 'No repo found. Cloning...\nCloned repo.\nCurrent commit (patch): 4d7add621bf6f54b520a02dd50c3aaf69a43b4f4\nComparing with previous commit: 3335d2691ceba843960d2b0b63c0c72f4dc1a5bc\nDisplaying patch information:\n\n\x1b[34mpassword.c\x1b[0m: In function \x1b[32mappend_string\x1b[0m\nPatch has added lines (new file indices): [8 9 10]\n\x1b[34mpassword.c\x1b[0m: In function \x1b[32mget_length\x1b[0m\nPatch has added lines (new file indices): [4 5 6]\n\x1b[34mpassword.c\x1b[0m: In function \x1b[32mcheck_password\x1b[0m\nPatch has added lines (new file indices): [13 20]\n\x1b[34mpassword.c\x1b[0m: In function \x1b[32mmain\x1b[0m\nPatch has added lines (new file indices): [29]\n\n'
    output = subprocess.check_output([sys.executable, 'getdiffs.py', test_url, sha1])
    
    self.assertEqual(correct, output.decode('utf-8'))

    # No repo right hash only fn output
    self.set_up_no_repo()

    correct = 'No repo found. Cloning...\nCloned repo.\nCurrent commit (patch): 4d7add621bf6f54b520a02dd50c3aaf69a43b4f4\nComparing with previous commit: 3335d2691ceba843960d2b0b63c0c72f4dc1a5bc\nDisplaying patch information:\n\nUpdated functions:\n  \x1b[32mappend_string\x1b[0m\n  \x1b[32mget_length\x1b[0m\n  \x1b[32mcheck_password\x1b[0m\n  \x1b[32mmain\x1b[0m\n\n'
    output = subprocess.check_output([sys.executable, 'getdiffs.py', test_url, sha1, '--only-function-names'])
    
    self.assertEqual(correct, output.decode('utf-8'))

    self.delete_repo()

    # Incorrect repo all output
    self.set_up_incorrect_repo()

    correct = 'Found repo is incorrect. Cloning required repo...\nCloned repo.\nCurrent commit (patch): 4d7add621bf6f54b520a02dd50c3aaf69a43b4f4\nComparing with previous commit: 3335d2691ceba843960d2b0b63c0c72f4dc1a5bc\nDisplaying patch information:\n\n\x1b[34mpassword.c\x1b[0m: In function \x1b[32mappend_string\x1b[0m\nPatch has added lines (new file indices): [8 9 10]\n\x1b[34mpassword.c\x1b[0m: In function \x1b[32mget_length\x1b[0m\nPatch has added lines (new file indices): [4 5 6]\n\x1b[34mpassword.c\x1b[0m: In function \x1b[32mcheck_password\x1b[0m\nPatch has added lines (new file indices): [13 20]\n\x1b[34mpassword.c\x1b[0m: In function \x1b[32mmain\x1b[0m\nPatch has added lines (new file indices): [29]\n\n'
    output = subprocess.check_output([sys.executable, 'getdiffs.py', test_url, sha1])
    
    self.assertEqual(correct, output.decode('utf-8'))

    self.delete_repo()

    # Incorrect repo only fn output
    self.set_up_incorrect_repo()

    correct = 'Found repo is incorrect. Cloning required repo...\nCloned repo.\nCurrent commit (patch): 4d7add621bf6f54b520a02dd50c3aaf69a43b4f4\nComparing with previous commit: 3335d2691ceba843960d2b0b63c0c72f4dc1a5bc\nDisplaying patch information:\n\nUpdated functions:\n  \x1b[32mappend_string\x1b[0m\n  \x1b[32mget_length\x1b[0m\n  \x1b[32mcheck_password\x1b[0m\n  \x1b[32mmain\x1b[0m\n\n'
    output = subprocess.check_output([sys.executable, 'getdiffs.py', test_url, sha1, '--only-function-names'])
    
    self.assertEqual(correct, output.decode('utf-8'))

    self.delete_repo()

    # Correct repo wrong commit all output
    self.set_up_correct_repo_wrong_hash()

    correct = 'Found required repo.\nCurrent commit (patch): 65eea916396822dc4963c597063742b74e995ff9\nChanging to desired commit...\nChanged to 4d7add621bf6f54b520a02dd50c3aaf69a43b4f4.\nComparing with previous commit: 3335d2691ceba843960d2b0b63c0c72f4dc1a5bc\nDisplaying patch information:\n\n\x1b[34mpassword.c\x1b[0m: In function \x1b[32mappend_string\x1b[0m\nPatch has added lines (new file indices): [8 9 10]\n\x1b[34mpassword.c\x1b[0m: In function \x1b[32mget_length\x1b[0m\nPatch has added lines (new file indices): [4 5 6]\n\x1b[34mpassword.c\x1b[0m: In function \x1b[32mcheck_password\x1b[0m\nPatch has added lines (new file indices): [13 20]\n\x1b[34mpassword.c\x1b[0m: In function \x1b[32mmain\x1b[0m\nPatch has added lines (new file indices): [29]\n\n'
    output = subprocess.check_output([sys.executable, 'getdiffs.py', test_url, sha1])
    
    self.assertEqual(correct, output.decode('utf-8'))

    self.delete_repo()

    # Correct repo wrong commit only fn output
    self.set_up_correct_repo_wrong_hash()

    correct = 'Found required repo.\nCurrent commit (patch): 65eea916396822dc4963c597063742b74e995ff9\nChanging to desired commit...\nChanged to 4d7add621bf6f54b520a02dd50c3aaf69a43b4f4.\nComparing with previous commit: 3335d2691ceba843960d2b0b63c0c72f4dc1a5bc\nDisplaying patch information:\n\nUpdated functions:\n  \x1b[32mappend_string\x1b[0m\n  \x1b[32mget_length\x1b[0m\n  \x1b[32mcheck_password\x1b[0m\n  \x1b[32mmain\x1b[0m\n\n'
    output = subprocess.check_output([sys.executable, 'getdiffs.py', test_url, sha1, '--only-function-names'])
    
    self.assertEqual(correct, output.decode('utf-8'))

    self.delete_repo()

  def delete_repo(self):
    shutil.rmtree(DiffsTest.curr_path + '/repo')

  def tearDown(self):
    if os.path.isdir(DiffsTest.curr_path + '/repo'):
      self.delete_repo()


if __name__ == '__main__': 
  unittest.main()