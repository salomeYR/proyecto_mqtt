import paho.mqtt.client as mqtt

# Función que se ejecuta cuando nos conectamos al servidor
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(" Conectado exitosamente al broker Mosquitto")
        # Nos suscribimos al tema/tópico 'sistema/metricas'
        client.subscribe("sistema/metricas")
        print(" Escuchando mensajes en el tópico: sistema/metricas...\n")
    else:
        print(f" Error al conectar. Código de respuesta: {rc}")

# Función que se ejecuta cuando llega un mensaje nuevo
def on_message(client, userdata, msg):
    print(f" Message recibido en [{msg.topic}]: {msg.payload.decode('utf-8')}")

# Crear el cliente MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

# Conectar al broker local (localhost) en el puerto 1883
client.connect("localhost", 1883, 60)

# Mantener la escucha continua
client.loop_forever()