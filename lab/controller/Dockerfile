# Lab controller: runs Gandalf's Python and Bash collectors against the targets
# over the private lab network. Gandalf's source is mounted read-only at
# /gandalf-src and copied to a scratch directory per run.
FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends openssh-client sshpass expect socat bash tar gzip zip unzip coreutils \
 && rm -rf /var/lib/apt/lists/* \
 && pip install --no-cache-dir paramiko scp cryptography

# ssh/scp shims that answer password prompts from $SSHPASS. They sit first on
# PATH so gandalf.sh runs unmodified.
RUN mkdir -p /opt/lab-bin \
 && printf '#!/bin/sh\nexec sshpass -e /usr/bin/ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR "$@"\n' > /opt/lab-bin/ssh \
 && printf '#!/bin/sh\nexec sshpass -e /usr/bin/scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR "$@"\n' > /opt/lab-bin/scp \
 && chmod +x /opt/lab-bin/ssh /opt/lab-bin/scp

ENTRYPOINT ["bash", "/lab/collect.sh"]
