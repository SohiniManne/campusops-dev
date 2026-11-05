# 🎓 CampusOps Viva Defense & Technical Interview Guide

> **Project Name**: CampusOps — Cloud-Native University Incident Management & SLA Automation Platform  
> **Tech Stack**: React 18 + Vite, Python 3.12 AWS Lambda, Amazon DynamoDB, Amazon Cognito, Amazon API Gateway, Amazon EventBridge, Amazon SNS, Terraform, GitHub Actions  
> **Target Region**: `ap-south-1` (Mumbai) • **100% AWS Free Tier Compliant**

---

## 1. 30-Second Elevator Pitch (Memorize This!)

> *"Good morning/afternoon, professors. My project is **CampusOps**, a cloud-native incident management platform built for universities.  
> Currently, college maintenance requests—like faulty lab equipment, electrical faults, or broken classroom benches—are reported through informal phone calls, paper slips, or WhatsApp messages, leading to lost complaints and zero accountability.  
>  
> CampusOps solves this with a **100% serverless, event-driven cloud architecture on AWS**. Students report incidents categorized by priority; technicians receive work orders on their dashboard; and administrators monitor real-time department metrics.  
> Crucially, it features **automated SLA enforcement**: an Amazon EventBridge scheduler triggers an AWS Lambda function every 10 minutes to scan for overdue tickets and instantly dispatches escalation emails to administrators via Amazon SNS before deadlines are missed.  
>  
> The entire infrastructure is automated using **Terraform (85 resources)**, tested with **32 unit tests**, governed by **GitHub Actions CI/CD**, and architected to cost **\$0.00 on the AWS Free Tier**."*

---

## 2. Every AWS Resource Explained in One Simple Line

If an examiner points to any AWS service on your architecture diagram and asks, *"What does this do?"*, give them this exact one-line answer:

| AWS Service | What It Does In CampusOps (One Line) |
| :--- | :--- |
| **Amazon S3** | Hosts the compiled React single-page frontend as static files (HTML/CSS/JS) with zero idle web server cost. |
| **Amazon Cognito** | Authenticates users and issues secure JSON Web Tokens (JWT) containing user groups (`Student`, `Staff`, `Admin`). |
| **Amazon API Gateway** | Acts as the secure front door that validates Cognito JWT tokens and routes HTTPS REST requests to backend Lambdas. |
| **AWS Lambda** | Runs our Python 3.12 backend business logic microservices on demand without provisioning or managing virtual machines. |
| **Amazon DynamoDB** | Stores all incident data in a fast, fully managed NoSQL table with single-digit millisecond read/write latency. |
| **DynamoDB GSIs** | Global Secondary Indexes that allow querying tickets by Student, by Assigned Staff, or by Status without expensive table scans. |
| **Amazon EventBridge** | Acts as a serverless cron job that automatically triggers our SLA monitoring Lambda function every 10 minutes. |
| **Amazon SNS** | Publishes urgent email notifications to administrators when an incident breaches its resolution deadline. |
| **Amazon CloudWatch** | Collects execution logs, triggers alarms on Lambda/API errors, and visualizes system health on a centralized dashboard. |
| **AWS Budgets** | Monitors cloud spending and sends an immediate email alert if monthly costs are forecasted to exceed \$1.00 USD. |
| **AWS IAM** | Enforces the principle of least privilege by giving Lambda execution roles only the exact permissions they need to run. |

---

## 3. Key Design Decisions & "Why Not X?"

Examiners love asking why you picked one technology over another. Here are your bulletproof justifications:

### Q1: Why Serverless (Lambda + DynamoDB) instead of a traditional EC2 + MySQL/PostgreSQL server?
- **Cost**: A traditional EC2 instance (`t3.medium`) or RDS database runs 24/7 and costs \$15–\$30/month even at 2 AM when no students are reporting incidents. Serverless scales to **zero**—when there is no traffic, the compute cost is literally **\$0.00**.
- **Maintenance**: With EC2, we must patch the operating system, configure auto-scaling groups, and manage load balancers. With Lambda, AWS handles server maintenance, OS updates, and horizontal scaling automatically.
- **Availability**: Serverless components in AWS are natively multi-AZ (deployed across multiple availability zones in Mumbai) without extra configuration.

### Q2: Why DynamoDB NoSQL instead of a Relational Database (SQL)?
- **Predictable Performance**: DynamoDB provides single-digit millisecond latency regardless of whether there are 100 or 1,000,000 tickets.
- **Pay-Per-Request Billing**: DynamoDB On-Demand capacity charges only for the exact read/write requests made, fitting perfectly within the AWS Free Tier (25 GB free forever).
- **Flexible Schema**: If future requirements add image URLs or audio notes to an incident, DynamoDB items can adapt without requiring complex database schema migration scripts (`ALTER TABLE`).

### Q3: Why DynamoDB Single-Table Design with GSIs instead of multiple tables?
- **Access Pattern Optimization**: In relational databases, you design tables around entities. In DynamoDB, you design tables around **access patterns**.
- We use 1 table (`campusops-incidents-dev`) and 3 Global Secondary Indexes (GSIs):
  1. `CreatedByGSI` (`PK: created_by`, `SK: created_at`): Allows a student to instantly view all their past tickets sorted chronologically.
  2. `AssignedToGSI` (`PK: assigned_to`, `SK: created_at`): Allows a technician to see only tickets assigned to them.
  3. `StatusGSI` (`PK: status`, `SK: sla_deadline`): Allows the SLA cron job to query only `OPEN` or `IN_PROGRESS` tickets with `sla_deadline < now` using a fast range query.
- **Eliminates `Scan()`**: A `Scan()` operation reads the entire database table, consuming massive read capacity and running slowly. Our GSIs ensure 100% of queries use efficient `Query()` operations.

### Q4: What is a DynamoDB "Sparse Index" and why did we use it?
- When a student creates a ticket, it is unassigned, so `assigned_to` does not exist on the item.
- DynamoDB only populates an item into a Global Secondary Index if the item actually contains the partition key for that index.
- Because newly created tickets omit `assigned_to`, they **do not consume storage or index write capacity** in `AssignedToGSI` until an administrator actually assigns a staff member. This is called a **Sparse Index**.

### Q5: Why is CloudWatch Log Group retention capped at 14 days?
- By default, AWS CloudWatch retains logs **forever** (Never Expire). Over months, log data accumulates and breaches the 5 GB Free Tier limit, resulting in unexpected storage charges.
- In our Terraform code (`cloudwatch.tf`), we explicitly set `retention_in_days = 14`. This ensures old logs are automatically pruned, keeping our project 100% Free Tier compliant forever.

### Q6: Why run Prometheus & Grafana locally in Docker Compose instead of deploying them to AWS?
- Hosting Prometheus and Grafana on AWS requires running an EC2 instance or an ECS container cluster 24/7, which incurs compute, storage, and networking charges exceeding the Free Tier.
- By providing a local `docker-compose.yml`, we demonstrate full modern DevOps observability skills (metrics scraping, promql, dashboarding) without spending a single rupee on AWS.

---

## 4. Priority-Based SLA Logic Explained

The examiner will likely ask how you calculate and enforce SLAs:

### The SLA Matrix
| Priority Level | Resolution Target | Example Campus Incident |
| :--- | :---: | :--- |
| **Critical** | **1 Hour** | Power outage in server room, major water pipeline burst, fire alarm malfunction. |
| **High** | **4 Hours** | Classroom projector broken before lecture, Wi-Fi down in library during exams. |
| **Medium** | **12 Hours** | Tube light flickering in hallway, restroom tap dripping, chair damaged. |
| **Low** | **24 Hours** | Request for extra whiteboard markers, aesthetic wall paint peeling. |

### How It Works in Code:
1. **Creation**: When `create_incident.py` runs, it takes `created_at` (UTC timestamp) and adds the priority duration using Python's `datetime.timedelta(hours=...)`. It saves `sla_deadline` and sets `sla_status = 'ON_SCHEDULE'`.
2. **Periodic Check**: Every 10 minutes, Amazon EventBridge triggers `check_sla.py`.
3. **Query**: The Lambda performs a range query on `StatusGSI`:
   - `status = 'OPEN'` where `sla_deadline < current_utc_time`
   - `status = 'IN_PROGRESS'` where `sla_deadline < current_utc_time`
4. **Deduplication Guard**: The code checks `if item.get("sla_status") != "BREACHED"`. If already marked breached, it skips sending an alert. This prevents spamming the administrator every 10 minutes for the same ticket!
5. **Notification**: If breached for the first time, DynamoDB is updated to `sla_status = 'BREACHED'` and an email is published to Amazon SNS.

---

## 5. Security Architecture & RBAC (Role-Based Access Control)

### Authentication Flow
1. User logs in with email and password via Amazon Cognito.
2. Cognito verifies credentials and issues a cryptographically signed **JWT (JSON Web Token)** containing the user's attributes and Cognito Group (`Student`, `Staff`, or `Admin`).
3. The frontend includes this token in the `Authorization: Bearer <token>` header for all API requests.
4. **API Gateway Authorizer**: Validates the JWT signature against Cognito's JSON Web Key Set (JWKS). If invalid or expired, API Gateway rejects the request with `401 Unauthorized` before it ever reaches Lambda (saving compute costs!).
5. **Lambda RBAC Check**: In `shared/auth.py`, the Lambda extracts the `cognito:groups` claim from the request context and enforces permissions:
   - Students can only create incidents and list their own tickets.
   - Staff can only view tickets assigned to them and update status to `IN_PROGRESS` or `RESOLVED`.
   - Admins can assign staff, view all department tickets, and receive SNS breach notifications.

### Principle of Least Privilege in IAM
In our Terraform code (`iam.tf`):
- Lambdas do **NOT** have `AdministratorAccess` or broad `*` permissions.
- The Lambda execution role has policy statements scoped down to the specific DynamoDB table ARN (`campusops-incidents-dev` and its indexes), the specific CloudWatch Log Groups, and the specific SNS topic ARN.

---

## 6. Top 20 Viva Questions & Winning Answers

### Architecture & AWS Concepts

#### 1. What is the difference between a synchronous and asynchronous Lambda invocation?
> *"In a **synchronous** invocation (like our API Gateway REST calls), the client waits for Lambda to finish processing and return a response (e.g., HTTP 201 Created). In an **asynchronous** invocation (like EventBridge triggering `check_sla`), the caller dispatches the event and does not wait for the result. AWS queues the event and automatically retries twice if the Lambda encounters an error."*

#### 2. What is a cold start in AWS Lambda, and how does CampusOps mitigate it?
> *"A cold start occurs when a Lambda function is invoked after being idle; AWS must initialize a new execution environment (microVM) and load the runtime code. We mitigate this by using **Python 3.12** (which has a very fast initialization time compared to Java or .NET), keeping our zip package lightweight (~15 KB) with zero heavy external dependencies in the Lambda handler, and allocating 128 MB RAM which is optimal for lightweight REST I/O operations."*

#### 3. Why did you use Amazon API Gateway REST API instead of HTTP API?
> *"While HTTP APIs are slightly cheaper, REST APIs natively support direct integration with **Cognito User Pool Authorizers**, granular execution logging in CloudWatch, custom Gateway Responses for CORS preflights on 4XX/5XX errors, and mock integrations without spinning up backend Lambdas."*

#### 4. How does DynamoDB partition data under the hood?
> *"DynamoDB hashes the Partition Key (`incident_id`) using an internal hashing algorithm to determine which physical storage partition will store the item. Because our partition key is a randomly generated UUID (`inc-...`), writes are distributed evenly across partitions, preventing 'hot partitions'."*

#### 5. What is the difference between Partition Key (PK) and Sort Key (SK)?
> *"A Partition Key determines physical data placement and must be queried with exact equality (`=`). A Sort Key arranges items with the same Partition Key in sorted physical order on disk, allowing range comparisons like `<`, `>`, `BETWEEN`, or `begins_with()`. In our `StatusGSI`, `status` is the PK and `sla_deadline` is the SK, which allows us to query `status = 'OPEN' AND sla_deadline < :now` in a single fast operation."*

#### 6. What happens if two administrators assign a technician to the same incident simultaneously?
> *"In DynamoDB, we can prevent race conditions using **Conditional Writes** (`ConditionExpression`). For example, we can specify `attribute_exists(incident_id)` or check that `status <> 'RESOLVED'` before applying the update. If the condition is not met, DynamoDB rejects the write with a `ConditionalCheckFailedException`."*

#### 7. How does CORS work, and where is it configured in your project?
> *"CORS (Cross-Origin Resource Sharing) is a browser security mechanism that prevents a web application hosted on one domain (e.g., S3 website bucket) from making unauthorized API requests to a different domain (API Gateway). We handled CORS at two levels:  
> 1. In API Gateway via `OPTIONS` mock preflight methods that return `Access-Control-Allow-Origin: *` and allowed headers/methods.  
> 2. In Lambda via our `shared/response.py` helper, ensuring all 200, 400, and 500 JSON responses include `Access-Control-Allow-Origin`."*

---

### DevOps & Infrastructure as Code (Terraform & CI/CD)

#### 8. What is Infrastructure as Code (IaC) and what are its advantages?
> *"IaC is the practice of managing and provisioning computing infrastructure through human-readable configuration files rather than manual clicking in the AWS Web Console. Advantages include:  
> - **Reproducibility**: We can spin up an identical staging or production environment in minutes.  
> - **Version Control**: Every infrastructure change is tracked in Git commits.  
> - **Safety**: `terraform plan` shows exactly what will be added, modified, or destroyed before any changes occur."*

#### 9. What is the difference between `terraform plan` and `terraform apply`?
> *" `terraform plan` is a dry-run execution that compares the desired state in `.tf` files with the current real-world state in `terraform.tfstate`, printing a speculative diff without touching real infrastructure. `terraform apply` actually makes API calls to AWS to provision or update the cloud resources."*

#### 10. Why is `terraform.tfstate` important and why shouldn't it be committed to GitHub?
> *"The state file maps Terraform resource definitions to actual AWS resource IDs and metadata. It should **never** be committed to public GitHub because it can contain sensitive configuration data or secrets in plain text, and concurrent team members pushing state files could corrupt environment state. In enterprise setups, state is stored in a remote S3 bucket with DynamoDB state locking."*

#### 11. What is the purpose of GitHub Actions CI/CD in your project?
> *"Our GitHub Actions setup has two automated workflows:  
> 1. **CI (`ci.yml`)**: Triggers on pull requests; automatically runs Flake8 linting, 32 pytest unit tests with Moto DynamoDB mocks, Vitest frontend tests, Vite production build, SonarCloud static security analysis, and `terraform plan`.  
> 2. **CD (`cd.yml`)**: Triggers on merges to main; contains a **manual approval gate** (GitHub Environment `production`) before running `terraform apply` and deploying the compiled frontend to S3."*

#### 12. How does SonarCloud improve your codebase?
> *"SonarCloud performs Static Application Security Testing (SAST) and code quality analysis. It scans for security vulnerabilities (e.g., SQL injection, hardcoded credentials), code smells (unreachable code, duplicate functions), and tracks test coverage."*

---

### Testing & Quality Assurance

#### 13. What is Moto and why did you use it for backend testing?
> *"Moto is an open-source Python library that intercepts Boto3 network calls and spins up an exact, in-memory mock of AWS services like DynamoDB and SNS. This allows us to run **32 complete integration tests in under 2 seconds** on any laptop without needing an internet connection, AWS credentials, or incurring AWS charges."*

#### 14. What is the difference between unit testing and integration testing in your project?
> *"Our frontend tests (`App.test.jsx`) are **unit tests** using Vitest and React Testing Library that verify individual UI components (e.g., verifying that the priority badge renders the correct color). Our backend tests (`test_create_incident.py`) are **integration tests** that execute the full Lambda handler code, authenticate input, perform real DynamoDB CRUD operations against Moto, and verify the resulting HTTP status code and response payload."*

---

### Cost, Monitoring & Resilience

#### 15. How do you prove that this project costs \$0.00 on AWS Free Tier?
> *"Every service utilized falls well within the AWS Free Tier allowances:  
> - **Lambda**: 1,000,000 free requests/month (we use ~4,320 invocations/month for SLA checks).  
> - **DynamoDB**: 25 GB of storage and 25 RCU/WCU free forever in Pay-Per-Request mode.  
> - **API Gateway**: 1,000,000 free REST API calls/month during the 12-month Free Tier.  
> - **Cognito**: 50,000 Monthly Active Users (MAUs) free forever.  
> - **S3**: 5 GB of standard storage and 20,000 GET requests free.  
> - **CloudWatch**: 5 GB of log ingestion free; our 14-day retention cap guarantees logs never accumulate beyond this.  
> - **AWS Budgets**: We configured a hard budget alert at \$1.00 USD with email notifications."*

#### 16. What happens if the Lambda function crashes due to an unhandled exception?
> *"1. The caller (API Gateway) receives an HTTP `502 Bad Gateway` error.  
> 2. The Python traceback is automatically captured in Amazon CloudWatch Logs.  
> 3. Our CloudWatch Metric Alarm (`campusops-lambda-errors-dev`) detects when `Errors >= 1` in a 5-minute period and automatically triggers an SNS notification to the admin."*

#### 17. Why did you choose region `ap-south-1` (Mumbai)?
> *"Because the university campus is located in India, choosing the Mumbai AWS region provides the lowest physical latency (round-trip ping ~15–30 ms). It also complies with data sovereignty guidelines by keeping student records within the national borders."*

#### 18. How does the frontend handle offline mode or API Gateway downtime?
> *"In `frontend/src/services/api.js`, we implemented an offline fallback mechanism. If the network request fails or if the live API URL is not yet configured, the app gracefully falls back to local in-memory storage seeded with sample tickets, allowing seamless demonstrations during exams even without live internet connectivity."*

#### 19. How would you handle file attachments (e.g., photos of broken lab equipment)?
> *"We would generate a pre-signed S3 URL via a Lambda function. The student's browser uploads the image directly to a private S3 bucket (`PUT s3://...`), bypassing the Lambda payload size limit (6 MB). The S3 object key would then be saved in the DynamoDB incident record."*

#### 20. If CampusOps grew to 50,000 students, what bottlenecks would you expect and how would you fix them?
> *"1. **Lambda Concurrency**: By default, an AWS account has a quota of 1,000 concurrent Lambda executions. We could request a quota increase or enable Provisioned Concurrency for peak hours.  
> 2. **DynamoDB Throughput**: In On-Demand mode, DynamoDB auto-scales up to double its previous peak instantaneously. For massive scale, we could enable DynamoDB Accelerator (DAX) for in-memory caching.  
> 3. **Frontend CDN**: We could put an Amazon CloudFront distribution in front of the S3 static website bucket to cache assets globally and provide custom domain SSL certificates."*

---

## 7. Step-by-Step Viva Demonstration Script

When asked to give a live walkthrough, follow this exact sequence:

1. **Open the Web UI (`localhost:5173` or S3 Endpoint)**:
   - Point out the clean, modern responsive layout.
   - Click the **"👨‍🎓 Student"** persona pill in the navbar.
2. **Submit a New Incident**:
   - Click **"+ Report Incident"**.
   - Title: *"Projector bulb dead in CS Lab 301"*.
   - Category: *"Electrical"*, Priority: *"High (4h target)"*.
   - Click Submit. Show that the ticket instantly appears with status `OPEN` and a live **SLA Countdown Timer** showing ~3h 59m remaining.
3. **Switch to Admin Persona**:
   - Click **"👑 Admin"** in the top navbar.
   - Show the KPI cards: Total Incidents, Open, In Progress, SLA Breached.
   - Locate the newly created projector ticket.
   - Click **"Assign Staff"** and choose technician *"Ramesh Kumar (Electrical Dept)"*.
   - Show that the ticket updates immediately.
4. **Switch to Staff Persona**:
   - Click **"🔧 Staff"** in the top navbar.
   - Show that Ramesh Kumar now sees the assigned ticket on his personal workbench.
   - Click **"Start Work"** (status moves to `IN_PROGRESS`).
   - Click **"Resolve"**; show that the modal requires mandatory resolution notes (*"Replaced halogen lamp with spare from store"*).
   - Submit resolution: ticket badge turns green `RESOLVED` and resolution timestamp is stamped.
5. **Show Backend Tests & Code Cleanliness**:
   - Open PowerShell and run: `python -m pytest backend/tests -v`.
   - Point out that **all 32 tests pass in ~2 seconds** using Moto AWS mocks.
6. **Show Infrastructure Code**:
   - Open `infra/terraform/`. Point out that every single AWS resource is codified, documented, and planned.
   - Run `terraform validate` to show: `Success! The configuration is valid.`

---

*Good luck with your viva! You have built a production-grade, enterprise-ready cloud application with genuine engineering rigour.* 🚀

