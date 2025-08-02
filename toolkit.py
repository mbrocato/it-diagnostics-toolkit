import os
import re
import json
from datetime import datetime
import logging
import subprocess
import xml.etree.ElementTree as ET
import psutil  # Assuming psutil is available; otherwise, fallback to subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def analyze_user_log(log_path):
    """Read and parse a user log file for common issues like software conflicts."""
    if not os.path.exists(log_path):
        raise FileNotFoundError(f"Log file not found: {log_path}")
    
    issues = []
    with open(log_path, 'r') as file:
        for line in file:
            if re.search(r'conflict|error|failed to load', line, re.IGNORECASE):
                issues.append({
                    'timestamp': datetime.now().isoformat(),
                    'description': line.strip(),
                    'issue_type': 'Software Conflict'
                })
    return issues

def analyze_system_logs(log_path):
    """Extract error codes and performance metrics from system logs."""
    errors = []
    with open(log_path, 'r') as file:
        for line in file:
            if 'ERROR' in line.upper():
                errors.append({
                    'error_code': line.split('ERROR')[1].strip()[:10],  # Simulated extraction
                    'description': line.strip()
                })
    return errors

def check_resource_usage():
    """Flag high resource usage using psutil or subprocess."""
    try:
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        flags = []
        if cpu_usage > 80:
            flags.append({'issue': 'High CPU usage', 'value': cpu_usage})
        if memory_usage > 80:
            flags.append({'issue': 'High Memory usage', 'value': memory_usage})
        return flags
    except ImportError:
        # Fallback to subprocess if psutil not available
        result = subprocess.run(['top', '-bn1'], capture_output=True, text=True)
        logging.info("Fallback to top command output.")
        return [{'issue': 'Resource check via top', 'output': result.stdout[:200]}]

def parse_event_logs(xml_path):
    """Parse Windows-like event logs (XML) for issues like application crashes."""
    if not os.path.exists(xml_path):
        raise FileNotFoundError(f"Event log file not found: {xml_path}")
    
    tree = ET.parse(xml_path)
    root = tree.getroot()
    anomalies = []
    for event in root.findall('.//Event'):
        desc = event.find('EventData/Data')
        if desc is not None and 'crash' in desc.text.lower():
            anomalies.append({
                'event_id': event.find('System/EventID').text,
                'description': desc.text,
                'issue_type': 'Application Crash'
            })
    return anomalies

def simulate_system_snapshot():
    """Use subprocess to extract processes and connections (simulated remote exec)."""
    try:
        processes = subprocess.run(['ps', 'aux'], capture_output=True, text=True).stdout
        connections = subprocess.run(['netstat', '-an'], capture_output=True, text=True).stdout
        return {
            'processes': processes[:500],  # Truncated for brevity
            'connections': connections[:500]
        }
    except FileNotFoundError:
        return {'error': 'Commands not available on this system.'}

def generate_support_report(issues, errors, flags, anomalies, snapshot, json_output='support_report.json', md_output='support_report.md'):
    """Generate combined JSON and Markdown reports for remote support."""
    # JSON Report
    report = {
        'summary': f"Found {len(issues)} user issues, {len(errors)} system errors, {len(flags)} resource flags, {len(anomalies)} anomalies.",
        'user_issues': issues,
        'system_errors': errors,
        'resource_flags': flags,
        'anomalies': anomalies,
        'system_snapshot': snapshot,
        'timestamp': datetime.now().isoformat(),
        'recommendations': ['Update conflicting software', 'Run compatibility checks', 'Investigate high resource usage']
    }
    with open(json_output, 'w') as file:
        json.dump(report, file, indent=4)
    logging.info(f"JSON report generated at {json_output}")

    # Markdown Report
    with open(md_output, 'w') as file:
        file.write('# Remote IT Support Report\n\n')
        file.write(f'## Timestamp: {datetime.now().isoformat()}\n\n')
        file.write('## User Issues\n')
        for issue in issues:
            file.write(f"- **Type:** {issue['issue_type']} - {issue['description']}\n")
        file.write('\n## System Errors\n')
        for error in errors:
            file.write(f"- **Code:** {error['error_code']} - {error['description']}\n")
        file.write('\n## Resource Flags\n')
        for flag in flags:
            file.write(f"- **Issue:** {flag['issue']} - Value: {flag.get('value', 'N/A')}\n")
        file.write('\n## Detected Anomalies\n')
        for anomaly in anomalies:
            file.write(f"- **Event ID:** {anomaly['event_id']} - {anomaly['description']}\n")
        file.write('\n## System Snapshot\n')
        file.write('### Processes\n```\n' + snapshot.get('processes', '') + '\n```\n')
        file.write('### Connections\n```\n' + snapshot.get('connections', '') + '\n```\n')
    logging.info(f"Markdown report generated at {md_output}")

# Example usage
if __name__ == "__main__":
    user_log_path = 'user_log.txt'  # Replace with actual user log path
    system_log_path = 'system_log.txt'  # Replace with actual system log path
    event_xml_path = 'event_log.xml'  # Replace with actual XML event log path
    
    user_issues = analyze_user_log(user_log_path)
    system_errors = analyze_system_logs(system_log_path)
    resource_flags = check_resource_usage()
    event_anomalies = parse_event_logs(event_xml_path)
    system_snapshot = simulate_system_snapshot()
    
    generate_support_report(user_issues, system_errors, resource_flags, event_anomalies, system_snapshot)
