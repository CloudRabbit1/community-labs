# Introduction

This lab contains a Linux system with four privilege escalation paths. All four are real configurations found in production systems. None require exploiting a software vulnerability — they are all misconfigurations that give a low-privilege user a path to read files owned by root.

**SUID binary**: a custom binary is owned by root and has the SUID bit set. When you run it as `lowpriv`, it executes with root's effective UID. The binary reads arbitrary files, so you can pass `/root/flag1.txt` as the argument and get the contents.

**sudo misconfiguration**: `lowpriv` can run `/usr/bin/find` as root without a password. `find` has a `-exec` flag that runs an arbitrary command for each matched file. You can use it to execute `cat` as root.

**World-writable sudo script**: `lowpriv` can also run `/opt/backup.sh` as root without a password. The script is world-writable. You overwrite it with a command that reads flag3, then run it via sudo.

**Linux capabilities**: a copy of Python at `/usr/local/bin/py3` has the `cap_dac_read_search` file capability. Any user who runs it gets that capability in their effective set, which lets them read any file regardless of permissions.

The lab SSH port is 2222. Log in as `lowpriv` with password `lowpriv123` and work through the four paths in any order.
