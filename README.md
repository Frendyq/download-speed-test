# download-speed-test

Console script that measures download speed. It requests one URL 10 times in a row, waits for the full response each time, then prints the average request time, the total amount of data and the download speed.

## Requirements

Python 3.8 or newer. No third-party packages.

## Run

```bash
python speedtest.py URL
```

Options:

- `-n, --count`: number of requests, default 10
- `-t, --timeout`: timeout of one request in seconds, default 30

Example:

```bash
python speedtest.py https://proof.ovh.net/files/1Mb.dat
```

Output:

```
request 1/10: 1.05 MB in 1.177 s
request 2/10: 1.05 MB in 1.099 s
...
request 10/10: 1.05 MB in 1.200 s

successful requests: 10 of 10
average request time: 1.203 s
total downloaded: 10.49 MB
download speed: 6.97 Mbit/s (0.87 MB/s)
```

## Units

- Time: seconds (s).
- Data: megabytes (MB), 1 MB = 1,000,000 bytes.
- Speed: megabits per second (Mbit/s), 1 Mbit = 1,000,000 bits. The speed in megabytes per second (MB/s) is printed in brackets.

## How the speed is calculated

Speed = total downloaded bytes * 8 / total time of the requests. The time of each request is measured from sending the request until the last byte of the response is read. The pauses between requests are not counted. The speed is the total data divided by the total time, not an average of the speeds of single requests, so a short request does not weigh more than a long one.

## Notes

- Requests run one after another, not in parallel.
- A request that fails (network error, HTTP error, timeout) is reported and left out of the statistics.
- Exit code: 0 if all requests succeeded, 2 if some failed, 1 if all failed.
- Pick a large file (several MB). With a small file the result mostly shows latency, not bandwidth, as in the example above.
- The script sends `Cache-Control: no-cache`, but a CDN can still serve the file from its cache.

## Tests

```bash
python -m unittest -v
```

The tests start a local HTTP server, so they do not need internet access.
