import time
import json
import random
import paho.mqtt.client as mqtt

NODE_ID = "sim_ambiente_01"
TOPIC = f"telemetria/ambiente/{NODE_ID}"
BROKER = "localhost"
PORT = 1883

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, PORT, 60)

sequence = 0
print(f" Iniciando {NODE_ID} en tema '{TOPIC}' (envío cada 10s)...")

try:
    while True:
        payload = {
            "node_id": NODE_ID,
            "sequence": sequence,
            "timestamp": time.time(),
            "temperatura": round(20.0 + random.uniform(-2, 2), 2),
            "humedad": round(50.0 + random.uniform(-5, 5), 2)
        }
        
        mensaje = json.dumps(payload)
        client.publish(TOPIC, mensaje)
        print(f"[{NODE_ID}] Enviado Seq={sequence}")
        
        sequence += 1
        time.sleep(10)

except KeyboardInterrupt:
    client.disconnect()
    print("\nSimulador de ambiente detenido.")