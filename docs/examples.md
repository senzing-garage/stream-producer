# stream-producer examples

## Examples

### Examples of CLI

The following examples require initialization described in
[Demonstrate using Command Line Interface](../README.md#demonstrate-using-command-line-interface).

#### Upload file to RabbitMQ

This example shows how to load a file of JSONlines onto a RabbitMQ queue using the `json-to-rabbitmq` subcommand.

1. `--help` will show all options for the subcommand.
   Example:

    ```console
    ~/stream-producer.py json-to-rabbitmq --help

    ```

1. :pencil2: Identify the file of JSON records on the local system to push to the RabbitMQ queue.
   Example:

    ```console
    export SENZING_INPUT_URL=/path/to/my/records.json

    ```

   :pencil2: or identify a URL.
   Example:

    ```console
    export SENZING_INPUT_URL=https://s3.amazonaws.com/public-read-access/TestDataSets/loadtest-dataset-1M.json

    ```

1. :pencil2: Identify RabbitMQ connection information.
   Example:

    ```console
    export SENZING_RABBITMQ_HOST=localhost
    export SENZING_RABBITMQ_QUEUE=senzing-rabbitmq-queue
    export SENZING_RABBITMQ_USERNAME=user
    export SENZING_RABBITMQ_PASSWORD=bitnami

    ```

1. :thinking: **Optional:** If limiting the number of records is desired, identify the maximum number of records to send.
   To load all records in the file, set the value to "0".
   For more information, see
   [SENZING_RECORD_MAX](https://github.com/Senzing/knowledge-base/blob/main/lists/environment-variables.md#senzing_record_max)
   Example:

    ```console
    export SENZING_RECORD_MAX=5000

    ```

1. Run `stream-producer.py`.
   Example:

    ```console
    ~/stream-producer.py json-to-rabbitmq \
        --input-url ${SENZING_INPUT_URL} \
        --rabbitmq-host ${SENZING_RABBITMQ_HOST} \
        --rabbitmq-password ${SENZING_RABBITMQ_PASSWORD} \
        --rabbitmq-queue ${SENZING_RABBITMQ_QUEUE} \
        --rabbitmq-username ${SENZING_RABBITMQ_USERNAME} \
        --record-max ${SENZING_RECORD_MAX}

    ```

#### Upload file to AWS SQS

This example shows how to load a file of JSONlines onto an AWS SQS queue using the `json-to-sqs` subcommand.

1. `--help` will show all options for the subcommand.
   Example:

    ```console
    ~/stream-producer.py json-to-sqs --help

    ```

1. :pencil2: For AWS access, set environment variables.
   For more information, see
   [How to set AWS environment variables](https://github.com/Senzing/knowledge-base/blob/main/HOWTO/set-aws-environment-variables.md)
   Example:

    ```console
    export AWS_ACCESS_KEY_ID=$(aws configure get default.aws_access_key_id)
    export AWS_SECRET_ACCESS_KEY=$(aws configure get default.aws_secret_access_key)
    export AWS_DEFAULT_REGION=$(aws configure get default.region)

    ```

1. :pencil2: Identify the file of JSON records on the local system to push to the AWS SQS queue.
   Example:

    ```console
    export SENZING_INPUT_URL=/path/to/my/records.json

    ```

   :pencil2: or identify a URL.
   Example:

    ```console
    export SENZING_INPUT_URL=https://s3.amazonaws.com/public-read-access/TestDataSets/loadtest-dataset-1M.json

    ```

1. :pencil2: Identify the AWS SQS queue.
   Example:

    ```console
    export SENZING_SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/000000000000/queue-name

    ```

1. :thinking: **Optional:** If limiting the number of records is desired, identify the maximum number of records to send.
   To load all records in the file, set the value to "0".
   For more information, see
   [SENZING_RECORD_MAX](https://github.com/Senzing/knowledge-base/blob/main/lists/environment-variables.md#senzing_record_max)
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
[Demonstrate using Docker](../README.md#demonstrate-using-docker).

1. Example docker and docker-compose invocations can be seen in
   [Tests](tests/README.md#test-docker)
1. There is a [tutorial](https://github.com/Senzing/docker-compose-demo/tree/main/docs/docker-compose-sqs-postgresql-advanced) showing AWS SQS usage.

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
