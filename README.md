# 📊 FinTrack — Sistema de Gestão Financeira Pessoal

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2%2B-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.25%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Licença](https://img.shields.io/badge/Licen%C3%A7a-MIT-green.svg)](LICENSE)

> **FinTrack** é uma solução web moderna projetada para simplificar o controle financeiro pessoal, eliminando a complexidade e a rigidez das planilhas tradicionais. Com foco em uma experiência fluida, rápida e segura, o projeto consolida práticas sólidas de engenharia de software com uma arquitetura desacoplada de alta performance.

---

## 🎯 Por que o FinTrack?

### 💼 Para Clientes e Usuários
Esqueça as fórmulas quebradas do Excel e interfaces poluídas. O FinTrack oferece clareza visual instantânea sobre suas receitas, despesas e saldo acumulado. Em menos de 5 minutos, você cria sua conta, registra seus lançamentos, categoriza suas movimentações e visualiza a saúde real do seu bolso por meio de gráficos interativos e dinâmicos.

### 🧠 Para Recrutadores e Líderes Técnicos
Este projeto foi concebido sob princípios estritos de **clean code**, **design patterns** e **desacoplamento arquitetural**. Ele demonstra a aplicação prática de:
- **Separação de Responsabilidades (SoC):** Backend robusto em Django servindo de barreira de segurança e regras de negócio via API RESTful, e um Frontend interativo e analítico desenvolvido em Streamlit.
- **Isolamento de Dados (Multi-tenancy):** Camada lógica que garante que cada usuário acesse e manipule única e estritamente os seus próprios dados.
- **Design de Banco de Dados Otimizado:** Tabelas normalizadas para evitar redundâncias e acelerar a agregação analítica no dashboard.

---

## 🛠️ Arquitetura e Tecnologias

A aplicação adota uma estrutura moderna dividida em duas camadas principais que se comunicam de forma assíncrona via **JSON**:

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

* **Backend (Django / Django REST Framework):** Gerencia a autenticação segura (JWT/Token Sessions), persistência de dados, serialização, regras de negócio e integridade referencial.
* **Frontend (Streamlit):** Interface do usuário altamente dinâmica, renderizando gráficos modernos de dispersão, linhas de evolução e pizza para análise de despesas de forma imediata.
* **Banco de Dados (PostgreSQL):** Armazenamento de dados relacional e otimizado para lidar com crescimento escalonável.

---

## 🚀 Funcionalidades Atuais (v1 - MVP)

- [] **Autenticação Segura:** Criação de conta, Login, Logout e fluxo de Recuperação de Senha por e-mail.
- [] **Gestão de Perfil:** Atualização de dados pessoais, personalização da moeda de exibição (ex: R$, $) e upload de foto de perfil.
- [] **Gerenciador de Categorias:** Organização personalizada de despesas e receitas por usuário com validação de tipo.
- [] **Lançamento Unificado de Movimentações:** Cadastro rápido de entradas e saídas em um único fluxo simplificado.
- [] **Painel de Indicadores (Dashboard):**
  - KPI de Saldo Atual, Receitas e Despesas acumuladas.
  - Gráfico de Despesas por Categoria.
  - Histórico de Evolução Mensal do Saldo.
  - Listagem inteligente das 5 maiores despesas e últimos lançamentos.
- [] **Exportação de Dados:** Download instantâneo de todas as movimentações filtradas em formato CSV para portabilidade.

---

## 🗄️ Modelo de Dados (DER)

A estrutura do banco de dados foi construída focando em **normalização de dados** e **integridade referencial**:

```
+---------------------+
|       USUARIO       |
| (Django auth_user)  |
|  - id [PK]          |
|  - nome             |
|  - email [Unique]   |
|  - senha            |
|  - moeda            |
|  - foto_perfil      |
|  - data_cadastro    |
+---------------------+
     |           |
     | 1 : N     |
     |           | 1 : N
     v           |
+---------------------+
|      CATEGORIA      |
|  - id [PK]          |
|  - nome             |
|  - tipo             |
|  - usuario_id [FK]  |
+---------------------+
     |
     | 1 : N (Comportamento ON DELETE PROTECT)
     v
+---------------------+
|    MOVIMENTACAO     |
|  - id [PK]          |
|  - descricao        |
|  - valor            |
|  - tipo             |
|  - data             |
|  - categoria_id [FK]|
|  - forma_pagamento  |
|  - observacoes      |
|  - usuario_id [FK]  |
|  - data_criacao     |
|  - data_atualizacao |
+---------------------+
```

### Regras de Negócio Críticas Aplicadas:
1. **Proteção Anti-Exclusão:** O sistema impede a remoção de uma Categoria caso existam movimentações vinculadas a ela (`models.PROTECT`), preservando o histórico financeiro histórico e impedindo dados órfãos.
2. **Validação de Valor Positivo:** Receitas e Despesas devem obrigatoriamente possuir valores positivos maiores do que zero na camada de persistência. A sinalização é controlada pelo campo lógico `tipo`.

---

## 🏁 Como Rodar o Projeto Localmente

### Pré-requisitos
- Python 3.14 ou superior
- PostgreSQL (ou SQLite para desenvolvimento rápido local)

### 1. Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/fintrack.git
cd fintrack
```

### 2. Configurar o Backend (Django)
```bash
# Navegar até o diretório do backend
cd backend

# Criar e ativar o ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows use: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Executar as migrações do banco de dados
python manage.py migrate

# Executar o servidor de desenvolvimento
python manage.py runserver
```

### 3. Configurar o Frontend (Streamlit)
Abra um novo terminal no diretório raiz do projeto:
```bash
# Navegar até o diretório do dashboard/frontend
cd dashboard

# Criar e ativar o ambiente virtual do front
python -m venv venv
source venv/bin/activate

# Instalar dependências do frontend
pip install -r requirements.txt

# Iniciar a aplicação Streamlit
streamlit run Home.py
```

---

## 🔮 Futuro Roadmap (v2)

Desejamos expandir o ecossistema do FinTrack trazendo lógicas analíticas herdadas da engenharia reversa da planilha de origem:
- **Módulo de Cartão de Crédito:** Controle avançado de faturas, definição de limites e metas de redução mensal de dívidas.
- **Módulo de Parcelamentos Recorrentes:** Motor inteligente de projeção mensal para diluir compras parceladas nas faturas futuras automaticamente.
- **Planejamento Orçamentário:** Definição de metas de gastos máximos por categoria com alertas visuais de estouro.
- **Importação automática de extratos bancários** via extrato OFX/CSV ou APIs Open Finance.

---

## ✉️ Contato & Conexões

Se você é um recrutador procurando um desenvolvedor focado em **Django, APIs escaláveis e arquitetura limpa**, ou um cliente interessado em customizações para a sua empresa, sinta-se à vontade para entrar em contato!

* **Desenvolvedor:** Seu Nome Completo
* **LinkedIn:** [linkedin.com/in/seu-perfil](https://linkedin.com/in/seu-perfil)
* **Portfólio:** [seu-portfolio.dev](https://seu-portfolio.dev)
* **E-mail:** [seu-email@dominio.com](mailto:seu-email@dominio.com)
