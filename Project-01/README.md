# AWS Instance Info Dashboard

A lightweight web application for displaying AWS EC2 instance and application information.

## Features

- Displays AWS/EC2 metadata using IMDSv2
- Shows application and runtime information
- REST API endpoints for programmatic access
- Works locally without AWS (returns N/A for AWS fields)
- Container-ready with Docker support

## API Endpoints

- `GET /health` - Health check endpoint
- `GET /api/info` - Combined application and system info
- `GET /api/aws` - AWS/EC2 instance metadata
- `GET /api/system` - System and runtime information

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

Access the dashboard at http://localhost:8080

## Docker Deployment

```bash
docker build -t aws-instance-info .
docker run -p 8080:8080 aws-instance-info
```

## AWS Deployment

Deploy to EC2, ECS, or EKS. The application will automatically:
- Detect AWS environment using IMDSv2
- Retrieve instance metadata without requiring AWS credentials
- Use IAM instance role for any API calls if configured

When running outside AWS, all AWS-specific fields will display "N/A".