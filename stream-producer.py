#! /usr/bin/env python3

# -----------------------------------------------------------------------------
# stream-producer.py Create a stream.
# - Uses a "pipes and filters" design pattern
# -----------------------------------------------------------------------------

from glob import glob
import argparse
import collections
import csv
import fastavro
import json
import linecache
import logging
import os
import pandas
import queue
import signal
import threading
import multiprocessing
import sys
import time

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

__all__ = []
__version__ = "1.0.0"  # See https://www.python.org/dev/peps/pep-0396/
__date__ = '2020-04-07'
__updated__ = '2020-04-08'

SENZING_PRODUCT_ID = "5014"  # See https://github.com/Senzing/knowledge-base/blob/master/lists/senzing-product-ids.md
log_format = '%(asctime)s %(message)s'

# Working with bytes.

KILOBYTES = 1024
MEGABYTES = 1024 * KILOBYTES
GIGABYTES = 1024 * MEGABYTES

# The "configuration_locator" describes where configuration variables are in:
# 1) Command line options, 2) Environment variables, 3) Configuration files, 4) Default values

configuration_locator = {
    "avro_schema_url": {
        "default": None,
        "env": "SENZING_AVRO_SCHEMA_URL",
        "cli": "avro-schema-url"
    },
    "debug": {
        "default": False,
        "env": "SENZING_DEBUG",
        "cli": "debug"
    },
    "delay_in_seconds": {
        "default": 0,
        "env": "SENZING_DELAY_IN_SECONDS",
        "cli": "delay-in-seconds"
    },
    "input_url": {
        "default": "https://s3.amazonaws.com/public-read-access/TestDataSets/loadtest-dataset-1M.json",
        "env": "SENZING_INPUT_URL",
        "cli": "input-url",
    },
    "monitoring_period_in_seconds": {
        "default": 60 * 10,
        "env": "SENZING_MONITORING_PERIOD_IN_SECONDS",
        "cli": "monitoring-period-in-seconds",
    },
    "password": {
        "default": None,
        "env": "SENZING_PASSWORD",
        "cli": "password"
    },
    "read_queue_maxsize": {
        "default": 50,
        "env": "SENZING_READ_QUEUE_MAXSIZE",
        "cli": "read-queue-maxsize"
    },
    "senzing_dir": {
        "default": "/opt/senzing",
        "env": "SENZING_DIR",
        "cli": "senzing-dir"
    },
    "sleep_time_in_seconds": {
        "default": 0,
        "env": "SENZING_SLEEP_TIME_IN_SECONDS",
        "cli": "sleep-time-in-seconds"
    },
    "subcommand": {
        "default": None,
        "env": "SENZING_SUBCOMMAND",
    },
    "threads_per_write_process": {
        "default": 4,
        "env": "SENZING_THREADS_PER_WRITE_PROCESS",
        "cli": "threads-per-write-process"
    }
}

# Enumerate keys in 'configuration_locator' that should not be printed to the log.

keys_to_redact = [
    "password",
]

# -----------------------------------------------------------------------------
# Define argument parser
# -----------------------------------------------------------------------------


def get_parser():
    ''' Parse commandline arguments. '''

    subcommands = {
        'avro-to-stdout': {
            "help": 'Read Avro file and print to STDOUT.',
            "arguments": {
                "--input-url": {
                    "dest": "input_url",
                    "metavar": "SENZING_INPUT_URL",
                    "help": "File/URL of input file. Default: None"
                },
            },
        },
        'csv-to-stdout': {
            "help": 'Read CSV file and print to STDOUT.',
            "arguments": {
                "--input-url": {
                    "dest": "input_url",
                    "metavar": "SENZING_INPUT_URL",
                    "help": "File/URL of input file. Default: None"
                },
            },
        },
        'json-to-stdout': {
            "help": 'Read JSON file and print to STDOUT.',
            "arguments": {
                "--input-url": {
                    "dest": "input_url",
                    "metavar": "SENZING_INPUT_URL",
                    "help": "File/URL of input file. Default: None"
                },
            },
        },
        'parquet-to-stdout': {
            "help": 'Read Parquet file and print to STDOUT.',
            "arguments": {
                "--input-url": {
                    "dest": "input_url",
                    "metavar": "SENZING_INPUT_URL",
                    "help": "File/URL of input file. Default: None"
                },
            },
        },
        'sleep': {
            "help": 'Do nothing but sleep. For Docker testing.',
            "arguments": {
                "--sleep-time-in-seconds": {
                    "dest": "sleep_time_in_seconds",
                    "metavar": "SENZING_SLEEP_TIME_IN_SECONDS",
                    "help": "Sleep time in seconds. DEFAULT: 0 (infinite)"
                },
            },
        },
        'version': {
            "help": 'Print version of program.',
        },
        'docker-acceptance-test': {
            "help": 'For Docker acceptance testing.',
        },
    }

    parser = argparse.ArgumentParser(prog="template-python.py", description="Example python skeleton. For more information, see https://github.com/Senzing/template-python")
    subparsers = parser.add_subparsers(dest='subcommand', help='Subcommands (SENZING_SUBCOMMAND):')

    for subcommand_key, subcommand_values in subcommands.items():
        subcommand_help = subcommand_values.get('help', "")
        subcommand_arguments = subcommand_values.get('arguments', {})
        subparser = subparsers.add_parser(subcommand_key, help=subcommand_help)
        for argument_key, argument_values in subcommand_arguments.items():
            subparser.add_argument(argument_key, **argument_values)

    return parser

# -----------------------------------------------------------------------------
# Message handling
# -----------------------------------------------------------------------------

# 1xx Informational (i.e. logging.info())
# 3xx Warning (i.e. logging.warning())
# 5xx User configuration issues (either logging.warning() or logging.err() for Client errors)
# 7xx Internal error (i.e. logging.error for Server errors)
# 9xx Debugging (i.e. logging.debug())


MESSAGE_INFO = 100
MESSAGE_WARN = 300
MESSAGE_ERROR = 700
MESSAGE_DEBUG = 900

message_dictionary = {
    "100": "senzing-" + SENZING_PRODUCT_ID + "{0:04d}I",
    "127": "Monitor: {0}",
    "129": "{0} is running.",
    "130": "{0} has exited.",
    "181": "Monitoring halted. No active workers.",
    "292": "Configuration change detected.  Old: {0} New: {1}",
    "293": "For information on warnings and errors, see https://github.com/Senzing/stream-loader#errors",
    "294": "Version: {0}  Updated: {1}",
    "295": "Sleeping infinitely.",
    "296": "Sleeping {0} seconds.",
    "297": "Enter {0}",
    "298": "Exit {0}",
    "299": "{0}",
    "300": "senzing-" + SENZING_PRODUCT_ID + "{0:04d}W",
    "499": "{0}",
    "500": "senzing-" + SENZING_PRODUCT_ID + "{0:04d}E",
    "695": "Unknown database scheme '{0}' in database url '{1}'",
    "696": "Bad SENZING_SUBCOMMAND: {0}.",
    "697": "No processing done.",
    "698": "Program terminated with error.",
    "699": "{0}",
    "700": "senzing-" + SENZING_PRODUCT_ID + "{0:04d}E",
    "721": "Running low on workers.  May need to restart",
    "885": "License has expired.",
    "886": "G2Engine.addRecord() bad return code: {0}; JSON: {1}",
    "888": "G2Engine.addRecord() G2ModuleNotInitialized: {0}; JSON: {1}",
    "889": "G2Engine.addRecord() G2ModuleGenericException: {0}; JSON: {1}",
    "890": "G2Engine.addRecord() Exception: {0}; JSON: {1}",
    "891": "Original and new database URLs do not match. Original URL: {0}; Reconstructed URL: {1}",
    "892": "Could not initialize G2Product with '{0}'. Error: {1}",
    "893": "Could not initialize G2Hasher with '{0}'. Error: {1}",
    "894": "Could not initialize G2Diagnostic with '{0}'. Error: {1}",
    "895": "Could not initialize G2Audit with '{0}'. Error: {1}",
    "896": "Could not initialize G2ConfigMgr with '{0}'. Error: {1}",
    "897": "Could not initialize G2Config with '{0}'. Error: {1}",
    "898": "Could not initialize G2Engine with '{0}'. Error: {1}",
    "899": "{0}",
    "900": "senzing-" + SENZING_PRODUCT_ID + "{0:04d}D",
    "902": "Thread: {0} Added message to internal queue: {1}",
    "995": "Thread: {0} Using Class: {1}",
    "996": "Thread: {0} Using Mixin: {1}",
    "997": "Thread: {0} Using Thread: {1}",
    "998": "Debugging enabled.",
    "999": "{0}",
}


def message(index, *args):
    index_string = str(index)
    template = message_dictionary.get(index_string, "No message for index {0}.".format(index_string))
    return template.format(*args)


def message_generic(generic_index, index, *args):
    index_string = str(index)
    return "{0} {1}".format(message(generic_index, index), message(index, *args))


def message_info(index, *args):
    return message_generic(MESSAGE_INFO, index, *args)


def message_warning(index, *args):
    return message_generic(MESSAGE_WARN, index, *args)


def message_error(index, *args):
    return message_generic(MESSAGE_ERROR, index, *args)


def message_debug(index, *args):
    return message_generic(MESSAGE_DEBUG, index, *args)


def get_exception():
    ''' Get details about an exception. '''
    exception_type, exception_object, traceback = sys.exc_info()
    frame = traceback.tb_frame
    line_number = traceback.tb_lineno
    filename = frame.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, line_number, frame.f_globals)
    return {
        "filename": filename,
        "line_number": line_number,
        "line": line.strip(),
        "exception": exception_object,
        "type": exception_type,
        "traceback": traceback,
    }

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------


def get_configuration(args):
    ''' Order of precedence: CLI, OS environment variables, INI file, default. '''
    result = {}

    # Copy default values into configuration dictionary.

    for key, value in list(configuration_locator.items()):
        result[key] = value.get('default', None)

    # "Prime the pump" with command line args. This will be done again as the last step.

    for key, value in list(args.__dict__.items()):
        new_key = key.format(subcommand.replace('-', '_'))
        if value:
            result[new_key] = value

    # Copy OS environment variables into configuration dictionary.

    for key, value in list(configuration_locator.items()):
        os_env_var = value.get('env', None)
        if os_env_var:
            os_env_value = os.getenv(os_env_var, None)
            if os_env_value:
                result[key] = os_env_value

    # Copy 'args' into configuration dictionary.

    for key, value in list(args.__dict__.items()):
        new_key = key.format(subcommand.replace('-', '_'))
        if value:
            result[new_key] = value

    # Special case: subcommand from command-line

    if args.subcommand:
        result['subcommand'] = args.subcommand

    # Special case: Change boolean strings to booleans.

    booleans = ['debug']
    for boolean in booleans:
        boolean_value = result.get(boolean)
        if isinstance(boolean_value, str):
            boolean_value_lower_case = boolean_value.lower()
            if boolean_value_lower_case in ['true', '1', 't', 'y', 'yes']:
                result[boolean] = True
            else:
                result[boolean] = False

    # Special case: Change integer strings to integers.

    integers = [
        'sleep_time_in_seconds'
    ]
    for integer in integers:
        integer_string = result.get(integer)
        result[integer] = int(integer_string)

    # Initialize counters.

    counters = [
        'input_counter',
        'output_counter',
    ]
    for counter in counters:
        result[counter] = 0

    return result


def validate_configuration(config):
    ''' Check aggregate configuration from commandline options, environment variables, config files, and defaults. '''

    user_warning_messages = []
    user_error_messages = []

    # Perform subcommand specific checking.

    subcommand = config.get('subcommand')

    if subcommand in ['task1']:

        if not config.get('senzing_dir'):
            user_error_messages.append(message_error(414))

    # Log warning messages.

    for user_warning_message in user_warning_messages:
        logging.warning(user_warning_message)

    # Log error messages.

    for user_error_message in user_error_messages:
        logging.error(user_error_message)

    # Log where to go for help.

    if len(user_warning_messages) > 0 or len(user_error_messages) > 0:
        logging.info(message_info(293))

    # If there are error messages, exit.

    if len(user_error_messages) > 0:
        exit_error(697)


def redact_configuration(config):
    ''' Return a shallow copy of config with certain keys removed. '''
    result = config.copy()
    for key in keys_to_redact:
        try:
            result.pop(key)
        except:
            pass
    return result

# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------


def bootstrap_signal_handler(signal, frame):
    sys.exit(0)


def create_signal_handler_function(args):
    ''' Tricky code.  Uses currying technique. Create a function for signal handling.
        that knows about "args".
    '''

    def result_function(signal_number, frame):
        logging.info(message_info(298, args))
        sys.exit(0)

    return result_function


def delay(config):
    delay_in_seconds = config.get('delay_in_seconds')
    if delay_in_seconds > 0:
        logging.info(message_info(120, delay_in_seconds))
        time.sleep(delay_in_seconds)


def entry_template(config):
    ''' Format of entry message. '''
    debug = config.get("debug", False)
    config['start_time'] = time.time()
    if debug:
        final_config = config
    else:
        final_config = redact_configuration(config)
    config_json = json.dumps(final_config, sort_keys=True)
    return message_info(297, config_json)


def exit_template(config):
    ''' Format of exit message. '''
    debug = config.get("debug", False)
    stop_time = time.time()
    config['stop_time'] = stop_time
    config['elapsed_time'] = stop_time - config.get('start_time', stop_time)
    if debug:
        final_config = config
    else:
        final_config = redact_configuration(config)
    config_json = json.dumps(final_config, sort_keys=True)
    return message_info(298, config_json)


def exit_error(index, *args):
    ''' Log error message and exit program. '''
    logging.error(message_error(index, *args))
    logging.error(message_error(698))
    sys.exit(1)


def exit_silently():
    ''' Exit program. '''
    sys.exit(0)

# -----------------------------------------------------------------------------
# Class: MonitorThread
# -----------------------------------------------------------------------------


class MonitorThread(threading.Thread):
    '''
    Periodically log operational metrics.
    '''

    def __init__(self, config=None, workers=None):
        threading.Thread.__init__(self)
        self.config = config
        self.workers = workers

    def run(self):
        '''Periodically monitor what is happening.'''

        # Show that thread is starting in the log.

        logging.info(message_info(129, threading.current_thread().name))

        # Initialize variables.

        last = {
            "input_counter": 0,
            "output_counter": 0,
        }

        # Define monitoring report interval.

        sleep_time_in_seconds = self.config.get('monitoring_period_in_seconds')

        # Sleep-monitor loop.

        active_workers = len(self.workers)
        for worker in self.workers:
            if not worker.is_alive():
                active_workers -= 1

        while active_workers > 0:

            # Tricky code.  Essentially this is an interruptible
            # time.sleep(sleep_time_in_seconds)

            interval_in_seconds = 5
            active_workers = len(self.workers)
            for step in range(1, sleep_time_in_seconds, interval_in_seconds):
                time.sleep(interval_in_seconds)
                active_workers = len(self.workers)
                for worker in self.workers:
                    if not worker.is_alive():
                        active_workers -= 1
                if active_workers == 0:
                    break;

            # Determine if we're running out of workers.

            if active_workers and (active_workers / float(len(self.workers))) < 0.5:
                logging.warning(message_warning(721))

            # Calculate times.

            now = time.time()
            uptime = now - self.config.get('start_time', now)

            # Construct and log monitor statistics.

            stats = {
                "uptime": int(uptime),
                "workers_total": len(self.workers),
                "workers_active": active_workers,
            }

            # Tricky code.  Avoid modifying dictionary in the loop.
            # i.e. "for key, value in last.items():" would loop infinitely
            # because of "last[key] = total".

            keys = last.keys()
            for key in keys:
                value = last.get(key)
                total = self.config.get(key)
                interval = total - value
                stats["{0}_total".format(key)] = total
                stats["{0}_interval".format(key)] = interval
                last[key] = total

            logging.info(message_info(127, json.dumps(stats, sort_keys=True)))
        logging.info(message_info(181))

# =============================================================================
# Mixins: Read*
#   Methods:
#   - read() - a Generator that produces one message per iteration
#   Classes:
#   - ReadFileCsvMixin - Read a local CSV file
#   - ReadFileMixin - Read from a local file
#   - ReadFileParquetMixin - Read a parquet file
#   - ReadQueueMixin - Read from an internal queue
# =============================================================================

# -----------------------------------------------------------------------------
# Class: ReadFileAvroMixin
# -----------------------------------------------------------------------------


class ReadFileAvroMixin():

    def __init__(self, input_url=None, *args, **kwargs):
        logging.debug(message_debug(996, threading.current_thread().name, "ReadFileAvroMixin"))
        self.input_url = input_url

    def read(self):
        with open(self.input_url, 'rb') as input_file:
            avro_reader = fastavro.reader(input_file)
            for record in avro_reader:
                yield record

# -----------------------------------------------------------------------------
# Class: ReadFileCsvMixin
# -----------------------------------------------------------------------------


class ReadFileCsvMixin():

    def __init__(self, input_url=None, *args, **kwargs):
        logging.debug(message_debug(996, threading.current_thread().name, "ReadFileCsvMixin"))
        self.input_url = input_url

    def read(self):
        with open(self.input_url, 'r') as input_file:
            csv_reader = csv.DictReader(input_file, skipinitialspace=True)
            for dictionary in csv_reader:
                result = dict(dictionary)
                assert type(result) == dict
                yield result

# -----------------------------------------------------------------------------
# Class: ReadFileMixin
# -----------------------------------------------------------------------------


class ReadFileMixin():

    def __init__(self, input_url=None, *args, **kwargs):
        logging.debug(message_debug(996, threading.current_thread().name, "ReadFileMixin"))
        self.input_url = input_url

    def read(self):
        with open(self.input_url, 'r') as input_file:
            for line in input_file:
                assert isinstance(line, str)
                yield line

# -----------------------------------------------------------------------------
# Class: ReadFileParquetMixin
# -----------------------------------------------------------------------------


class ReadFileParquetMixin():

    def __init__(self, input_url=None, *args, **kwargs):
        logging.debug(message_debug(996, threading.current_thread().name, "ReadFileParquetMixin"))
        self.input_url = input_url

    def read(self):
        data_frame = pandas.read_parquet(self.input_url)
        for row in data_frame.to_dict(orient="records"):
            assert type(row) == dict
            yield row

# -----------------------------------------------------------------------------
# Class: ReadQueueMixin
# -----------------------------------------------------------------------------


class ReadQueueMixin():

    def __init__(self, read_queue=None, *args, **kwargs):
        logging.debug(message_debug(996, threading.current_thread().name, "ReadQueueMixin"))
        self.read_queue = read_queue

    def read(self):
        while True:
            message = self.read_queue.get()
            yield message

# -----------------------------------------------------------------------------
# Class: ReadQueueTransientMixin
# -----------------------------------------------------------------------------


class ReadQueueTransientMixin():

    def __init__(self, read_queue=None, *args, **kwargs):
        logging.debug(message_debug(996, threading.current_thread().name, "ReadQueueTransientMixin"))
        self.read_queue = read_queue

    def read(self):
        block = True
        timeout = 10
        while not self.read_queue.empty():
            try:
                message = self.read_queue.get(block, timeout)
            except queue.Empty:
                continue
            except ValueError:
                continue
            yield message

# =============================================================================
# Mixins: Evaluate*
#   Methods:
#   - evaluate(message) -> transformed-message
#   Classes:
#   - EvaluateDictToJsonMixin - Transform Python dictionary to JSON string
#   - EvaluateJsonToDictMixin - Transform JSON string to Python dictionary
#   - EvaluateNullObjectMixin - Simply pass on the message
#   - EvaluateMakeSerializeableDictMixin - Make dictionary serializeable
# =============================================================================

# -----------------------------------------------------------------------------
# Class: EvaluateDictToJsonMixin
# -----------------------------------------------------------------------------


class EvaluateDictToJsonMixin():

    def __init__(self, input_url=None, *args, **kwargs):
        logging.debug(message_debug(996, threading.current_thread().name, "EvaluateDictToJsonMixin"))

    def evaluate(self, message):
        return json.dumps(message)

# -----------------------------------------------------------------------------
# Class: EvaluateJsonToDictMixin
# -----------------------------------------------------------------------------


class EvaluateJsonToDictMixin():

    def __init__(self, input_url=None, *args, **kwargs):
        logging.debug(message_debug(996, threading.current_thread().name, "EvaluateJsonToDictMixin"))

    def evaluate(self, message):
        return json.loads(message)

# -----------------------------------------------------------------------------
# Class: EvaluateNullObjectMixin
# -----------------------------------------------------------------------------


class EvaluateNullObjectMixin():

    def __init__(self, input_url=None, *args, **kwargs):
        logging.debug(message_debug(996, threading.current_thread().name, "EvaluateDictToJsonMixin"))

    def evaluate(self, message):
        return message

# -----------------------------------------------------------------------------
# Class: EvaluateMakeSerializeableDictMixin
# -----------------------------------------------------------------------------


class EvaluateMakeSerializeableDictMixin():

    def __init__(self, input_url=None, *args, **kwargs):
        logging.debug(message_debug(996, threading.current_thread().name, "EvaluateMakeSerializeableDictMixin"))

    def evaluate(self, message):
        new_message = {}
        for key, value in message.items():
            new_message[key] = str(value)
            try:
                if value.isnumeric():
                    new_message[key] = value
            except:
                pass
        return new_message

# =============================================================================
# Mixins: Print*
#   Methods:
#   - print()
#   Classes:
#   - PrintQueueMixin - Send to internal queue
#   - PrintStdoutMixin - Send to STDOUT
# =============================================================================

# -----------------------------------------------------------------------------
# Class: PrintQueueMixin
# -----------------------------------------------------------------------------


class PrintQueueMixin():

    def __init__(self, print_queue=None, *args, **kwargs):
        logging.debug(message_debug(996, threading.current_thread().name, "PrintQueueMixin"))
        self.print_queue = print_queue

    def print(self, message):
        assert isinstance(message, dict)
        self.print_queue.put(message)

# -----------------------------------------------------------------------------
# Class: PrintStdoutMixin
# -----------------------------------------------------------------------------


class PrintStdoutMixin():

    def __init__(self, *args, **kwargs):
        logging.debug(message_debug(996, threading.current_thread().name, "PrintStdoutMixin"))

    def print(self, message):
        assert type(message) == str
        print(message)

# =============================================================================
# Threads: *Thread
#   Methods:
#   - run
#   Classes:
#   - ReadEvaluatePrintLoopThread - Simple REPL
# =============================================================================

# -----------------------------------------------------------------------------
# Class: ReadEvaluatePrintLoopThread
# -----------------------------------------------------------------------------


class ReadEvaluatePrintLoopThread(threading.Thread):

    def __init__(self, config=None, counter_name=None, *args, **kwargs):
        threading.Thread.__init__(self)
        logging.debug(message_debug(997, threading.current_thread().name, "ReadEvaluatePrintLoopThread"))
        self.config = config
        self.counter_name = counter_name

    def run(self):
        '''Read-Evaluate-Print Loop (REPL).'''

        # Show that thread is starting in the log.

        logging.info(message_info(129, threading.current_thread().name))

        # Read-Evaluate-Print Loop  (REPL)

        for message in self.read():
            logging.debug(message_debug(902, threading.current_thread().name, self.counter_name, message))
            self.config[self.counter_name] += 1
            self.print(self.evaluate(message))

        # Log message for thread exiting.

        logging.info(message_info(130, threading.current_thread().name))

# =============================================================================
# Filter* classes created with mixins
# =============================================================================


class FilterFileAvroToDictQueueThread(ReadEvaluatePrintLoopThread, ReadFileAvroMixin, EvaluateNullObjectMixin, PrintQueueMixin):

    def __init__(self, *args, **kwargs):
        logging.debug(message_debug(997, threading.current_thread().name, "FilterFileAvroToDictQueueThread"))
        for base in type(self).__bases__:
            base.__init__(self, *args, **kwargs)


class FilterFileCsvToDictQueueThread(ReadEvaluatePrintLoopThread, ReadFileCsvMixin, EvaluateNullObjectMixin, PrintQueueMixin):

    def __init__(self, *args, **kwargs):
        logging.debug(message_debug(997, threading.current_thread().name, "FilterFileCsvToDictQueueThread"))
        for base in type(self).__bases__:
            base.__init__(self, *args, **kwargs)


class FilterFileJsonToDictQueueThread(ReadEvaluatePrintLoopThread, ReadFileMixin, EvaluateJsonToDictMixin, PrintQueueMixin):

    def __init__(self, *args, **kwargs):
        logging.debug(message_debug(997, threading.current_thread().name, "FilterFileJsonToDictQueueThread"))
        for base in type(self).__bases__:
            base.__init__(self, *args, **kwargs)


class FilterFileParquetToDictQueueThread(ReadEvaluatePrintLoopThread, ReadFileParquetMixin, EvaluateMakeSerializeableDictMixin, PrintQueueMixin):

    def __init__(self, *args, **kwargs):
        logging.debug(message_debug(997, threading.current_thread().name, "FilterFileParquetToDictQueueThread"))
        for base in type(self).__bases__:
            base.__init__(self, *args, **kwargs)


class FilterQueueDictToJsonStdoutThread(ReadEvaluatePrintLoopThread, ReadQueueTransientMixin, EvaluateDictToJsonMixin, PrintStdoutMixin):

    def __init__(self, *args, **kwargs):
        logging.debug(message_debug(997, threading.current_thread().name, "FilterQueueDictToJsonStdoutThread"))
        for base in type(self).__bases__:
            base.__init__(self, *args, **kwargs)

# -----------------------------------------------------------------------------
# *_processor
# -----------------------------------------------------------------------------


def pipeline_read_write(
    args=None,
    options_to_defaults_map={},
    read_thread=None,
    write_thread=None,
    monitor_thread=None,
):

    # Get context from CLI, environment variables, and ini files.

    config = get_configuration(args)
    validate_configuration(config)

    # If configuration values not specified, use defaults.

    for key, value in options_to_defaults_map.items():
        if not config.get(key):
            config[key] = config.get(value)

    # Prolog.

    logging.info(entry_template(config))

    # If requested, delay start.

    delay(config)

    # Pull values from configuration.

    threads_per_write_process = config.get('threads_per_write_process')
    read_queue_maxsize = config.get('read_queue_maxsize')
    input_url = config.get('input_url')

    # Create internal Queue.

    read_queue = multiprocessing.Queue(read_queue_maxsize)

    # Create threads for master process.

    threads = []

    # Add a single thread for reading from source and placing on internal queue.

    if read_thread:
        thread = read_thread(
            config=config,
            counter_name="input_counter",
            input_url=input_url,
            print_queue=read_queue
        )
        thread.name = "Process-0-{0}-0".format(thread.__class__.__name__)
        threads.append(thread)
        thread.start()

    # Let read thread get a head start.

    time.sleep(5)

    # Add a number of threads for reading from source queue writing to "sink".

    if write_thread:
        for i in range(0, threads_per_write_process):
            thread = write_thread(
                config=config,
                counter_name="output_counter",
                read_queue=read_queue,
            )
            thread.name = "Process-0-{0}-{1}".format(thread.__class__.__name__, i)
            threads.append(thread)
            thread.start()

    # Add a monitoring thread.

    adminThreads = []

    if monitor_thread:
        thread = monitor_thread(
            config=config,
            workers=threads,
        )
        thread.name = "Process-0-{0}-0".format(thread.__class__.__name__)
        adminThreads.append(thread)
        thread.start()

    # Collect inactive threads.

    for thread in threads:
        thread.join()
    for thread in adminThreads:
        thread.join()

    # Epilog.

    logging.info(exit_template(config))

# -----------------------------------------------------------------------------
# do_* functions
#   Common function signature: do_XXX(args)
# -----------------------------------------------------------------------------


def do_avro_to_stdout(args):
    ''' Read file of JSON, print to STDOUT. '''

    # Get context variables.

    config = get_configuration(args)
    input_url = config.get("input_url")
    avro_schema_url = config.get("avro_schema_url")
    parsed_file_name = urlparse(input_url)

    # Determine Read thread.

    read_thread = FilterFileAvroToDictQueueThread
    if parsed_file_name.scheme in ['http', 'https']:
        read_thread = None  # TODO:

    # Determine Write thread.

    write_thread = FilterQueueDictToJsonStdoutThread

    # Cascading defaults.

    options_to_defaults_map = {}

    # Run pipeline.

    pipeline_read_write(
        args=args,
        options_to_defaults_map=options_to_defaults_map,
        read_thread=read_thread,
        write_thread=write_thread,
        monitor_thread=MonitorThread
    )


def do_csv_to_stdout(args):
    ''' Read file of JSON, print to STDOUT. '''

    # Get context variables.

    config = get_configuration(args)
    input_url = config.get("input_url")
    parsed_file_name = urlparse(input_url)

    # Determine Read thread.

    read_thread = FilterFileCsvToDictQueueThread
    if parsed_file_name.scheme in ['http', 'https']:
        read_thread = None  # TODO:

    # Determine Write thread.

    write_thread = FilterQueueDictToJsonStdoutThread

    # Cascading defaults.

    options_to_defaults_map = {
        "xxx": "yyy",
    }

    # Run pipeline.

    pipeline_read_write(
        args=args,
        options_to_defaults_map=options_to_defaults_map,
        read_thread=read_thread,
        write_thread=write_thread,
        monitor_thread=MonitorThread
    )


def do_docker_acceptance_test(args):
    ''' For use with Docker acceptance testing. '''

    # Get context from CLI, environment variables, and ini files.

    config = get_configuration(args)

    # Prolog.

    logging.info(entry_template(config))

    # Epilog.

    logging.info(exit_template(config))


def do_json_to_stdout(args):
    ''' Read file of JSON, print to STDOUT. '''

    # Get context variables.

    config = get_configuration(args)
    input_url = config.get("input_url")
    parsed_file_name = urlparse(input_url)

    # Determine Read thread.

    read_thread = FilterFileJsonToDictQueueThread
    if parsed_file_name.scheme in ['http', 'https']:
        read_thread = None  # TODO:

    # Determine Write thread.

    write_thread = FilterQueueDictToJsonStdoutThread

    # Cascading defaults.

    options_to_defaults_map = {
        "xxx": "yyy",
    }

    # Run pipeline.

    pipeline_read_write(
        args=args,
        options_to_defaults_map=options_to_defaults_map,
        read_thread=read_thread,
        write_thread=write_thread,
        monitor_thread=MonitorThread
    )


def do_parquet_to_stdout(args):
    ''' Read file of JSON, print to STDOUT. '''

    # Get context variables.

    config = get_configuration(args)
    input_url = config.get("input_url")
    parsed_file_name = urlparse(input_url)

    # Determine Read thread.

    read_thread = FilterFileParquetToDictQueueThread
    if parsed_file_name.scheme in ['http', 'https']:
        read_thread = None  # TODO:

    # Determine Write thread.

    write_thread = FilterQueueDictToJsonStdoutThread

    # Cascading defaults.

    options_to_defaults_map = {
        "xxx": "yyy",
    }

    # Run pipeline.

    pipeline_read_write(
        args=args,
        options_to_defaults_map=options_to_defaults_map,
        read_thread=read_thread,
        write_thread=write_thread,
        monitor_thread=MonitorThread
    )


def do_sleep(args):
    ''' Sleep.  Used for debugging. '''

    # Get context from CLI, environment variables, and ini files.

    config = get_configuration(args)

    # Prolog.

    logging.info(entry_template(config))

    # Pull values from configuration.

    sleep_time_in_seconds = config.get('sleep_time_in_seconds')

    # Sleep

    if sleep_time_in_seconds > 0:
        logging.info(message_info(296, sleep_time_in_seconds))
        time.sleep(sleep_time_in_seconds)

    else:
        sleep_time_in_seconds = 3600
        while True:
            logging.info(message_info(295))
            time.sleep(sleep_time_in_seconds)

    # Epilog.

    logging.info(exit_template(config))


def do_version(args):
    ''' Log version information. '''

    logging.info(message_info(294, __version__, __updated__))

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


if __name__ == "__main__":

    # Configure logging. See https://docs.python.org/2/library/logging.html#levels

    log_level_map = {
        "notset": logging.NOTSET,
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "fatal": logging.FATAL,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }

    log_level_parameter = os.getenv("SENZING_LOG_LEVEL", "info").lower()
    log_level = log_level_map.get(log_level_parameter, logging.INFO)
    logging.basicConfig(format=log_format, level=log_level)
    logging.debug(message_debug(998))

    # Trap signals temporarily until args are parsed.

    signal.signal(signal.SIGTERM, bootstrap_signal_handler)
    signal.signal(signal.SIGINT, bootstrap_signal_handler)

    # Parse the command line arguments.

    subcommand = os.getenv("SENZING_SUBCOMMAND", None)
    parser = get_parser()
    if len(sys.argv) > 1:
        args = parser.parse_args()
        subcommand = args.subcommand
    elif subcommand:
        args = argparse.Namespace(subcommand=subcommand)
    else:
        parser.print_help()
        if len(os.getenv("SENZING_DOCKER_LAUNCHED", "")):
            subcommand = "sleep"
            args = argparse.Namespace(subcommand=subcommand)
            do_sleep(args)
        exit_silently()

    # Catch interrupts. Tricky code: Uses currying.

    signal_handler = create_signal_handler_function(args)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Transform subcommand from CLI parameter to function name string.

    subcommand_function_name = "do_{0}".format(subcommand.replace('-', '_'))

    # Test to see if function exists in the code.

    if subcommand_function_name not in globals():
        logging.warning(message_warning(696, subcommand))
        parser.print_help()
        exit_silently()

    # Tricky code for calling function based on string.

    globals()[subcommand_function_name](args)
