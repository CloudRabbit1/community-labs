# Defense

## The Fix

Update glibc to 2.39 or later. The fix adds a length check before copying the
`GLIBC_TUNABLES` value into the heap buffer, and also strips the variable entirely
when launching SUID/SGID binaries.

**Fedora/RHEL:**
```bash
sudo dnf update glibc
```

**Debian/Ubuntu:**
```bash
sudo apt-get update && sudo apt-get upgrade libc6
```

## Mitigation Without Upgrading

Disable SUID on binaries that an attacker could use as the trigger:

```bash
# Check which SUID binaries are present
find / -perm -4000 -type f 2>/dev/null

# Remove SUID from non-essential binaries (verify before doing this)
chmod u-s /usr/bin/pkexec
```

This does not fix the underlying buffer overflow. It only removes the execution
vector that makes the overflow privilege-escalating.

## Detection

Monitor for unexpected process privilege changes. A process that starts as uid=1000
and spawns a child as uid=0 without going through `su`, `sudo`, or `newuidmap` is
suspicious. Auditd rule:

```
-a always,exit -F arch=b64 -S setuid -F a0=0 -F exe!=/usr/bin/sudo -F exe!=/bin/su -k suid_escalation
```

Alert on any `setuid(0)` call from a non-privileged parent process.
