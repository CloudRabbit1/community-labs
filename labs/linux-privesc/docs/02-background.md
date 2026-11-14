# Background

## SUID

The SUID (Set User ID) bit on an executable means: when any user runs this file, the process's effective UID becomes the file owner's UID. For a binary owned by root with SUID set, any user who executes it runs it as root.

This is legitimate for programs like `passwd`, which need to write to `/etc/shadow` as root but should be runnable by any user. It becomes a problem when the binary is a general-purpose tool — a file reader, a shell, an interpreter — that lets the caller supply arbitrary input.

```bash
ls -la /usr/local/bin/readfile
# -rwsr-xr-x 1 root root ... /usr/local/bin/readfile
#    ^ the 's' in owner's execute position is the SUID bit
```

## sudo

`sudo` runs a command as another user, typically root. The `/etc/sudoers` file controls which users can run which commands as which other users, with or without a password.

A misconfigured sudoers entry allows a user to run a command that itself can spawn other commands. This is called a GTFOBin (Get The F*** Out Binaries) — a legitimate binary that can be used to escape restrictions.

`find` is a classic example: its `-exec` flag executes an arbitrary command for each matched file. If a user can run `find` as root without a password, they can run any command as root.

```
# /etc/sudoers.d/lowpriv (the misconfiguration)
lowpriv ALL=(ALL) NOPASSWD: /usr/bin/find
```

## Writable files in sudo rules

A sudoers rule that allows running a script without a password is dangerous if the script can be modified by the user. The privilege runs as root, but the script content is controlled by the user.

```
lowpriv ALL=(ALL) NOPASSWD: /opt/backup.sh
```

If `/opt/backup.sh` has permissions `777` (world-writable), `lowpriv` can overwrite the script with any command and then run it as root.

## Linux capabilities

Linux capabilities divide the traditional all-or-nothing root privilege into discrete units. `CAP_DAC_READ_SEARCH` bypasses the standard file read and directory traversal permission checks. A process with this capability in its effective set can open any file, regardless of its owner and permission bits.

File capabilities allow a binary to gain specific capabilities when run, without being SUID root. The `cap_dac_read_search+ep` flag on a binary means: any user who executes it gets `CAP_DAC_READ_SEARCH` in their effective and permitted capability sets.

```bash
getcap /usr/local/bin/py3
# /usr/local/bin/py3 cap_dac_read_search=ep
```

A Python binary with this capability can open `/root/flag4.txt` even when run as `lowpriv`.
