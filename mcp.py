import os
from lxml import etree


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
    return False

