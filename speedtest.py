#!/usr/bin/env python3
"""Measure download speed by requesting one URL several times in a row."""

import argparse
import sys
import time
import urllib.error
import urllib.request

CHUNK_SIZE = 64 * 1024


def fetch(url, timeout):
    """Download the whole response body. Return (bytes_read, seconds)."""
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "speedtest-cli/1.0", "Cache-Control": "no-cache"},
    )
    started = time.perf_counter()
    total = 0
    with urllib.request.urlopen(request, timeout=timeout) as response:
        while True:
            chunk = response.read(CHUNK_SIZE)
            if not chunk:
                break
            total += len(chunk)
    return total, time.perf_counter() - started


def run(url, count, timeout):
    """Make `count` sequential requests. Return a list of (bytes, seconds) for successful ones."""
    results = []
    failed = 0
    for number in range(1, count + 1):
        try:
            size, seconds = fetch(url, timeout)
        except (urllib.error.URLError, TimeoutError, ValueError, OSError) as error:
            failed += 1
            print(f"request {number}/{count}: failed ({error})")
            continue
        results.append((size, seconds))
        print(f"request {number}/{count}: {size / 1_000_000:.2f} MB in {seconds:.3f} s")
    return results, failed


def summarize(results):
    """Return (average_seconds, total_bytes, megabits_per_second)."""
    total_bytes = sum(size for size, _ in results)
    total_seconds = sum(seconds for _, seconds in results)
    average_seconds = total_seconds / len(results)
    # Speed is total data divided by total time, not an average of per-request speeds.
    megabits_per_second = total_bytes * 8 / total_seconds / 1_000_000
    return average_seconds, total_bytes, megabits_per_second


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Measure download speed for a URL.")
    parser.add_argument("url", help="address to download, for example a large image")
    parser.add_argument("-n", "--count", type=int, default=10, help="number of requests (default 10)")
    parser.add_argument("-t", "--timeout", type=float, default=30.0, help="timeout per request in seconds (default 30)")
    args = parser.parse_args(argv)
    if args.count < 1:
        parser.error("--count must be at least 1")
    return args


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    results, failed = run(args.url, args.count, args.timeout)
    if not results:
        print("all requests failed, nothing to measure")
        return 1

    average_seconds, total_bytes, mbps = summarize(results)
    print()
    print(f"successful requests: {len(results)} of {args.count}" + (f" ({failed} failed)" if failed else ""))
    print(f"average request time: {average_seconds:.3f} s")
    print(f"total downloaded: {total_bytes / 1_000_000:.2f} MB")
    print(f"download speed: {mbps:.2f} Mbit/s ({mbps / 8:.2f} MB/s)")
    return 0 if not failed else 2


if __name__ == "__main__":
    sys.exit(main())
