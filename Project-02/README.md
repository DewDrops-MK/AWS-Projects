# Project-02: Two-Tier Employee Profile Application

## Project Overview

A simple two-tier web application for managing employee profiles. The application demonstrates a traditional two-tier architecture with a web/application tier and a database tier.

## Application Architecture

- **Frontend**: HTML/CSS/JavaScript single-page application
- **Backend**: Node.js with Express.js
- **Database**: PostgreSQL
- **Communication**: RESTful API over HTTP

## Two-Tier Architecture

### Tier 1 - Application/Web Tier
- Runs on AWS EC2 instance
- Serves web UI and REST APIs
- Handles business logic and database connectivity
- Communicates with database over private network

### Tier 2 - Database Tier
- PostgreSQL database in private subnet
- Stores all employee information
- Not accessible from the internet

## Prerequisites

- Node.js (v18 or higher)
- PostgreSQL (v14 or higher)
- npm

## Local Database Setup

1. Install PostgreSQL and create a database:
```bash
createdb employee_db
```

2. Run the initialization script:
```bash
psql -d employee_db -f init.sql
```

## Local Application Setup

1. Install dependencies:
```bash
npm install
```

2. Copy environment configuration:
```bash
cp .env.example .env
```

3. Edit `.env` with your database credentials:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=employee_db
DB_USER=your_username
DB_PASSWORD=your_password
APP_PORT=3000
APP_ENV=development
```

4. Start the application:
```bash
npm start
```

5. Access the application at `http://localhost:3000`

## Configuration

All database and application settings use environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| DB_HOST | Database host | - |
| DB_PORT | Database port | 5432 |
| DB_NAME | Database name | - |
| DB_USER | Database username | - |
| DB_PASSWORD | Database password | - |
| APP_PORT | Application port | 3000 |
| APP_ENV | Environment | development |

## Database Schema

### employees table

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| first_name | VARCHAR(100) | Employee first name |
| last_name | VARCHAR(100) | Employee last name |
| email | VARCHAR(255) | Unique email address |
| phone | VARCHAR(20) | Phone number |
| job_title | VARCHAR(100) | Job position |
| department | VARCHAR(100) | Department name |
| location | VARCHAR(100) | Work location |
| joining_date | DATE | Date of joining |
| created_at | TIMESTAMP | Record creation time |
| updated_at | TIMESTAMP | Last update time |

## API Documentation

### Health Endpoints

#### GET /health
Returns application health status.

Response:
```json
{
  "status": "UP"
}
```

#### GET /health/db
Returns application and database health status.

Response:
```json
{
  "application": "UP",
  "database": "UP"
}
```

### Employee Endpoints

#### GET /api/employees
Returns all employees.

#### GET /api/employees/{id}
Returns a specific employee by ID.

#### GET /api/employees/search?name={name}
Searches employees by first or last name.

#### POST /api/employees
Creates a new employee.

Request body:
```json
{
  "firstName": "Manjunath",
  "lastName": "K",
  "email": "manjunath@example.com",
  "phone": "9876543210",
  "jobTitle": "DevOps Engineer",
  "department": "Engineering",
  "location": "Bangalore",
  "joiningDate": "2026-08-09"
}
```

#### PUT /api/employees/{id}
Updates an existing employee.

#### DELETE /api/employees/{id}
Deletes an employee.

## Sample API Requests

### Create Employee
```bash
curl -X POST http://localhost:3000/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "jobTitle": "Developer",
    "department": "Engineering"
  }'
```

### Get All Employees
```bash
curl http://localhost:3000/api/employees
```

### Search Employees
```bash
curl "http://localhost:3000/api/employees/search?name=John"
```

## AWS Deployment Architecture

```
                         AWS Region
                             |
                             v
                           VPC
                             |
                    +--------+--------+
                    |                 |
              Public Subnet      Private Subnet
                    |                 |
                    |                 |
             +-------------+    +-------------+
Internet --->|     EC2     |--->|  Database   |
             | Web / App   |    | PostgreSQL  |
             +-------------+    +-------------+
                    ^
                    |
              Internet Gateway
```

### Security Groups

#### EC2 Security Group
- Allow HTTP (port 80/3000) from 0.0.0.0/0
- Allow SSH (port 22) from trusted IP only
- Allow outbound traffic to database security group

#### Database Security Group
- Allow PostgreSQL (port 5432) from EC2 security group only
- No inbound from 0.0.0.0/0

### Required AWS Resources

- 1 VPC with public and private subnets
- 1 Internet Gateway
- 1 EC2 instance (t2.micro or larger)
- 1 PostgreSQL database (self-managed on EC2 or RDS)
- 2 Security Groups (EC2 and Database)

### Database Connection

The application connects to the database using:
- Private IP address when both tiers are in the same VPC
- Security group rules control access
- No public internet access to database

## Troubleshooting

### Database Connection Issues
- Verify database credentials in .env file
- Ensure PostgreSQL is running
- Check database host is reachable from application server
- Verify security group allows database port access

### Application Won't Start
- Check if port 3000 is already in use
- Verify all environment variables are set
- Check Node.js version compatibility

### API Returns Errors
- Check application logs for detailed error messages
- Verify database tables exist (run init.sql)
- Ensure required fields are provided in requests

### Health Check Shows Database DOWN
- Confirm database server is running
- Verify connection parameters
- Check network connectivity between application and database
- Review security group rules for database access