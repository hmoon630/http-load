import time
import re
import argparse
import threading
import signal
from sys import exit

import progressbar
import requests

DURATION = 10
RATE = 10
TIMEOUT = 10
URL = "http://localhost/health"

status_counts = dict()
durations = list()


def reqeust_to_endpoint(url: str):
    try:
        return requests.get(url=url, timeout=TIMEOUT)
    except (
        requests.exceptions.ReadTimeout,
        requests.exceptions.ConnectTimeout,
        requests.exceptions.ConnectionError,
    ):
        return None


def process_response(response, duration: float):
    if response is None:
        status = "Timeout"
        duration = TIMEOUT
    else:
        status = response.status_code

    try:
        status_counts[str(status)] += 1
    except KeyError:
        status_counts[str(status)] = 1

    durations.append(duration)


def print_statistic():
    status_result = ", ".join(
        sorted([f"{code}: {count}" for code, count in status_counts.items()])
    )
    durations.sort()
    min_time = round(min(durations), 3)
    mean_time = round(sum(durations) / len(durations), 3)
    p50_time = round(durations[int(len(durations) * 50 / 100) - 1], 3)
    p90_time = round(durations[int(len(durations) * 90 / 100) - 1], 3)
    p99_time = round(durations[int(len(durations) * 99 / 100) - 1], 3)

    print(f"Duration: {DURATION}, Rate: {RATE}, URL: {URL}")
    print(f"Status codes: {status_result}")
    print(
        f"Min: {min_time}, Mean: {mean_time}, p50: {p50_time}, p90: {p90_time}, p99: {p99_time}"
    )


def load():
    start = time.time()
    response = reqeust_to_endpoint(URL)
    duration = time.time() - start

    process_response(response=response, duration=duration)


def get_command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Http endpoint to send request")
    parser.add_argument(
        "-d", "--duration", help="Generate load for [duration] seconds. Default 10"
    )
    parser.add_argument(
        "-r", "--rate", help="Generate [rate] requests per second. Default 10"
    )
    parser.add_argument(
        "-t", "--timeout", help="Timeout seconds for http request. Default 10"
    )
    return parser.parse_args()


def get_parsed_args(args):
    url = args.url
    duration = int(args.duration or "10")
    rate = int(args.rate or "10")
    timeout = int(args.timeout or "10")

    http_regex = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
    pattern = re.compile(http_regex)
    is_valid_url = pattern.fullmatch(url)
    if is_valid_url is None:
        print(f"Invalid url: {url}. Check the url again or provide a schema for url.")
        exit(1)
    return url, duration, rate, timeout


def signal_handler(signum, frame):
    print("Stopped sending requests. Here's a stats for finished requests.")
    print_statistic()
    exit(1)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    args = get_command_line_args()
    URL, DURATION, RATE, TIMEOUT = get_parsed_args(args)

    total_start = time.time()
    bar = progressbar.ProgressBar(
        maxval=DURATION,
        widgets=[progressbar.Bar("=", "[", "]"), " ", progressbar.Percentage()],
    )
    bar.start()

    jobs = []
    for i in range(DURATION):
        new_jobs = [threading.Thread(target=load) for _ in range(RATE)]
        [job.start() for job in new_jobs]
        jobs += new_jobs

        bar.update(i + 1)
        time.sleep(1)
    bar.finish()
    print("Waiting for all requests to end..")
    [job.join() for job in jobs]
    print(f"Finished all requests.")

    print_statistic()
