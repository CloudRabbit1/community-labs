#!/bin/sh
# Generate flags
printf 'POC{%s}\n' "$(openssl rand -hex 16)" > /flag1.txt
printf 'POC{%s}\n' "$(openssl rand -hex 16)" > /flag2.txt

# Simulate a Kubernetes pod environment
# FLAG1: pod-level secret (accessible within the container via proc/env)
FLAG1=$(cat /flag1.txt)
export POD_SECRET="$FLAG1"

# Simulate a hostPath volume mount: data the node wrote before the pod started
# FLAG2: in the "host" volume -- simulates /proc/self/fd escape giving host fs access
mkdir -p /mnt/hostpath
printf '%s\n' "$(cat /flag2.txt)" > /mnt/hostpath/node-secret.txt

# Write a fake /etc/kubernetes-style service account token (educational, not real)
mkdir -p /var/run/secrets/kubernetes.io/serviceaccount
echo 'eyJhbGciOiJSUzI1NiIsImtpZCI6ImZha2UifQ.eyJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6ZGVmYXVsdDpkZWZhdWx0In0.fake' \
    > /var/run/secrets/kubernetes.io/serviceaccount/token
echo 'kube-system' > /var/run/secrets/kubernetes.io/serviceaccount/namespace
echo 'fake-ca-cert-data' > /var/run/secrets/kubernetes.io/serviceaccount/ca.crt

exec python3 /app/app.py
