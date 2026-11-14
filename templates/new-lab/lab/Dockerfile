# Pin to a specific image version that has the vulnerable behaviour.
# Document WHY this exact version matters.
FROM alpine:3.18

# Runtime libraries (kept after build cleanup)
RUN apk add --no-cache openssl zlib shadow

# Build toolchain (removed after compile)
# RUN apk add --no-cache --virtual .build-deps \
#     build-base openssl-dev zlib-dev linux-headers wget

# Privsep user and sandbox required by sshd
RUN adduser -D -h /var/empty -s /sbin/nologin sshd 2>/dev/null || true \
    && mkdir -p /var/empty \
    && chmod 711 /var/empty

# --- Install the vulnerable service ---
# Option A: build from source (use this when the package manager has patched it)
#   RUN wget -q https://example.com/service-VERSION.tar.gz \
#       && tar -xzf service-VERSION.tar.gz \
#       && cd service-VERSION && ./configure && make -j$(nproc) && make install \
#       && cd / && rm -rf service-VERSION service-VERSION.tar.gz
#
# Option B: pin an exact package version from the distro
#   RUN apk add --no-cache 'package=VERSION'
#
# Option C: copy a pre-built binary (only when source build is impractical)
#   COPY binary /usr/local/bin/binary

COPY sshd_config /etc/ssh/sshd_config
COPY setup.sh /setup.sh
RUN chmod +x /setup.sh && /setup.sh

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D", "-e"]
