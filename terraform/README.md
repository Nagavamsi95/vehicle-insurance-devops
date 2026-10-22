# Vehicle Insurance DevOps Project

A Flask web app that estimates vehicle insurance premiums, packaged in Docker, deployed to AWS with Terraform, and delivered through a GitHub Actions CI/CD pipeline.

The application is intentionally simple. The focus of this project is the DevOps workflow around it: automated testing, containerization, infrastructure as code, and automated deployment.

## Architecture

```
Developer pushes to main
        │
        ▼
GitHub Actions
  ├── test          run pytest
  ├── build-and-push build Docker image, push to Docker Hub
  └── deploy        SSH into AWS EC2, pull image, restart container
                              │
                              ▼
AWS (provisioned by Terraform)
  VPC 10.0.0.0/16
  └── Public subnet 10.0.1.0/24
      └── EC2 t3.micro (Amazon Linux 2023)
          └── Docker container running Flask + gunicorn on port 80
```

## Features

- Web form to calculate an estimated annual premium
- JSON API at `/api/quote`
- Health endpoint at `/health`, for load balancers and monitoring
- Unit tests with pytest

## Tech stack

| Area | Tools |
|---|---|
| Application | Python, Flask, gunicorn |
| Testing | pytest |
| Containers | Docker (python:3.12-slim base, non-root user) |
| Infrastructure as code | Terraform (AWS provider) |
| Cloud | AWS VPC, EC2, security groups, key pairs |
| CI/CD | GitHub Actions |
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

Before applying, set `ssh_public_key_path` to your public key and, ideally, set `allowed_ssh_cidr` to your own IP.

## CI/CD pipeline

The workflow in `.github/workflows/ci.yml` runs on every push to `main`:

1. **test**: installs dependencies and runs pytest. A failure stops the pipeline.
2. **build-and-push**: builds the Docker image and pushes it to Docker Hub, tagged `latest` and with the commit SHA.
3. **deploy**: connects to the server over SSH, pulls the new image, and replaces the running container.

Required GitHub secrets: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, `SERVER_HOST`, `SERVER_SSH_KEY`.

## Security

- The app runs as a non-root user inside the container.
- Secrets are stored in GitHub Actions secrets, never in the repository.
- Terraform state files are excluded from Git.
- SSH access uses key-based login only.

## What I'd improve next

- Put an Application Load Balancer in front of an Auto Scaling group for high availability
- Store Terraform state remotely in S3 with DynamoDB locking
- Add a CloudWatch alarm on the health endpoint
- Scan the image for vulnerabilities with Trivy in the pipeline
- Replace the single server's startup script with Ansible for configuration management
- Replace the placeholder premium formula with a trained ML model