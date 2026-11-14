FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server sudo python3 openssl build-essential libcap2-bin \
    && rm -rf /var/lib/apt/lists/*

# Compile the SUID readfile binary
COPY readfile.c /tmp/readfile.c
RUN gcc -o /usr/local/bin/readfile /tmp/readfile.c \
    && rm /tmp/readfile.c \
    && chown root:root /usr/local/bin/readfile \
    && chmod 4755 /usr/local/bin/readfile

# Copy of Python for the capabilities demonstration
RUN cp $(readlink -f /usr/bin/python3) /usr/local/bin/py3 \
    && setcap cap_dac_read_search+ep /usr/local/bin/py3

# Create lowpriv user
RUN useradd -m -s /bin/bash lowpriv \
    && echo 'lowpriv:lowpriv123' | chpasswd

# sudo: lowpriv can run find and backup.sh as root without password
RUN echo 'lowpriv ALL=(ALL) NOPASSWD: /usr/bin/find' > /etc/sudoers.d/lowpriv \
    && echo 'lowpriv ALL=(ALL) NOPASSWD: /opt/backup.sh' >> /etc/sudoers.d/lowpriv \
    && chmod 440 /etc/sudoers.d/lowpriv

# World-writable sudo script
RUN echo '#!/bin/sh' > /opt/backup.sh \
    && chmod 0777 /opt/backup.sh

# sshd setup
RUN mkdir -p /run/sshd
COPY sshd_config /etc/ssh/sshd_config

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22
ENTRYPOINT ["/entrypoint.sh"]
