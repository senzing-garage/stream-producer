ARG BASE_IMAGE=debian:10.2
FROM ${BASE_IMAGE}

ENV REFRESHED_AT=2021-03-11

LABEL Name="senzing/stream-producer" \
      Maintainer="support@senzing.com" \
      Version="1.4.2"

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
 && pip3 install -r requirements.txt

# Copy files from repository.

COPY ./rootfs /
COPY ./stream-producer.py /app/

# Make non-root container.

USER 1001

# Runtime execution.

ENV SENZING_DOCKER_LAUNCHED=true

WORKDIR /app
ENTRYPOINT ["/app/stream-producer.py"]
