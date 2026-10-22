import json
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC_BASE = "telemetria/#"

# Diccionario para almacenar el último sequence recibido de cada node_id
ultimos_secuencias = {}

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(" Suscriptor de Validación conectado exitosamente a Mosquitto")
        client.subscribe(TOPIC_BASE)
        print(f" Escuchando en el comodín '{TOPIC_BASE}'...\n")
    else:
        print(f" Error de conexión con código: {rc}")

def on_message(client, userdata, msg):
    topic = msg.topic
    
    # 1. Validación de Mensaje Mal Formado (JSON válido)
    try:
        data = json.loads(msg.payload.decode('utf-8'))
    except Exception as e:
        print(f" [ERROR MAL FORMADO] Mensaje en [{topic}] no es un JSON válido: {e}")
        return

    # 2. Validación de Campos Mínimos Requeridos
    campos_requeridos = ["node_id", "sequence", "timestamp"]
    for campo in campos_requeridos:
        if campo not in data:
            print(f" [ERROR CAMPO FALTANTE] Falta '{campo}' en mensaje de [{topic}]")
            return

    node_id = data["node_id"]
    seq = data["sequence"]

    # 3. Validar correspondencia entre el Tema y el Node_ID
    if node_id not in topic:
        print(f" [ERROR TEMA INCONSISTENTE] El node_id '{node_id}' no coincide con el tema '{topic}'")

    # 4. Control de Saltos de Secuencia y Duplicados
    if node_id in ultimos_secuencias:
        prev_seq = ultimos_secuencias[node_id]
        
        if seq == prev_seq:
            print(f" [ALERTA DUPLICADO] Nodo '{node_id}' envió Seq={seq} repetido.")
        elif seq < prev_seq:
            print(f" [ALERTA DESORDEN/REINICIO] Nodo '{node_id}' envió Seq={seq} (anterior era {prev_seq}).")
        elif seq > prev_seq + 1:
            saltos = seq - (prev_seq + 1)
            print(f" [ALERTA SALTO DE SECUENCIA] Nodo '{node_id}' perdió {saltos} mensaje(s). (Prev: {prev_seq}, Actual: {seq})")

    ultimos_secuencias[node_id] = seq

    # Resumen de Recepción Exitosa
    if "telemetria/ambiente" in topic:
        print(f" [OK AMBIENTE] Node: {node_id} | Seq: {seq} | Temp: {data.get('temperatura')}°C")
    elif "telemetria/vibracion" in topic:
        num_muestras = len(data.get("muestras", []))
        print(f" [OK VIBRACIÓN] Node: {node_id} | Seq: {seq} | Lote: {num_muestras} muestras")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()