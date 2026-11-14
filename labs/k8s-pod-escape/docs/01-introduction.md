# 01: Introduction

This lab simulates what an attacker can do after gaining arbitrary file read access inside a Kubernetes pod. It models two escalation paths: reading pod-level secrets from the proc filesystem, and accessing node-level data through a misconfigured hostPath volume.

## The scenario

An attacker has found an arbitrary file read vulnerability in a service running inside a Kubernetes pod. The service exposes a debug endpoint that reads files from an allowlist of "safe" paths. These paths include proc filesystem entries and a directory mounted from the node.

## The two escalation steps

**Step 1: pod-level secrets.** Environment variables are readable via `/proc/self/environ`. Kubernetes injects secrets, tokens, and configuration into the pod environment. Reading this file exposes everything the pod was given at startup, including the flag embedded in `POD_SECRET`.

**Step 2: node-level data via hostPath.** Kubernetes hostPath volumes mount a directory from the underlying node directly into the pod. A pod with a hostPath mount can read (and write, if writable) the node's filesystem in that directory. The flag in `/mnt/hostpath/node-secret.txt` represents data that only the node should hold, now accessible from within the pod.

## Connection to CVE-2024-21626

CVE-2024-21626 (the Leaky Vessels runc vulnerability) exploits a file descriptor leak in the runc container runtime. When a container is configured with a working directory of `/proc/self/fd/7` (or similar), runc leaves an open file descriptor pointing to the host's root filesystem. The container process starts with its working directory on the host. This allows the attacker to traverse the host filesystem from inside the container, which is the same access model this lab demonstrates using a hostPath volume.
