"""
Network Monitor
Phase 2 - Project 03

A defensive network monitoring tool that checks host availability,
measures latency, optionally checks TCP ports, tracks packet loss,
logs monitoring events, and exports JSON reports.

Standard library only.

Use this tool only on systems and networks you own or are authorized
to monitor.
"""

import argparse
import concurrent.futures
import datetime
import json
import os
import platform
import re
import socket
import subprocess
import threading
import time
from dataclasses import asdict, dataclass
from typing import List, Optional


# ============================================================
# Configuration
# ============================================================

DEFAULT_TIMEOUT = 2.0
DEFAULT_INTERVAL = 5
DEFAULT_WORKERS = 10

DEFAULT_PORTS = [22, 80, 443]

LOG_DIR = "logs"
REPORT_DIR = "reports"

LOG_FILE = os.path.join(LOG_DIR, "network_monitor.log")


# ============================================================
# Data Models
# ============================================================

@dataclass
class HostResult:
    target: str
    resolved_ip: Optional[str]
    status: str
    latency_ms: Optional[float]
    packet_loss: Optional[float]
    timestamp: str
    method: str
    error: Optional[str] = None


@dataclass
class PortResult:
    target: str
    port: int
    status: str
    service: str
    response_time_ms: Optional[float]
    timestamp: str
    error: Optional[str] = None


# ============================================================
# Utility Functions
# ============================================================

def utc_now() -> str:
    """Return the current UTC timestamp."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def ensure_directories() -> None:
    """Create required directories if they do not exist."""
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)


def log_event(message: str) -> None:
    """Write an event to the monitoring log."""
    ensure_directories()

    timestamp = utc_now()

    line = f"[{timestamp}] {message}"

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as file:
            file.write(line + "\n")
    except OSError:
        pass


def print_header(title: str) -> None:
    """Display a formatted section header."""
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def resolve_hostname(target: str) -> Optional[str]:
    """Resolve a hostname to an IP address."""
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        return None


def get_service_name(port: int) -> str:
    """Return the registered service name for a TCP port."""
    try:
        return socket.getservbyport(port, "tcp")
    except OSError:
        return "unknown"


# ============================================================
# ICMP/System Ping
# ============================================================

def system_ping(
    target: str,
    timeout: float
) -> HostResult:
    """
    Perform a system-level ping.

    Windows:
        ping -n 1 -w <milliseconds> target

    Linux/macOS:
        ping -c 1 -W <seconds> target
    """

    timestamp = utc_now()
    resolved_ip = resolve_hostname(target)

    if resolved_ip is None:
        return HostResult(
            target=target,
            resolved_ip=None,
            status="DOWN",
            latency_ms=None,
            packet_loss=100.0,
            timestamp=timestamp,
            method="system_ping",
            error="Hostname could not be resolved"
        )

    system = platform.system().lower()

    if system == "windows":
        command = [
            "ping",
            "-n",
            "1",
            "-w",
            str(int(timeout * 1000)),
            target
        ]

    else:
        command = [
            "ping",
            "-c",
            "1",
            "-W",
            str(max(1, int(timeout))),
            target
        ]

    start = time.perf_counter()

    try:
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout + 2
        )

        elapsed_ms = round(
            (time.perf_counter() - start) * 1000,
            2
        )

        output = process.stdout + process.stderr

        if process.returncode == 0:
            latency = extract_ping_latency(output)

            if latency is None:
                latency = elapsed_ms

            return HostResult(
                target=target,
                resolved_ip=resolved_ip,
                status="UP",
                latency_ms=latency,
                packet_loss=0.0,
                timestamp=timestamp,
                method="system_ping"
            )

        return HostResult(
            target=target,
            resolved_ip=resolved_ip,
            status="DOWN",
            latency_ms=None,
            packet_loss=100.0,
            timestamp=timestamp,
            method="system_ping",
            error="Ping request failed"
        )

    except subprocess.TimeoutExpired:
        return HostResult(
            target=target,
            resolved_ip=resolved_ip,
            status="DOWN",
            latency_ms=None,
            packet_loss=100.0,
            timestamp=timestamp,
            method="system_ping",
            error="Ping timed out"
        )

    except FileNotFoundError:
        return HostResult(
            target=target,
            resolved_ip=resolved_ip,
            status="ERROR",
            latency_ms=None,
            packet_loss=None,
            timestamp=timestamp,
            method="system_ping",
            error="System ping command was not found"
        )

    except Exception as exc:
        return HostResult(
            target=target,
            resolved_ip=resolved_ip,
            status="ERROR",
            latency_ms=None,
            packet_loss=None,
            timestamp=timestamp,
            method="system_ping",
            error=str(exc)
        )


def extract_ping_latency(output: str) -> Optional[float]:
    """
    Extract latency from Windows/Linux/macOS ping output.
    """

    patterns = [
        r"time[=<]\s*(\d+(?:\.\d+)?)\s*ms",
        r"time[=<]\s*(\d+)\s*ms",
        r"Average = (\d+)ms",
        r"avg[^\n]*=\s*[\d.]+/([\d.]+)/"
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            output,
            re.IGNORECASE
        )

        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue

    return None


# ============================================================
# TCP Connectivity Check
# ============================================================

def check_tcp_port(
    target: str,
    port: int,
    timeout: float
) -> PortResult:
    """Check whether a TCP port accepts connections."""

    timestamp = utc_now()

    try:
        start = time.perf_counter()

        with socket.create_connection(
            (target, port),
            timeout=timeout
        ):
            elapsed_ms = round(
                (time.perf_counter() - start) * 1000,
                2
            )

        return PortResult(
            target=target,
            port=port,
            status="OPEN",
            service=get_service_name(port),
            response_time_ms=elapsed_ms,
            timestamp=timestamp
        )

    except socket.timeout:
        return PortResult(
            target=target,
            port=port,
            status="FILTERED/TIMEOUT",
            service=get_service_name(port),
            response_time_ms=None,
            timestamp=timestamp,
            error="Connection timed out"
        )

    except ConnectionRefusedError:
        return PortResult(
            target=target,
            port=port,
            status="CLOSED",
            service=get_service_name(port),
            response_time_ms=None,
            timestamp=timestamp,
            error="Connection refused"
        )

    except socket.gaierror:
        return PortResult(
            target=target,
            port=port,
            status="ERROR",
            service=get_service_name(port),
            response_time_ms=None,
            timestamp=timestamp,
            error="Hostname could not be resolved"
        )

    except OSError as exc:
        return PortResult(
            target=target,
            port=port,
            status="CLOSED/ERROR",
            service=get_service_name(port),
            response_time_ms=None,
            timestamp=timestamp,
            error=str(exc)
        )


# ============================================================
# Monitoring
# ============================================================

def monitor_host(
    target: str,
    timeout: float
) -> HostResult:
    """Monitor a single host."""

    result = system_ping(target, timeout)

    if result.status == "UP":
        print(
            f"[UP]   {target:<25} "
            f"{result.resolved_ip:<16} "
            f"{result.latency_ms:>8.2f} ms"
        )

        log_event(
            f"HOST UP | {target} | "
            f"{result.resolved_ip} | "
            f"{result.latency_ms} ms"
        )

    elif result.status == "DOWN":
        print(
            f"[DOWN] {target:<25} "
            f"{result.error}"
        )

        log_event(
            f"HOST DOWN | {target} | {result.error}"
        )

    else:
        print(
            f"[ERROR] {target:<25} "
            f"{result.error}"
        )

        log_event(
            f"HOST ERROR | {target} | {result.error}"
        )

    return result


def monitor_hosts(
    targets: List[str],
    timeout: float,
    workers: int
) -> List[HostResult]:
    """Monitor multiple hosts concurrently."""

    results = []

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=workers
    ) as executor:

        futures = [
            executor.submit(
                monitor_host,
                target,
                timeout
            )
            for target in targets
        ]

        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    return results


def monitor_ports(
    target: str,
    ports: List[int],
    timeout: float,
    workers: int
) -> List[PortResult]:
    """Check multiple TCP ports concurrently."""

    print_header(
        f"TCP PORT MONITORING — {target}"
    )

    results = []

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=workers
    ) as executor:

        futures = {
            executor.submit(
                check_tcp_port,
                target,
                port,
                timeout
            ): port
            for port in ports
        }

        for future in concurrent.futures.as_completed(futures):
            result = future.result()

            results.append(result)

            if result.status == "OPEN":
                print(
                    f"[OPEN]    "
                    f"{result.port:<6} "
                    f"{result.service:<15} "
                    f"{result.response_time_ms:>8.2f} ms"
                )

                log_event(
                    f"PORT OPEN | {target}:{result.port} | "
                    f"{result.service}"
                )

            elif result.status == "CLOSED":
                print(
                    f"[CLOSED]  "
                    f"{result.port:<6} "
                    f"{result.service}"
                )

            elif result.status == "FILTERED/TIMEOUT":
                print(
                    f"[FILTERED] "
                    f"{result.port:<6} "
                    f"{result.service}"
                )

            else:
                print(
                    f"[ERROR]   "
                    f"{result.port:<6} "
                    f"{result.error}"
                )

    return sorted(
        results,
        key=lambda item: item.port
    )


# ============================================================
# Statistics
# ============================================================

def calculate_statistics(
    history: List[HostResult]
) -> dict:
    """Calculate monitoring statistics."""

    if not history:
        return {
            "total_checks": 0,
            "successful_checks": 0,
            "failed_checks": 0,
            "packet_loss_percent": 0.0,
            "average_latency_ms": None,
            "minimum_latency_ms": None,
            "maximum_latency_ms": None
        }

    successful = [
        item for item in history
        if item.status == "UP"
        and item.latency_ms is not None
    ]

    failed = [
        item for item in history
        if item.status == "DOWN"
    ]

    latencies = [
        item.latency_ms
        for item in successful
        if item.latency_ms is not None
    ]

    total = len(history)

    packet_loss = round(
        (len(failed) / total) * 100,
        2
    )

    return {
        "total_checks": total,
        "successful_checks": len(successful),
        "failed_checks": len(failed),
        "packet_loss_percent": packet_loss,
        "average_latency_ms": (
            round(sum(latencies) / len(latencies), 2)
            if latencies else None
        ),
        "minimum_latency_ms": (
            round(min(latencies), 2)
            if latencies else None
        ),
        "maximum_latency_ms": (
            round(max(latencies), 2)
            if latencies else None
        )
    }


# ============================================================
# JSON Reporting
# ============================================================

def save_json_report(
    filename: str,
    host_results: List[HostResult],
    port_results: Optional[List[PortResult]] = None,
    statistics: Optional[dict] = None
) -> None:
    """Save monitoring information as JSON."""

    ensure_directories()

    data = {
        "tool": "Network Monitor",
        "version": "1.0",
        "generated_at": utc_now(),
        "host_results": [
            asdict(result)
            for result in host_results
        ],
        "port_results": [
            asdict(result)
            for result in (port_results or [])
        ],
        "statistics": statistics or {}
    }

    try:
        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

        print()
        print(f"[+] Report saved: {filename}")

        log_event(
            f"REPORT SAVED | {filename}"
        )

    except OSError as exc:
        print(
            f"[!] Could not save report: {exc}"
        )


# ============================================================
# Display Statistics
# ============================================================

def display_statistics(
    statistics: dict
) -> None:

    print_header("MONITORING STATISTICS")

    print(
        f"Total checks       : "
        f"{statistics['total_checks']}"
    )

    print(
        f"Successful checks  : "
        f"{statistics['successful_checks']}"
    )

    print(
        f"Failed checks      : "
        f"{statistics['failed_checks']}"
    )

    print(
        f"Packet loss        : "
        f"{statistics['packet_loss_percent']}%"
    )

    average = statistics["average_latency_ms"]
    minimum = statistics["minimum_latency_ms"]
    maximum = statistics["maximum_latency_ms"]

    print(
        f"Average latency    : "
        f"{average if average is not None else 'N/A'} ms"
    )

    print(
        f"Minimum latency    : "
        f"{minimum if minimum is not None else 'N/A'} ms"
    )

    print(
        f"Maximum latency    : "
        f"{maximum if maximum is not None else 'N/A'} ms"
    )


# ============================================================
# Continuous Monitoring
# ============================================================

def continuous_monitor(
    targets: List[str],
    timeout: float,
    interval: int,
    workers: int,
    cycles: Optional[int]
) -> List[HostResult]:

    history = []

    cycle_number = 0

    print_header("CONTINUOUS NETWORK MONITOR")

    print(
        f"Targets   : {', '.join(targets)}"
    )

    print(
        f"Interval  : {interval} seconds"
    )

    print(
        f"Timeout   : {timeout} seconds"
    )

    print(
        "Press Ctrl+C to stop monitoring."
    )

    while True:

        cycle_number += 1

        print()
        print(
            f"--- Monitoring Cycle "
            f"{cycle_number} | {utc_now()} ---"
        )

        results = monitor_hosts(
            targets,
            timeout,
            workers
        )

        history.extend(results)

        if cycles is not None:
            if cycle_number >= cycles:
                break

        try:
            time.sleep(interval)

        except KeyboardInterrupt:
            break

    return history


# ============================================================
# Argument Parsing
# ============================================================

def parse_ports(value: str) -> List[int]:
    """Parse comma-separated ports and ranges."""

    ports = set()

    for part in value.split(","):

        part = part.strip()

        if not part:
            continue

        if "-" in part:

            pieces = part.split("-", 1)

            if len(pieces) != 2:
                raise ValueError(
                    f"Invalid port range: {part}"
                )

            start = int(pieces[0])
            end = int(pieces[1])

            if start > end:
                raise ValueError(
                    f"Invalid port range: {part}"
                )

            for port in range(start, end + 1):
                if 1 <= port <= 65535:
                    ports.add(port)

        else:

            port = int(part)

            if not 1 <= port <= 65535:
                raise ValueError(
                    f"Port must be between 1 and 65535: {port}"
                )

            ports.add(port)

    if not ports:
        raise ValueError(
            "No valid ports were provided."
        )

    return sorted(ports)


def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=(
            "Defensive network monitoring tool for "
            "authorized systems and networks."
        )
    )

    parser.add_argument(
        "targets",
        nargs="+",
        help=(
            "Hostname or IP address to monitor. "
            "Example: 127.0.0.1 google.com"
        )
    )

    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=(
            f"Network timeout in seconds "
            f"(default: {DEFAULT_TIMEOUT})"
        )
    )

    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default=DEFAULT_INTERVAL,
        help=(
            f"Monitoring interval in seconds "
            f"(default: {DEFAULT_INTERVAL})"
        )
    )

    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=(
            f"Maximum concurrent workers "
            f"(default: {DEFAULT_WORKERS})"
        )
    )

    parser.add_argument(
        "-c",
        "--continuous",
        action="store_true",
        help="Enable continuous monitoring mode."
    )

    parser.add_argument(
        "--cycles",
        type=int,
        default=None,
        help=(
            "Number of monitoring cycles in continuous "
            "mode. If omitted, runs until Ctrl+C."
        )
    )

    parser.add_argument(
        "--ports",
        type=str,
        default=None,
        help=(
            "TCP ports to check. "
            "Example: 22,80,443 or 1-100"
        )
    )

    parser.add_argument(
        "--report",
        type=str,
        default=None,
        help=(
            "Save results to a JSON report."
        )
    )

    parser.add_argument(
        "--no-ping",
        action="store_true",
        help=(
            "Skip system ping and only perform "
            "TCP port checks."
        )
    )

    return parser


# ============================================================
# Validation
# ============================================================

def validate_arguments(args: argparse.Namespace) -> None:

    if args.timeout <= 0:
        raise ValueError(
            "Timeout must be greater than 0."
        )

    if args.interval <= 0:
        raise ValueError(
            "Interval must be greater than 0."
        )

    if args.workers <= 0:
        raise ValueError(
            "Workers must be greater than 0."
        )

    if args.cycles is not None and args.cycles <= 0:
        raise ValueError(
            "Cycles must be greater than 0."
        )


# ============================================================
# Main Application
# ============================================================

def main() -> None:

    parser = build_parser()

    args = parser.parse_args()

    try:
        validate_arguments(args)

        ports = None

        if args.ports:
            ports = parse_ports(args.ports)

    except ValueError as exc:

        parser.error(str(exc))

        return

    ensure_directories()

    print()
    print("=" * 70)
    print("                 NETWORK MONITOR")
    print("             Phase 2 - Project 03")
    print("=" * 70)

    print()
    print(
        "Authorized monitoring only."
    )

    host_results = []
    port_results = []

    # --------------------------------------------------------
    # Continuous monitoring
    # --------------------------------------------------------

    if args.continuous:

        if args.no_ping:
            print(
                "\n[!] Continuous mode requires host monitoring."
            )
            return

        host_results = continuous_monitor(
            targets=args.targets,
            timeout=args.timeout,
            interval=args.interval,
            workers=args.workers,
            cycles=args.cycles
        )

    # --------------------------------------------------------
    # One-time host monitoring
    # --------------------------------------------------------

    elif not args.no_ping:

        print_header("HOST AVAILABILITY")

        print(
            f"{'STATUS':<8}"
            f"{'TARGET':<25}"
            f"{'IP ADDRESS':<16}"
            f"{'LATENCY':>12}"
        )

        print("-" * 70)

        host_results = monitor_hosts(
            args.targets,
            args.timeout,
            args.workers
        )

    # --------------------------------------------------------
    # TCP port monitoring
    # --------------------------------------------------------

    if ports:

        for target in args.targets:

            target_port_results = monitor_ports(
                target=target,
                ports=ports,
                timeout=args.timeout,
                workers=args.workers
            )

            port_results.extend(
                target_port_results
            )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    if host_results:

        statistics = calculate_statistics(
            host_results
        )

        display_statistics(
            statistics
        )

    else:

        statistics = {}

    # --------------------------------------------------------
    # Save report
    # --------------------------------------------------------

    if args.report:

        save_json_report(
            filename=args.report,
            host_results=host_results,
            port_results=port_results,
            statistics=statistics
        )

    print()
    print("=" * 70)
    print("Monitoring completed.")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:

        print()
        print(
            "\n[!] Monitoring stopped by user."
        )

        log_event(
            "MONITORING STOPPED BY USER"
        )
