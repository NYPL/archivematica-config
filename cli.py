import mcp
import os
import glob
import argparse
import pymysql
import configparser

def _parse_db_config():
  configParser = configparser.RawConfigParser()   
  configFilePath = 'dbsettings'
  configParser.read(configFilePath)

  return configParser


def _collect_db_data(configParser):
  try:
    pw = configParser.get('client', 'password')
  except:
    pw = ''

  conn = pymysql.connect(
    host=configParser.get('client', 'host'),
    user=configParser.get('client', 'user'),
    passwd=pw,
    db=configParser.get('client', 'database'))
  cur = conn.cursor()

  def mcp_query(sql, cur):
    cur.execute(sql)
    return dict(cur.fetchall())

  links = mcp_query("SELECT pk, microserviceGroup FROM MicroServiceChainLinks", cur)
  chain_choices = mcp_query("SELECT pk, description FROM MicroServiceChoiceReplacementDic", cur)
  chains = mcp_query("SELECT pk, description FROM MicroServiceChains", cur)

  mcp_dict = {}
  for k,v in links.items()+chain_choices.items()+chains.items():
    mcp_dict[k]= v
    
  return mcp_dict


def _make_parser():
  parser = argparse.ArgumentParser()
  parser.description = "add human readable text to archivematica MCPs"
  parser.add_argument("-f", "-x", "--file",
    help = "path to an MCP file")
  parser.add_argument("-d", "--dir",
    help = "path to a directory of MCP files")
  parser.add_argument("-o", "--output",
    help = "directory to save output",
    default = '.')
  return parser

if __name__ == '__main__':
  parser = _make_parser()
  args = parser.parse_args()

  mcps = []

  if args.dir:
    directory_path = os.path.abspath(args.dir)
    for path in glob.glob(os.path.join(directory_path, '*ProcessingMCP.xml')):
      mcps.append(path)

  if args.file:
    mcps.append(os.path.abspath(args.file))

  configParser = _parse_db_config()
  mcp_dict = _collect_db_data(configParser)

  for path in set(mcps):
    mcp_data = mcp.MCP(path)
    mcp_data.set_uuid_labels(mcp_dict)
    mcp_data.write(args.output)