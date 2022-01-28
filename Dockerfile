ARG BASE_IMAGE=debian:11.2-slim@sha256:4c25ffa6ef572cf0d57da8c634769a08ae94529f7de5be5587ec8ce7b9b50f9c
FROM ${BASE_IMAGE}

ENV REFRESHED_AT=2022-01-28

LABEL Name="senzing/stream-producer" \
      Maintainer="support@senzing.com" \
      Version="1.6.5"

HEALTHCHECK CMD ["/app/healthcheck.sh"]

# Run as "root" for system installation.

USER root

# Install packages via apt.

RUN apt-get update \
      && apt-get -y install \
      librdkafka-dev \
      python3-dev \
      python3-pip \
      && rm -rf /var/lib/apt/lists/*

# Install packages via PIP.

COPY requirements.txt ./
RUN pip3 install --upgrade pip \
      && pip3 install -r requirements.txt \
      && rm requirements.txt

# Copy files from repository.

COPY ./rootfs /
COPY ./stream-producer.py /app/

# Make non-root container.

USER 1001

# Runtime execution.

ENV SENZING_DOCKER_LAUNCHED=true

WORKDIR /app
ENTRYPOINT ["/app/stream-producer.py"]
