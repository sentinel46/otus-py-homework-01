#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import gzip
import json
import logging
import optparse
import os
import re
import statistics
import sys

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "ERROR_RATE": 0.1,
    "LOG_NAME": "log_analyzer.log"
}


def update_config(config_file_name, config_):
    """Update default config with data from file in json format"""

    with open(config_file_name) as config_file:
        new_config = json.load(config_file)

    config_.update(new_config)
    return config_


def find_last_log_file(pattern, log_dir="."):
    """
    Find matching regexp pattern file with last timestamp,
    returns file_name and it's timestamp string
    """

    log_files = {}
    for name in glob.glob(os.path.join(log_dir, "*")):
        match = re.match(pattern, name)
        if match:
            log_files.update({match.group("date"): name})
    if not log_files:
        return None

    last_date = sorted(log_files.keys(), reverse=True)[0]
    return log_files[last_date], last_date


def parse_log_file(pattern, file_name, error_rate):
    """
    Parse log file with given log pattern,
    return dictionary with urls and request times
    and dictionary with total log file statistics
    """

    open_log = gzip.open if file_name.endswith(".gz") else open

    total = 0
    succeed = 0
    total_time = 0
    url_stats = {}

    print("{} log parsing started".format(file_name))
    with open_log(file_name, "rb") as log_file:
        for line in log_file:
            total += 1
            if total % 10000 == 0:
                print("{} rows processed, {} are succeed".format(total, succeed))

            line = line.decode("utf-8")

            match = re.match(pattern, line)
            if match:
                url = match.group("request")

                time = float(match.group("request_time"))
                total_time += time
                if url not in url_stats:
                    url_stats[url] = []
                url_stats[url].append(time)

                succeed += 1
            else:
                logging.info("Cannot parse line: {}".format(line))

    if succeed / total < 1 - error_rate:
        return

    info = {"total": total, "succeed": succeed, "total_time": total_time}

    return url_stats, info


def get_stats(url, request_times, succeed, total_time):
    """Calculate url's statistics"""

    time_sum = sum(request_times)
    count = len(request_times)
    return {"url": url,
            "count": count,
            "count_perc": round(100 * count / succeed, 3),
            "time_sum": round(time_sum, 3),
            "time_perc": round(100 * time_sum / total_time, 3),
            "time_avg": round(time_sum / count, 3),
            "time_max": round(max(request_times), 3),
            "time_med": round(statistics.median(request_times), 3)}


def prepare_report(url_stats, info, report_size):
    """Prepare url's statistics and filter urls with longest request time"""

    all_urls_stats = []
    for url, request_times in url_stats.items():
        all_urls_stats.append(get_stats(url, request_times, info["succeed"], info["total_time"]))

    return list(sorted(all_urls_stats,
                       key=lambda report: report["time_sum"],
                       reverse=True))[:report_size]


def write_report_to_html(report, report_template, report_file_name):
    """Save report to file"""

    json_information = json.dumps(report)

    with open(report_template) as html_file:
        html = html_file.read()

    html = html.replace("$table_json", json_information)

    with open(report_file_name, "w") as report_file:
        report_file.write(html)


def main():
    parser = optparse.OptionParser()
    parser.add_option("--config", dest="new_config", default=None, type="string")
    options, args = parser.parse_args()

    logger_config = config
    if options.new_config:
        try:
            logger_config = update_config(options.new_config, logger_config)
        except (IOError, json.JSONDecodeError, TypeError) as e:
            sys.exit("Error while trying to read configuration file: {}".format(e))

    logging.basicConfig(filename=logger_config["LOG_NAME"] if logger_config["LOG_NAME"] else None,
                        format="[%(asctime)s] %(levelname).1s %(message)s",
                        datefmt="%Y.%m.%d %H:%M:%S",
                        level=logging.INFO)

    try:
        nginx_file_name_pattern = re.compile(".*nginx-access-ui\.log-(?P<date>\d{8})(\.gz)?$")
        result = find_last_log_file(nginx_file_name_pattern, logger_config["LOG_DIR"])
        if not result:
            logging.info("Log file not found. Nothing to parse. Exit.")
            sys.exit()
        log_file_name, timestamp = result

        report_file_name = "report-{}.{}.{}.html".format(timestamp[:4], timestamp[4:6], timestamp[6:8])
        report_file_name = os.path.join(logger_config["REPORT_DIR"], report_file_name)
        if report_file_name in glob.glob(os.path.join(logger_config["REPORT_DIR"], "*")):
            logging.info("Log report already exists. Nothing to do. Exit.")
            sys.exit()

        nginx_log_pattern = re.compile(
            "(?P<remote_addr>.+)\s+(?P<remote_user>.+)\s+(?P<http_x_real_ip>.+)\s+\[(?P<time_local>.+)\]\s+" \
            "\"[A-Z]{1,} (?P<request>.+) .*\"\s+(?P<status>.+)\s+(?P<body_bytes_send>.+)\s+" \
            "\"(?P<http_referer>.+)\"\s+\"(?P<http_user_agent>.+)\"\s+\"(?P<http_x_forwarded_for>.+)\"\s+" \
            "\"(?P<http_X_REQUEST_ID>.+)\"\s+\"(?P<http_X_RB_USER>.+)\"\s+(?P<request_time>.+)")

        result = parse_log_file(nginx_log_pattern, log_file_name, logger_config["ERROR_RATE"])
        if not result:
            logging.error("Too many log file parsing errors. Abort.")
            sys.exit()
        url_stats, info = result
        report = prepare_report(url_stats, info, logger_config["REPORT_SIZE"])
        write_report_to_html(report, "./report.html", report_file_name)
    except Exception as e:
        logging.exception("Unhandled error:\n{}".format(e))


if __name__ == "__main__":
    main()
