"""
Kubernetes Pod Escape lab.

This lab simulates a Kubernetes pod that exposes an arbitrary file read
vulnerability. The student uses it to:

1. Read /proc/self/environ to discover the POD_SECRET (FLAG1).
   This simulates what an attacker can read once inside a pod.

2. Read /proc/self/mounts to discover a hostPath volume at /mnt/hostpath.
   The hostPath mount gives the pod read access to part of the node's
   filesystem. This models CVE-2024-21626 (Leaky Vessels / runc) where
   a container's working directory resolves to a path on the host,
   allowing the container process to traverse the node filesystem.

3. Read /mnt/hostpath/node-secret.txt to get FLAG2.
   This simulates escalating from pod-level to node-level data access.

Flags:
  FLAG1: in the POD_SECRET environment variable (read via /proc/self/environ)
  FLAG2: in /mnt/hostpath/node-secret.txt (hostPath volume)
"""
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

ALLOWED_READ_PATHS = {
    '/proc/self/environ',
    '/proc/self/mounts',
    '/proc/self/status',
    '/proc/self/cmdline',
    '/var/run/secrets/kubernetes.io/serviceaccount/token',
    '/var/run/secrets/kubernetes.io/serviceaccount/namespace',
    '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt',
    '/mnt/hostpath/node-secret.txt',
    '/etc/hostname',
    '/etc/os-release',
}


@app.get('/')
def index():
    return jsonify({
        'app': 'k8s-pod-svc',
        'version': '1.0',
        'endpoints': [
            'GET /api/info              -- pod info',
            'GET /api/read?path=<path>  -- read a file (debugging endpoint)',
            'GET /api/mounts            -- list /proc/self/mounts',
        ],
        'hint': 'Try reading /proc/self/environ and /proc/self/mounts',
    })


@app.get('/api/info')
def api_info():
    return jsonify({
        'hostname': os.environ.get('HOSTNAME', 'unknown'),
        'namespace': 'default',
        'service_account': 'default',
        'node_name': 'node-01',
    })


@app.get('/api/mounts')
def api_mounts():
    try:
        with open('/proc/self/mounts') as f:
            content = f.read()
        mounts = []
        for line in content.strip().split('\n'):
            parts = line.split()
            if len(parts) >= 2:
                mounts.append({'device': parts[0], 'mountpoint': parts[1], 'fstype': parts[2] if len(parts) > 2 else ''})
        return jsonify({'mounts': mounts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.get('/api/read')
def api_read():
    path = request.args.get('path', '')
    if not path:
        return jsonify({'error': 'path parameter required',
                        'hint': 'Try /proc/self/environ or /proc/self/mounts'}), 400

    # Intentionally weak check: only allows a known set of "debug" paths
    # but the real vulnerability is that /proc/self/environ leaks secrets
    # and /mnt/hostpath leaks node data
    if path not in ALLOWED_READ_PATHS:
        return jsonify({'error': f'path not in allowed debug paths',
                        'allowed': sorted(ALLOWED_READ_PATHS)}), 403

    try:
        with open(path, 'rb') as f:
            raw = f.read()
        # Null-separate environ to newlines for readability
        if path.endswith('/environ'):
            text = raw.replace(b'\x00', b'\n').decode(errors='replace')
        else:
            text = raw.decode(errors='replace')
        return jsonify({'path': path, 'content': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
