# Projeto de Monitoramento de Conexões de Rede

Este projeto monitora as conexões de rede ativas em um sistema Windows, enviando dados via MQTT e armazenando-os em um banco de dados PostgreSQL. O monitoramento é feito para um conjunto específico de portas, e as informações das conexões são formatadas em JSON.

## Primeiros Passos

### 1. Clonar o repositório

Clone o repositório do projeto para sua máquina local.

```bash
git clone https://github.com/Saulodtasso/Monitor_TCP.git
cd Monitor_TCP
```

### 2. Criar e ativar um ambiente virtual

Crie e ative um ambiente virtual para o projeto. Isso garante que as dependências do projeto não interfiram com outras instalações de pacotes Python no seu sistema.

#### No Windows:
```bash
python -m venv novo_ambiente
novo_ambiente\Scripts\activate
```

#### No MacOS/Linux:
```bash
python -m venv novo_ambiente
source novo_ambiente/bin/activate
```

### 3. Instalar as dependências

Com o ambiente virtual ativado, instale as dependências listadas no arquivo `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 4. Preencher o arquivo de configuração

Crie um arquivo chamado `config.ini` na raiz do projeto. Este arquivo deve conter as configurações para o MQTT, PostgreSQL e as portas a serem monitoradas.

Exemplo de `config.ini`:

```ini
[mqtt]
broker = 172.18.224.126
port = 1883
topic = topico/das/conexoes

[postgres]
dbname = postgres
user = postgres
password = postgres
host = 172.18.224.126
port = 5432

[monitor]
ports = 22,10052,49320,56233
```

### 5. Executar o script

Com tudo configurado, execute o script principal para iniciar o monitoramento das conexões.

```bash
python main.py
```

## Funcionamento do Projeto

1. **Configuração:** O script lê as configurações do arquivo `monitor.conf` para configurar as conexões com o broker MQTT e o banco de dados PostgreSQL, além de definir as portas que serão monitoradas.

2. **Conexão MQTT:** O script se conecta ao broker MQTT usando as configurações fornecidas e publica mensagens JSON no tópico especificado.

3. **Banco de Dados PostgreSQL:** O script se conecta ao banco de dados PostgreSQL e cria uma tabela (se não existir) para armazenar os dados das conexões monitoradas.

4. **Monitoramento de Conexões:** Utilizando a biblioteca `psutil`, o script monitora continuamente as conexões de rede para as portas especificadas. Ele detecta novas conexões e conexões fechadas, enviando essas informações via MQTT e inserindo-as no banco de dados.

5. **Formato de Dados:** As informações de cada conexão são formatadas em JSON com os seguintes campos:
   - `Time`: Timestamp do evento.
   - `Protocolo`: Tipo de protocolo (TCP/UDP).
   - `Endereço Local`: Endereço IP local.
   - `Porta Local`: Porta local.
   - `Endereço Remoto`: Endereço IP remoto.
   - `Porta Remota`: Porta remota.
   - `Estado`: Estado da conexão (conectado/desconectado).

### Estrutura do Projeto

- `main.py`: Script principal que realiza o monitoramento e envio dos dados.
- `config.ini`: Arquivo de configuração com as informações do MQTT, PostgreSQL e portas a serem monitoradas.
- `requirements.txt`: Lista de dependências do projeto.

## Notas

- Certifique-se de que o broker MQTT e o banco de dados PostgreSQL estão acessíveis e corretamente configurados antes de executar o script.
- O script foi desenvolvido e testado em um ambiente Windows. Algumas funcionalidades podem precisar de ajustes para outros sistemas operacionais.

## Licença

Este projeto está licenciado sob os termos da licença MIT. Veja o arquivo LICENSE para mais detalhes.

---

Sinta-se à vontade para contribuir com melhorias ou correções!
