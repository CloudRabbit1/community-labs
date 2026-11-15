# Background

## Apache Options and directory listing

Apache httpd controls which features are active per directory through the `Options` directive. One of those features is `Indexes`. When `Options +Indexes` is set for a directory, Apache generates an HTML file listing if no `index.html` or `index.php` is present. This is a convenience for file-sharing servers but a hazard on application servers where backup directories, configuration dumps, and log files accumulate over time.

The correct setting is `Options -Indexes`, which causes Apache to return a 403 Forbidden response instead of listing the directory contents.

Example of the vulnerable configuration:

```apache
<Directory "/var/www/html/backup">
    Options +Indexes
</Directory>
```

Example of the correct configuration:

```apache
<Directory "/var/www/html/backup">
    Options -Indexes
</Directory>
```

## CGI and how Apache executes scripts

CGI (Common Gateway Interface) is an older mechanism for running programs in response to HTTP requests. Apache passes the request details to the script as environment variables, then sends the script's stdout back to the client as the HTTP response. The `QUERY_STRING` environment variable contains the raw query string from the URL.

A shell script used as a CGI endpoint receives the query string but must parse it manually. If the developer passes user-supplied values directly to a shell command, any special characters in the input become part of the command itself.

## Shell injection via semicolons and subshells

In bash, a semicolon separates two independent commands:

```bash
bash -c "ping -c 1 127.0.0.1; id"
```

This runs `ping`, waits for it to finish, then runs `id`. The two commands are unrelated. The semicolon is the injection point.

If a web application builds a shell command by concatenating user input, an attacker who controls the input can terminate the intended command early and append their own. The injected command runs with the same privileges as the process that executed bash, which in this case is the Apache worker process running as `www-data`.

URL encoding: browsers and curl percent-encode certain characters in query strings. A semicolon in a URL becomes `%3B`. Apache decodes it before setting `QUERY_STRING`, so the script sees the literal semicolon, and bash interprets it as a command separator.
