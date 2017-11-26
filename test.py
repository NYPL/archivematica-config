import unittest
import lxml
import pymysql
import os
import tempfile
import shutil
import mcp


class SelfCleaningTestCase(unittest.TestCase):

  def setUp(self):
    super(SelfCleaningTestCase, self).setUp()

    self.starting_directory = os.getcwd()
    self.tmpdir = tempfile.mkdtemp()

  def tearDown(self):
    if os.path.isdir(self.tmpdir):
      # Clean up after tests which leave inaccessible files behind:
      os.chmod(self.tmpdir, 0o700)

      for dirpath, subdirs, filenames in os.walk(self.tmpdir, topdown=True):
        for i in subdirs:
          os.chmod(os.path.join(dirpath, i), 0o700)

      shutil.rmtree(self.tmpdir)

    super(SelfCleaningTestCase, self).tearDown()


class TranslateMCP(SelfCleaningTestCase):

  def test_no_file(self):
    not_file = os.path.join(self.tmpdir, 'a.notfile')
    with self.assertRaises(OSError) as error_catcher:
      mcp.MCP(path = not_file)

    self.assertEqual('No such file or directory: {}'.format(not_file),
      str(error_catcher.exception))


  def test_not_xml(self):
    not_xml_filename = 'a.notxml'
    not_xml = os.path.join(self.tmpdir, not_xml_filename)
    with open(not_xml, 'w+') as f:
      f.write('"i_am_json": "lol"')

    with self.assertRaises(mcp.MCPError) as error_catcher:
      mcp.MCP(path = not_xml)

    self.assertEqual('{} does not contain valid XML'.format(not_xml_filename),
      str(error_catcher.exception))


  def test_not_mcp(self):
    not_mcp_filename = 'a.notcmp'
    not_mcp = os.path.join(self.tmpdir, not_mcp_filename)
    with open(not_mcp, 'w+') as f:
      f.write('<fakeMCP></fakeMCP>')

    with self.assertRaises(mcp.MCPError) as error_catcher:
      mcp.MCP(path = not_mcp)

    self.assertEqual('{} does not appear to be a valid Archivematica MCP'.format(not_mcp_filename),
      str(error_catcher.exception))


if __name__ == '__main__':
    unittest.main()