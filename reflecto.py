import json
import re
import os
import subprocess
import urlparse


GIT='/usr/bin/git'
ROOT='/var/repos/git'


def clean(s):
    return re.sub('[^-/:.\w]', '', s)


def create_or_update_repo(url, path):
    target = os.path.join(ROOT, path)
    if not os.path.isdir(target): 
        subprocess.Popen([GIT, 'clone',
                                '--mirror', url, target]).communicate()
    else:
        subprocess.Popen([GIT, 'fetch'], cwd=target)


def application(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    if env['REQUEST_METHOD'] != 'POST':
        return ''

    payload = dict(urlparse.parse_qsl(env['wsgi.input'].read()))['payload']
    repo = json.loads(payload)['repository']
    url = clean(repo['url'] + '.git')
    path = clean(repo['owner']['name'] + '/' + repo['name'])

    create_or_update_repo(url, path)

    return url
