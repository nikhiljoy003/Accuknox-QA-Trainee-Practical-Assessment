import re
import sys
from collections import defaultdict
from datetime import datetime
from operator import itemgetter
from io import StringIO

# Sample log data for environments where file access might be restricted
SAMPLE_LOG_DATA = """
127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326 "http://www.example.com/start.html" "Mozilla/4.08 [en] (Win98; I ;Nav)"
127.0.0.2 - john [10/Oct/2000:13:56:36 -0700] "GET /missing.html HTTP/1.0" 404 721 "-" "Mozilla/4.08 [en] (Win98; I ;Nav)"
"""

def parse_log_line(line, log_format):
    if log_format == 'apache':
        pattern = r'^(\S+) (\S+) (\S+) \[([^\]]+)\] "(\S+) (\S+) (\S+)" (\d+) (\d+) "([^"]*)" "([^"]*)"'
    elif log_format == 'nginx':
        pattern = r'^(\S+) - (\S+) \[([^\]]+)\] "(\S+) (\S+) (\S+)" (\d+) (\d+) "([^"]*)" "([^"]*)"'
    else:
        return None

    match = re.match(pattern, line)
    if match:
        return {
            'ip': match.group(1),
            'date': match.group(4),
            'method': match.group(5),
            'url': match.group(6),
            'protocol': match.group(7),
            'status': int(match.group(8)),
            'size': int(match.group(9)),
            'referer': match.group(10),
            'user_agent': match.group(11)
        }
    return None

def analyze_logs(log_stream, log_format='apache'):
    total_requests = 0
    status_codes = defaultdict(int)
    ip_addresses = defaultdict(int)
    requested_urls = defaultdict(int)
    not_found_urls = defaultdict(int)
    user_agents = defaultdict(int)
    hourly_requests = defaultdict(int)

    for line in log_stream:
        if not line.strip():
            continue

        entry = parse_log_line(line, log_format)
        if not entry:
            continue

        total_requests += 1
        status_codes[entry['status']] += 1
        ip_addresses[entry['ip']] += 1
        requested_urls[entry['url']] += 1

        if entry['status'] == 404:
            not_found_urls[entry['url']] += 1

        user_agents[entry['user_agent']] += 1

        try:
            dt = datetime.strptime(entry['date'], '%d/%b/%Y:%H:%M:%S %z')
            hourly_requests[dt.hour] += 1
        except ValueError:
            pass

    return {
        'total_requests': total_requests,
        'status_codes': dict(status_codes),
        'ip_addresses': dict(ip_addresses),
        'requested_urls': dict(requested_urls),
        'not_found_urls': dict(not_found_urls),
        'user_agents': dict(user_agents),
        'hourly_requests': dict(hourly_requests)
    }

def generate_report(stats, top_n=5):
    report = []
    report.append("=" * 60)
    report.append("WEB SERVER LOG ANALYSIS REPORT")
    report.append("=" * 60)
    report.append(f"\nTotal Requests: {stats['total_requests']:,}")

    report.append("\nHTTP Status Codes:")
    for code, count in sorted(stats['status_codes'].items()):
        report.append(f"  {code}: {count:,} ({count/stats['total_requests']:.1%})")

    report.append(f"\nTop {top_n} IP Addresses:")
    for ip, count in sorted(stats['ip_addresses'].items(), key=itemgetter(1), reverse=True)[:top_n]:
        report.append(f"  {ip}: {count:,} requests")

    report.append(f"\nTop {top_n} Requested URLs:")
    for url, count in sorted(stats['requested_urls'].items(), key=itemgetter(1), reverse=True)[:top_n]:
        report.append(f"  {url}: {count:,} requests")

    report.append(f"\nTop {top_n} Not Found URLs (404):")
    if stats['not_found_urls']:
        for url, count in sorted(stats['not_found_urls'].items(), key=itemgetter(1), reverse=True)[:top_n]:
            report.append(f"  {url}: {count:,} errors")
    else:
        report.append("  No 404 errors found")

    report.append("\nRequests by Hour:")
    for hour in sorted(stats['hourly_requests'].keys()):
        report.append(f"  {hour:02}:00 - {hour:02}:59: {stats['hourly_requests'][hour]:,} requests")

    report.append(f"\nTop {top_n} User Agents:")
    for agent, count in sorted(stats['user_agents'].items(), key=itemgetter(1), reverse=True)[:top_n]:
        report.append(f"  {agent}: {count:,} requests")

    return "\n".join(report)

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        log_file = sys.argv[1]
        log_format = sys.argv[2].lower() if len(sys.argv) > 2 else 'apache'

        if log_format not in ['apache', 'nginx']:
            print("Error: Invalid log format. Use 'apache' or 'nginx'")
            sys.exit(1)

        try:
            with open(log_file, 'r') as f:
                stats = analyze_logs(f, log_format)
        except FileNotFoundError:
            print(f"Error: File '{log_file}' not found.")
            sys.exit(1)
    else:
        print("No log file provided. Using sample data.")
        stats = analyze_logs(StringIO(SAMPLE_LOG_DATA), 'apache')

    report = generate_report(stats)
    print(report)

    with open('log_analysis_report.txt', 'w') as f:
        f.write(report)
    print("\nReport saved to 'log_analysis_report.txt'")
