# Gandalf Linux target: sshd + sudo + python3, seeded with known artefacts.
# One Dockerfile for every distro; BASE picks the image and setup.sh picks the
# package manager. Built by linux-targets/docker-compose.yml.
ARG BASE=ubuntu:24.04
FROM ${BASE}

COPY setup.sh /lab/setup.sh
RUN sh /lab/setup.sh

COPY seed/ /lab/seed/
RUN sh /lab/seed/seed-artefacts.sh

COPY entrypoint.sh /lab/entrypoint.sh
EXPOSE 22
ENTRYPOINT ["sh", "/lab/entrypoint.sh"]
