# Finding the Vulnerability

## Enumerate the container configuration

Connect to the diagnostic service and check the container info endpoint:

```
curl http://localhost:8080/info
```

```json
{
  "container": "privileged",
  "pid_namespace": "host",
  "cgroup_version": "v1",
  "note": "This container runs privileged to support low-level infrastructure diagnostics."
}
```

The service tells you directly: the container is privileged. That means you
can mount filesystems.

## Confirm cgroup v1 is available

Check whether the cgroup memory controller is accessible from inside the
container:

```
curl "http://localhost:8080/execute?cmd=ls+/sys/fs/cgroup"
```

```
blkio  cpu  cpuacct  cpuset  devices  freezer
hugetlb  memory  net_cls  net_prio  perf_event  pids
```

The `memory` controller is listed. cgroup v1 is active on this host.

## Understand what you can do

Three facts combine to make the escape possible:

1. The container is privileged, so you can run `mount`.
2. cgroup v1 is available, so you can create a new hierarchy mount point.
3. The kernel's release_agent runs in the host namespace, so whatever you
   write there executes on the host.

The diagnostic endpoint executes commands without restriction. All the
conditions for the release_agent technique are present.
