#Reference, paho
#based on: https://pypi.org/project/paho-mqtt/#client
from flask import Flask, request, render_template
from pybluemonday import StrictPolicy
import paho.mqtt.client as mqtt
import requests, json, sys, time, ssl

strict = StrictPolicy()

broker = "*insert IP"
broker_port = 1883

# The callback for when the client receives a CONN-ACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and reconnect then subscriptions will be renewed.
    client.subscribe("Citydata")

def on_publish(client, userdata, mid):
    print("Message Published")

def send_to_MQTT(msg):
    client = mqtt.Client()
    client.username_pw_set("user", password="test")
    client.on_connect = on_connect
    client.on_publish = on_publish

    client.connect(broker, port=broker_port, keepalive=60)
    client.publish("Citydata", payload=msg, qos=0, retain=False)
    client.disconnect()

app = Flask(__name__, template_folder = "./")

@app.route("/", methods=["POST"])
def send(): 
  print(request.form)
  city = strict.sanitize(request.form.get("city"));
  print (city)
  if not city:
    return "Invalid input"
  send_to_MQTT(city)
  return (city + " Published") 
@app.route("/", methods=["GET"])
def home():
  return  render_template("index.html")
app.run(host="0.0.0.0", port=80)
