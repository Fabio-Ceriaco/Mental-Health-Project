# Mental-Health-Project


A complete and professional application for assessing, monitoring, and managing mental health in a corporate environment, with predictions based on Artificial Intelligence.

---

## Index

1. [Project Overview](#project-overview)
2. [Technical Architecture](#technical-architecture)
3. [Technology Stack](#technology-stack)
4. [Installation and Configuration](#installation-and-configuration)
5. [How to Run](#how-to-run)
6. [Project Structure](#project-structure)
7. [Prediction Model (AI)](#ai-prediction-model)
8. [Performance Metrics](#performance-metrics)
9. [API Endpoints](#api-endpoints)

---

## Project Overview

The **Mental Health Application** is an integrated corporate solution that enables:

- **Mental Health Assessment**: Comprehensive questionnaires covering 18 psychological dimensions
- **Real-Time Monitoring**: Assessment history and user progress
- **Risk Predictions (AI)**: Machine learning model that predicts risk levels with 97.41% accuracy
- **Intervention Management**: Planning and execution of improvement actions
- **Executive Dashboard**: Real-time visualizations for HR and psychologists
- **Security**: JWT authentication, role-based control (RBAC)

### Target Audiences

- **Employees**: Self-assessment and personal monitoring
- **HR Managers**: Employee management and interventions

- **Psychologists**: Detailed analysis and action planning
- **Administrators**: System management and configurations

---

## Technical Architecture

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Angular 17+)                    │
│        Tailwind CSS | ApexCharts | RxJS | TypeScript        │
│                  http://localhost:4200                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                      API Proxy
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                 Backend (FastAPI + Python)                   │
│  Validação | Autenticação | Lógica de Negócio | Predições  │
│                  http://localhost:8000                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   Camada de Dados                            │
│     SQLAlchemy ORM | SQLite | Alembic Migrations           │
│                  mental_health.db                            │
└─────────────────────────────────────────────────────────────┘
                           │
                    ┌──────▼───────┐
                    │  ML Models   │
                    │  (joblib)    │
                    └──────────────┘
```

### Data Flow

1. **Authentication**: User logs in
2. **Assessment**: Completes questionnaire with 18 dimensions
3. **Processing**: Data validated and stored
4. **AI Prediction**: Model predicts risk level
5. **Visualization**: Dashboard shows results
6. **Intervention**: HR/Psychologist plans actions

---

## 🛠️ Stack Tecnológico

### Backend

Component | Technology | Version | Purpose |
|-----------|-----------|--------|----------|
| **Web Framework** | FastAPI | 0.122.0 | Modern and fast REST API |
| **WSGI Server** | Uvicorn | 0.38.0 | Asynchronous HTTP Server |
| **ORM** | SQLAlchemy | 2.0.44 | Object-relational mapping |
| **DB Migrations** | Alembic | 1.17.2 | Database versioning |
| **Validation** | Pydantic | 2.12.5 | Schema validation |
| **Authentication** | python-jose | 3.5.0 | JWT tokens |
| **Cryptography** | bcrypt | 5.0.0 | Password hashing |
| **ML** | scikit-learn | 1.7.2 | Machine learning models |
| **Data** | pandas | 2.3.3 | Data Analysis and Manipulation |
| **Numerical** | numpy | 2.3.5 | Numerical Computing |
| **Environment** | python-dotenv | 1.2.1 | Environment Variables |

### Frontend

Component | Technology | Version | Purpose |
|-----------|-----------|--------|----------|
| **Framework** | Angular | 17+ | Reactive SPA Framework |
| **Language** | TypeScript | Latest | Static typing in JavaScript |
| **Styles** | Tailwind CSS | Latest | Utility-first CSS framework |
| **Charts** | ApexCharts | Latest | Interactive visualizations |
| **Reactivity** | RxJS | Latest | Reactive programming |
| **HTTP Client** | HttpClient | Integrated | HTTP Client |

### Data Base

| Appearance | Technology |
|--------|-----------|
| **Type** | SQLite (local file) |
| **File** | `API/mental_health.db` |
| **Tables** | 20+ |
| **Records** | 857 collaborators, 851 reviews |
| **Migrations** | Alembic with versioning |

---

## Installation and Configuration

### System Requirements

- **Python**: 3.9+ (3.11 recommended)
- **Node.js**: 18+ (for Angular)
- **npm**: 8+ (Node package manager)
- **Git**: For version control
- **macOS/Linux/Windows**: Operating system

### Step 1: Clone the Repository

```bash
git clone <your-repository>
cd Mental_Health_Final
```

### Step 2: Configure Backend

#### 2.1 Create a Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate # macOS/Linux
# or
venv\Scripts\activate # Windows
```

#### 2.2 Install Dependencies

```bash
cd API
pip install -r ../requirements.txt

```

#### 2.3 Configure Environment Variables

Create a `.env` file in the root of the `API` folder:

```env
# Database
DATABASE_URL=sqlite:///mental_health.db

# JWT Authentication
JWT_SECRET_KEY=your_super_secure_secret_key_here_123456789
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# API
API_PORT=8000
API_HOST=0.0.0.0

# Environment
ENVIRONMENT=development
```

⚠️ **IMPORTANT**: Change `JWT_SECRET_KEY` to a unique and secure key in production!

#### 2.4 Initialize Database (Optional)

If the database does not exist:

```bash
python -m alembic upgrade head

```

### Step 3: Configure Frontend

#### 3.1 Install Node Dependencies

```bash
cd FRONTEND
npm install

```

#### 3.2 Configure Proxy (Already Included)

The file `FRONTEND/proxy.conf.json` is already configured to:

- Redirect `http://localhost:4200/api/*` to `http://localhost:8000`

---

## 🚀How to Run

### Option 1: Manual Execution (Recommended for Development)

#### Terminal 1 - Backend

```bash
cd /Users/fabioceriaco/Mental_Health_Final/API

# Activate virtual environment (if not already active)
source ../venv/bin/activate

# Run FastAPI server
python3 run.py
```

The following will be displayed:
```
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Application startup complete
```

#### Terminal 2 - Frontend

```bash
cd /Users/fabioceriaco/Mental_Health_Final/FRONTEND

# Run Angular server ng serve -o
```

The following will be displayed:
```
✔ Compiled successfully.

✔ Build successful. **Accessing the Application**: Open your browser at [http://localhost:4200](http://localhost:4200)

### Option 2: Execution via Script (If Available)

```bash
cd /Users/fabioceriaco/Mental_Health_Final
chmod +x start.sh
./start.sh

```

### Test Credentials

After the first run, use demo credentials:

- **Email**: `demo@example.com`

- **Password**: `12345`

---
