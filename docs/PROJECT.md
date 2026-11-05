# CampusOps: A Cloud-Native Incident Management and Automated Response Platform

## 1. Project Overview

CampusOps is a cloud-based incident management platform designed to simplify the reporting, tracking, assignment, and resolution of maintenance issues within a university campus.

In colleges and universities, problems such as Wi-Fi failures, electrical issues, damaged classroom equipment, plumbing problems, and laboratory maintenance are often reported through informal communication channels such as phone calls, WhatsApp messages, or direct communication with faculty.

These methods make it difficult to track complaints, assign responsibilities, monitor resolution times, and ensure that reported issues are addressed promptly.

CampusOps addresses these challenges by providing a centralized web-based platform where students can report incidents, maintenance staff can manage assigned tasks, and administrators can monitor all campus-related incidents.

The platform uses AWS cloud services for application hosting, backend processing, database management, authentication, monitoring, and automated notifications. DevOps tools are integrated to automate application testing, deployment, infrastructure provisioning, and monitoring.

## 2. Problem Statement

Traditional campus maintenance management systems often have the following limitations:

1. No centralized platform for reporting and managing incidents.
2. Difficulty tracking the status of reported complaints.
3. Lack of proper incident assignment and responsibility tracking.
4. Delays in identifying and resolving high-priority issues.
5. No automated mechanism for monitoring overdue complaints.
6. Limited visibility into overall maintenance performance.
7. Manual application deployment and infrastructure management.

Therefore, there is a need for a centralized, cloud-native platform that improves incident management through automation, scalability, and continuous monitoring.

## 3. Proposed Solution

CampusOps provides a centralized incident management system built using AWS cloud infrastructure.

The platform supports three major user roles:

Student

- Submit campus-related incidents.
- Select incident category and priority.
- Provide incident location and description.
- Track submitted incident status.

Maintenance Staff

- View assigned incidents.
- Update incident progress.
- Add resolution details.
- Mark incidents as resolved.

Administrator

- View all reported incidents.
- Assign incidents to maintenance staff.
- Monitor incident priorities and statuses.
- Track overdue incidents.
- View incident statistics and reports.

The platform also incorporates Service Level Agreement (SLA) monitoring to identify incidents that exceed their expected resolution time and trigger automated notifications.

## 4. Technologies Used

### Frontend Technologies

| Technology      | Purpose                        |
| --------------- | ------------------------------ |
| React.js        | Building the user interface    |
| Vite            | Frontend development and build |
| JavaScript      | Application functionality      |
| CSS / Bootstrap | Responsive user interface      |

### Backend Technologies

| Technology  | Purpose                      |
| ----------- | ---------------------------- |
| Python      | Backend programming          |
| AWS Lambda  | Serverless backend execution |
| Boto3       | Python integration with AWS  |
| API Gateway | Backend API management       |

### AWS Cloud Services

| AWS Service        | Purpose                            |
| ------------------ | ---------------------------------- |
| Amazon S3          | Frontend hosting and file storage  |
| AWS Lambda         | Backend application processing     |
| Amazon API Gateway | Connecting frontend and backend    |
| Amazon DynamoDB    | Storing incident information       |
| Amazon Cognito     | User authentication                |
| Amazon CloudWatch  | Application monitoring and logging |
| Amazon EventBridge | Scheduled SLA monitoring           |
| Amazon SNS         | Automated notifications            |

### DevOps Tools

| Tool           | Purpose                |
| -------------- | ---------------------- |
| Git            | Version control        |
| GitHub         | Source code management |
| GitHub Actions | CI/CD automation       |
| Terraform      | Infrastructure as Code |
| SonarQube      | Code quality analysis  |
| Prometheus     | Metrics collection     |
| Grafana        | Monitoring dashboards  |

## 5. System Architecture

The CampusOps architecture follows a serverless cloud computing approach.

The React frontend is hosted using Amazon S3. Users interact with the application through a web browser. API Gateway receives frontend requests and routes them to the appropriate AWS Lambda functions.

Lambda functions perform backend operations such as creating incidents, retrieving incident records, assigning maintenance staff, and updating incident statuses.

Amazon DynamoDB stores the incident information.

Amazon Cognito manages authentication and user identities.

Amazon CloudWatch collects application logs and monitoring information.

Amazon EventBridge periodically triggers an SLA monitoring Lambda function. This function checks for overdue incidents in DynamoDB. When an incident exceeds its defined resolution deadline, Amazon SNS can send notifications to the administrator or responsible maintenance team.

## 6. Three Core Modules

### Module 1: AWS Cloud Infrastructure and Application Development

Objective: Design and implement the core CampusOps application using AWS cloud services.

Activities:

- Develop the React frontend.
- Implement Python Lambda backend functions.
- Configure API Gateway endpoints.
- Create DynamoDB tables for incident storage.
- Configure Amazon S3 for frontend hosting.
- Implement user authentication using Cognito.
- Configure basic CloudWatch logging.

Expected outcome:

A functional incident management application deployed on AWS, allowing students to report incidents and administrators to manage them.

### Module 2: DevOps Automation and CI/CD Pipeline

Objective: Automate application development, testing, code quality analysis, and deployment.

Activities:

- Maintain application source code using Git and GitHub.
- Configure GitHub Actions workflows.
- Automate application build and testing.
- Integrate SonarQube for code quality analysis.
- Use Terraform to define AWS infrastructure.
- Automate deployment through CI/CD pipelines.

Expected outcome:

An automated development and deployment pipeline that reduces manual intervention, improves code quality, and ensures consistent application releases.

### Module 3: Cloud Monitoring, SLA Management and Automated Response

Objective: Monitor application performance and automate responses to overdue incidents.

Activities:

- Configure CloudWatch monitoring and logging.
- Implement SLA rules based on incident priority.
- Use EventBridge for scheduled incident checks.
- Develop Lambda functions for identifying overdue incidents.
- Integrate SNS for automated notifications.
- Use Prometheus and Grafana for additional monitoring dashboards, if required.

Expected outcome:

A monitoring and automated response system that identifies overdue incidents, triggers alerts, and improves campus maintenance management.

## 7. SLA Management

Service Level Agreement (SLA) management defines the expected time within which an incident should be addressed or resolved.

CampusOps can use configurable resolution targets based on incident priority.

| Priority | Example resolution target |
| -------- | ------------------------- |
| Critical | 1 hour                    |
| High     | 4 hours                   |
| Medium   | 12 hours                  |
| Low      | 24 hours                  |

These are proposed project-level targets.

For example, if a student reports a high-priority electrical issue at 10 AM, the system assigns a proposed resolution deadline of 2 PM.

If the issue remains unresolved after the deadline:

1. EventBridge triggers the SLA monitoring process.
2. Lambda checks the incident's deadline and status.
3. The system identifies the overdue incident.
4. SNS sends an alert to the administrator.
5. The administrator can escalate the issue to the responsible maintenance team.

This feature reduces manual monitoring and improves incident response efficiency.

## 8. CI/CD Pipeline

CampusOps uses a Continuous Integration and Continuous Deployment pipeline to automate software development and deployment.

The proposed workflow is:

1. Developer writes or modifies application code.
2. Code is pushed to GitHub.
3. GitHub Actions triggers the CI/CD workflow.
4. Automated tests are executed.
5. SonarQube performs code quality analysis.
6. Terraform manages infrastructure definitions.
7. Approved deployment workflows publish the updated frontend and backend components to AWS.

This approach reduces deployment errors and improves software delivery consistency.

## 9. Expected Outcomes

The proposed CampusOps platform is expected to provide:

- Centralized campus incident management.
- Faster reporting and tracking of maintenance issues.
- Improved incident assignment and accountability.
- Priority-based incident management.
- Automated SLA monitoring.
- Notifications for overdue incidents.
- Cloud-based application availability.
- Automated application testing and deployment.
- Improved operational visibility through monitoring.
- Reduced manual intervention in campus maintenance workflows.

## 10. Advantages

1. Centralization: All campus incidents are managed through one platform.
2. Scalability: AWS serverless services can scale with application demand.
3. Automation: CI/CD and scheduled workflows reduce manual effort.
4. Monitoring: CloudWatch provides visibility into application execution.
5. Accountability: Incident assignment and status tracking improve responsibility management.
6. Cost optimization: Serverless architecture avoids maintaining continuously running application servers, although AWS usage can still incur charges.
7. Reliability: Managed AWS services reduce infrastructure maintenance requirements.

## 11. Conclusion

CampusOps is a cloud-native incident management and automated response platform designed to improve campus maintenance operations. By integrating AWS cloud services with DevOps practices, the system provides centralized incident reporting, tracking, assignment, and resolution.

The implementation is divided into three modules covering AWS cloud infrastructure, DevOps automation, and cloud monitoring with SLA-based automated response.

The proposed solution demonstrates how serverless computing, Infrastructure as Code, CI/CD pipelines, and automated monitoring can be combined to develop a scalable and efficient campus operations management platform.

## Project summary at a glance

| Particular                | Details                                              |
| ------------------------- | ---------------------------------------------------- |
| Project name              | CampusOps                                            |
| Project type              | Cloud Computing and DevOps                           |
| Architecture              | Serverless                                           |
| Frontend                  | React + Vite                                         |
| Backend                   | Python + AWS Lambda                                  |
| Database                  | DynamoDB                                             |
| Cloud platform            | AWS                                                  |
| Infrastructure automation | Terraform                                            |
| CI/CD                     | GitHub Actions                                       |
| Monitoring                | CloudWatch, Prometheus, Grafana                      |
| Main feature              | Incident management and SLA-based automated response |
| Development environment   | VS Code + WSL                                        |
| AWS region                | ap-south-1 (Mumbai)                                  |
| Budget                    | AWS Free Tier eligible usage only                    |

In one sentence: CampusOps is a centralized, AWS-powered campus maintenance platform that combines incident management, DevOps automation, cloud monitoring, and SLA-based automated response.