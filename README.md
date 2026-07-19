# 📊 FinTrack — Sistema Completo de Gestão e Planejamento Financeiro Pessoal

[![Python](https://img.shields.io/badge/Python-3.14%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0%2B-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.59%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Poetry](https://img.shields.io/badge/Poetry-Dependency--Manager-blueviolet?logo=poetry&logoColor=white)](https://python-poetry.org/)
[![Licença](https://img.shields.io/badge/Licen%C3%A7a-MIT-green.svg)](LICENSE)

> **FinTrack** é uma solução web moderna e abrangente projetada para transformar o controle financeiro pessoal. Combinando gestão de fluxo de caixa, cartões de crédito, carteira de investimentos e planejamento orçamentário consciente (Regra 50/30/20), o FinTrack elimina planilhas complexas com uma arquitetura desacoplada de alta performance.

---

## 🎯 Por que o FinTrack?

### 💼 Para Usuários
Tenha visibilidade total do seu patrimônio e fluxo financeiro em uma única plataforma intuitiva:
- **Fluxo de Caixa & Recorrências:** Registre entradas e saídas pontuais ou recorrentes (com ou sem data limite).
- **Gestão de Cartões de Crédito:** Monitore faturas, fechamentos e parcelamentos futuros atrelados obrigatoriamente a cartões específicos.
- **Carteira de Investimentos:** Acompanhe aportes e operações por classe de ativo (Ações, FIIs, Renda Fixa, ETFs, Cripto e Internacional) com cálculo automático do **Preço Médio Ponderado**.
- **Planejamento Orçamentário Consciente:** Metodologia 50/30/20 com cálculo automático do **Disponível Livre para Gastar** e simulador de compras parceladas.

### 🧠 Para Recrutadores e Líderes Técnicos
Este projeto consolida princípios estritos de **clean code**, **arquitetura em camadas** e **segurança**:
- **Desacoplamento de Responsabilidades:** Backend em Django servindo APIs RESTful e um Frontend reativo desenvolvido em Streamlit utilizando o padrão **Repository / Service Pattern**.
- **Isolamento de Dados (Multi-tenancy Lógico):** Segurança rigorosa ao nível de ORM e API para impedir acesso a dados de outros usuários.
- **Auditoria & LGPD:** Exclusão definitiva de conta com janela de retenção temporária e exportação completa dos lançamentos em CSV (Art. 16 e 18 da LGPD).
- **Cobertura de Testes Automatizados:** Suíte de testes Django cobrindo isolamento de dados, upserts e integridade referencial.

---

## 🛠️ Arquitetura e Tecnologias

A aplicação adota uma estrutura desacoplada em duas camadas principais mantidas via **Poetry**:

```
 ┌────────────────────────┐                ┌────────────────────────┐
 │       STREAMLIT        │   API REST     │      DJANGO BACKEND    │
 │  (Frontend & Graphics) │ <────────────> │ (Security & Business)  │
 └────────────────────────┘     (JSON)     └────────────────────────┘
                                                       │
                                                       ▼
                                           ┌────────────────────────┐
                                           │       POSTGRESQL       │
                                           │   (Relational DB)      │
                                           └────────────────────────┘
```

* **Backend (Django 6 / Django REST Framework):** Autenticação segura por token, serialização, validação de regras de negócio, migrações e persistência de dados.
* **Frontend (Streamlit / Plotly):** Dashboard reativo com gráficos agrupados, formulários modernos em abas e layout responsivo.
* **Gerenciador de Dependências (Poetry):** Gerenciamento unificado de pacotes Python em ambiente virtual dedicado.

---

## 🚀 Módulos e Funcionalidades

- [X] **1. Dashboard Principal (`1_📊_Dashboard.py`):**
  - Indicadores globais (Saldo Atual, Total de Receitas, Total de Despesas e Fatura Atual).
  - Gráficos por Categoria e Evolução Mensal do Saldo.
  - Maiores despesas do mês e movimentações recentes.

- [X] **2. Receitas & Recorrências (`2_💰_Receitas.py`):**
  - Lançamento de receitas pontuais e recorrentes (Salários, Freelance, Rendimentos).
  - Suporte a data final limite para repetição automática.

- [X] **3. Despesas & Recorrências (`3_💸_Despesas.py`):**
  - Lançamento de saídas por categoria e meio de pagamento.
  - Suporte a despesas recorrentes (Aluguel, Assinaturas).

- [X] **4. Cartões & Parcelamentos (`4_💳_Cartao_e_Parcelamentos.py`):**
  - Cadastro de múltiplos cartões (Bandeira, Limite, Dias de Fechamento e Vencimento).
  - Lançamento de parcelamentos futuros vinculados compulsoriamente a um cartão.
  - Projeção de comprometimento de limite e metas de redução de dívidas.

- [X] **5. Gestão de Investimentos (`5_📈_Investimentos.py`):**
  - Cadastro de ativos e registro de operações de compra e venda.
  - Cálculo automático do **Preço Médio Ponderado** por ativo.
  - Gráfico de distribuição de carteira por classe de ativo.

- [X] **6. Categorias Personalizadas (`6_🏷️_Categorias.py`):**
  - Gestão de categorias por usuário com proteção contra remoção de categorias em uso (`PROTECT`).

- [X] **7. Perfil de Usuário & LGPD (`7_👤_Perfil.py`):**
  - Atualização de dados pessoais, personalização de moeda e foto de perfil.
  - Exportação de movimentações em CSV e exclusão de conta em conformidade com a LGPD.

- [X] **8. Planejamento Consciente 50/30/20 (`8_🎯_Planejamento_Consciente.py`):**
  - Configuração do planejamento base (auto-repetível nos meses subsequentes).
  - Indicador do **Disponível Livre** e Score de Saúde Financeira.
  - Simulador de novas compras no cartão de crédito.
  - Gráfico comparativo de Teto Ideal vs Realizado (Plotly).

---

## 🗄️ Modelo de Dados (DER)

```
+---------------------+           +------------------------+
|       USUARIO       | 1 : N     |      CONFIGCARTAO      |
| (Django auth_user)  |---------->|  - nome_exibicao       |
|  - id [PK]          |           |  - limite_cartao       |
|  - nome             |           |  - dia_fechamento      |
|  - email [Unique]   |           |  - dia_vencimento      |
|  - moeda            |           +------------------------+
+---------------------+                        |
     |           |                             | 1 : N
     | 1 : N     | 1 : N                       v
     v           v                        +------------------------+
+-------------+ +--------------------+    |      PARCELAMENTO      |
|  CATEGORIA  | | PLANEJAMENTOMENSAL |    |  - descricao           |
|  - nome     | |  - mes_referencia  |    |  - valor_total         |
|  - tipo     | |  - receita_esperada|    |  - num_parcelas        |
+-------------+ |  - alocacao 50/30/20|    |  - cartao_id [FK]      |
     |          +--------------------+    +------------------------+
     | 1 : N
     v
+------------------------------------+    +------------------------+
|            MOVIMENTACAO            |    |         ATIVO          |
|  - descricao                       |    |  - codigo_ticker       |
|  - valor                           |    |  - tipo_ativo          |
|  - tipo (RECEITA / DESPESA)        |    +------------------------+
|  - is_recorrente                   |                 | 1 : N
|  - frequencia_recorrencia          |                 v
|  - data_fim_recorrencia            |    +------------------------+
|  - categoria_id [FK]               |    |  OPERACAOINVESTIMENTO  |
|  - cartao_id [FK]                  |    |  - tipo_operacao (C/V) |
+------------------------------------+    |  - quantidade, preco   |
                                          +------------------------+
```

---

## 🏁 Como Rodar o Projeto Localmente

### Pré-requisitos
- Python 3.14+
- Poetry (`pip install poetry`)

### 1. Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/fintrack.git
cd fintrack
```

### 2. Instalar Dependências
```bash
poetry install
```

### 3. Executar o Backend (Django)
```bash
poetry run python manage.py migrate
poetry run python manage.py runserver
```

### 4. Executar o Frontend (Streamlit)
Em outro terminal (no mesmo diretório do projeto):
```bash
poetry run streamlit run dashboard/Home.py
```

---

## 🧪 Executando a Suíte de Testes Automatizados

Para validar o funcionamento das APIs, autenticação, upserts e isolamento de usuários:

```bash
poetry run python manage.py test
```

---

## ✉️ Contato & Conexões

* **Desenvolvedor:** Deyved Antonio
* **LinkedIn:** [linkedin.com/in/deyvedantonio](https://linkedin.com/in/deyvedantonio)
* **Portfólio:** [sistemaslotus.com.br](https://sistemaslotus.com.br)
* **E-mail:** [deyved.antonio@gmail.com](mailto:deyved.antonio@gmail.com)
