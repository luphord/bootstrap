#!/usr/bin/env python3

import json
import urllib.request

repos_url = 'https://api.github.com/users/luphord/repos'
f = urllib.request.urlopen(repos_url)
repos = json.loads((f.read().decode('utf-8')))

for repo in repos:
    print(repo['url'])