import paho.mqtt.client as mqtt
import ssl
import time
import json
from pymongo import MongoClient
from config import BROKER, USERNAME, PASSWORD, MONGO_URI

# mqtt broker info
broker = BROKER
port = 8883
username = USERNAME
password = PASSWORD
topic = "thermocouple-readings"

# mongodb info
mongo_uri = MONGO_URI
client_mongo = MongoClient(mongo_uri)
db_compare = client_mongo["temp-compare"]
db_solar = client_mongo["temp-solar"]

# connection state
is_connected = False

def on_connect(client, userdata, flags, rc):
    global is_connected
    if rc == 0:
        print("Connected successfully")
        is_connected = True
        client.subscribe(topic)
    else:
        print(f"Connection failed with code {rc}")
        is_connected = False

def on_disconnect(client, userdata, rc):
    global is_connected
    print("Disconnected from broker")
    is_connected = False

def on_message(client, userdata, msg):
    print(f"Received message: '{msg.payload.decode()}' on topic '{msg.topic}'")
    # pass to mongodb
    msg_d = json.loads(msg.payload.decode())
    sensor_name = msg_d["sensor"]
    date_time = msg_d["time"].split()
    date = int(date_time[0])
    time = int(date_time[1])
    if (sensor_name == "solar"):
        db = db_solar
    elif (sensor_name == "compare"):
        db = db_compare
    
    coll = db[f"{date}"]

    data = {
        "temp": msg_d["temp"],
        "time": time
    }

    try:
        result = coll.insert_one(data)
        print(f"Inserted into MongoDB with _id: {result.inserted_id}")
    except Exception as e:
        print(f"Failed to insert into MongoDB: {e}")


# mqtt setup
client_mqtt = mqtt.Client()
client_mqtt.username_pw_set(username, password)
client_mqtt.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)

client_mqtt.on_connect = on_connect
client_mqtt.on_disconnect = on_disconnect
client_mqtt.on_message = on_message



# loop_start() is non-blocking and concurrent
client_mqtt.loop_start()
# loop_forever() is blocking codes after it
# client.loop_forever()

# reconnect if connection is broken
while True:
    if not is_connected:
        try:
            client_mqtt.connect(broker, port, keepalive=60)
        except Exception as e:
            print(f"Connection failed: {e}")
    time.sleep(10)