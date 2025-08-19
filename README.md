# Conthabil - Desafio Técnico: Automação Python

Este repositório contém a solução para o desafio técnico de Desenvolvedor Python da Conthabil.
O projeto é uma aplicação Python que automatiza o processo de busca (scraping), upload e armazenamento de publicações do diário oficial da prefeitura.

A aplicação foi containerizada usando Docker e orquestrada com Docker Compose, garantindo um ambiente de desenvolvimento e execução consistente e fácil de gerenciar. Foram selecionadas bibliotecas e ferramentas alinhadas as melhores práticas e ao ecossistema Python moderno, visando melhor experiência de desenvolvimento, maior robustez e facilidade de manutenção futura.


**NOTA**: Não havia especificações de testes, mas como finalizei o projeto com algum tempo de folga, implementei testes básicos para os endpoints e adicionei outras melhorias não previstas em especificação, Embora que em um contexto real de dia a dia de desenvolvimento, só faria implementações extras após alinhar previamente com o responsável pela especificação e com o time.


## Deploy da Aplicação

Hospedei a aplicação no seguinte endereço: **[URL_DA_APLICACAO_AQUI]**

Neste endereço, é possível acessar o endpoint de listar e filtrar inserções por competência, assim como a documentação e interface gráfica Swagger com mais dados sobre a aplicação em **[URL_DA_DOCUMENTACAO_SWAGGER_AQUI]**.


## Funcionalidades Principais

- **Scraper**: Utiliza Selenium para navegar no site `https://www.natal.rn.gov.br/dom` e baixar todas as publicações do diário oficial referentes ao mês anterior ao mês atual.
- **Uploader**: Faz o upload dos arquivos PDF baixados para `https://0x0.st` e recupera suas URLs públicas.
- **Armazenamento em Banco de Dados**: Armazena as URLs públicas e as datas de publicação em uma tabela em um banco de dados PostgreSQL.
- **Armazenamento Idempotente**: A função de criação de registros no banco de dados (`crud.py`) verifica a existência de duplicatas por URL, garantindo que a mesma publicação não seja armazenada múltiplas vezes, tornando a operação idempotente.
- **API Pública**: Uma aplicação FastAPI que fornece endpoints para listar e filtrar os registros de diários oficiais armazenados.
- **Orquestrador**: Um script principal que executa todo o fluxo de trabalho de ponta a ponta que poderia por ex ser executado com um cronjob ou uma chamada de API.


## Tecnologias Utilizadas

- **Linguagem**: Python 3.13
- **Gerenciador de Pacotes**: `uv`
- **Coleta de Dados Web**: Selenium
- **Framework da API**: FastAPI
- **Banco de Dados**: PostgreSQL
- **ORM**: SQLAlchemy
- **Cliente HTTP**: httpx
- **Containerização**: Docker, Docker Compose


## Estrutura do Projeto

O projeto segue um layout `src` para separar a lógica de negócio dos arquivos de configuração, mantendo a organização buscando honrar as melhores práticas de packaging do Python.

```
/
├── docker-compose.yml
├── docker-entrypoint.sh # Script de entrada para o contêiner Docker
├── Dockerfile
├── main.py              # Ponto de entrada da aplicação FastAPI
├── pyproject.toml
├── README.md
├── .env.example         # Exemplo de arquivo de variáveis de ambiente
├── .python-version      # Define a versão do Python utilizada pelo projeto (ex. para pyenv)
├── requirements.txt     # Dependências do projeto
├── uv.lock              # Arquivo de lock de dependências do uv para builds reprodutíveis
├── src/
│   └── conthabil/
│       ├── __init__.py
│       ├── api_client.py    # Cliente para comunicar com a nossa própria API
│       ├── config.py        # Gerencia e valida variáveis de ambiente usando Pydantic Settings, garantindo robustez e tipagem.
│       ├── crud.py          # Operações de Leitura/Escrita no banco
│       ├── database.py      # Gerenciamento da sessão do DB
│       ├── initialize_db.py # Script para criar as tabelas iniciais
│       ├── main_runner.py   # Orquestrador principal do fluxo
│       ├── models.py        # Modelos de tabela do SQLAlchemy
│       ├── schemas.py       # Modelos de dados do Pydantic
│       ├── scraper.py       # Lógica de scraping com Selenium
│       └── uploader.py      # Lógica de upload de arquivos
└── tests/
    ├── conftest.py      # Configurações e fixtures para testes Pytest
    └── test_api.py      # Testes para a API

```


## Padrões de Código e Documentação

Este projeto busca aderir a boas práticas de desenvolvimento, incluindo:

-   **Docstrings Abrangentes**: Busquei implementar em todas as funções e métodos críticos documentação com docstrings claras e informativas, descrevendo seu propósito, argumentos e valores de retorno.
-   **Logging Detalhado**: A aplicação utiliza um sistema de logging configurado para registrar eventos importantes, facilitando o rastreamento e a depuração do fluxo de execução.
-   **Gerenciamento de Recursos com Context Managers**: O Scraper utiliza o protocolo de context manager (`with` statement) para garantir que o WebDriver do Selenium seja inicializado e, crucialmente, encerrado de forma limpa e automática, mesmo em caso de erros, prevenindo vazamentos de recursos.
-   **Processamento Concorrente com Multithreading**: Visando otimizar a eficiência no scraping e upload de arquivos, foi implementado processamento concorrente utilizando multithreading. Esta abordagem foi escolhida em detrimento de soluções assíncronas devido à natureza síncrona da biblioteca Selenium. O número de workers foi limitado para evitar respostas 429 (Misdirected Request) dos servidores de destino, garantindo mais estabilidade as operações.


## Decisões de Design Arquitetural

Tomei a decisão arquitetural de fazer a comunicação entre o orquestrador (`main_runner.py`) e a aplicação FastAPI (`main.py`) via chamadas HTTP para a API, em vez de chamadas diretas às funções da camada de banco de dados. Esta abordagem prioriza:

-   **Separação de Responsabilidades**: Cada componente (scraper, uploader, API, orquestrador) possui uma responsabilidade distinta e bem definida.
-   **API como Contrato**: A FastAPI define uma interface clara e consistente para a interação de dados, garantindo que todos os clientes (incluindo o `main_runner.py`) adiram às mesmas regras e validações.
-   **Escalabilidade e Deploy Independentes**: Os componentes podem ser escalados e implantados de forma independente, oferecendo flexibilidade para crescimento futuro.
-   **Robustez e Manutenibilidade**: Alterações em um componente (por exemplo, mudar o banco de dados de postgres para mysql) não impactam necessariamente outros, desde que o contrato da API permaneça estável.


## -> Rodando o Projeto

### Pré-requisitos

- Docker
- Docker Compose

### Configuração

1.  **Clone o repositório:**
     ```bash
     git clone https://github.com/felixoakz/conthabil_test.git # via HTTPS
     git clone git@github.com:felixoakz/conthabil_test.git #via SSH

     cd conthabil_test
     ```

2.  **Crie o arquivo de ambiente:**
    Copie o arquivo de ambiente de exemplo. Os valores padrão já estão configurados para funcionar com o `docker-compose.yml`.
    ```bash
    cp .env.example .env
    ```

3.  **Builde e inicie os serviços:**
    Este comando irá construir a imagem `app` e iniciar os containeres `app`, `db` e `selenium` em modo de segundo plano (detached).
    ```bash
    docker-compose up -d --build
    ```
    As tabelas do banco de dados serão criadas e o logging da aplicação será configurado automaticamente na inicialização do contêiner 'app' através do script 'docker-entrypoint.sh'.

### Executando a Automação

Com os serviços Docker em execução, execute o script principal do fluxo de trabalho dentro do contêiner `app`:

```bash
docker-compose exec app python -m src.conthabil.main_runner
```

Isso irá disparar o processo completo:
1.  Busca dos PDFs no site.
2.  Upload dos arquivos para `0x0.st`.
3.  Armazenamento das URLs resultantes no banco de dados PostgreSQL através da API.


## Utilizando a API


A API estará acessivel localmente em `http://localhost:8000` (ou na porta `APP_PORT` que você definiu em `.env`).

- **Documentação Interativa (Swagger UI)**: Acesse [http://localhost:8000/docs](http://localhost:8000/docs) para visualizar a documentação interativa da API, que inclui todos os endpoints, seus detalhes e um interface gráfica para testar as requisições diretamente no navegador.
- **URL Base da API**: `http://localhost:8000/api`

#### Endpoints

- `GET /api/gazettes/`: Lista todos os diários oficiais armazenados.
- `GET /api/gazettes/?month=8&year=2025`: filtra os diários oficiais por mês e ano ao passar parametros extras para o mesmo endpoint.
- `POST /api/gazettes/`: Cria uma nova entrada de diário oficial (usado internamente pelo `main_runner`).


## Testes

Os testes são escritos com `pytest` e utilizam mocks para simular as interações com o banco de dados, permitindo que sejam executados de forma independente, sem a necessidade de ter os contêineres Docker em execução e mais simples comparado a usar db in memoria com sqlite.

O arquivo `tests/conftest.py` é necessário para que o `pytest` consiga localizar os módulos da aplicação (como `main.py`), resolvendo problemas de importação durante a execução dos testes.

### Como Executar os Testes

1.  **Instale as dependências de desenvolvimento:**
    A partir da raiz do projeto, instale as dependências principais e as de desenvolvimento (`pytest`):
    ```bash
    uv pip install -e '.[dev]'
    ```

2.  **Execute a suíte de testes:**
    Com as dependências instaladas, execute o `pytest`:
    ```bash
    pytest
    ```


## -> Possíveis Melhorias e Implementações

Esta seção lista melhorias e funcionalidades que podem ser consideradas para o futuro do projeto:

-   **Tratamento de Erros Aprimorado**: Implementar estratégias de retry e circuit breaker para operações externas (scraping, upload, chamadas de API), tornando a aplicação mais tolerante a falhas pois verifiquei que o site da prefeitura não responde bem em algumas chamadas sequenciais.
-   **Deploy em Produção**: Implementar um pipeline de CI/CD para automação do deploy em ambientes de produção de acordo com a branch, utilizando ferramentas como Gunicorn para o servidor ASGI.
-   **Melhoria dos Testes**: Expandir a cobertura de testes com mais testes unitários, de integração e end-to-end, garantindo a robustez da aplicação.
-   **Gerenciamento de Conexões DB**: Refatorar o gerenciamento de sessões de banco de dados no `main.py` utilizando decorators ou dependências mais avançadas do FastAPI para um controle mais limpo e eficiente.
-   **Migrações de Banco de Dados**: Adotar uma ferramenta de migração de banco de dados (ex. Alembic) para gerenciar as alterações de esquema de forma controlada e versionada.
-   **Autenticação e Autorização da API**: Implementar mecanismos de segurança (ex. OAuth2, JWT) para proteger os endpoints da API, caso ela seja exposta publicamente.
-   **Processamento Assíncrono com Filas de Mensagens**: Integrar filas de mensagens (ex. RabbitMQ, Kafka) para desacoplar o processo de scraping/upload da API, permitindo escalabilidade e resiliência.
-   **Monitoramento e Alerta**: Adicionar ferramentas de monitoramento (ex. Prometheus, Grafana) para acompanhar a saúde da aplicação e configurar alertas para anomalias ou falhas críticas.
-   **Otimização para Grande Volume de Arquivos**: Se o volume de arquivos a serem processados aumentar significativamente, considerar a transição de um processamento em lote para um processamento por arquivo (download, upload, inserção) com concorrência interna. Isso otimizaria o uso de recursos (memória e disco) e permitiria um fluxo mais contínuo, embora exigisse uma orquestração de concorrência mais granular.

