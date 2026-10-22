import time
import json
import psutil
import numpy as np
import paho.mqtt.client as mqtt

# Crear cliente MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect("localhost", 1883, 60)

print(" Iniciando envío de métricas del sistema (Ctrl + C para detener)...")

try:
    while True:
        # Obtener uso de CPU y RAM con psutil
        cpu_usage = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory().percent
        
        # Ejemplo de uso de numpy: calcular un promedio simple o redondeo
        datos_cpu = np.array([cpu_usage])
        cpu_promedio = np.round(datos_cpu[0], 2)

        # Crear un diccionario con los datos
        payload = {
            "cpu_percent": float(cpu_promedio),
            "ram_percent": ram_usage,
            "timestamp": time.time()
        }

        # Convertir a texto JSON
        mensaje_json = json.dumps(payload)

        # Publicar en el tópico 'sistema/metricas'
        client.publish("sistema/metricas", mensaje_json)
        print(f" Enviado: {mensaje_json}")

        time.sleep(2)  # Esperar 2 segundos entre envíos

except KeyboardInterrupt:
    print("\n Envío detenido por el usuario.")
    client.disconnect()