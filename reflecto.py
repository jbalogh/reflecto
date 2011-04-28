import glob
import json
import logging
import logging.handlers
import re
import os
import subprocess
import urlparse

from jinja2 import Environment, FileSystemLoader


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

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


def get_repo_config(repo, key):
    p = subprocess.Popen([GIT, 'config', '--get', key],
                         stdout=subprocess.PIPE, cwd=repo)
    return p.communicate()[0].strip()


def get_latest_rev(repo):
    p = subprocess.Popen([GIT, 'show', '-s', '--pretty=format:%h', 'master'],
                         stdout=subprocess.PIPE, cwd=repo)
    return p.communicate()[0].strip()


def list_repos():
    repos = glob.glob(os.path.join(ROOT, "*", "*"))
    for r in repos:
        url = get_repo_config(r, 'remote.origin.url')
        rev = get_latest_rev(r)

        m = re.search('(.+/(.+/.+))\.git', url)
        if m:
            url = m.group(1)
            name = m.group(2)
            if rev:
                url = "%s/commits/%s" % (url, rev)

            yield {'url': url, 'rev': rev, 'name': name}


def repo_list():
    return env.get_template('repo_list.html').render(repos=sorted(list_repos()))


def application(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    if env['REQUEST_METHOD'] != 'POST':
        return [repo_list().encode('utf-8')]

    payload = dict(urlparse.parse_qsl(env['wsgi.input'].read()))['payload']
    repo = json.loads(payload)['repository']
    url = clean(repo['url'] + '.git')
    path = clean(repo['owner']['name'] + '/' + repo['name'])

    log.info('Updating %s => %s.' % (url, path))
    create_or_update_repo(url, path)

    return 'OK'
