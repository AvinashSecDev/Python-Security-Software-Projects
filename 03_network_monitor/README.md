# 🌐 Network Monitor

A defensive Python-based network monitoring tool designed to monitor host availability, measure network latency, detect connectivity failures, check TCP port availability, calculate packet loss, record monitoring events, and generate structured JSON reports.

> **Phase 2 — Python Security & Software Projects | Project 03**

---

## 📌 Overview

The **Network Monitor** is a lightweight command-line network monitoring application built entirely with Python's standard library.

The project is designed to provide a practical way to monitor authorized hosts and services without relying on third-party Python packages.

It can:

* 🌐 Monitor multiple hosts
* 📡 Check host availability using the system `ping` command
* ⏱️ Measure network latency
* 📉 Calculate packet loss
* 🔌 Check TCP port connectivity
* 🚨 Detect UP, DOWN, CLOSED, and TIMEOUT states
* ⚡ Monitor multiple targets concurrently
* 🔄 Continuously monitor hosts at configurable intervals
* 📝 Record monitoring events in log files
* 📊 Calculate monitoring statistics
* 💾 Export monitoring results to JSON
* 🖥️ Work from a command-line interface
* 🪟 Support Windows
* 🐧 Support Linux and other Unix-like systems where the system `ping` command is available

The project focuses on **network visibility, monitoring, reliability, and defensive security** rather than exploitation or intrusive network activity.

---

# 🎯 Project Goals

The main goals of this project are to build a practical network monitoring application while improving understanding of:

* Python networking
* TCP/IP fundamentals
* Host availability monitoring
* Network latency
* Packet loss
* TCP connectivity
* Concurrent programming
* Thread pools
* Socket programming
* Subprocess execution
* JSON data serialization
* Logging
* CLI application design
* Error handling
* Defensive security practices

The project also demonstrates how a larger Python security application can be structured instead of building only small standalone scripts.

---

# ✨ Features

## 🌐 1. Host Availability Monitoring

The monitor can check whether a target host is reachable.

Example:

```bash
python network_monitor.py 127.0.0.1
```

The program performs a system-level ping and reports whether the target is:

```text
UP
DOWN
ERROR
```

For reachable hosts, the monitor attempts to record the response latency.

---

## ⏱️ 2. Latency Measurement

When a host responds successfully, the application measures the response time.

Example:

```text
[UP]   127.0.0.1                 127.0.0.1              1.00 ms
```

Latency is useful for identifying changes in network responsiveness.

The application records:

* Average latency
* Minimum latency
* Maximum latency

---

## 📉 3. Packet Loss Calculation

The application calculates packet loss based on monitoring results.

For example:

```text
Total checks       : 10
Successful checks  : 8
Failed checks      : 2
Packet loss        : 20.0%
```

Packet loss can indicate connectivity problems, unavailable systems, or network instability.

---

# 🔌 4. TCP Port Monitoring

The application can also check whether selected TCP ports accept connections.

Example:

```bash
python network_monitor.py 127.0.0.1 --ports 22,80,443
```

Possible results include:

```text
[OPEN]
[CLOSED]
[FILTERED/TIMEOUT]
[ERROR]
```

For open ports, the application also attempts to display the registered service name.

Example:

```text
[OPEN]    443    https               12.35 ms
[CLOSED]  22     ssh
[CLOSED]  80     http
```

This functionality is intended for monitoring systems and services that you are authorized to manage.

---

# ⚡ 5. Concurrent Monitoring

The application uses Python's:

```python
concurrent.futures.ThreadPoolExecutor
```

to monitor multiple targets concurrently.

Instead of waiting for every host to finish before checking the next host, multiple checks can execute concurrently.

This makes the application more practical when monitoring several hosts.

The number of workers can be configured.

Example:

```bash
python network_monitor.py 192.168.1.1 192.168.1.10 192.168.1.20 -w 20
```

---

# 🔄 6. Continuous Monitoring

The monitor can run continuously at a configurable interval.

Example:

```bash
python network_monitor.py 127.0.0.1 -c
```

By default, the application performs monitoring cycles every few seconds.

The interval can be changed:

```bash
python network_monitor.py 127.0.0.1 -c -i 10
```

This performs a monitoring cycle every 10 seconds.

To stop continuous monitoring:

```text
Ctrl + C
```

---

# 🔢 7. Limited Monitoring Cycles

Continuous mode can also be configured to run for a specific number of cycles.

Example:

```bash
python network_monitor.py 127.0.0.1 -c --cycles 5
```

The program performs five monitoring cycles and then stops.

This is useful for testing and demonstrations.

---

# 📝 8. Event Logging

The application records important monitoring events in:

```text
logs/network_monitor.log
```

Examples of events include:

```text
HOST UP
HOST DOWN
HOST ERROR
PORT OPEN
REPORT SAVED
MONITORING STOPPED
```

Example:

```text
[2026-09-21T14:30:00+00:00] HOST UP | 127.0.0.1 | 127.0.0.1 | 1.0 ms
```

The logging system provides a basic historical record of monitoring activity.

---

# 📊 9. Monitoring Statistics

After monitoring completes, the application calculates statistics such as:

```text
Total checks
Successful checks
Failed checks
Packet loss
Average latency
Minimum latency
Maximum latency
```

Example:

```text
======================================================================
MONITORING STATISTICS
======================================================================
Total checks       : 5
Successful checks  : 5
Failed checks      : 0
Packet loss        : 0.0%
Average latency    : 1.2 ms
Minimum latency    : 1.0 ms
Maximum latency    : 1.8 ms
```

---

# 💾 10. JSON Report Generation

Monitoring results can be exported into a JSON file.

Example:

```bash
python network_monitor.py 127.0.0.1 --report reports/local_scan.json
```

The report contains information such as:

* Tool information
* Report generation time
* Host monitoring results
* TCP port results
* Monitoring statistics

Example structure:

```json
{
    "tool": "Network Monitor",
    "version": "1.0",
    "generated_at": "timestamp",
    "host_results": [],
    "port_results": [],
    "statistics": {}
}
```

JSON makes the monitoring data easier to process programmatically in future versions.

---

# 🖥️ Command-Line Interface

The application uses Python's built-in:

```python
argparse
```

module for command-line configuration.

Run:

```bash
python network_monitor.py --help
```

to view all available options.

---

# 🚀 Usage

## Basic Host Monitoring

Monitor localhost:

```bash
python network_monitor.py 127.0.0.1
```

Monitor a hostname:

```bash
python network_monitor.py example.com
```

Monitor multiple hosts:

```bash
python network_monitor.py 127.0.0.1 example.com
```

---

# 🔌 TCP Port Monitoring

Check common ports:

```bash
python network_monitor.py 127.0.0.1 --ports 22,80,443
```

Check a range of ports:

```bash
python network_monitor.py 127.0.0.1 --ports 1-100
```

Combine individual ports and ranges:

```bash
python network_monitor.py 127.0.0.1 --ports 22,80,443,8000-8010
```

---

# ⏱️ Configure Timeout

Change the network timeout:

```bash
python network_monitor.py 127.0.0.1 -t 5
```

This sets the timeout to 5 seconds.

---

# ⚡ Configure Concurrent Workers

Change the number of concurrent workers:

```bash
python network_monitor.py 192.168.1.1 192.168.1.2 -w 20
```

---

# 🔄 Continuous Monitoring

Start continuous monitoring:

```bash
python network_monitor.py 127.0.0.1 -c
```

Set a custom interval:

```bash
python network_monitor.py 127.0.0.1 -c -i 10
```

Run exactly 10 monitoring cycles:

```bash
python network_monitor.py 127.0.0.1 -c --cycles 10
```

---

# 📄 Generate a JSON Report

```bash
python network_monitor.py 127.0.0.1 --report reports/local_scan.json
```

You can combine monitoring and TCP checks:

```bash
python network_monitor.py 127.0.0.1 \
    --ports 22,80,443 \
    --report reports/local_scan.json
```

On Windows PowerShell, the command can also be written on one line:

```powershell
python network_monitor.py 127.0.0.1 --ports 22,80,443 --report reports/local_scan.json
```

---

# 🚫 Skip Ping

If you only want to perform TCP port checks:

```bash
python network_monitor.py 127.0.0.1 --ports 80,443 --no-ping
```

This skips host availability testing and focuses on TCP connectivity.

---

# 🧩 Command-Line Options

| Option               | Description                       |
| -------------------- | --------------------------------- |
| `targets`            | Hostname or IP address to monitor |
| `-t`, `--timeout`    | Network timeout in seconds        |
| `-i`, `--interval`   | Continuous monitoring interval    |
| `-w`, `--workers`    | Number of concurrent workers      |
| `-c`, `--continuous` | Enable continuous monitoring      |
| `--cycles`           | Number of monitoring cycles       |
| `--ports`            | TCP ports or port ranges to check |
| `--report`           | JSON report output path           |
| `--no-ping`          | Skip system ping                  |
| `-h`, `--help`       | Display help information          |

---

# 🏗️ Project Structure

```text
03_network_monitor/
│
├── network_monitor.py
│
├── README.md
│
├── requirements.txt
│
├── reports/
│   └── .gitkeep
│
└── logs/
    └── .gitkeep
```

---

# 📁 File Description

### `network_monitor.py`

The main application.

Contains:

* Host monitoring
* Ping execution
* Latency extraction
* TCP connectivity testing
* Concurrent execution
* Continuous monitoring
* Statistics
* Logging
* JSON report generation
* CLI argument handling

---

### `requirements.txt`

The project does not require external Python packages.

It uses only Python's standard library.

---

### `reports/`

Stores locally generated JSON monitoring reports.

Example:

```text
reports/local_scan.json
```

Generated reports should generally **not be committed to a public repository** if they contain private network information.

---

### `logs/`

Stores local monitoring logs.

Example:

```text
logs/network_monitor.log
```

Logs should generally remain local when they contain private infrastructure information.

---

# 🛠️ Technologies Used

| Technology          | Purpose                                |
| ------------------- | -------------------------------------- |
| Python              | Main programming language              |
| Socket              | TCP connectivity and DNS functionality |
| Subprocess          | Execute system ping                    |
| ThreadPoolExecutor  | Concurrent monitoring                  |
| Argparse            | CLI interface                          |
| JSON                | Report generation                      |
| Dataclasses         | Structured monitoring results          |
| Time                | Latency and monitoring intervals       |
| Logging/File I/O    | Event recording                        |
| Regular Expressions | Ping latency extraction                |

---

# 🧠 Python Concepts Demonstrated

This project demonstrates several practical Python concepts.

### Networking

```python
socket
```

Used for:

* DNS resolution
* TCP connections
* Port connectivity testing

### Concurrency

```python
concurrent.futures.ThreadPoolExecutor
```

Used to monitor multiple hosts concurrently.

### Subprocess Management

```python
subprocess.run()
```

Used to execute the operating system's ping command.

### Data Classes

```python
@dataclass
```

Used to represent host and port monitoring results.

### JSON Serialization

```python
json.dump()
```

Used to generate structured reports.

### Command-Line Arguments

```python
argparse
```

Used to provide configurable CLI functionality.

### Regular Expressions

```python
re
```

Used to extract latency values from ping output.

---

# 🔐 Security Considerations

This project is designed as a **defensive monitoring tool**.

It does not attempt to:

* Exploit vulnerabilities
* Bypass authentication
* Brute-force credentials
* Capture passwords
* Intercept private traffic
* Perform packet injection
* Exploit discovered services
* Circumvent network security controls

The TCP functionality only attempts normal TCP connections to the ports explicitly supplied by the user.

---

# ⚠️ Authorization & Legal Use

Only monitor systems and networks that you own or have explicit authorization to monitor.

Examples of appropriate targets include:

* Your own computer
* Your own home lab
* Your own virtual machines
* Your own servers
* Authorized test environments
* Systems where you have explicit permission to perform monitoring

Do not use this tool to monitor networks or systems without authorization.

The author is not responsible for misuse of this software.

---

# 🔒 Privacy Considerations

Network monitoring data can contain sensitive information.

Generated reports and logs may include:

* IP addresses
* Hostnames
* Port information
* Service information
* Monitoring timestamps
* Network availability information

Therefore:

> Do not upload real infrastructure reports or logs to a public GitHub repository unless you have confirmed that the information is safe to disclose.

For GitHub development, use test environments and sanitized data.

---

# 🧪 Testing

The project can be tested safely using localhost.

## Test 1 — Localhost

```bash
python network_monitor.py 127.0.0.1
```

Expected result:

```text
[UP] 127.0.0.1
```

---

## Test 2 — TCP Ports

```bash
python network_monitor.py 127.0.0.1 --ports 22,80,443
```

The result depends on which services are actually running on your machine.

---

## Test 3 — Continuous Monitoring

```bash
python network_monitor.py 127.0.0.1 -c -i 5 --cycles 3
```

This performs three monitoring cycles with a five-second interval.

---

## Test 4 — JSON Report

```bash
python network_monitor.py 127.0.0.1 --report reports/test.json
```

Verify that:

```text
reports/test.json
```

was generated.

Remember to remove or keep the generated report locally rather than uploading sensitive monitoring data.

---

# 🛡️ Error Handling

The application handles several possible failures.

Examples include:

### DNS Resolution Failure

```text
Hostname could not be resolved
```

### Ping Timeout

```text
Ping timed out
```

### TCP Connection Timeout

```text
Connection timed out
```

### Connection Refused

```text
Connection refused
```

### Missing Ping Command

```text
System ping command was not found
```

### Invalid Arguments

The CLI validates:

* Timeout
* Interval
* Worker count
* Port numbers
* Port ranges
* Monitoring cycles

---

# 📊 Monitoring Workflow

The basic monitoring workflow is:

```text
                ┌─────────────────────┐
                │     Start Tool      │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Parse CLI Arguments │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Resolve Target Host │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Check Availability│
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Measure Latency     │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Optional TCP Checks │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Calculate Statistics│
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Log Monitoring Data │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Optional JSON Report│
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │       Finish        │
                └─────────────────────┘
```

---

# 🧱 Application Architecture

The application is divided logically into several components.

```text
CLI
 │
 ├── Argument Validation
 │
 ├── Host Monitoring
 │    ├── DNS Resolution
 │    ├── System Ping
 │    └── Latency Measurement
 │
 ├── TCP Monitoring
 │    ├── Socket Connection
 │    └── Service Identification
 │
 ├── Concurrency
 │    └── ThreadPoolExecutor
 │
 ├── Statistics
 │    ├── Success Rate
 │    ├── Packet Loss
 │    └── Latency
 │
 ├── Logging
 │
 └── Reporting
      └── JSON
```

---

# ⚙️ Requirements

## Python

Python **3.9+** is recommended.

Check your installed Python version:

```bash
python --version
```

or:

```bash
python3 --version
```

---

# 📦 Installation

Clone or download the repository.

Navigate to the project directory:

```bash
cd 03_network_monitor
```

No external packages are required.

Run:

```bash
python network_monitor.py --help
```

If the help menu appears, the application is ready.

---

# 🖥️ Platform Compatibility

The project is designed around standard Python functionality and the operating system's `ping` utility.

### Windows

Supported.

Example:

```powershell
python network_monitor.py 127.0.0.1
```

### Linux

Supported where the standard `ping` command is available.

Example:

```bash
python3 network_monitor.py 127.0.0.1
```

### macOS

The application may require minor adjustments to the system ping arguments depending on the operating system's ping implementation.

---

# 🚧 Current Limitations

This version intentionally keeps the project lightweight.

Current limitations include:

* It relies on the operating system's `ping` command.
* Only one ping attempt is performed per monitoring cycle.
* TCP checks only test connection availability.
* It does not capture network packets.
* It does not perform deep protocol analysis.
* It does not automatically identify vulnerabilities.
* It does not provide a graphical dashboard.
* Historical data is stored primarily through logs and JSON reports.
* Ping output formats can differ between operating systems.
* The application does not provide a centralized multi-user monitoring server.

These limitations leave room for future development.

---

# 🚀 Future Improvements

Possible future versions could include:

### 📊 Web Dashboard

Create a dashboard showing:

* Online hosts
* Offline hosts
* Latency graphs
* Packet-loss graphs
* Port status
* Monitoring history

Possible technologies:

```text
FastAPI
Flask
React
Next.js
```

---

### 🗄️ Database Storage

Instead of relying only on JSON and log files, monitoring data could be stored in:

```text
SQLite
PostgreSQL
```

This would allow long-term historical analysis.

---

### 🚨 Alert System

Add alerts when:

* Host becomes unavailable
* Host comes back online
* Latency exceeds a threshold
* Packet loss exceeds a threshold
* Important TCP service becomes unavailable

Potential notification systems:

```text
Email
Discord
Telegram
Webhook
```

---

### 📈 Historical Analytics

Track:

```text
Average latency over time
Packet loss over time
Availability percentage
Downtime duration
Service availability
```

---

### 🔐 Security Monitoring

Future versions could integrate additional defensive checks such as:

* TLS certificate expiration monitoring
* HTTP availability monitoring
* HTTP response-time monitoring
* DNS monitoring
* Service health checks
* Certificate validation
* Secure configuration checks

---

### 🖥️ Configuration File

A future version could support a configuration file such as:

```yaml
targets:
  - 192.168.1.1
  - 192.168.1.10

ports:
  - 22
  - 80
  - 443

interval: 10
timeout: 2
```

---

# 📚 Learning Outcomes

By completing this project, the following concepts are practiced:

* Python network programming
* TCP connections
* DNS resolution
* Network latency
* Packet loss
* Concurrent programming
* Thread pools
* Command-line application development
* JSON serialization
* File handling
* Logging
* Error handling
* Cross-platform considerations
* Defensive security practices
* Monitoring architecture

---

# 🧠 Security Philosophy

This project follows the broader security principles used throughout the repository:

### Secure by Design

Security considerations are included during application development rather than added afterward.

### Least Privilege

The application performs only the network checks required by the user.

### Defense in Depth

Monitoring information can come from multiple mechanisms:

```text
Host availability
+
Latency
+
TCP connectivity
+
Logging
+
Statistics
```

### Secure Defaults

The application uses reasonable default timeouts and worker counts.

### Privacy by Design

The project warns against publicly exposing real infrastructure information.

---

# 📌 Example Session

Example:

```text
======================================================================
                 NETWORK MONITOR
             Phase 2 - Project 03
======================================================================

Authorized monitoring only.

======================================================================
HOST AVAILABILITY
======================================================================
STATUS  TARGET                   IP ADDRESS         LATENCY
----------------------------------------------------------------------
[UP]    127.0.0.1                127.0.0.1              1.00 ms

======================================================================
MONITORING STATISTICS
======================================================================
Total checks       : 1
Successful checks  : 1
Failed checks      : 0
Packet loss        : 0.0%
Average latency    : 1.0 ms
Minimum latency    : 1.0 ms
Maximum latency    : 1.0 ms

======================================================================
Monitoring completed.
======================================================================
```

---

# 📈 Project Status

```text
Phase 2
└── Project 03 — Network Monitor
    ├── Host Monitoring       ✅
    ├── Latency Measurement   ✅
    ├── Packet Loss           ✅
    ├── TCP Monitoring        ✅
    ├── Concurrent Monitoring ✅
    ├── Continuous Mode       ✅
    ├── Event Logging         ✅
    ├── JSON Reports          ✅
    └── CLI Interface         ✅
```

**Status: ✅ Completed**

---

# 🔗 Repository

Part of:

**Python Security & Software Projects — Phase 2**

GitHub:

`https://github.com/AvinashSecDev/Python-Security-Software-Projects`

Project directory:

```text
03_network_monitor/
```

---

# 👨‍💻 Author

**AvinashSecDev**

Cybersecurity • Python • Software Development • Web Development • Networking

---

# ⚠️ Disclaimer

This project is developed for **educational, defensive security, network administration, and authorized testing purposes**.

Only monitor systems and networks that you own or have explicit permission to monitor.

The author does not encourage unauthorized network monitoring, scanning, interception, or other activity against systems without permission.

---

# ⭐ Project Philosophy

> **Build → Monitor → Test → Analyze → Improve → Secure**

This project is part of a larger learning journey focused on building practical Python applications while developing stronger cybersecurity and software-development skills.
