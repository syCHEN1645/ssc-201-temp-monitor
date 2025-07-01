import paho.mqtt.client as mqtt
import ssl
import time
import json
from pymongo import MongoClient
# from datetime import datetime
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
db = client_mongo["test"]
coll_solar = db["test-data-solar"]
coll_compare = db["test-data-compare"]

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

    data = {
        "temp": msg_d["temp"],
        "date": date,
        "time": time
        # no longer need as msg itself is timestamped
        # "timestamp": datetime.now()
    }
    if (sensor_name == "solar"):
        collection = coll_solar
    elif (sensor_name == "compare"):
        collection = coll_compare
    try:
        result = collection.insert_one(data)
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