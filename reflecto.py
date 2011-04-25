import glob
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


def get_repo_config(dir, key):
    p = subprocess.Popen([GIT, 'config', '--get', key],
                            stdout=subprocess.PIPE, cwd=dir)
    value = p.communicate()[0].strip()
    return value


def repo_list():

    def to_url(url, rev):
        m = re.search('(.+/(.+/.+))\.git', url)
        if m:
            base = m.group(1)
            name = m.group(2)
            if rev:
                return '<a href="{0}/commit/{1}">{2} ({1})</a>'.format(base, rev[:6], name)
            else:
                return '<a href="{0}">{1}</a>'.format(base, name)


    def get_latest_rev(r):
        master_ref_path = os.path.join(r, 'refs', 'heads', 'master')
        try:
            return open(master_ref_path).read().strip()
        except IOError:
            return ''


    def repo_urls():
        repos = glob.glob(os.path.join(ROOT, "*", "*"))
        for r in repos:
            url = get_repo_config(r, 'remote.origin.url') 
            rev = get_latest_rev(r)
            yield to_url(url, rev)


    def to_ul(items):
        return '<ul>%s</ul>' % "\n".join('<li>%s</li>' % u for u in items)


    return to_ul(repo_urls())


def application(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    if env['REQUEST_METHOD'] != 'POST':
        return [repo_list()]

    payload = dict(urlparse.parse_qsl(env['wsgi.input'].read()))['payload']
    repo = json.loads(payload)['repository']
    url = clean(repo['url'] + '.git')
    path = clean(repo['owner']['name'] + '/' + repo['name'])

    log.info('Updating %s => %s.' % (url, path))
    create_or_update_repo(url, path)

    return 'OK'
