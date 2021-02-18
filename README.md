# stream-producer

## Preamble

At [Senzing](http://senzing.com),
we strive to create GitHub documentation in a
"[don't make me think](https://github.com/Senzing/knowledge-base/blob/master/WHATIS/dont-make-me-think.md)" style.
For the most part, instructions are copy and paste.
Whenever thinking is needed, it's marked with a "thinking" icon :thinking:.
Whenever customization is needed, it's marked with a "pencil" icon :pencil2:.
If the instructions are not clear, please let us know by opening a new
[Documentation issue](https://github.com/Senzing/stream-producer/issues/new?template=documentation_request.md)
describing where we can improve.   Now on with the show...

## Overview

### Contents

1. [Related artifacts](#related-artifacts)
1. [Expectations](#expectations)
1. [Demonstrate using Command Line Interface](#demonstrate-using-command-line-interface)
    1. [Prerequisites for CLI](#prerequisites-for-cli)
    1. [Download](#download)
    1. [Run command](#run-command)
1. [Demonstrate using Docker](#demonstrate-using-docker)
    1. [Prerequisites for Docker](#prerequisites-for-docker)
    1. [Docker network](#docker-network)
    1. [Run Docker container](#run-docker-container)
1. [Develop](#develop)
    1. [Prerequisites for development](#prerequisites-for-development)
    1. [Clone repository](#clone-repository)
    1. [Build Docker image](#build-docker-image)
1. [Examples](#examples)
    1. [Examples of CLI](#examples-of-cli)
    1. [Examples of Docker](#examples-of-docker)
1. [Advanced](#advanced)
    1. [Configuration](#configuration)
    1. [AWS configuration](#aws-configuration)
1. [Errors](#errors)
1. [References](#references)

#### Legend

1. :thinking: - A "thinker" icon means that a little extra thinking may be required.
   Perhaps there are some choices to be made.
   Perhaps it's an optional step.
1. :pencil2: - A "pencil" icon means that the instructions may need modification before performing.
1. :warning: - A "warning" icon means that something tricky is happening, so pay attention.

## Related artifacts

1. [DockerHub](https://hub.docker.com/r/senzing/stream-producer)

## Expectations

- **Space:** This repository and demonstration require 6 GB free disk space.
- **Time:** Budget 40 minutes to get the demonstration up-and-running, depending on CPU and network speeds.
- **Background knowledge:** This repository assumes a working knowledge of:
  - [Docker](https://github.com/Senzing/knowledge-base/blob/master/WHATIS/docker.md)

## Demonstrate using Command Line Interface

### Prerequisites for CLI

:thinking: The following tasks need to be complete before proceeding.
These are "one-time tasks" which may already have been completed.

1. Install Python prerequisites.
   Example:

    ```console
    pip3 install -r https://raw.githubusercontent.com/Senzing/stream-producer/master/requirements.txt
    ```

    1. See [requirements.txt](requirements.txt) for list.
        1. [Installation hints](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-python-dependencies.md)

### Download

1. Get a local copy of
   [stream-producer.py](stream-producer.py).
   Example:

    1. :pencil2: Specify where to download file.
       Example:

        ```console
        export SENZING_DOWNLOAD_FILE=~/stream-producer.py
        ```

    1. Download file.
       Example:

        ```console
        curl -X GET \
          --output ${SENZING_DOWNLOAD_FILE} \
          https://raw.githubusercontent.com/Senzing/stream-producer/master/stream-producer.py
        ```

    1. Make file executable.
       Example:

        ```console
        chmod +x ${SENZING_DOWNLOAD_FILE}
        ```

1. :thinking: **Alternative:** The entire git repository can be downloaded by following instructions at
   [Clone repository](#clone-repository)

### Run command

1. Run the command.
   Example:

   ```console
   ${SENZING_DOWNLOAD_FILE} --help
   ```

1. For more examples of use, see [Examples of CLI](#examples-of-cli).

## Demonstrate using Docker

### Prerequisites for Docker

:thinking: The following tasks need to be complete before proceeding.
These are "one-time tasks" which may already have been completed.

1. The following software programs need to be installed:
    1. [docker](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-docker.md)

### Docker network

:thinking: **Optional:**  Use if Docker container is part of a Docker network.

1. List Docker networks.
   Example:

    ```console
    sudo docker network ls
    ```

1. :pencil2: Specify Docker network.
   Choose value from NAME column of `docker network ls`.
   Example:

    ```console
    export SENZING_NETWORK=*nameofthe_network*
    ```

1. Construct parameter for `docker run`.
   Example:

    ```console
    export SENZING_NETWORK_PARAMETER="--net ${SENZING_NETWORK}"
    ```

### Run Docker container

Although the `Docker run` command looks complex,
it accounts for all of the optional variations described above.
Unset environment variables have no effect on the
`docker run` command and may be removed or remain.

1. Run Docker container.
   This command will print the `--help`, then sleep.
   Example:

    ```console
    sudo docker run \
      --interactive \
      --rm \
      --tty \
      ${SENZING_NETWORK_PARAMETER} \
      senzing/stream-producer
    ```

1. For more examples of use, see [Examples of Docker](#examples-of-docker).

## Develop

The following instructions are used when modifying and building the Docker image.

### Prerequisites for development

:thinking: The following tasks need to be complete before proceeding.
These are "one-time tasks" which may already have been completed.

1. The following software programs need to be installed:
    1. [git](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-git.md)
    1. [make](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-make.md)
    1. [docker](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-docker.md)

### Clone repository

For more information on environment variables,
see [Environment Variables](https://github.com/Senzing/knowledge-base/blob/master/lists/environment-variables.md).

1. Set these environment variable values:

    ```console
    export GIT_ACCOUNT=senzing
    export GIT_REPOSITORY=stream-producer
    export GIT_ACCOUNT_DIR=~/${GIT_ACCOUNT}.git
    export GIT_REPOSITORY_DIR="${GIT_ACCOUNT_DIR}/${GIT_REPOSITORY}"
    ```

1. Using the environment variables values just set, follow steps in [clone-repository](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/clone-repository.md) to install the Git repository.

### Build Docker image

1. **Option #1:** Using `docker` command and GitHub.

    ```console
    sudo docker build \
      --tag senzing/stream-producer \
      https://github.com/senzing/stream-producer.git
    ```

1. **Option #2:** Using `docker` command and local repository.

    ```console
    cd ${GIT_REPOSITORY_DIR}
    sudo docker build --tag senzing/stream-producer .
    ```

1. **Option #3:** Using `make` command.

    ```console
    cd ${GIT_REPOSITORY_DIR}
    sudo make docker-build
    ```

    Note: `sudo make docker-build-development-cache` can be used to create cached Docker layers.

## Examples

### Examples of CLI

The following examples require initialization described in
[Demonstrate using Command Line Interface](#demonstrate-using-command-line-interface).

#### Upload file to AWS SQS

1. :pencil2: For AWS access, set environment variables.
   For more information, see
   [How to set AWS environment variables](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/set-aws-environment-variables.md)
   Example:

    ```console
    export AWS_ACCESS_KEY_ID=$(aws configure get default.aws_access_key_id)
    export AWS_SECRET_ACCESS_KEY=$(aws configure get default.aws_secret_access_key)
    export AWS_DEFAULT_REGION=$(aws configure get default.region)
    ```

1. :pencil2: Identify the file on the local system to push to the AWS SQS queue.
   Example:

    ```console
    export SENZING_INPUT_URL=/path/to/my/records.json
    ```

1. :pencil2: Identify the AWS SQS queue.
   Example:

    ```console
    export SENZING_SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/000000000000/queue-name
    ```

1. :thinking: **Optional:** If limiting the number of records is desired, identify the maximum number of records to send.
   To load all records in the file, set the value to "0".
   For more information, see
   [SENZING_RECORD_MAX](https://github.com/Senzing/knowledge-base/blob/master/lists/environment-variables.md#senzing_record_max)
   Example:

    ```console
    export SENZING_RECORD_MAX=100
    ```

1. Run `stream-producer.py`.
   Example:

    ```console
    ~/stream-producer.py json-to-sqs \
        --input-url ${SENZING_INPUT_URL} \
        --record-max ${SENZING_RECORD_MAX} \
        --sqs-queue-url ${SENZING_SQS_QUEUE_URL}
    ```

#### More

1. More example CLI invocations can be seen in
   [Tests](tests/README.md#test-cli)

### Examples of Docker

The following examples require initialization described in
[Demonstrate using Docker](#demonstrate-using-docker).

1. Example docker and docker-compose invocations can be seen in
   [Tests](tests/README.md#test-docker)
1. There is a [tutorial](https://github.com/Senzing/docker-compose-demo/tree/master/docs/docker-compose-sqs-postgresql-advanced) showing AWS SQS usage.

1. `docker run` command for populating Amazon SQS.
   Example:

    ```console
    docker run \
      --env AWS_ACCESS_KEY_ID=AAAAAAAAAAAAAAAAAAAA \
      --env AWS_DEFAULT_REGION=us-east-1 \
      --env AWS_SECRET_ACCESS_KEY=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa \
      --env SENZING_INPUT_URL="https://s3.amazonaws.com/public-read-access/TestDataSets/loadtest-dataset-1M.json" \
      --env SENZING_RECORD_MAX=100 \
      --env SENZING_SQS_QUEUE_URL="https://sqs.us-east-1.amazonaws.com/000000000000/queue-name" \
      --env SENZING_SUBCOMMAND=json-to-sqs \
      --interactive \
      --rm \
      --tty \
      senzing/stream-producer
    ```

## Advanced

### Configuration

Configuration values specified by environment variable or command line parameter.

- **[SENZING_NETWORK](https://github.com/Senzing/knowledge-base/blob/master/lists/environment-variables.md#senzing_network)**

### AWS configuration

[stream-producer.py](stream-producer.py) uses
[AWS SDK for Python (Boto3)](https://aws.amazon.com/sdk-for-python/)
to access AWS services.
This library may be configured via environment variables  or `~/.aws/config` file.

Example environment variables for configuration:

- **[AWS_ACCESS_KEY_ID](https://github.com/Senzing/knowledge-base/blob/master/lists/environment-variables.md#aws_access_key_id)**
- **[AWS_SECRET_ACCESS_KEY](https://github.com/Senzing/knowledge-base/blob/master/lists/environment-variables.md#aws_secret_access_key)**
- **[AWS_DEFAULT_REGION](https://github.com/Senzing/knowledge-base/blob/master/lists/environment-variables.md#aws_default_region)**

References:

- Boto3 [Configuration](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html)
- Boto3 [Credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)

## Errors

1. See [docs/errors.md](docs/errors.md).

## References
