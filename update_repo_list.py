#!/usr/bin/env python3

import os
import json
from pathlib import Path
import urllib.request

repos_url = 'https://api.github.com/users/luphord/repos'
repos_envs_txt = Path(__file__).parent / 'repos_envs.txt'

repos_envs_dict = {}
with open(repos_envs_txt) as f:
    for line in f:
        parts = line.split()
        repo = parts[0]
        env = parts[1] if len(parts) > 1 else None
        repos_envs_dict[repo] = env


f = urllib.request.urlopen(repos_url)
repos = json.loads((f.read().decode('utf-8')))

for repo in repos:
    repo_url = repo['clone_url']
    if not repo_url in repos_envs_dict:
        print('Adding {} to {}...'.format(repo_url, repos_envs_txt))
        repos_envs_dict[repo_url] = None

with open(repos_envs_txt, 'w') as f:
    for repo, env in sorted(repos_envs_dict.items()):
        if env:
            line = '{}\t{}'.format(repo, env)
        else:
            line = repo
        f.write(line + os.linesep)