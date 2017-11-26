import unittest
import lxml
import pymysql


class SelfCleaningTestCase(unittest.TestCase):

	def setUp(self):
    super(SelfCleaningTestCase, self).setUp()
    self.starting_directory = os.getcwd()
    self.tmpdir = tempfile.mkdtemp()
    if os.path.isdir(self.tmpdir):
      shutil.rmtree(self.tmpdir)

  def tearDown(self):
    if os.path.isdir(self.tmpdir):
      # Clean up after tests which leave inaccessible files behind:
      os.chmod(self.tmpdir, 0o700)

      for dirpath, subdirs, filenames in os.walk(self.tmpdir, topdown=True):
        for i in subdirs:
          os.chmod(os.path.join(dirpath, i), 0o700)

      shutil.rmtree(self.tmpdir)

    super(SelfCleaningTestCase, self).tearDown()