from flask import Flask, request, jsonify
import os

app = Flask(__name__)
FLAG1 = os.environ.get('FLAG1', 'POC{flag1_missing}')
FLAG2 = os.environ.get('FLAG2', 'POC{flag2_missing}')

_containers = []


@app.get('/')
def index():
    return '''<html><head><title>WebApp</title></head><body>
<h1>Container Management Portal</h1>
<p>Docker socket: /var/run/docker.sock</p>
<p>API: GET /api/info | GET /api/containers/json | POST /api/containers/create | POST /api/containers/start | GET /api/escape</p>
</body></html>'''


@app.get('/api/info')
def docker_info():
    return jsonify({
        'DockerRootDir': '/var/lib/docker',
        'HttpProxy': '',
        'OperatingSystem': 'Ubuntu 22.04.3 LTS',
        'ServerVersion': '24.0.5',
        'SocketPath': '/var/run/docker.sock',
        'flag1': FLAG1
    })


@app.get('/api/containers/json')
def list_containers():
    return jsonify(_containers)


@app.post('/api/containers/create')
def create_container():
    data = request.get_json() or {}
    image = data.get('Image', '')
    binds = data.get('HostConfig', {}).get('Binds', [])
    privileged = data.get('HostConfig', {}).get('Privileged', False)

    escape_ready = privileged and any(
        '/:/' in b or b.startswith('/:/') or 'hostfs' in b.lower()
        for b in binds
    )

    if escape_ready:
        container_id = 'escapedeadbeef12345678'
        _containers.append({'Id': container_id, 'Image': image, 'Status': 'created', 'escape_ready': True})
        return jsonify({'Id': container_id, 'Warnings': []}), 201

    container_id = 'normalabcdef12345678'
    _containers.append({'Id': container_id, 'Image': image, 'Status': 'created', 'escape_ready': False})
    return jsonify({'Id': container_id, 'Warnings': []}), 201


@app.post('/api/containers/<container_id>/start')
def start_container(container_id):
    return jsonify({}), 204


@app.get('/api/escape')
def escape():
    if any(c.get('escape_ready') for c in _containers):
        return jsonify({
            'escaped': True,
            'host_file': '/etc/shadow',
            'content': 'root:$6$xyz:19000:0:99999:7:::',
            'flag2': FLAG2
        })
    return jsonify({'escaped': False, 'message': 'Create a privileged container with /:/hostfs first'}), 403


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
