# Introduction

This lab contains an Apache web server with two misconfigurations that are common in real deployments.

**Directory listing**: Apache's `Options +Indexes` directive makes the server generate a browsable file listing for a directory when no index file exists. The backup directory on this server has that option enabled. It contains a configuration file with credentials and a flag that was never meant to be accessible from the web.

**CGI command injection**: Apache's CGI support lets the server execute scripts and return their output as HTTP responses. The network status tool at `/cgi-bin/status.sh` takes a `host` parameter and passes it to `bash -c "ping -c 1 $HOST"` without any sanitization. Sending a semicolon followed by a command injects a second command that runs as the web server user.

Both flaws require no authentication, no special tools, and no prior knowledge of the system beyond its hostname and port. You need curl and the ability to construct a URL.
