# Introduction

Mounting the Docker socket (`/var/run/docker.sock`) inside a container is a common misconfiguration that grants the container full control over the Docker daemon. Any process inside the container can create new containers, including privileged ones with the host filesystem mounted. This turns container isolation into nothing.

## What you will do in this lab

1. Discover that the Docker socket is exposed via the application's API.
2. Create a privileged container that mounts the host filesystem at `/hostfs`.
3. Use that container to read a file that only exists on the host, capturing the second flag.

## Why it matters

This misconfiguration appears frequently in CI/CD environments, monitoring tools, and admin dashboards where developers need container management from inside a container. Once an attacker has code execution in the container (even as a low-privilege user), the socket gives them root on the Docker host.
