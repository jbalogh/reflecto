import json
import subprocess
import urlparse


def app(env, start_response):
    start_response(200, [('Content-Type', 'text/plain')])
    if env['REQUEST_METHOD'] != 'POST':
        return ''

    payload = dict(urlparse.parse_qsl(env['wsgi.input'].read()))['payload']
    repo = json.loads(payload)['repository']
    url = repo['url'] + '.git'
    path = repo['owner']['name'] + '/' + repo['name']
    subprocess.Popen(['reflecto.sh', url, path]).communicate()
    return url
