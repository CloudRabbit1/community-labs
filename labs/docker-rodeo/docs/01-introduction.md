# Introduction

Docker containers are isolated from each other and from the host by default. That isolation depends on not sharing sensitive resources. The Docker daemon socket at `/var/run/docker.sock` is one of those resources. Any process that can write to this socket has the same level of access to the Docker daemon as `root` on the host.

This lab runs a "Docker management dashboard" inside a container. The container has `/var/run/docker.sock` mounted in from the host, and the dashboard exposes HTTP endpoints that proxy calls to that socket. An attacker who can reach port 8080 can create a new container that mounts a secret volume, run a command inside it, and read a file that was not intended to be accessible.

The Docker socket misconfiguration is one of the most common container escape paths in real penetration tests.
