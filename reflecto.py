import json
import logging
import logging.handlers
import re
import os
import subprocess
import urlparse


GIT='/usr/bin/git'
ROOT='/var/repos/git'

log = logging.getLogger('reflecto')
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler())


def clean(s):
    return re.sub('[^-/:.\w]', '', s)


def create_or_update_repo(url, path):
    target = os.path.join(ROOT, path)
    if not os.path.exists(target):
        log.info('git clone --mirror %s %s' % (url, target))
        subprocess.Popen([GIT, 'clone', '--mirror', url, target]).communicate()
    else:
        log.info('cd %s && git fetch' % target)
        subprocess.Popen([GIT, 'fetch'], cwd=target)


def application(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    if env['REQUEST_METHOD'] != 'POST':
        return ''

    payload = dict(urlparse.parse_qsl(env['wsgi.input'].read()))['payload']
    repo = json.loads(payload)['repository']
    url = clean(repo['url'] + '.git')
    path = clean(repo['owner']['name'] + '/' + repo['name'])

    log.info('Updating %s => %s.' % (url, path))
    create_or_update_repo(url, path)

    return 'OK'
