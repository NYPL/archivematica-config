import os
from lxml import etree
import pymysql
import re


class MCPError(Exception):
  def __init__(self, message):
    self.message = message


class MCP:

  def __init__(self, path = None):
    if path:
      if os.path.exists(path):
        self.path = path
        self.filename = os.path.basename(path)
      else:
        raise OSError('No such file or directory: {}'.format(path))

      try:
        self.tree = etree.parse(self.path)
      except etree.XMLSyntaxError:
        raise MCPError('{} does not contain valid XML'.format(self.filename))

      if not self.validate_mcp():
        raise MCPError('{} does not appear to be a valid Archivematica MCP'.format(self.filename))


  def validate_mcp(self):
    mcp_schema_doc = etree.parse('mcp.xsd')
    mcp_schema = etree.XMLSchema(mcp_schema_doc)
    if mcp_schema.validate(self.tree):
      return True
    else:
      return False


  def get_uuids(self):
    uuid_regex = re.compile('[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}')
    choices = etree.XPath("//preconfiguredChoice")
    uuids = []

    for element in choices(self.tree):
      uuid_dict = {}
      for subelement in element.getchildren():
        if uuid_regex.match(subelement.text):
          uuid_dict[subelement.tag] = subelement.text
      uuids.append(uuid_dict)

    return uuids


  def set_uuid_labels(self, replacement_dict):
    choices = etree.XPath("//preconfiguredChoice")

    for element in choices(self.tree):
      for subelement in element.getchildren():
        try:
          attrib = replacement_dict[subelement.text]
        except:
          attrib = None
        if attrib:
          subelement.attrib['label'] = attrib



