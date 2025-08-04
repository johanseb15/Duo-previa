# Duo-previa PWA Setup and Deployment Guide

This guide provides comprehensive steps to set up your development environment, run tests, and deploy the Duo-previa Progressive Web Application (PWA).

## 1. Project Overview

Duo-previa is a multi-tenant food delivery PWA with a React (Vite) frontend and a FastAPI (Python) backend. It utilizes MongoDB for data storage and is designed for secure and scalable deployment using Docker and Nginx.

## 2. Local Development Setup

### 2.1. Prerequisites

Before you begin, ensure you have the following installed:

*   **Python 3.11+**: For the backend.
*   **Node.js 16+ & npm**: For the frontend.
*   **Docker & Docker Compose**: For containerized development and deployment.
*   **MongoDB**: A running MongoDB instance (local or cloud-based).

### 2.2. Automated Setup Script

For a quick initial setup of project dependencies, you can use the provided `setup.sh` script.

```bash
# Navigate to the root of your project
cd C:\Users\johan\Documents\Duo-previa

# Make the script executable (Linux/macOS)
# chmod +x setup.sh

# Run the setup script
./setup.sh
```

This script will install both backend (Python) and frontend (Node.js) dependencies.

### 2.3. Backend Setup (Python/FastAPI)

#### 2.3.1. Configure Environment Variables

Create a `.env` file in the `backend/` directory (`C:\Users\johan\Documents\Duo-previa\backend\.env`) and populate it with your development environment variables. Replace placeholder values with your actual credentials.

```
MONGODB_URL=mongodb+srv://sebasmol2010:4SJ8Va8N0enwtE5f@cluster0.unnmsqm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
DATABASE_NAME=duo_previa
SECRET_KEY=super-secret-key-for-jwt-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development
PORT=8000

# Security settings
RATE_LIMIT_CALLS=100
RATE_LIMIT_PERIOD=3600
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,https://duo-previa.vercel.app

# Monitoring
SENTRY_DSN=
LOG_LEVEL=INFO

# API Keys (for additional protection)
API_KEYS=
```

#### 2.3.2. Initialize Sample Data (Optional)

To populate your MongoDB with sample data for development and testing, run the `init_sample_data.py` script from the `backend/` directory:

```bash
cd C:\Users\johan\Documents\Duo-previa\backend
python init_sample_data.py
```

#### 2.3.3. Run Backend Locally

Start the FastAPI application from the `backend/` directory:

```bash
cd C:\Users\johan\Documents\Duo-previa\backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be accessible at `http://localhost:8000`. API documentation will be available at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc` (ReDoc) in development mode.

### 2.4. Frontend Setup (React/Vite)

#### 2.4.1. Run Frontend Locally

Start the Vite development server from the `frontend/` directory:

```bash
cd C:\Users\johan\Documents\Duo-previa\frontend
npm run dev
```

The frontend will typically be accessible at `http://localhost:5173` (or another port if 5173 is in use). It will proxy API requests to the backend running on `http://localhost:8000` via `vite.config.js`.

## 3. Testing

### 3.1. Running Backend Unit and Integration Tests

From the `backend/` directory, run the tests using `pytest`:

```bash
cd C:\Users\johan\Documents\Duo-previa\backend
pytest
```

This will execute tests defined in `backend/tests/test_auth.py` and `backend/tests/test_api_endpoints.py`, and generate a coverage report.

### 3.2. Running Backend End-to-End Tests

Ensure your backend is running locally (as described in 2.3.3). Then, from the `backend/` directory, run the end-to-end test script:

```bash
cd C:\Users\johan\Documents\Duo-previa\backend
python test_backend.py
```

This script will perform a series of API calls to verify the backend's functionality.

## 4. Deployment

This section outlines the deployment process for both the frontend (Vercel) and the backend (Docker Compose).

### 4.1. Production Environment Variables

Create or update the `.env.production` file in the root of your project (`C:\Users\johan\Documents\Duo-previa\.env.production`). **Ensure this file is NOT committed to your Git repository.**

```
# NO COMMITTEAR ESTE ARCHIVO
MONGODB_URL=your_production_mongodb_connection_string
SECRET_KEY=your_strong_random_secret_key_for_jwt_production
MONGO_ROOT_PASSWORD=your_strong_random_mongo_password_production
```

### 4.2. Docker Deployment (Backend & Nginx)

This method is suitable for deploying your backend and Nginx on a cloud VM or dedicated server.

#### 4.2.1. Generate Docker Secrets

These secrets will be used by Docker Swarm for enhanced security. Run these commands from the root of your project (`C:\Users\johan\Documents\Duo-previa`):

```bash
openssl rand -hex 32 > secret_key.txt
openssl rand -hex 16 > mongo_root_password.txt
```

#### 4.2.2. Initialize Docker Swarm and Create Secrets

If you haven't already, initialize Docker Swarm on your server and create the secrets. Replace `secret_key.txt` and `mongo_root_password.txt` with the paths to your generated files.

```bash
docker swarm init
docker secret create secret_key secret_key.txt
docker secret create mongo_root_password mongo_root_password.txt
```

#### 4.2.3. Deploy with Docker Compose

From the root of your project (`C:\Users\johan\Documents\Duo-previa`), build and deploy the services:

```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

#### 4.2.4. Configure Nginx for HTTPS (Recommended)

The `nginx.conf` is already set up to use SSL certificates. You'll need to obtain these (e.g., using Let's Encrypt's Certbot) and ensure they are mounted correctly in your Nginx container.

```bash
# Example using Certbot (ensure Certbot is installed on your server)
# Replace 'tudominio.com' with your actual domain
docker run -it --rm -p 443:443 -p 80:80 \
  -v "/etc/letsencrypt:/etc/letsencrypt" \
  certbot/certbot certonly --standalone -d tudominio.com
```

#### 4.2.5. Configure Firewall

Ensure your server's firewall allows inbound traffic on ports 80 (HTTP), 443 (HTTPS), and 22 (SSH for management).

### 4.3. Vercel Deployment (Frontend)

Vercel provides an excellent and easy deployment platform for your React frontend.

#### 4.3.1. Connect GitHub Repository

1.  Go to [Vercel](https://vercel.com/) and log in.
2.  Click "Add New..." -> "Project".
3.  Select your GitHub repository (`johanseb15/Duo-previa`).

#### 4.3.2. Configure Project Settings

1.  **Root Directory:** Set the root directory to `frontend/`.
2.  **Build Command:** `npm run build`
3.  **Output Directory:** `build` (Vite's default for `npm run build`)
4.  **Environment Variables:**
    *   Add `NODE_ENV` with value `production`.
    *   Add `VITE_REACT_APP_API_URL` (or whatever prefix your Vite app uses for env vars) with the public URL of your backend API (e.g., `https://api.tudominio.com/api`). This is crucial for the frontend to know where to send API requests in production.

#### 4.3.3. Deploy

Vercel will automatically build and deploy your frontend. Subsequent pushes to your main branch (or configured production branch) will trigger automatic deployments.

## 5. Final Recommendations

*   **Monitoring & Alerting**: Implement robust monitoring for both frontend (e.g., Sentry, Vercel Analytics) and backend (e.g., Prometheus + Grafana, Google Cloud Monitoring) to proactively identify and address issues.
*   **Security Audits**: Regularly review your code and configurations for security vulnerabilities.
*   **Backup Strategy**: Establish a reliable backup strategy for your MongoDB database.
*   **CI/CD Enhancements**: Consider adding automated tests (unit, integration, E2E) to your GitHub Actions workflows to ensure code quality and prevent regressions before deployment.
*   **Documentation**: Keep this `SETUP.md` and your `README.md` updated with any changes or new features.

---
