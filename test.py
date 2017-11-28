import unittest
from lxml import etree
import pymysql
import os
import tempfile
import shutil
import uuid
import mcp


MCP_LEVEL1 = 'processingMCP'
MCP_LEVEL2 = 'preconfiguredChoices'
MCP_LEVEL3 = 'preconfiguredChoice'
MCP_LEVEL4A = 'appliesTo'
MCP_LEVEL4B = 'goToChain'


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
    not_file_path = os.path.join(self.tmpdir, 'a.notfile')
    with self.assertRaises(OSError) as error_catcher:
      mcp.MCP(path = not_file_path)

    self.assertEqual('No such file or directory: {}'.format(not_file_path),
      str(error_catcher.exception))


  def test_not_xml(self):
    not_xml_filename = 'a.notxml'
    not_xml_path = os.path.join(self.tmpdir, not_xml_filename)
    with open(not_xml_path, 'w+') as f:
      f.write('"i_am_json": "lol"')

    with self.assertRaises(mcp.MCPError) as error_catcher:
      mcp.MCP(path = not_xml_path)

    self.assertEqual('{} does not contain valid XML'.format(not_xml_filename),
      str(error_catcher.exception))


  def test_not_mcp_first_level(self):
    not_mcp_filename = 'a.notmcp'
    not_mcp_path = os.path.join(self.tmpdir, not_mcp_filename)

    mcp_tree = generate_fake_mcp(MCP_LEVEL1[:-1], MCP_LEVEL2, MCP_LEVEL3,
      MCP_LEVEL4A, MCP_LEVEL4B)
    mcp_tree.write(not_mcp_path)

    with self.assertRaises(mcp.MCPError) as error_catcher:
      mcp.MCP(path = not_mcp_path)

    self.assertEqual('{} does not appear to be a valid Archivematica MCP'.format(not_mcp_filename),
      str(error_catcher.exception))


  def test_not_mcp_second_level(self):
    not_mcp_filename = 'a.notmcp'
    not_mcp_path = os.path.join(self.tmpdir, not_mcp_filename)
    
    mcp_tree = generate_fake_mcp(MCP_LEVEL1, MCP_LEVEL2[:-1], MCP_LEVEL3,
      MCP_LEVEL4A, MCP_LEVEL4B)
    mcp_tree.write(not_mcp_path)

    with self.assertRaises(mcp.MCPError) as error_catcher:
      mcp.MCP(path = not_mcp_path)

    self.assertEqual('{} does not appear to be a valid Archivematica MCP'.format(not_mcp_filename),
      str(error_catcher.exception))


  def test_not_mcp_third_level(self):
    not_mcp_filename = 'a.notmcp'
    not_mcp_path = os.path.join(self.tmpdir, not_mcp_filename)
    
    mcp_tree = generate_fake_mcp(MCP_LEVEL1, MCP_LEVEL2, MCP_LEVEL3[:-1],
      MCP_LEVEL4A, MCP_LEVEL4B)
    mcp_tree.write(not_mcp_path)

    with self.assertRaises(mcp.MCPError) as error_catcher:
      mcp.MCP(path = not_mcp_path)

    self.assertEqual('{} does not appear to be a valid Archivematica MCP'.format(not_mcp_filename),
      str(error_catcher.exception))


  def test_not_mcp_fourth_level(self):
    not_mcp_filename = 'a.notmcp'
    not_mcp_path = os.path.join(self.tmpdir, not_mcp_filename)
    
    mcp_tree = generate_fake_mcp(MCP_LEVEL1, MCP_LEVEL2, MCP_LEVEL3,
      MCP_LEVEL4A[:-1], MCP_LEVEL4B)
    mcp_tree.write(not_mcp_path)

    with self.assertRaises(mcp.MCPError) as error_catcher:
      mcp.MCP(path = not_mcp_path)

    self.assertEqual('{} does not appear to be a valid Archivematica MCP'.format(not_mcp_filename),
      str(error_catcher.exception))


  def test_valid_mcp(self):
    mcp_filename = 'a.mcp'
    mcp_path = os.path.join(self.tmpdir, mcp_filename)
    
    mcp_tree = generate_fake_mcp(MCP_LEVEL1, MCP_LEVEL2, MCP_LEVEL3,
      MCP_LEVEL4A, MCP_LEVEL4B)
    mcp_tree.write(mcp_path)

    valid_mcp = mcp.MCP(path = mcp_path)

    self.assertEqual(valid_mcp.filename, mcp_filename)
    self.assertEqual(valid_mcp.path, mcp_path)
    self.assertTrue(valid_mcp.validate_mcp())


  def test_return_all_uuids(self):
    mcp_filename = 'a.mcp'
    mcp_path = os.path.join(self.tmpdir, mcp_filename)
    
    mcp_tree = generate_fake_mcp(MCP_LEVEL1, MCP_LEVEL2, MCP_LEVEL3,
      MCP_LEVEL4A, MCP_LEVEL4B)
    mcp_tree.write(mcp_path)

    valid_mcp = mcp.MCP(path = mcp_path)

    uuids = valid_mcp.get_uuids()

    self.assertEqual(len(uuids), 3)

    def is_uuid(value):
      try:
        val = uuid.UUID(value)
      except ValueError:
          return False
      return True

    for choice in uuids:
      self.assertTrue(len(choice.keys()), 2)
      for uuid_string in choice.values():
        self.assertTrue(is_uuid(uuid_string))


  def test_translate_uuids(self):
    mcp_filename = 'a.mcp'
    mcp_path = os.path.join(self.tmpdir, mcp_filename)
    
    mcp_tree = generate_fake_mcp(MCP_LEVEL1, MCP_LEVEL2, MCP_LEVEL3,
      MCP_LEVEL4A, MCP_LEVEL4B)
    mcp_tree.write(mcp_path)

    valid_mcp = mcp.MCP(path = mcp_path)
    uuids = valid_mcp.get_uuids()

    replacement_dict = {uuids[0]['goToChain']: 'test_label'}
    valid_mcp.set_uuid_labels(replacement_dict)

    count_labels = etree.XPath("count(//preconfiguredChoice/*/@label)")
    self.assertTrue(count_labels(valid_mcp.tree), 1)

    all_labels = etree.XPath("//preconfiguredChoice/goToChain/@label")
    self.assertTrue(all_labels(valid_mcp.tree), ['test_label'])


  def test_translated_xml_still_valid(self):
    mcp_filename = 'a.mcp'
    mcp_path = os.path.join(self.tmpdir, mcp_filename)
    
    mcp_tree = generate_fake_mcp(MCP_LEVEL1, MCP_LEVEL2, MCP_LEVEL3,
      MCP_LEVEL4A, MCP_LEVEL4B)
    mcp_tree.write(mcp_path)

    valid_mcp = mcp.MCP(path = mcp_path)
    uuids = valid_mcp.get_uuids()

    replacement_dict = {uuids[0]['goToChain']: 'test_label'}
    valid_mcp.set_uuid_labels(replacement_dict)

    self.assertTrue(valid_mcp.validate_mcp())


  def test_write_xml(self):
    mcp_filename = 'a.mcp'
    mcp_path = os.path.join(self.tmpdir, mcp_filename)
    
    mcp_tree = generate_fake_mcp(MCP_LEVEL1, MCP_LEVEL2, MCP_LEVEL3,
      MCP_LEVEL4A, MCP_LEVEL4B)
    mcp_tree.write(mcp_path)

    valid_mcp = mcp.MCP(path = mcp_path)

    new_path = os.path.join(self.tmpdir, 'a/bunch/of/fake/directories/', mcp_filename)
    valid_mcp.write(new_path)
    self.assertTrue(os.path.exists(new_path))


def generate_fake_mcp(level1, level2, level3, level4a, level4b):
  mcp_level1 = etree.Element(level1)
  mcp_level2 = etree.SubElement(mcp_level1, level2)
  for i in range(1,4):
    mcp_level3 = etree.SubElement(mcp_level2, level3)
    mcp_level4a = etree.SubElement(mcp_level3, level4a)
    mcp_level4a.text = str(uuid.uuid4())
    mcp_level4b = etree.SubElement(mcp_level3, level4b)
    mcp_level4b.text = str(uuid.uuid4())
  mcp_tree = etree.ElementTree(mcp_level1)
  return etree.ElementTree(mcp_level1)

if __name__ == '__main__':
    unittest.main()