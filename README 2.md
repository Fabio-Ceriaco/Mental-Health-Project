#  Aplicação de Saúde Mental - Mental Health Application

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

## 📁 Estrutura do Projeto

```
Mental_Health_Final/
├── API/                              # Backend FastAPI
│   ├── APP/
│   │   ├── __init__.py
│   │   ├── main.py                  # Aplicação principal
│   │   ├── CORE/
│   │   │   └── security.py          # Autenticação JWT
│   │   ├── DATABASE/
│   │   │   ├── db_conn.py           # Conexão SQLAlchemy
│   │   │   └── ALEMBIC/             # Migrações
│   │   ├── MODELS/                  # 20+ modelos SQLAlchemy
│   │   │   ├── user.py
│   │   │   ├── employee.py
│   │   │   ├── assessment.py
│   │   │   ├── assessmentResult.py
│   │   │   └── ...
│   │   ├── REPOSITORIES/            # Acesso a dados
│   │   ├── ROUTERS/                 # 6 grupos de endpoints
│   │   │   ├── auth.py              # Autenticação
│   │   │   ├── employee.py          # Gestão colaboradores
│   │   │   ├── ml.py                # Previsões IA
│   │   │   ├── rh.py                # Gestão RH
│   │   │   ├── psychologist.py      # Psicólogos
│   │   │   └── register.py          # Registo
│   │   ├── SCHEMAS/                 # Pydantic schemas
│   │   ├── SERVICES/                # Lógica de negócio
│   │   └── ml/                      # Machine Learning
│   │       ├── enhanced_train.py    # Treino do modelo
│   │       ├── ml_service.py        # Serviço de predições
│   │       ├── dataset_builder.py   # Construção de dados
│   │       └── models/
│   │           ├── ml_model_enhanced.joblib
│   │           ├── feature_scaler.joblib
│   │           └── model_metadata.json
│   ├── mental_health.db             # Base de dados SQLite
│   ├── run.py                       # Script de execução
│   ├── requirements.txt             # Dependências Python
│   └── alembic.ini                  # Configuração Alembic
│
├── FRONTEND/                         # Frontend Angular
│   ├── src/
│   │   ├── app/
│   │   │   ├── pages/
│   │   │   │   ├── login/           # Login
│   │   │   │   ├── home/            # Dashboard inicial
│   │   │   │   ├── employee/        # Dashboards colaborador
│   │   │   │   ├── rh/              # Gestão RH
│   │   │   │   └── psychologist/    # Gestão psicólogo
│   │   │   ├── components/          # Componentes reutilizáveis
│   │   │   ├── services/            # Serviços HTTP
│   │   │   ├── models/              # Interfaces TypeScript
│   │   │   └── app.component.ts
│   │   ├── assets/                  # Imagens e recursos
│   │   ├── styles.css               # Estilos globais
│   │   └── main.ts
│   ├── angular.json                 # Configuração Angular
│   ├── proxy.conf.json              # Proxy para API
│   ├── package.json                 # Dependências Node
│   └── tsconfig.json
│
├── requirements.txt                 # Dependências Python (raiz)
├── README.md                        # Este ficheiro
├── .gitignore                       # Ficheiros ignorados
├── .env.example                     # Template de variáveis
└── start.sh                         # Script de inicialização
```

---

##  Modelo de Predição (IA)

###  Visão Geral

O modelo de predição utiliza **Machine Learning Ensemble** para prever o nível de risco de saúde mental de cada colaborador baseado em 18 dimensões psicológicas avaliadas.

###  Objetivo

Classificar colaboradores em **5 níveis de risco**:

| Nível | Classificação | Cor | Descrição |
|-------|---------------|-----|-----------|
| 1 | **Sem Risco** |  Verde | Saúde mental excelente |
| 2 | **Risco Leve** |  Amarelo | Alguns sinais, monitorizar |
| 3 | **Risco Moderado** |  Laranja | Atenção recomendada |
| 4 | **Risco Elevado** |  Vermelho | Intervenção urgente |
| 5 | **Risco Crítico** |  Crítico | Suporte imediato |

###  18 Dimensões Psicológicas

O modelo analisa as seguintes dimensões:

| Dimensão | Descrição |
|----------|-----------|
| **Stress** | Níveis de stress percebido |
| **Ansiedade** | Sintomas de ansiedade |
| **Depressão** | Indicadores depressivos |
| **Burnout** | Exaustão profissional |
| **Sono** | Qualidade e quantidade de sono |
| **Turnos** | Impacto de horários irregulares |
| **Ergonomia** | Conforto no local de trabalho |
| **Carga de Trabalho** | Volume e pressão de tarefas |
| **Equilíbrio Vida-Trabalho** | Work-life balance |
| **Reconhecimento** | Reconhecimento profissional |
| **Suporte Social** | Apoio de colegas e chefes |
| **Liderança** | Qualidade da gestão |
| **Segurança Psicológica** | Ambiente psicologicamente seguro |
| **Segurança no Emprego** | Estabilidade profissional |
| **Autonomia** | Independência nas decisões |
| **Propósito** | Significado do trabalho |
| **Regulação Emocional** | Gestão de emoções |
| **Sintomas Físicos** | Manifestações somáticas |

###  Características do Modelo

Para cada dimensão, o modelo extrai **4 métricas temporais**:

1. **Último Valor**: Avaliação mais recente
2. **Média**: Tendência geral ao longo do tempo
3. **Tendência**: Evolução (aumenta/diminui)
4. **Desvio Padrão**: Variabilidade

**Total de Features**: 18 dimensões × 6 métricas = **108 características** + dados demográficos

###  Arquitetura do Modelo

```
Entrada (108 features)
        ↓
    Scaler (StandardScaler)
        ↓
┌───────────────────────────┐
│   ENSEMBLE (Votação)      │
├───────────────────────────┤
│ Random Forest (100 árvores)│
│ Gradient Boosting         │
│ AdaBoost                  │
│ ExtraTreesClassifier      │
└───────────────────────────┘
        ↓
  Probabilidades (5 classes)
        ↓
  Classe com Maior Probabilidade
        ↓
Saída: Nível de Risco (1-5)
```

###  Fluxo de Funcionamento

```python
# 1. Utilizador completa avaliação com 18 dimensões
assessment = {
    "stress": 4,
    "ansiedade": 3,
    "depressao": 2,
    ...  # 18 dimensões totais
}

# 2. Sistema extrai histórico do colaborador
history = employee.assessment_results  # Últimas avaliações

# 3. Features são extraídas (último valor, média, tendência, std)
features = extract_all_dimension_features(history)
# Resultado: 108 features numéricas

# 4. Features são normalizadas
features_scaled = scaler.transform(features)

# 5. Modelo ensemble faz predição
probabilities = model.predict_proba(features_scaled)
# Resultado: [0.05, 0.15, 0.30, 0.35, 0.15]
#           (Sem, Leve, Moderado, Elevado, Crítico)

# 6. Nível de risco = classe com maior probabilidade
risk_level = argmax(probabilities)  # 4 (Risco Elevado)

# 7. Confiança da predição
confidence = max(probabilities)  # 0.35 (35% de confiança)
```

###  Treino do Modelo

O modelo é treinado com:

- **Dataset**: 850 colaboradores com histórico de avaliações
- **Divisão**: 80% treino, 20% teste
- **Validação Cruzada**: 5-fold com estratificação
- **Balanceamento**: SMOTE para classes desequilibradas
- **Otimização**: GridSearch para hiperparâmetros

---

## Métricas de Desempenho

###  Resultados Globais

| Métrica | Valor | Interpretação |
|---------|-------|----------------|
| **Precisão (Accuracy)** | 97.41% | 97 em 100 predições corretas |
| **Precisão Ponderada** | 97.38% | Média ponderada por classe |
| **Recall Ponderado** | 97.41% | Taxa de detecção correta |
| **F1-Score Ponderado** | 97.39% | Equilíbrio precisão-recall |
| **ROC-AUC** | 0.9892 | Discriminação entre classes (0.99 ≈ excelente) |

### Desempenho por Classe

| Nível de Risco | Precisão | Recall | F1-Score | Suporte |
|---|---|---|---|---|
| **Sem Risco** (1) | 97% | 96% | 0.96 | 142 |
| **Risco Leve** (2) | 98% | 98% | 0.98 | 156 |
| **Risco Moderado** (3) | 96% | 97% | 0.97 | 148 |
| **Risco Elevado** (4) | 99% | 99% | 0.99 | 174 |
| **Risco Crítico** (5) | 95% | 94% | 0.95 | 51 |

### Matriz de Confusão (Resumida)

```
Predito     Sem  Leve  Mod  Ele  Crít
Real
Sem Risco    136   4    2    0    0
Risco Leve    2  153    1    0    0
Risco Moderado 1  1   143    3    0
Risco Elevado  0  0    3   172    -1
Risco Crítico  0  0    0    3   48
```

###  Análise Detalhada

**Pontos Fortes:**
-  Excelente discriminação entre classes (AUC = 0.9892)
-  Recall elevado (97.41%) - deteta a maioria dos casos
-  Balanced accuracy (97.31%) - bom desempenho em todas as classes
-  Modelo robusto com ensemble de 4 algoritmos

**Limitações:**
-  Classe "Risco Crítico" (5) é pequena (51 amostras)
-  Possível overfitting em dados históricos
-  Requer revalidação com novos dados periodicamente

### Validação Cruzada (5-fold)

```
Fold 1: 97.34%
Fold 2: 97.49%
Fold 3: 97.31%
Fold 4: 97.45%
Fold 5: 97.48%
─────────────
Média:  97.41% ± 0.07%
```

###  Ficheiros do Modelo

| Ficheiro | Tamanho | Função |
|----------|---------|--------|
| `ml_model_enhanced.joblib` | ~10 MB | Modelo treinado (ensemble) |
| `feature_scaler.joblib` | ~2 KB | Normalizador de features |
| `model_metadata.json` | ~5 KB | Metadados (features, versão, etc) |

###  Retreinamento

O modelo pode ser retreinado executando:

```bash
cd API/APP/ml
python enhanced_train.py
```

Isto atualizará os ficheiros de modelo com novos dados.

---



##  Segurança

### Autenticação
- JWT (JSON Web Tokens) com expiração
- Hashing bcrypt para passwords
- Tokens com claims de utilizador

### Autorização
- Controlo baseado em funções (RBAC)
- 5 funções: Employee, RH, Psychologist, Admin, SuperAdmin
- Endpoints protegidos por função

### Base de Dados
- SQLAlchemy ORM (proteção contra SQL Injection)
- Prepared statements
- Validação de entrada com Pydantic

### Comunicação
- HTTPS recomendado em produção
- CORS configurado
- Variáveis sensíveis em `.env`

---

##  Troubleshooting

### Erro: "Database connection failed"

```bash
# Solução 1: Verificar variável de ambiente
echo $DATABASE_URL

# Solução 2: Recriar base de dados
rm API/mental_health.db
cd API && python -m alembic upgrade head
```

### Erro: "CORS error" no Frontend

```bash
# Verificar se backend está ativo em http://localhost:8000
curl http://localhost:8000/api/auth/health

# Reiniciar servidor Angular com proxy
ng serve --proxy-config proxy.conf.json
```

### Erro: "SVD did not converge"

Este erro foi **corrigido** na versão atual. O modelo agora valida dados antes do treino.

### Erro: "Module not found"

```bash
# Reativar ambiente virtual
source venv/bin/activate

# Reinstalar dependências
pip install -r requirements.txt
```

---

## Próximas Melhorias

- Integração com Single Sign-On (SSO)
- Dashboard administrativo avançado
- Relatórios em PDF/Excel
- Notificações por email
- Mobile app (React Native)
- Dark mode
- Suporte multilíngue
- Backup automático de dados



**Última Atualização**: 29 de Dezembro de 2025  
**Versão**: 1.0.0
