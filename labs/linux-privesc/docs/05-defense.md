# Defense

## Audit SUID binaries

Find all SUID root binaries on the system:

```bash
find / -perm -4000 -user root -type f 2>/dev/null
```

Each binary in that list should be an OS-distributed binary with a known legitimate purpose. Any custom or unexpected binary in the list should be investigated. Remove the SUID bit if it is not needed:

```bash
chmod u-s /usr/local/bin/readfile
```

Do not create custom SUID binaries. If a task needs to run as root, use sudo with a tightly scoped rule.

## Harden sudo entries

Review all sudoers entries:

```bash
sudo -l
visudo -c
```

Avoid NOPASSWD entries for commands that can run arbitrary code. The GTFOBins project (gtfobins.github.io) lists binaries with known sudo escape paths. If `find`, `vim`, `python`, `awk`, or similar tools appear in a NOPASSWD entry, they are exploitable.

For the backup script pattern specifically: either run the cron job or scheduled task as a dedicated low-privilege service account, or give it a specific script that is not modifiable by the user who can invoke it.

## Check file permissions on sudo-accessible scripts

Any script that a user can run via sudo must not be writable by that user:

```bash
# Correct: owned by root, not world-writable
chown root:root /opt/backup.sh
chmod 750 /opt/backup.sh
```

An automated check:

```bash
grep -r NOPASSWD /etc/sudoers /etc/sudoers.d/ | grep -v '^#' | \
  awk '{print $NF}' | while read cmd; do
    [ -f "$cmd" ] && ls -la "$cmd"
  done
```

## Audit and remove unnecessary file capabilities

List all files with capabilities:

```bash
find / -not -path '/proc/*' -not -path '/sys/*' -type f 2>/dev/null | xargs getcap 2>/dev/null
```

Remove capabilities that are not needed:

```bash
setcap -r /usr/local/bin/py3
```

Do not give interpreters (Python, Perl, Ruby, bash) any capabilities. An interpreter with any dangerous capability is equivalent to giving that capability to any script it can run.
