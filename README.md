# Mental-Health-Project


Uma aplicação completa e profissional para avaliação, monitorização e gestão de saúde mental em ambiente corporativo, com previsões baseadas em Inteligência Artificial.



---

##  Índice

1. [Visão Geral do Projeto](#visão-geral-do-projeto)
2. [Arquitetura Técnica](#arquitetura-técnica)
3. [Stack Tecnológico](#stack-tecnológico)
4. [Instalação e Configuração](#instalação-e-configuração)
5. [Como Executar](#como-executar)
6. [Estrutura do Projeto](#estrutura-do-projeto)
7. [Modelo de Predição (IA)](#modelo-de-predição-ia)
8. [Métricas de Desempenho](#métricas-de-desempenho)
9. [API Endpoints](#api-endpoints)


---

## Visão Geral do Projeto

A **Aplicação de Saúde Mental** é uma solução corporativa integrada que permite:

- **Avaliação de Saúde Mental**: Questionários abrangentes com 18 dimensões psicológicas
- **Monitorização em Tempo Real**: Histórico de avaliações e progressão do utilizador
- **Predições de Risco (IA)**: Modelo de machine learning que prevê níveis de risco com 97.41% de precisão
- **Gestão de Intervenções**: Planeamento e execução de ações de melhoria
- **Dashboard Executivo**: Visualizações em tempo real para RH e psicólogos
- **Segurança**: Autenticação JWT, controlo baseado em funções (RBAC)

### Públicos-Alvo

-  **Colaboradores**: Auto-avaliação e monitorização pessoal
-  **Gestores de RH**: Gestão de colaboradores e intervenções
-  **Psicólogos**: Análise detalhada e planeamento de ações
-  **Administradores**: Gestão do sistema e configurações

---

##  Arquitetura Técnica

### Diagrama de Arquitetura

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

### Fluxo de Dados

1. **Autenticação**: Utilizador faz login
2. **Avaliação**: Completa questionário com 18 dimensões
3. **Processamento**: Dados validados e armazenados
4. **Predição IA**: Modelo prevê nível de risco
5. **Visualização**: Dashboard mostra resultados
6. **Intervenção**: RH/Psicólogo planeia ações

---

## 🛠️ Stack Tecnológico

### Backend

| Componente | Tecnologia | Versão | Propósito |
|-----------|-----------|--------|----------|
| **Framework Web** | FastAPI | 0.122.0 | API REST moderna e rápida |
| **Servidor WSGI** | Uvicorn | 0.38.0 | Servidor HTTP assíncrono |
| **ORM** | SQLAlchemy | 2.0.44 | Mapeamento objeto-relacional |
| **Migrações DB** | Alembic | 1.17.2 | Versionamento da base de dados |
| **Validação** | Pydantic | 2.12.5 | Validação de schemas |
| **Autenticação** | python-jose | 3.5.0 | JWT tokens |
| **Criptografia** | bcrypt | 5.0.0 | Hashing de passwords |
| **ML** | scikit-learn | 1.7.2 | Modelos de machine learning |
| **Dados** | pandas | 2.3.3 | Análise e manipulação de dados |
| **Numérica** | numpy | 2.3.5 | Computação numérica |
| **Ambiente** | python-dotenv | 1.2.1 | Variáveis de ambiente |

### Frontend

| Componente | Tecnologia | Versão | Propósito |
|-----------|-----------|--------|----------|
| **Framework** | Angular | 17+ | Framework SPA reativo |
| **Linguagem** | TypeScript | Último | Tipagem estática em JavaScript |
| **Estilos** | Tailwind CSS | Último | Utility-first CSS framework |
| **Gráficos** | ApexCharts | Último | Visualizações interativas |
| **Reatividade** | RxJS | Último | Programação reativa |
| **HTTP Client** | HttpClient | Integrado | Cliente HTTP |

### Base de Dados

| Aspecto | Tecnologia |
|--------|-----------|
| **Tipo** | SQLite (ficheiro local) |
| **Ficheiro** | `API/mental_health.db` |
| **Tabelas** | 20+ |
| **Registos** | 857 colaboradores, 851 avaliações |
| **Migrations** | Alembic com versionamento |

---

##  Instalação e Configuração

### Requisitos do Sistema

- **Python**: 3.9+ (recomendado 3.11)
- **Node.js**: 18+ (para Angular)
- **npm**: 8+ (gestor de pacotes Node)
- **Git**: Para controlo de versão
- **macOS/Linux/Windows**: Sistema operativo

### Passo 1: Clonar o Repositório

```bash
git clone <seu-repositorio>
cd Mental_Health_Final
```

### Passo 2: Configurar Backend

#### 2.1 Criar Ambiente Virtual Python

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate  # Windows
```

#### 2.2 Instalar Dependências

```bash
cd API
pip install -r ../requirements.txt
```

#### 2.3 Configurar Variáveis de Ambiente

Criar ficheiro `.env` na raiz da pasta `API`:

```env
# Database
DATABASE_URL=sqlite:///mental_health.db

# JWT Authentication
JWT_SECRET_KEY=sua_chave_secreta_super_segura_aqui_123456789
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# API
API_PORT=8000
API_HOST=0.0.0.0

# Ambiente
ENVIRONMENT=development
```

⚠️ **IMPORTANTE**: Alterar `JWT_SECRET_KEY` para uma chave única e segura em produção!

#### 2.4 Inicializar Base de Dados (Opcional)

Se a base de dados não existir:

```bash
python -m alembic upgrade head
```

### Passo 3: Configurar Frontend

#### 3.1 Instalar Dependências Node

```bash
cd FRONTEND
npm install
```

#### 3.2 Configurar Proxy (Já Incluído)

Ficheiro `FRONTEND/proxy.conf.json` já está configurado para:
- Redirecionar `http://localhost:4200/api/*` para `http://localhost:8000`

---

## 🚀 Como Executar

### Opção 1: Execução Manual (Recomendado para Desenvolvimento)

#### Terminal 1 - Backend

```bash
cd /Users/fabioceriaco/Mental_Health_Final/API

# Ativar ambiente virtual (se não estiver já ativo)
source ../venv/bin/activate

# Executar servidor FastAPI
python3 run.py
```

Será exibido:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

#### Terminal 2 - Frontend

```bash
cd /Users/fabioceriaco/Mental_Health_Final/FRONTEND

# Executar servidor Angular 
ng serve -o
```

Será exibido:
```
✔ Compiled successfully.
✔ Build successful.
```

**Aceder à Aplicação**: Abrir navegador em [http://localhost:4200](http://localhost:4200)

### Opção 2: Execução via Script (Se Disponível)

```bash
cd /Users/fabioceriaco/Mental_Health_Final
chmod +x start.sh
./start.sh
```

### Credenciais de Teste

Após a primeira execução, utilize credenciais de demonstração:

- **Email**: `demo@example.com`
- **Senha**: `12345`

---
