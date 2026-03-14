<div align="center">

# 🩺 Hygeia Digital

**Sistema de busca ativa para rastreamento de câncer de colo do útero e mama**

*Hackathon Hygeia Digital 2025 · Faculdade de Medicina de Botucatu · UNESP*

[![Python](https://img.shields.io/badge/Python-3.14+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Twilio](https://img.shields.io/badge/Twilio-WhatsApp-F22F46?style=flat-square&logo=twilio&logoColor=white)](https://twilio.com)
[![License](https://img.shields.io/badge/Licença-MIT-22C55E?style=flat-square)](LICENSE)

</div>

---

## 📋 Sumário

- [Sobre o projeto](#-sobre-o-projeto)
- [O problema](#-o-problema)
- [A solução](#-a-solução)
- [Funcionalidades](#-funcionalidades)
- [Tecnologias](#-tecnologias)
- [Arquitetura](#-arquitetura)
- [Estrutura de diretórios](#-estrutura-de-diretórios)
- [Instalação e execução](#-instalação-e-execução)
- [Configuração do ambiente](#-configuração-do-ambiente)
- [Como usar](#-como-usar)
- [API Reference](#-api-reference)
- [Fluxo de rastreamento](#-fluxo-de-rastreamento)
- [Evoluções futuras](#-evoluções-futuras)
- [Autores](#-autores)

---

## 🎯 Sobre o projeto

O **Hygeia Digital** é uma plataforma web desenvolvida durante o **Hackathon Hygeia Digital 2025**, promovido pela Faculdade de Medicina de Botucatu (UNESP), com o objetivo de modernizar e ampliar o alcance das ações de rastreamento de câncer de colo do útero e mama no SUS.

O sistema automatiza a **busca ativa de pacientes**, enviando convites personalizados via WhatsApp, processando respostas automaticamente e organizando os agendamentos — tudo em um painel de controle acessível para as equipes de saúde.

---

## 🔍 O problema

Em municípios como Botucatu, o rastreamento organizado abrange milhares de mulheres entre 25 e 64 anos. O processo tradicional de convocação enfrenta limitações críticas:

- 📞 **Alto índice de chamadas não atendidas** nas abordagens por telefone
- 🚧 **Barreiras de acesso à informação** em comunidades vulneráveis
- ⏱️ **Processo manual e lento** entre o primeiro contato e a realização do exame
- 📊 **Ausência de indicadores** para monitorar cobertura e efetividade
- 🔄 **Dificuldade de escala** para abranger toda a população-alvo

---

## 💡 A solução

O Hygeia Digital resolve esses problemas com uma plataforma que:

1. **Importa automaticamente** a lista de pacientes a partir de planilhas Excel ou CSV geradas pelos sistemas de saúde existentes
2. **Dispara mensagens personalizadas** via WhatsApp para todas as pacientes elegíveis com um clique
3. **Processa respostas automaticamente** — quando a paciente responde "SIM", o agendamento é criado e a confirmação é enviada instantaneamente
4. **Exibe indicadores em tempo real** — cobertura, taxa de resposta, distribuição por UBS e faixa etária
5. **Respeita o opt-out** — pacientes que respondem "PARAR" são removidas das próximas listas automaticamente

---

## ✨ Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| 📥 Importação de planilhas | Suporte a `.xlsx`, `.xls` e `.csv` com normalização automática de dados |
| 📱 Envio via WhatsApp | Integração com Twilio (Sandbox e produção) e Meta Cloud API |
| 🤖 Webhook automático | Processa respostas das pacientes em tempo real |
| 📅 Agendamento automático | Cria agendamento ao receber confirmação da paciente |
| 📅 Agendamento manual | Permite agendar diretamente pelo painel informando o telefone |
| 📊 Dashboard com gráficos | Métricas de cobertura, status de convites, UBS e faixas etárias |
| 👩‍⚕️ Gestão de pacientes | Tabela paginada com busca, filtros por UBS e status |
| 📋 Gestão de agendamentos | Visualização e atualização de status (realizado / cancelado) |
| 🔕 Opt-out respeitado | Pacientes que pedem para sair não recebem mais mensagens |
| 📖 API documentada | Swagger UI e ReDoc disponíveis automaticamente |

---

## 🛠️ Tecnologias

**Backend**
- [Python 3.11+](https://python.org) — linguagem principal
- [FastAPI](https://fastapi.tiangolo.com) — framework web assíncrono de alta performance
- [SQLAlchemy 2.0](https://sqlalchemy.org) — ORM robusto para acesso ao banco de dados
- [SQLite](https://sqlite.org) — banco de dados local, sem configuração extra
- [Pandas](https://pandas.pydata.org) — leitura e processamento de planilhas
- [Twilio](https://twilio.com) — envio de mensagens WhatsApp
- [Uvicorn](https://www.uvicorn.org) — servidor ASGI de produção
- [Jinja2](https://jinja.palletsprojects.com) — templates HTML server-side

**Frontend**
- HTML5 semântico com Jinja2 templating
- CSS3 puro com variáveis customizadas (sem framework)
- [Chart.js 4](https://chartjs.org) — gráficos interativos
- [Lucide Icons](https://lucide.dev) — ícones SVG leves
- Google Fonts: DM Serif Display + DM Sans
- JavaScript ES2022 (vanilla, sem bundler)

---

## 🏗️ Arquitetura
```
Navegador  ←→  FastAPI (Uvicorn)
                   │
          ┌────────┼────────────┐
          │        │            │
       Jinja2   Routers      SQLite
      Templates  ├─ dashboard    │
                 ├─ api       SQLAlchemy
                 └─ webhook      │
                      │       service.py
                   Twilio     (lógica de
                   API         negócio)
```

O sistema segue o padrão **MVC simplificado**:
- **Models** → `app/models.py` (Person, Invitation, Appointment)
- **Views** → `app/templates/` (Jinja2 + Chart.js)
- **Controllers** → `app/routers/` (dashboard, api, webhook)
- **Services** → `app/service.py` (toda a lógica de negócio isolada)

---

## 📁 Estrutura de diretórios
```
hygeia/
├── app/
│   ├── __init__.py
│   ├── main.py               # App FastAPI, rotas, lifespan
│   ├── models.py             # Modelos do banco (Person, Invitation, Appointment)
│   ├── db.py                 # Engine SQLite e gerenciador de sessão
│   ├── service.py            # Lógica de negócio (importação, convites, métricas)
│   ├── notify.py             # Envio de mensagens (console / Twilio / Meta)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── dashboard.py      # Rotas HTML (páginas)
│   │   ├── api.py            # Rotas JSON (consumidas pelo JS)
│   │   └── webhook.py        # Webhook Twilio WhatsApp
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css     # Estilos completos
│   │   └── js/
│   │       ├── app.js        # Interatividade (fetch, toast, sidebar)
│   │       └── charts.js     # Gráficos Chart.js
│   └── templates/
│       ├── base.html         # Layout base (sidebar, topbar, toast)
│       ├── dashboard.html    # Painel principal
│       ├── patients.html     # Listagem de pacientes
│       └── appointments.html # Listagem de agendamentos
├── data/
│   └── simulated_com_cep_nascimento.xlsx  # Dados simulados do hackathon
├── scripts/
│   └── send_test.py          # Script de teste de envio
├── .env.example              # Modelo de variáveis de ambiente
├── .gitignore                # Arquivos ignorados pelo Git
├── requirements.txt          # Dependências Python
├── run.py                    # Ponto de entrada da aplicação
└── README.md                 # Este arquivo
```

---

## 🚀 Instalação e execução

### Pré-requisitos

- Python 3.14 ou superior
- pip

### Passo a passo

**1. Clone o repositório**
```bash
git clone https://github.com/seu-usuario/hygeia-digital.git
cd hygeia-digital
```

**2. Crie e ative o ambiente virtual**
```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o .env com suas credenciais (veja a seção abaixo)
```

**5. Execute a aplicação**
```bash
python run.py
```

**6. Acesse no navegador**
```
http://localhost:8000
```

---

## ⚙️ Configuração do ambiente

Copie `.env.example` para `.env` e preencha os valores:
```env
# Modo de notificação: console (dev) | twilio | whatsapp
NOTIFIER=console

# Credenciais Twilio (necessárias se NOTIFIER=twilio)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_WHATSAPP_TO=whatsapp:+5514900000000

# Banco de dados (SQLite por padrão)
DATABASE_URL=sqlite:///./hygeia.db

# Servidor
HOST=0.0.0.0
PORT=8000
```

### Modos de notificação

| Modo | Descrição | Quando usar |
|---|---|---|
| `console` | Imprime mensagens no terminal | Desenvolvimento e testes |
| `twilio` | Envia via WhatsApp (Twilio) | Demonstração e produção |
| `whatsapp` | Envia via Meta Cloud API | Produção com WABA aprovado |

### Configurando o Twilio Sandbox

1. Acesse [console.twilio.com](https://console.twilio.com)
2. Vá em **Messaging → Try it out → Send a WhatsApp message**
3. Siga as instruções para conectar seu número ao Sandbox
4. Copie as credenciais para o `.env`

### Configurando o Webhook (para receber respostas)

Para processar as respostas das pacientes localmente, use o [ngrok](https://ngrok.com):
```bash
# Em um terminal separado
ngrok http 8000
```

Configure a URL gerada no Twilio Console:
```
https://xxxx.ngrok.io/twilio/webhook
```

---

## 📖 Como usar

### 1. Importar pacientes

- Na tela principal, arraste ou selecione um arquivo `.xlsx` ou `.csv`
- Clique em **Importar arquivo**
- O sistema normaliza os telefones, remove duplicatas e cria os convites automaticamente

### 2. Disparar convites

- Edite a mensagem template se necessário (suporta `{primeiro_nome}`, `{ubs}`)
- Defina o limite de envios por rodada
- Clique em **Enviar convites**

### 3. Processar respostas automaticamente

- Com o webhook configurado, as respostas chegam em tempo real
- Paciente responde **SIM** → agendamento criado, confirmação enviada
- Paciente responde **PARAR** → opt-out ativado automaticamente

### 4. Gerenciar pacientes

- Acesse **Pacientes** na sidebar
- Use os filtros por UBS e status para segmentar
- Ative/desative opt-out diretamente na tabela

### 5. Acompanhar agendamentos

- Acesse **Agendamentos** na sidebar
- Marque consultas como **realizadas** ou **canceladas**
- Acompanhe os indicadores no dashboard

---

## 📡 API Reference

A documentação completa da API está disponível em:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### Endpoints principais

| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/api/import` | Importa pacientes de arquivo |
| `POST` | `/api/invite` | Dispara convites pendentes |
| `POST` | `/api/schedule` | Cria agendamento manual |
| `GET` | `/api/metrics` | Retorna métricas em JSON |
| `GET` | `/api/patients` | Lista pacientes (paginado) |
| `PUT` | `/api/patients/{id}/optout` | Alterna opt-out da paciente |
| `PUT` | `/api/appointments/{id}/status` | Atualiza status do agendamento |
| `POST` | `/twilio/webhook` | Recebe respostas via WhatsApp |

---

## 🔄 Fluxo de rastreamento
```
1. Importação
   Planilha Excel/CSV
        │
        ▼
2. Cadastro automático
   Person + Invitation (pending)
        │
        ▼
3. Disparo de convites
   WhatsApp → paciente
        │
        ▼
4. Resposta da paciente
   "SIM" via WhatsApp
        │
        ▼
5. Webhook processa
   Invitation → responded
   Appointment → scheduled
        │
        ▼
6. Confirmação enviada
   WhatsApp ← sistema
        │
        ▼
7. Acompanhamento
   Dashboard + tabelas
```

---

## 🔭 Evoluções futuras

- [ ] **Autenticação** — login por equipe de saúde com controle de acesso
- [ ] **Relatórios exportáveis** — PDF/Excel com indicadores por período
- [ ] **Agendamento inteligente** — sugestão de horários baseada na disponibilidade da UBS
- [ ] **Mapa de cobertura** — visualização geográfica por bairro/CEP
- [ ] **Integração com e-SUS** — importação direta da base nacional
- [ ] **Múltiplos municípios** — suporte multi-tenant para outras regiões do SUS
- [ ] **App mobile** — PWA para agentes de saúde em campo
- [ ] **IA para priorização** — identificação de grupos de maior risco com base em dados históricos
- [ ] **Lembretes automáticos** — reenvio para pacientes que não responderam após N dias
- [ ] **Dashboard para gestores** — visão consolidada por regional de saúde

---

## 👥 Autores

Desenvolvido com 💚 pela equipe do Hackathon Hygeia Digital 2025:

| Nome | GitHub |
|---|---|
| Carlos Gabriel | [@carlosgabriel](https://github.com) |
| Gustavo Vital | [@gustavovital](https://github.com) |
| Renam Augusto | [@renamaugusto](https://github.com) |

**Faculdade de Medicina de Botucatu — UNESP**
Hackathon Hygeia Digital 2025

---

<div align="center">

*"A tecnologia a serviço da saúde pública — porque prevenir salva vidas."*

</div>