from flask import Flask, jsonify, render_template_string
import os
import platform
import socket
import psutil
import requests
import json
from datetime import datetime
import time

app = Flask(__name__)

# Application metadata
APP_NAME = "AWS Instance Info Dashboard"
APP_VERSION = "1.0.0"
APP_BUILD = "001"
APP_ENV = os.environ.get('APP_ENV', 'Development')
APP_STARTUP = datetime.now().isoformat()

def get_aws_metadata():
    """Fetch AWS EC2 metadata using IMDSv2"""
    metadata = {}
    base_url = "http://169.254.169.254/latest"

    try:
        # Get IMDSv2 token
        token_response = requests.put(
            f"{base_url}/api/token",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
            timeout=2
        )
        if token_response.status_code != 200:
            raise Exception("Failed to get IMDSv2 token")

        token = token_response.text

        headers = {"X-aws-ec2-metadata-token": token}

        # Fetch metadata
        metadata_endpoints = {
            'instance_id': '/meta-data/instance-id',
            'instance_type': '/meta-data/instance-type',
            'ami_id': '/meta-data/ami-id',
            'hostname': '/meta-data/hostname',
            'local_ipv4': '/meta-data/local-ipv4',
            'public_ipv4': '/meta-data/public-ipv4',
            'local_hostname': '/meta-data/local-hostname',
            'public_hostname': '/meta-data/public-hostname',
            'placement/availability-zone': '/meta-data/placement/availability-zone',
            'mac': '/meta-data/mac',
            'iam/security-credentials/': '/meta-data/iam/security-credentials/',
        }

        for key, endpoint in metadata_endpoints.items():
            try:
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=2)
                if response.status_code == 200:
                    if key == 'iam/security-credentials/':
                        # Get IAM role name
                        roles = response.text.strip().split('\n')
                        if roles and roles[0]:
                            role_name = roles[0]
                            # Get role details
                            role_response = requests.get(f"{base_url}/meta-data/iam/security-credentials/{role_name}", headers=headers, timeout=2)
                            if role_response.status_code == 200:
                                metadata['iam_role'] = role_name
                    else:
                        metadata[key.replace('/', '_')] = response.text.strip()
            except:
                metadata[key.replace('/', '_')] = "N/A"

        # Get VPC info from network interfaces
        try:
            mac = metadata.get('mac', '')
            if mac and mac != "N/A":
                vpc_response = requests.get(f"{base_url}/meta-data/network/interfaces/macs/{mac}/vpc-id", headers=headers, timeout=2)
                if vpc_response.status_code == 200:
                    metadata['vpc_id'] = vpc_response.text.strip()

                subnet_response = requests.get(f"{base_url}/meta-data/network/interfaces/macs/{mac}/subnet-id", headers=headers, timeout=2)
                if subnet_response.status_code == 200:
                    metadata['subnet_id'] = subnet_response.text.strip()

                sg_response = requests.get(f"{base_url}/meta-data/network/interfaces/macs/{mac}/security-groups", headers=headers, timeout=2)
                if sg_response.status_code == 200:
                    metadata['security_groups'] = sg_response.text.strip().replace('\n', ', ')
        except:
            pass

        # Get instance state and launch time (requires AWS API)
        metadata['instance_state'] = "N/A - Requires AWS API"
        metadata['launch_time'] = "N/A - Requires AWS API"
        metadata['account_id'] = "N/A - Requires AWS API"
        metadata['region'] = metadata.get('placement_availability_zone', 'N/A')[:-1] if metadata.get('placement_availability_zone', 'N/A') != 'N/A' else 'N/A'

    except Exception as e:
        # Return N/A for all AWS metadata if not available
        return {
            'instance_id': 'N/A',
            'instance_type': 'N/A',
            'ami_id': 'N/A',
            'hostname': 'N/A',
            'local_ipv4': 'N/A',
            'public_ipv4': 'N/A',
            'local_hostname': 'N/A',
            'public_hostname': 'N/A',
            'placement_availability_zone': 'N/A',
            'vpc_id': 'N/A',
            'subnet_id': 'N/A',
            'security_groups': 'N/A',
            'iam_role': 'N/A',
            'instance_state': 'N/A',
            'launch_time': 'N/A',
            'account_id': 'N/A',
            'region': 'N/A'
        }

    return metadata

def get_system_info():
    """Get system and runtime information"""
    info = {}

    # Container/Host info
    info['container_hostname'] = socket.gethostname()
    info['container_id'] = os.environ.get('HOSTNAME', 'N/A')

    # Process info
    info['process_id'] = os.getpid()

    # Runtime info
    info['python_version'] = platform.python_version()
    info['cpu_cores'] = os.cpu_count()

    # Memory info
    mem = psutil.virtual_memory()
    info['total_memory'] = f"{mem.total / (1024**3):.2f} GB"
    info['available_memory'] = f"{mem.available / (1024**3):.2f} GB"

    # OS info
    info['os'] = f"{platform.system()} {platform.release()}"
    info['architecture'] = platform.machine()

    # Current time
    info['current_time'] = datetime.now().isoformat()

    return info

@app.route('/')
def dashboard():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>AWS Instance Info Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #232f3e; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .section { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .section h2 { color: #232f3e; border-bottom: 2px solid #ff9900; padding-bottom: 10px; }
        .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }
        .info-item { padding: 10px; background: #f9f9f9; border-radius: 4px; }
        .info-item strong { color: #232f3e; display: block; margin-bottom: 5px; }
        .info-item span { color: #666; }
        .refresh-btn { background: #ff9900; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-size: 16px; }
        .refresh-btn:hover { background: #ec8c00; }
        .status-up { color: #28a745; }
        .na-value { color: #999; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AWS Instance Information Dashboard</h1>
            <p>Application: {{ app_name }} | Version: {{ app_version }} | Environment: {{ app_env }}</p>
        </div>

        <div class="section">
            <h2>AWS / EC2 Information</h2>
            <div class="info-grid">
                <div class="info-item"><strong>Account ID</strong><span>{{ aws.account_id }}</span></div>
                <div class="info-item"><strong>Region</strong><span>{{ aws.region }}</span></div>
                <div class="info-item"><strong>Availability Zone</strong><span>{{ aws.placement_availability_zone }}</span></div>
                <div class="info-item"><strong>Instance ID</strong><span>{{ aws.instance_id }}</span></div>
                <div class="info-item"><strong>Instance Type</strong><span>{{ aws.instance_type }}</span></div>
                <div class="info-item"><strong>AMI ID</strong><span>{{ aws.ami_id }}</span></div>
                <div class="info-item"><strong>Instance Hostname</strong><span>{{ aws.hostname }}</span></div>
                <div class="info-item"><strong>Private IP</strong><span>{{ aws.local_ipv4 }}</span></div>
                <div class="info-item"><strong>Public IP</strong><span>{{ aws.public_ipv4 }}</span></div>
                <div class="info-item"><strong>Private DNS</strong><span>{{ aws.local_hostname }}</span></div>
                <div class="info-item"><strong>Public DNS</strong><span>{{ aws.public_hostname }}</span></div>
                <div class="info-item"><strong>Subnet ID</strong><span>{{ aws.subnet_id }}</span></div>
                <div class="info-item"><strong>VPC ID</strong><span>{{ aws.vpc_id }}</span></div>
                <div class="info-item"><strong>Security Groups</strong><span>{{ aws.security_groups }}</span></div>
                <div class="info-item"><strong>IAM Role</strong><span>{{ aws.iam_role }}</span></div>
                <div class="info-item"><strong>Launch Time</strong><span>{{ aws.launch_time }}</span></div>
                <div class="info-item"><strong>Instance State</strong><span>{{ aws.instance_state }}</span></div>
            </div>
        </div>

        <div class="section">
            <h2>Application Information</h2>
            <div class="info-grid">
                <div class="info-item"><strong>Application Name</strong><span>{{ app_name }}</span></div>
                <div class="info-item"><strong>Version</strong><span>{{ app_version }} (Build: {{ app_build }})</span></div>
                <div class="info-item"><strong>Environment</strong><span>{{ app_env }}</span></div>
                <div class="info-item"><strong>Hostname</strong><span>{{ system.container_hostname }}</span></div>
                <div class="info-item"><strong>Startup Time</strong><span>{{ app_startup }}</span></div>
                <div class="info-item"><strong>Current Server Time</strong><span>{{ system.current_time }}</span></div>
                <div class="info-item"><strong>Operating System</strong><span>{{ system.os }} ({{ system.architecture }})</span></div>
                <div class="info-item"><strong>CPU Information</strong><span>{{ system.cpu_cores }} cores</span></div>
                <div class="info-item"><strong>Memory</strong><span>{{ system.total_memory }} total, {{ system.available_memory }} available</span></div>
            </div>
        </div>

        <div class="section">
            <h2>Runtime Information</h2>
            <div class="info-grid">
                <div class="info-item"><strong>Container Hostname</strong><span>{{ system.container_hostname }}</span></div>
                <div class="info-item"><strong>Container ID</strong><span>{{ system.container_id }}</span></div>
                <div class="info-item"><strong>Process ID</strong><span>{{ system.process_id }}</span></div>
                <div class="info-item"><strong>Runtime/Language</strong><span>Python {{ system.python_version }}</span></div>
                <div class="info-item"><strong>CPU Cores</strong><span>{{ system.cpu_cores }}</span></div>
                <div class="info-item"><strong>Available Memory</strong><span>{{ system.available_memory }}</span></div>
            </div>
        </div>

        <button class="refresh-btn" onclick="location.reload()">Refresh Information</button>
    </div>
</body>
</html>
    ''',
    app_name=APP_NAME,
    app_version=APP_VERSION,
    app_build=APP_BUILD,
    app_env=APP_ENV,
    app_startup=APP_STARTUP,
    aws=get_aws_metadata(),
    system=get_system_info()
    )

@app.route('/health')
def health():
    return jsonify({"status": "UP"})

@app.route('/api/info')
def api_info():
    return jsonify({
        "application": {
            "name": APP_NAME,
            "version": APP_VERSION,
            "build": APP_BUILD,
            "environment": APP_ENV,
            "hostname": socket.gethostname(),
            "startup_time": APP_STARTUP
        },
        "system": get_system_info()
    })

@app.route('/api/aws')
def api_aws():
    return jsonify(get_aws_metadata())

@app.route('/api/system')
def api_system():
    return jsonify(get_system_info())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)