#!/usr/bin/env python

import urllib2

url = 'https://example.org/virtual-planner/board/cron/'

passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
passman.add_password(None, url, 'username', 'password')

authhandler = urllib2.HTTPBasicAuthHandler(passman)
opener = urllib2.build_opener(authhandler)
urllib2.install_opener(opener)

urllib2.urlopen(url)
