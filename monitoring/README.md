# Local Monitoring Suite: Prometheus & Grafana

> **Viva Defense Insight**:  
> In production AWS cloud, we use **Amazon CloudWatch** (Log Groups, Metrics, Alarms, and Dashboard) which is natively serverless and Free Tier eligible.  
> Deploying dedicated Prometheus servers and Grafana instances directly inside AWS requires 24/7 EC2 virtual machines, which would incur monthly infrastructure costs (~$15-$25/month) and break our project's **AWS Free Tier Guarantee**.  
> Therefore, Prometheus and Grafana are configured exclusively as an **optional local Docker Compose stack** for local testing, offline simulation, and project demonstration.

---

## 1. Stack Components

| Service | Container Port | Host Port | Purpose |
| :--- | :---: | :---: | :--- |
| **Prometheus** | 9090 | `9090` | Time-series metrics collection and scraping engine |
| **Grafana** | 3000 | `3000` | Data visualization dashboard with pre-configured admin panel |

---

## 2. How to Run Locally

If Docker Desktop is installed on your development machine:

```powershell
cd monitoring
docker compose up -d
```

### Accessing Dashboards:
- **Prometheus UI**: Open [http://localhost:9090](http://localhost:9090) to inspect raw metrics and targets.
- **Grafana UI**: Open [http://localhost:3000](http://localhost:3000)
  - **Username**: `admin`
  - **Password**: `admin`

### Stopping the Stack:
```powershell
docker compose down
```
*(No cloud resources are touched, no cost is ever incurred).*

