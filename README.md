# http load

## How to run

```bash
$ http-load -h

usage: http-load [-h] [-d DURATION] [-r RATE] [-t TIMEOUT] url

positional arguments:
  url                   Http endpoint to send request

options:
  -h, --help            show this help message and exit
  -d DURATION, --duration DURATION
                        Generate load for [duration] seconds. Default 10
  -r RATE, --rate RATE  Generate [rate] requests per second. Default 10
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout seconds for http request. Default 10
```

## Result Example

```
$ http-load http://localhost/health
[========================================================================] 100%
Waiting for all requests to end..
Finished all requests.
Duration: 10, Rate: 10, URL: http://localhost/health
Status codes: 400: 100
Min: 0.745, Mean: 0.851, p50: 0.845, p90: 0.919, p99: 0.939
```

## How to build

```
python -m PyInstaller main.py -F -n http-load
```

NOTE: This is a http benchmarking tool. It is purely made for load test, not for attacking.
