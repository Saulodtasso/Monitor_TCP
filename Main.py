import paho.mqtt.client as mqtt
import psutil,socket,json,configparser,time
from datetime import datetime
import psycopg2
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Ler as configurações do arquivo
config = configparser.ConfigParser()
config.read('config.ini')
print("================ Monitor ====================")

# Configurações do MQTT
MQTT_BROKER = config.get('mqtt', 'broker')
MQTT_PORT = config.getint('mqtt', 'port')
MQTT_TOPIC = config.get('mqtt', 'topic')

# Configurações do PostgreSQL
DB_NAME = config.get('postgres', 'dbname')
DB_USER = config.get('postgres', 'user')
DB_PASSWORD = config.get('postgres', 'password')
DB_HOST = config.get('postgres', 'host')
DB_PORT = config.get('postgres', 'port')

# Portas a serem monitoradas
PORTAS_MONITORADAS = set(map(int, config.get('monitor', 'ports').split(',')))

# Inicializa o cliente MQTT
mqtt_client = mqtt.Client()

# Funções de callback para o cliente MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Conectado ao broker MQTT com sucesso ( {MQTT_BROKER} : {MQTT_PORT} )")
        print(f"Enviando dados no Topico : ( {MQTT_TOPIC} )")
    else:
        print(f"Falha na conexão com o broker MQTT, código: {rc}")

def is_monitored_port(conn):
    return conn.laddr.port in PORTAS_MONITORADAS or (conn.raddr and conn.raddr.port in PORTAS_MONITORADAS)

mqtt_client.on_connect = on_connect

# Conectar ao broker MQTT
try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
except Exception as e:
    print(f"Erro ao conectar ao broker MQTT: {e}")

# Função para converter conexões em dicionários formatados
def connection_to_dict(conn):
    return {
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Protocolo": "TCP" if conn.type == socket.SOCK_STREAM else "UDP",
        "Endereço Local": conn.laddr.ip,
        "Porta Local": conn.laddr.port,
        "Endereço Remoto": conn.raddr.ip if conn.raddr else '',
        "Porta Remota": conn.raddr.port if conn.raddr else '',
        "Estado": conn.status
    }

# Função para criar a tabela no PostgreSQL
def create_table_if_not_exists():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        create_table_query = """
            CREATE TABLE IF NOT EXISTS conexoes (
                id SERIAL PRIMARY KEY,
                time TIMESTAMP,
                protocolo TEXT,
                endereco_local TEXT,
                porta_local INTEGER,
                endereco_remoto TEXT,
                porta_remota INTEGER,
                estado TEXT
            );
        """
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Conectado ao Postgres ( {DB_HOST} : {DB_PORT} )")
    except Exception as e:
        print(f"Erro ao criar tabela no PostgreSQL: {e}")

# Função para inserir dados no PostgreSQL
def insert_into_postgres(data):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO conexoes (time, protocolo, endereco_local, porta_local, endereco_remoto, porta_remota, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            data["Time"],
            data["Protocolo"],
            data["Endereço Local"],
            data["Porta Local"],
            data["Endereço Remoto"],
            data["Porta Remota"],
            data["Estado"]
        ))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erro ao inserir dados no PostgreSQL: {e}")

# Criar tabela se não existir
create_table_if_not_exists()

# Monitorar conexões ativas e enviar via MQTT
previous_connections = {}
print(f"Portas Monitoradas: {PORTAS_MONITORADAS}")

while True:
    current_connections = {conn: connection_to_dict(conn) for conn in psutil.net_connections(kind='inet') if is_monitored_port(conn)}

    # Detectar novas conexões
    new_connections = {conn: data for conn, data in current_connections.items() if conn not in previous_connections}
    for conn_data in new_connections.values():
        mqtt_client.publish(MQTT_TOPIC, json.dumps(conn_data))
        insert_into_postgres(conn_data)
    
    # Detectar conexões fechadas
    closed_connections = {conn: data for conn, data in previous_connections.items() if conn not in current_connections}
    for conn_data in closed_connections.values():
        conn_data["Estado"] = "Desconectado"
        mqtt_client.publish(MQTT_TOPIC, json.dumps(conn_data))
        insert_into_postgres(conn_data)
    
    previous_connections = current_connections
    
    # Aguardar um tempo antes de verificar novamente
    time.sleep(5)
