#!/usr/bin/env python3

# Import error
from features import error
from features import access
from features import config_parse
from features import sys_info
from features import analyse_log
from features import delete_log
from cloud.s3 import uploadS3

# Import standard modules
try:
    import argparse
    import os
    import sys
    import re
except ModuleNotFoundError as err:
    message = f"Cloudmetrics: Error: {err}. \nUse 'pip install' to install module"
    error.WriteToErrorLog(message).log()
    print(message)
    sys.exit(1)

# Create the parser
parser = argparse.ArgumentParser(
    prog="cloudmetrics",
    description="Collect, analyze, and report useful system metrics",
    allow_abbrev=False,
    epilog="Enjoy the program!"
)

# Version
parser.version = 'cloudmetrics: version 1.0'

# Add arguments
parser.add_argument('-c', metavar='Config file', type=str, help="Specify alternative YAML configuration file")
parser.add_argument('-e', '--email', metavar='Email address', type=str, help="Specify an email address to send the report")
parser.add_argument('-f', '--format', metavar='Log format', type=str, choices=["plain_text", "csv", "json"], help="Specify format for log reporting")
parser.add_argument('-t', '--test', action="store_true", help="Test configuration and exit")
parser.add_argument('-T', action="store_true", help="Test configuration file, dump it, and exit")
parser.add_argument('-v', '--version', action="version", help="Print version and exit")

# Execute parse_args
args = parser.parse_args()

# Define YAML configuration file
config_file = args.c if args.c else "cloudmetrics.conf.yml"
if not os.path.isfile(config_file):
    message = f"Cloudmetrics: Error: {config_file} is not a valid file."
    error.WriteToErrorLog(message).log()
    print(message)
    sys.exit(1)

# Parse configuration
parser_class = config_parse.YamlParser(config_file)
parsed_values = parser_class.yaml_to_python()

if args.test or args.T:
    if parsed_values:
        print(f"The configuration file {config_file} syntax is OK.")
        if args.T:
            print(parsed_values)
        sys.exit(0)
    else:
        print(f"The configuration file {config_file} has bad syntax")
        sys.exit(1)

# Load configuration values with defaults
try:
    values = {
        "log_files": parsed_values.get("log_files", []),
        "log_format": args.format or parsed_values.get("log_report_format", "plain_text"),
        "delete_logs": parsed_values.get("delete_logs", False),
        "expire_logs": parsed_values.get("expire_logs", False),
        "notify": parsed_values.get("notify", False),
        "email": args.email or parsed_values.get("email_address", None),
        "web_log": parsed_values.get("web_server", {}).get("logs", None),
        "web_data": parsed_values.get("web_server", {}).get("data", None),
        "timeout": parsed_values.get("timeout", 30),
        "url": parsed_values.get("url", None),
        "cloud": parsed_values.get("cloud", {})
    }

    cloud = values["cloud"]
    if cloud.get("active"):
        region = cloud["config"][0].get("region", "")
        bucket = cloud.get("s3_bucket_name")
        if not bucket:
            message = "Cloudmetrics: Info: S3 bucket name is not provided. Cloud operations are disabled."
            error.WriteToErrorLog(message).log()
            print(message)
            cloud["active"] = False
except KeyError as key_err:
    message = f"Cloudmetrics: Error: Key {key_err} is missing in {config_file}. Exiting..."
    error.WriteToErrorLog(message).log()
    print(message)
    sys.exit(1)

# Validate email
if values["email"] and not re.fullmatch(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", values["email"]):
    message = "Cloudmetrics: Info: Invalid email address provided. Omitting email notifications."
    error.WriteToErrorLog(message).log()
    print(message)
    values["email"] = None

# Log access
def logAccess():
    access.WriteToAccessLog().log()
    return True
logAccess()

# Collect and log system information
def logMetrics():
    info = sys_info.SysFetch(values)
    log = sys_info.LogSysFetch(values)
    logs = analyse_log.Logs(values)

    log.logGeneral()
    log.logConnection()
    log.logInterface()
    log.logMem()
    log.logLogin()

    logs.logSudo()
    logs.logCron()
    logs.logAuth()

    if not logs.logSudo():
        message = "Cloudmetrics: Info: Unable to collect metrics for sudo.log. Check permissions or file existence."
        error.WriteToErrorLog(message).log()

    gc = delete_log.DeleteLog(values)
    gc.deleteOldLogs()

logMetrics()

# Upload logs to S3 if cloud is active
if values["cloud"].get("active"):
    if not uploadS3(region, bucket):
        message = "Cloudmetrics: Error: Failed to connect to AWS S3 endpoint or bucket does not exist."
        error.WriteToErrorLog(message).log()
        print(message)

sys.exit(0)
