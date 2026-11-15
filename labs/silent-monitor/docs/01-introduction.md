# Introduction

This lab contains a network monitoring dashboard called PulseMon. It has two security problems that chain together.

**Default credentials**: The login page includes an HTML comment that reveals the administrator password. Using those credentials gets you into the application.

**Command injection on the ping endpoint**: Once logged in, the dashboard offers a "ping check" tool that lets you test whether a monitored host is reachable. The backend passes your input directly to bash without any sanitisation. Sending a semicolon followed by a command injects a second command that runs on the server.

**Internal service pivot**: A second service runs inside the container and listens only on localhost port 9090. It is not exposed externally. The only way to reach it is to use the command injection to run curl from inside the container. This is a simplified model of a network pivot: exploiting one service to reach another that is not directly accessible.

The two flags are:
- flag1: in `/flag1.txt` on the server, readable via command injection
- flag2: served by the internal service at `http://127.0.0.1:9090/`, reachable only via the injection
