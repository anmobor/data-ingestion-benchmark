import paho.mqtt.client as mqtt
import click
from app.s3todb.timescalewide import run

if __name__ == "__main__":
    run()
