# Vehicle Insurance DevOps Project

A Flask web app that estimates vehicle insurance premiums, packaged in Docker, provisioned on AWS with Terraform, and delivered through a GitHub Actions CI/CD pipeline. The application is intentionally simple. The focus is the DevOps workflow around it: automated testing, container security scanning, infrastructure as code, and automated delivery.

## Architecture

```
Developer pushes to main
        │
        ▼
GitHub Actions
  ├── test              run pytest
  ├── build-and-push    build Docker image, scan with Trivy, push to Docker Hub
  └── deploy            SSH into AWS EC2, pull image, restart container
                              │
                              ▼
AWS (provisioned by Terraform)
  VPC 10.0.0.0/16
  └── Public subnet 10.0.1.0/24
      └── EC2 t3.micro (Amazon Linux 2023)
          └── Docker container running Flask + gunicorn on port 80
```

## Features

- Web form that calculates an estimated annual premium
- JSON API at `/api/quote`
- Health endpoint at `/health`, for load balancers and monitoring
- Unit tests with pytest

## Tech stack

| Area | Tools |
|---|---|
| Application | Python 3.12, Flask, gunicorn |
| Testing | pytest |
| Containers | Docker (python:3.12-slim base, non-root user) |
| Security scanning | Trivy (CRITICAL and HIGH severities) |
| Infrastructure as code | Terraform (AWS provider 5.x) |
| Cloud | AWS VPC, internet gateway, subnet, security group, EC2 key pair, EC2 |
| CI/CD | GitHub Actions on ubuntu-24.04 |
| Registry | Docker Hub |

## Run locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -v
python -m app.main              # open http://127.0.0.1:5000
```

## Run in Docker

```bash
docker build -t vehicle-insurance:v1 .
docker run -p 5000:5000 vehicle-insurance:v1   # open http://localhost:5000
```

## Deploy to AWS

```bash
cd terraform
terraform init
terraform plan
terraform apply                 # outputs public_ip
terraform destroy               # removes all resources when finished
```

Terraform creates a startup script that installs Docker and runs the image from Docker Hub on first boot. The `ssh_public_key_path` variable points to the public key that GitHub Actions uses to log in.

## CI/CD pipeline

The workflow in `.github/workflows/ci.yml` runs on every push to `main`:

1. **test** installs dependencies and runs pytest. A failure stops the pipeline.
2. **build-and-push** builds the image, scans it with Trivy, and pushes it to Docker Hub only if the scan passes. Images are tagged `latest` and with the commit SHA.
3. **deploy** connects to the server over SSH, pulls the new image, and replaces the running container.

Required GitHub secrets: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, `SERVER_HOST`, `SERVER_SSH_KEY`.

The deploy job is disabled between sessions, because the server is destroyed with `terraform destroy` to avoid AWS charges. The job fails when no server is running at `SERVER_HOST`. To deploy again, run `terraform apply`, update `SERVER_HOST` with the new IP, and re-run the failed job.

## Security

- The container runs as a non-root user.
- Secrets are stored in GitHub Actions secrets and never committed.
- Terraform state files are excluded from Git.
- Images with known CRITICAL or HIGH vulnerabilities that have a fix are blocked before they are pushed.
- SSH access uses key-based login only.

## Lessons learned

- The Trivy scan first failed on an invalid action version tag, then on a missing dependency inside the action. Running the scanner directly in Docker removed both external dependencies.
- The GitHub Actions secrets had to match the workflow names exactly. A missing `DOCKERHUB_USERNAME` caused the first build failure.
- Replacing the AWS server changes its public IP, so the deploy target must be updated each time the infrastructure is recreated.

## What I'd improve next

- Put an Application Load Balancer in front of an Auto Scaling group for high availability
- Store Terraform state remotely in S3 with DynamoDB locking
- Add a CloudWatch alarm on the health endpoint
- Replace the single server's startup script with Ansible for configuration management
- Replace the placeholder premium formula with a trained ML model