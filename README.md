# Archivematica Configurations

This repository contains Archivematica MCPs and tools to manipulate them.

Installation
------------

* Copy your git ssh credentials to the Archivematica instance and clone this repository
```
sudo git clone git@github.com:NYPL/archivematica-config /usr/lib/archivematica/archivematica-config
```

* Install required python packages
```
virtualenv /usr/share/python/archivematica-config
cd /usr/share/python/archivematica-config
source bin/activate
pip install -r /usr/lib/archivematica/archivematica-config/requirements.txt
```

* Test the installation of the tools
```
cd /usr/lib/archivematica/archivematica-config/
/usr/share/python/archivematica-config/bin/python cli.py
```
* Create a crontab entry to schedule a repeated runs of the script.
```
*/5 * * * * /etc/archivematica/archivematica-config/
```