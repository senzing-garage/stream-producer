# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
[markdownlint](https://dlaa.me/markdownlint/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

-

## [1.8.11] - 2024-06-24

### Changed in 1.8.11

- In `Dockerfile`, updated FROM instruction to `debian:11.9-slim@sha256:acc5810124f0929ab44fc7913c0ad936b074cbd3eadf094ac120190862ba36c4`
- In `requirements.txt`, updated:
  - s3fs==2024.6.0

## [1.8.10] - 2024-05-22

### Changed in 1.8.10

- In `Dockerfile`, updated FROM instruction to `debian:11.9-slim@sha256:0e75382930ceb533e2f438071307708e79dc86d9b8e433cc6dd1a96872f2651d`
- In `requirements.txt`, updated:
  - azure-servicebus==7.12.2
  - boto3
  - confluent-kafka==2.4.0
  - fastavro==1.9.4
  - fastparquet==2024.2.0
  - pandas==2.2.2
  - pyarrow==16.1.0
  - s3fs==2024.5.0

## [1.8.9] - 2023-11-14

### Changed in 1.8.9

- In `Dockerfile`, updated FROM instruction to `debian:11.8-slim@sha256:19664a5752dddba7f59bb460410a0e1887af346e21877fa7cec78bfd3cb77da5`
- In `requirements.txt`, updated:
  - azure-servicebus==7.11.4
  - boto3==1.28.85
  - confluent-kafka==2.3.0
  - fastavro==1.9.0
  - fastparquet==2023.10.1
  - pandas==2.1.3
  - pyarrow==14.0.1
  - websockets==12.0

## [1.8.8] - 2023-09-29

### Changed in 1.8.8

- In `Dockerfile`, updated FROM instruction to `debian:11.7-slim@sha256:c618be84fc82aa8ba203abbb07218410b0f5b3c7cb6b4e7248fda7785d4f9946`
- In `requirements.txt`, updated:
  - azure-servicebus==7.11.2
  - boto3==1.28.56
  - confluent-kafka==2.2.0
  - fastavro==1.8.3
  - fastparquet==2023.8.0
  - pandas==2.1.1
  - pyarrow==13.0.0

## [1.8.7] - 2023-06-15

### Changed in 1.8.7

- In `Dockerfile`, updated FROM instruction to `debian:11.7-slim@sha256:924df86f8aad741a0134b2de7d8e70c5c6863f839caadef62609c1be1340daf5`
- In `requirements.txt`, updated:
  - azure-servicebus==7.11.0
  - boto3==1.26.153
  - pandas==2.0.2
  - pyarrow==12.0.1

## [1.8.6] - 2023-05-09

### Changed in 1.8.6

- In `Dockerfile`, updated FROM instruction to `BASE_IMAGE=debian:11.7-slim@sha256:f4da3f9b18fc242b739807a0fb3e77747f644f2fb3f67f4403fafce2286b431a`
- In `requirements.txt`, updated:
  - azure-servicebus==7.10.0
  - boto3==1.26.130
  - confluent-kafka==2.1.1
  - fastavro==1.7.4
  - fastparquet==2023.4.0
  - pandas==2.0.1
  - pika==1.3.2
  - pyarrow==12.0.0
  - websockets==11.0.3

## [1.8.5] - 2023-04-03

### Changed in 1.8.5

- In `Dockerfile`, updated FROM instruction to `BASE_IMAGE=debian:11.6-slim@sha256:7acda01e55b086181a6fa596941503648e423091ca563258e2c1657d140355b1`
- In `requirements.txt`, updated:
  - azure-servicebus==7.8.3
  - boto3==1.26.104
  - confluent-kafka==2.0.2
  - fastavro==1.7.3
  - fastparquet==2023.2.0
  - pandas==2.0.0
  - pyarrow==11.0.0
  - websockets==11.0

## [1.8.4] - 2023-01-12

### Changed in 1.8.4

- In `Dockerfile`, updated FROM instruction to `debian:11.6-slim@sha256:98d3b4b0cee264301eb1354e0b549323af2d0633e1c43375d0b25c01826b6790`
- In `requirements.txt`, updated:
  - boto3==1.26.48
  - fastparquet==2022.12.0
  - pandas==1.5.2
  - pyarrow==10.0.1

## [1.8.3] - 2022-10-27

### Changed in 1.8.3

- In `Dockerfile`, updated FROM instruction to `debian:11.5-slim@sha256:e8ad0bc7d0ee6afd46e904780942033ab83b42b446b58efa88d31ecf3adf4678`
- In `requirements.txt`, updated:
  - boto3==1.25.4
  - fastavro==1.7.0
  - pandas==1.5.1
  - pika==1.3.1
  - pyarrow==10.0.0
  - websockets==10.4

## [1.8.2] - 2022-10-18

### Changed in 1.8.2

- Removed support for `SENZING_DEFAULT_ENTITY_TYPE`
- Single messages are sent as JSON Objects, not JSON lists

## [1.8.1] - 2022-09-28

### Changed in 1.8.1

- In `Dockerfile`, updated FROM instruction to `debian:11.5-slim@sha256:5cf1d98cd0805951484f33b34c1ab25aac7007bb41c8b9901d97e4be3cf3ab04`
- In `requirements.txt`, updated:
  - boto3==1.24.81
  - pandas==1.5.0

## [1.8.0] - 2022-09-12

### Added in 1.8.0

- Support for directory of `.json*` files

## [1.7.3] - 2022-07-29

### Changed in 1.7.3

- Changed from `SENZING_AZURE_CONNECTION_STRING` to `SENZING_AZURE_QUEUE_CONNECTION_STRING` for clarity

## [1.7.2] - 2022-06-08

### Changed in 1.7.2

- Upgrade `Dockerfile` to `FROM debian:11.3-slim@sha256:06a93cbdd49a265795ef7b24fe374fee670148a7973190fb798e43b3cf7c5d0f`

## [1.7.1] - 2022-05-05

### Fixed in 1.7.1

- JSON default wasn't a string.

## [1.7.0] - 2022-04-27

### Changed in 1.7.0

- Added support for Stream loader directives
  - `SENZING_STREAM_LOADER_DIRECTIVE_NAME`
  - `SENZING_STREAM_LOADER_DIRECTIVE_ACTION`

## [1.6.6] - 2022-01-31

### Changed in 1.6.6

- Added support for Kafka configuration (`SENZING_KAFKA_CONFIGURATION`)

## [1.6.5] - 2022-01-28

### Changed in 1.6.5

- Updated to Debian 11.2

## [1.6.4] - 2021-12-23

### Changed in 1.6.4

- Fixed [issue 95](https://github.com/Senzing/stream-producer/issues/95) which handles records that may have been previously dropped.

## [1.6.3] - 2021-11-29

### Changed in 1.6.3

- Fixed [issue 91](https://github.com/Senzing/stream-producer/issues/91) to properly log records that exceed the max size of a queue message.

## [1.6.2] - 2021-10-11

### Changed in 1.6.2

- Updated Debian version 10.10

## [1.6.1] - 2021-09-09

### Added in 1.6.1

- Added subcommands for Azure Queue:
  - Updated Makefile to use Debian 10.10 as the base image

## [1.6.0] - 2021-09-08

### Added in 1.6.0

- Added subcommands for Azure Queue:
  - `avro-to-azure-queue`
  - `csv-to-azure-queue`
  - `gzipped-json-to-azure-queue`
  - `json-to-azure-queue`
  - `parquet-to-azure-queue`

## [1.5.1] - 2021-07-15

### Added in 1.5.1

- Updated Debian version to 10.10

## [1.5.0] - 2021-07-13

### Added in 1.5.0

- Support `s3://` protocol
- updated debian version to 10.9

## [1.4.2] - 2021-07-07

### Added in 1.4.2

- Added a max message size to batching for SQS, RabbitMQ, and Kafka.

## [1.4.1] - 2021-06-23

### Added in 1.4.1

- RabbitMQ virtual host is now a settable parameter.
- Removed support for adding records to a queue from a websocket. Loading records via websocket has been moved to the Senzing API server.
- Stream-producer no longer hangs if it cannot connect to the messaging server when first starting

## [1.4.0] - 2021-03-12

### Added in 1.4.0

- Support for `SENZING_DEFAULT_DATA_SOURCE` and `SENZING_DEFAULT_ENTITY_TYPE`
- Support `file://` protocol

## [1.3.3] - 2021-02-18

### Added in 1.3.3

- Added `endpoint_url` in AWS SQS configuration.

## [1.3.2] - 2021-02-08

### Added in 1.3.2

- Implemented reading csv files in chunks to reduce memory usage when loading large files. Use SENZING_CSV_ROWS_IN_CHUNK (default 10000) to set the number of rows per chunk.
- Programmable csv delimiter. Use SENZING_CSV_DELIMITER (default is ',')
- Fixed [issue #49](https://github.com/Senzing/stream-producer/issues/49) to handle CSV input files with empty values.

## [1.3.1] - 2021-01-20

### Added in 1.3.1

- Added support for websocket: `websocket-to-kafka`, `websocket-to-rabbitmq`, `websocket-to-sqs`,`websocket-to-sqs-batch`, `websocket-to-stdout`

## [1.3.0] - 2021-01-19

### Added in 1.3.0

- Microbatching for RabbitMQ, Kafka, and SQS. The batch of records is formatted as a json array
  - SENZING_RECORDS_PER_MESSAGE is the number of records to include in a single message.

## [1.2.3] - 2020-10-09

### Added in 1.2.3

- Support for Governor
- Support for environment variables:
  - `SENZING_RABBITMQ_ROUTING_KEY`
  - `SENZING_RABBITMQ_USE_EXISTING_ENTITIES`
  - `SENZING_RECORD_IDENTIFIER`
  - `SENZING_RECORD_SIZE_MAX`

## [1.2.2] - 2020-07-30

### Added in 1.2.2

- Added support for gzip: `gzipped-json-to-kafka`, `gzipped-json-to-rabbitmq`, `gzipped-json-to-sqs`, `gzipped-json-to-sqs-batch`, `gzipped-json-to-stdout`

## [1.2.1] - 2020-07-28

### Added in 1.2.1

- Monitoring metrics: input_counter_rate_interval, input_counter_rate_total, output_counter_rate_interval, output_counter_rate_total
- Exit metric: rate

## [1.2.0] - 2020-07-24

### Added in 1.2.0

- Subcommands: avro-to-sqs-batch, csv-to-sqs-batch, json-to-sqs-batch, and parquet-to-sqs-batch

## [1.1.1] - 2020-06-23

### Fixed in 1.1.1

- Bad variable

## [1.1.0] - 2020-06-19

### Added to 1.1.0

- Support for AWS SQS queue.

## [1.0.0] - 2020-06-18

### Added to 1.0.0

- Initial functionality
  - File formats: JSON, CSV, Avro, Parquet
  - Queues: RabbitMQ, Kafka, STDOUT
