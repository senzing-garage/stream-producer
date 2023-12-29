# stream-producer

If you are beginning your journey with
[Senzing](https://senzing.com/),
please start with
[Senzing Quick Start guides](https://docs.senzing.com/quickstart/).

You are in the
[Senzing Garage](https://github.com/senzing-garage)
where projects are "tinkered" on.
Although this GitHub repository may help you understand an approach to using Senzing,
it's not considered to be "production ready" and is not considered to be part of the Senzing product.
Heck, it may not even be appropriate for your application of Senzing!

## Synopsis

Populate a queue with records to be consumed by
[stream-loader](https://github.com/Senzing/stream-loader).

## Overview

The [stream-produder.py](stream-producer.py) python script reads files of different formats
(JSON, CSV, Parquet, Avro) and publishes it to a queue (RabbitMQ, Kafka, AWS SQS).
The `senzing/stream-producer` docker image is a wrapper for use in docker formations (e.g. docker-compose, kubernetes).

To see all of the subcommands, run:

```console
$ ./stream-producer.py --help
usage: stream-producer.py [-h]
                          {avro-to-kafka,avro-to-rabbitmq,avro-to-sqs,avro-to-sqs-batch,avro-to-stdout,csv-to-kafka,csv-to-rabbitmq,csv-to-sqs,csv-to-sqs-batch,csv-to-stdout,gzipped-json-to-kafka,gzipped-json-to-rabbitmq,gzipped-json-to-sqs,gzipped-json-to-sqs-batch,gzipped-json-to-stdout,json-to-kafka,json-to-rabbitmq,json-to-sqs,json-to-sqs-batch,json-to-stdout,parquet-to-kafka,parquet-to-rabbitmq,parquet-to-sqs,parquet-to-sqs-batch,parquet-to-stdout,websocket-to-kafka,websocket-to-rabbitmq,websocket-to-sqs,websocket-to-sqs-batch,websocket-to-stdout,sleep,version,docker-acceptance-test}
                          ...

Queue messages. For more information, see https://github.com/Senzing/stream-
producer

positional arguments:
  {avro-to-kafka,avro-to-rabbitmq,avro-to-sqs,avro-to-sqs-batch,avro-to-stdout,csv-to-kafka,csv-to-rabbitmq,csv-to-sqs,csv-to-sqs-batch,csv-to-stdout,gzipped-json-to-kafka,gzipped-json-to-rabbitmq,gzipped-json-to-sqs,gzipped-json-to-sqs-batch,gzipped-json-to-stdout,json-to-kafka,json-to-rabbitmq,json-to-sqs,json-to-sqs-batch,json-to-stdout,parquet-to-kafka,parquet-to-rabbitmq,parquet-to-sqs,parquet-to-sqs-batch,parquet-to-stdout,websocket-to-kafka,websocket-to-rabbitmq,websocket-to-sqs,websocket-to-sqs-batch,websocket-to-stdout,sleep,version,docker-acceptance-test}
                              Subcommands (SENZING_SUBCOMMAND):
    avro-to-kafka             Read Avro file and send to Kafka.
    avro-to-rabbitmq          Read Avro file and send to RabbitMQ.
    avro-to-sqs               Read Avro file and print to AWS SQS.
    avro-to-stdout            Read Avro file and print to STDOUT.

    csv-to-kafka              Read CSV file and send to Kafka.
    csv-to-rabbitmq           Read CSV file and send to RabbitMQ.
    csv-to-sqs                Read CSV file and print to SQS.
    csv-to-stdout             Read CSV file and print to STDOUT.

    gzipped-json-to-kafka     Read gzipped JSON file and send to Kafka.
    gzipped-json-to-rabbitmq  Read gzipped JSON file and send to RabbitMQ.
    gzipped-json-to-sqs       Read gzipped JSON file and send to AWS SQS.
    gzipped-json-to-stdout    Read gzipped JSON file and print to STDOUT.

    json-to-kafka             Read JSON file and send to Kafka.
    json-to-rabbitmq          Read JSON file and send to RabbitMQ.
    json-to-sqs               Read JSON file and send to AWS SQS.
    json-to-stdout            Read JSON file and print to STDOUT.

    parquet-to-kafka          Read Parquet file and send to Kafka.
    parquet-to-rabbitmq       Read Parquet file and send to RabbitMQ.
    parquet-to-sqs            Read Parquet file and print to AWS SQS.
    parquet-to-stdout         Read Parquet file and print to STDOUT.

    sleep                     Do nothing but sleep. For Docker testing.
    version                   Print version of program.
    docker-acceptance-test    For Docker acceptance testing.

optional arguments:
  -h, --help                  show this help message and exit
```

### Contents

1. [Demonstrate using Docker](#demonstrate-using-docker)
1. [Demonstrate using docker-compose](#demonstrate-using-docker-compose)
1. [Demonstrate using Command Line Interface](#demonstrate-using-command-line-interface)
    1. [Prerequisites for CLI](#prerequisites-for-cli)
    1. [Download](#download)
    1. [Run command](#run-command)
1. [Configuration](#configuration)
1. [AWS configuration](#aws-configuration)
1. [References](#references)

### Preamble

At [Senzing](http://senzing.com),
we strive to create GitHub documentation in a
"[don't make me think](https://github.com/Senzing/knowledge-base/blob/main/WHATIS/dont-make-me-think.md)" style.
For the most part, instructions are copy and paste.
Whenever thinking is needed, it's marked with a "thinking" icon :thinking:.
Whenever customization is needed, it's marked with a "pencil" icon :pencil2:.
If the instructions are not clear, please let us know by opening a new
[Documentation issue](https://github.com/Senzing/template-python/issues/new?template=documentation_request.md)
describing where we can improve.   Now on with the show...

### Legend

1. :thinking: - A "thinker" icon means that a little extra thinking may be required.
   Perhaps there are some choices to be made.
   Perhaps it's an optional step.
1. :pencil2: - A "pencil" icon means that the instructions may need modification before performing.
1. :warning: - A "warning" icon means that something tricky is happening, so pay attention.

### Expectations

- **Space:** This repository and demonstration require 6 GB free disk space.
- **Time:** Budget 40 minutes to get the demonstration up-and-running, depending on CPU and network speeds.
- **Background knowledge:** This repository assumes a working knowledge of:
  - [Docker](https://github.com/Senzing/knowledge-base/blob/main/WHATIS/docker.md)

## Demonstrate using Docker

1. Run Docker container.
   This command will show help.
   Example:

    ```console
    docker run \
      --rm \
      senzing/stream-producer --help

    ```

1. For more examples of use, see [Examples of Docker](docs/examples.md#examples-of-docker).

## Demonstrate using docker-compose

1. Deploy the
   [Backing Services](https://github.com/Senzing/knowledge-base/blob/main/HOWTO/deploy-rabbitmq-postgresql-backing-services.md#using-docker-compose)
   required by the Stream Loader.

1. Specify a directory to place artifacts in.
   Example:

    ```console
    export SENZING_VOLUME=~/my-senzing
    mkdir -p ${SENZING_VOLUME}

    ```

1. Download `docker-compose.yaml` file.
   Example:

    ```console
    curl -X GET \
      --output ${SENZING_VOLUME}/docker-compose.yaml \
      https://raw.githubusercontent.com/Senzing/stream-producer/main/docker-compose.yaml

    ```

1. Bring up docker-compose stack.
   Example:

    ```console
    docker-compose -f ${SENZING_VOLUME}/docker-compose.yaml up

    ```

## Demonstrate using Command Line Interface

### Prerequisites for CLI

:thinking: The following tasks need to be complete before proceeding.
These are "one-time tasks" which may already have been completed.

1. Install Python prerequisites.
   Example:

    ```console
    pip3 install -r https://raw.githubusercontent.com/Senzing/stream-producer/main/requirements.txt

    ```

    1. See [requirements.txt](requirements.txt) for list.
        1. [Installation hints](https://github.com/Senzing/knowledge-base/blob/main/HOWTO/install-python-dependencies.md)

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
          https://raw.githubusercontent.com/Senzing/stream-producer/main/stream-producer.py

        ```

    1. Make file executable.
       Example:

        ```console
        chmod +x ${SENZING_DOWNLOAD_FILE}

        ```

1. :thinking: **Alternative:** The entire git repository can be downloaded by following instructions at
   [Clone repository](docs/development.md#clone-repository)

### Run command

1. Run the command.
   Example:

   ```console
   ${SENZING_DOWNLOAD_FILE} --help

   ```

1. For more examples of use, see [Examples of CLI](docs/examples.md#examples-of-cli).

## Configuration

Configuration values specified by environment variable or command line parameter.

- **[SENZING_NETWORK](https://github.com/Senzing/knowledge-base/blob/main/lists/environment-variables.md#senzing_network)**

## AWS configuration

[stream-producer.py](stream-producer.py) uses
[AWS SDK for Python (Boto3)](https://aws.amazon.com/sdk-for-python/)
to access AWS services.
This library may be configured via environment variables  or `~/.aws/config` file.

Example environment variables for configuration:

- **[AWS_ACCESS_KEY_ID](https://github.com/Senzing/knowledge-base/blob/main/lists/environment-variables.md#aws_access_key_id)**
- **[AWS_SECRET_ACCESS_KEY](https://github.com/Senzing/knowledge-base/blob/main/lists/environment-variables.md#aws_secret_access_key)**
- **[AWS_DEFAULT_REGION](https://github.com/Senzing/knowledge-base/blob/main/lists/environment-variables.md#aws_default_region)**

## References

1. Boto3 [Configuration](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html)
1. Boto3 [Credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)
1. [Development](docs/development.md)
1. [Errors](docs/errors.md)
1. [Examples](docs/examples.md)
1. Related artifacts:
    1. [DockerHub](https://hub.docker.com/r/senzing/stream-producer)
