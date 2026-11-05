# CampusOps Implementation Progress

## Status Overview
- Current Phase: Phase 7 (Finish - README, Architecture Mermaid, Setup Guide, VIVA_NOTES.md) - Completed & Validated
- Project Status: **100% Complete** (Phases 0 through 7 fully implemented, tested, and documented)
- AWS Region: `ap-south-1` (Mumbai)
- Python Version: `3.12`
- Budget Status: 100% Free Tier Eligible ($0.00 / budget guardrail at $1.00)

---

## Phases Tracker

| Phase | Description | Status | Date Completed | Notes |
|-------|-------------|--------|----------------|-------|
| **Phase 0** | Design (Repo structure, DynamoDB schema, Lambda/API matrix, SLA logic, Risks) | Completed | 2026-11-05 | Full viva-ready architecture approved |
| **Phase 1** | Backend (Python 3.12 Lambdas, RBAC validation, pytest + moto mock tests) | Completed | 2026-11-05 | 28/28 pytest unit tests passing with Moto DynamoDB mocks |
| **Phase 2** | Infrastructure (Terraform IaC, IAM least privilege, API Gateway, Cognito, S3, Budget) | Completed | 2026-11-05 | Terraform configuration validated; 69 resources planned |
| **Phase 3** | Frontend (React + Vite, Student/Staff/Admin views, Cognito auth, responsive UI) | Completed | 2026-11-05 | 7/7 Vitest component tests passing; production bundle built (60kB gzip) |
| **Phase 4** | SLA Automation (EventBridge rule, overdue check Lambda, SNS email alerts) | Completed | 2026-11-05 | 32/32 pytest tests passing; EventBridge 10m cron & SNS in Terraform (75 resources) |
| **Phase 5** | CI/CD (GitHub Actions for test, lint, SonarCloud, Terraform plan & deploy workflow) | Completed | 2026-11-05 | Validated CI & CD workflows created; Sonar properties configured; secrets mapped |
| **Phase 6** | Monitoring (CloudWatch log groups, alarms, dashboard, local Prometheus/Grafana) | Completed | 2026-11-05 | 14-day capped log groups, 2 CloudWatch alarms, dashboard (85 resources planned) |
| **Phase 7** | Viva Notes & Documentation (Architecture diagram, setup guide, VIVA_NOTES.md) | Completed | 2026-11-05 | Full viva defense guide, architecture diagram, and one-line summaries |

---

## Detailed Log

### Phase 0: Design
- Proposed clean repository layout separating `backend`, `frontend`, `infra/terraform`, `docs`, and `.github`.
- Designed single-table DynamoDB schema with 3 GSIs for optimal query patterns (`CreatedByGSI`, `AssignedToGSI`, `StatusGSI`) avoiding table scans.
- Defined 7 Lambda functions with strict role-based access control (RBAC) via Cognito JWT claims (`Student`, `Staff`, `Admin`).
- Defined priority-based SLA calculation (Critical 1h, High 4h, Medium 12h, Low 24h) and automated breach detection logic.
- Identified Free Tier constraints and technical risks with mitigation strategies.

### Phase 1: Backend
- Implemented shared modules (`response.py`, `auth.py`, `utils.py`, `db.py`).
- Implemented 6 core Lambda handlers (`create_incident.py`, `get_incident.py`, `list_incidents.py`, `assign_staff.py`, `update_status.py`, `resolve_incident.py`).
- Built comprehensive test suite with 28 tests using Moto to emulate AWS DynamoDB.
- Ran pytest locally: **28/28 tests passed (100% pass rate)**.

### Phase 2: Infrastructure (Terraform)
- Authored production-ready Terraform configurations in `infra/terraform/`:
  - `dynamodb.tf`: Table `campusops-incidents-dev` with Pay-Per-Request on-demand billing and 3 GSIs.
  - `cognito.tf`: User pool, web client, and `Student`, `Staff`, `Admin` user groups.
  - `iam.tf`: Least-privilege IAM execution role and scoped access policies for Lambdas.
  - `lambda.tf`: Auto-packaged zip archive deploying 6 Python 3.12 Lambdas (128MB, 10s timeout).
  - `apigateway.tf`: REST API with Cognito User Pool Authorizer, 5 proxy resources, CORS OPTIONS preflight mock integrations, and 4XX/5XX CORS error responses.
  - `s3.tf`: Static website hosting bucket for React frontend with public read bucket policy.
  - `budget.tf`: AWS Budget alert ($1.00 USD) with 80% actual and 100% forecasted email alerts.
  - `outputs.tf`: Outputs for API URL, Cognito IDs, DynamoDB table, and S3 endpoint.
- Initialized Terraform providers (`aws ~> 5.0`, `archive ~> 2.4`, `random ~> 3.5`).
- Ran `terraform validate`: **Success! The configuration is valid.**
- Ran `terraform plan`: **Plan: 69 to add, 0 to change, 0 to destroy.**

### Phase 3: Frontend (React + Vite SPA)
- Built modern React 18 single-page application bundled with Vite in `frontend/`:
  - `styles.css`: Responsive mobile-first CSS design with CSS variables, badge classes, metric cards, and modals.
  - `services/auth.js`: User session management with live Cognito authentication and 1-click viva demo switches.
  - `services/api.js`: API client connecting to API Gateway with seamless offline demo fallback and initial seed incidents.
  - `components/`: `Navbar`, `StatusBadge`, `PriorityBadge`, `SLAIndicator` (live countdown timer), and `CreateIncidentModal`.
  - `views/StudentView.jsx`: Student ticket reporting, category selection, and live SLA countdown tracking.
  - `views/StaffView.jsx`: Technician workbench for assigned tasks, status updates to `IN_PROGRESS`, and resolution notes logging.
  - `views/AdminView.jsx`: Central operations control room, department metrics, SLA breach warnings, and technician assignment modal.
  - `views/LoginView.jsx`: Login portal with quick demo buttons for examiners.
- Verified test suite with Vitest (`frontend/src/test/App.test.jsx`): **7/7 tests passed (100%)**.
- Executed production build (`npm run build`): compiled static bundle to `frontend/dist/` (total gzipped size ~60kB).

### Phase 4: SLA Automation
- Implemented `backend/src/lambdas/check_sla.py` triggered on schedule to detect active overdue tickets and escalate via Amazon SNS.
- Added re-alert deduplication guard (`sla_status != 'BREACHED'`) to avoid spamming administrators.
- Added comprehensive unit tests in `backend/tests/test_check_sla.py` using Moto DynamoDB and SNS mocks.
- Executed full backend pytest suite: **32/32 tests passed (100% pass rate)**.
- Authored Terraform infrastructure for SLA:
  - `eventbridge.tf`: Scheduled rule `rate(10 minutes)`, target pointing to `check_sla` Lambda, and invoke permission.
  - `sns.tf`: SNS topic `campusops-sla-alerts-dev` with email subscription for `alert_email`.
  - `iam.tf`: Added least-privilege `sns:Publish` permission to Lambda execution role.
  - `lambda.tf`: Added `check_sla` function with `SNS_TOPIC_ARN` environment variable.
- Ran `terraform validate` and `terraform plan`: **Plan: 75 to add, 0 to change, 0 to destroy**.

### Phase 5: CI/CD Pipelines
- Authored `.github/workflows/ci.yml`:
  - `backend-test`: Python 3.12 environment, Flake8 linting, and pytest unit testing with Moto DynamoDB mocks & coverage.
  - `frontend-test`: Node.js 20 environment, Vitest component test run, and Vite production bundle build.
  - `sonarcloud-scan`: Static code analysis for quality, security vulnerabilities, and code smells.
  - `terraform-plan`: Terraform formatting check, initialization, validation, and PR speculative planning.
- Authored `.github/workflows/cd.yml`:
  - Deployment pipeline requiring manual approval via GitHub Environment `production`.
  - Provisions AWS infrastructure with `terraform apply -auto-approve`.
  - Captures dynamic Terraform outputs and deploys compiled frontend to Amazon S3 website bucket.
- Configured `sonar-project.properties` with source/test boundaries and exclusion patterns.

### Phase 6: Monitoring (CloudWatch & Local Prometheus/Grafana)
- Authored `infra/terraform/cloudwatch.tf`:
  - 7 CloudWatch Log Groups with strict 14-day retention limit (100% Free Tier safe, avoiding infinite log accumulation).
  - 2 CloudWatch Metric Alarms (Lambda unhandled exceptions & API Gateway 5XX server errors) wired to SNS admin alerts.
  - Centralized CloudWatch Operational Dashboard (`campusops-dashboard-dev`) displaying API traffic, error status, latency, Lambda invocations/errors, and DynamoDB RCU/WCU throughput.
- Authored optional local Docker Compose observability suite in `monitoring/` (`docker-compose.yml`, `prometheus.yml`, `README.md`) avoiding AWS EC2 server costs.
- Ran `terraform validate` and `terraform plan`: **Plan: 85 to add, 0 to change, 0 to destroy**.

### Phase 7: Finish, Viva Preparation & Live AWS Deployment
- Authored `README.md` with:
  - System architecture diagram in Mermaid format covering Clients, S3, Cognito, API Gateway, Lambdas, DynamoDB + GSIs, EventBridge, SNS, CloudWatch, and AWS Budgets.
  - Quick-start guide for local execution and testing.
  - Step-by-step AWS deployment commands for Terraform and S3 frontend deployment.
  - Directory structure and AWS Free Tier cost protection guarantees.
- Authored `docs/VIVA_NOTES.md` with:
  - 30-second elevator pitch for the viva examination.
  - One-line plain English explanation for every single AWS resource in CampusOps.
  - Deep-dive justifications for Serverless vs EC2/Monolithic, DynamoDB Single-Table Design, Sparse Indexing, and 14-day log retention.
  - Comprehensive explanation of priority-based SLA calculation and EventBridge cron automation.
  - Top 20 anticipated viva questions with ready-to-recite answers.
  - Step-by-step viva live demo walkthrough script for examiners.
- Successfully deployed complete infrastructure to AWS `ap-south-1` via Terraform:
  - **Live Frontend Web URL**: http://campusops-frontend-dev-c0cf6c4c.s3-website.ap-south-1.amazonaws.com
  - **Live API Gateway Endpoint**: https://lp0jvwl5f9.execute-api.ap-south-1.amazonaws.com/dev
  - **Cognito User Pool ID**: `ap-south-1_UmR09agC8`
  - **Cognito App Client ID**: `3037at1btmphctj8j46a85gg79`
  - **DynamoDB Table**: `campusops-incidents-dev`
  - **CloudWatch Operational Dashboard**: `campusops-dashboard-dev`
  - **Amazon SNS Topic**: `arn:aws:sns:ap-south-1:418059030221:campusops-sla-alerts-dev`
- Executed automated live smoke test suite (`scripts/smoke_test.py`):
  - 1. Unauthenticated request rejected: HTTP 401 Unauthorized (Cognito Authorizer) ✅
  - 2. Cognito Student test user provisioned and assigned to 'Student' group ✅
  - 3. Authenticated Student with Cognito InitiateAuth & acquired valid JWT ✅
  - 4. Created live test incident (`inc-20261105-5ee468`) via API Gateway -> Lambda -> DynamoDB: HTTP 201 Created ✅
  - 5. Verified Lambda RBAC: Student attempting admin route `/assign` strictly blocked with HTTP 403 Forbidden ✅
- Provisioned verified live production accounts in Cognito:
  - Admin: `umeshreddy3005@gmail.com` (Group: `Admin`) ✅
  - Staff: `sohinimanne@gmail.com` (Group: `Staff`) ✅
  - Verified authentication via `InitiateAuth` (both PASS) and stored credentials securely in `~/campusops-credentials.txt` (`chmod 600`) outside repo.
  - Purged old placeholder users (`admin@campusops.edu` and `staff@campusops.edu`).
- Updated Terraform infrastructure:
  - Re-pointed SNS SLA escalation alert topic subscription to `umeshreddy3005@gmail.com`.
  - Re-pointed AWS Budgets 80% & 100% cost threshold alerts to `umeshreddy3005@gmail.com`.










