import time
import json
import numpy as np
import paho.mqtt.client as mqtt

NODE_ID = "sim_vib_01"
TOPIC = f"telemetria/vibracion/{NODE_ID}"
BROKER = "localhost"
PORT = 1883

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, PORT, 60)

sequence = 0
print(f" Iniciando {NODE_ID} en tema '{TOPIC}' (100 muestras/s enviadas cada 1s)...")

try:
    while True:
        # Semilla fija para reproducibilidad basada en el número de secuencia
        np.random.seed(sequence)
        
        # Generar 100 muestras con señal base sinusoidal + ruido gaussiano
        t = np.linspace(0, 1, 100, endpoint=False)
        ruido = np.random.normal(0, 0.1, 100)
        senos = np.sin(2 * np.pi * 5 * t) + ruido
        
        # Inyectar una anomalía reproducible cada 5 secuencias
        if sequence % 5 == 0:
            senos[50] += 3.5  # Pico anómalo

        payload = {
            "node_id": NODE_ID,
            "sequence": sequence,
            "timestamp": time.time(),
            "frecuencia_muestreo_hz": 100,
            "muestras": np.round(senos, 4).tolist()
        }
        
        mensaje = json.dumps(payload)
        client.publish(TOPIC, mensaje)
        print(f"[{NODE_ID}] Enviado Lote Seq={sequence} (100 muestras)")
        
        sequence += 1
        time.sleep(1)

except KeyboardInterrupt:
    client.disconnect()
    print("\nSimulador de vibración detenido.")