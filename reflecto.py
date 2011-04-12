import json
import re
import subprocess
import urlparse


def clean(s):
    return re.sub('[^-/:.\w]', '', s)


def app(env, start_response):
    start_response(200, [('Content-Type', 'text/plain')])
    if env['REQUEST_METHOD'] != 'POST':
        return ''

    payload = dict(urlparse.parse_qsl(env['wsgi.input'].read()))['payload']
    repo = json.loads(payload)['repository']
    url = clean(repo['url'] + '.git')
    path = clean(repo['owner']['name'] + '/' + repo['name'])
    subprocess.Popen(['reflecto.sh', url, path]).communicate()
    return url
