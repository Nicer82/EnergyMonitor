#! /usr/bin/python3
import json
import socket
from flask import Flask
from flask_restful import Resource, reqparse ,Api

app = Flask(__name__)
api = Api(app)

with open('/home/pi/EnergyMonitorRAM/state.json') as json_data:
    state = json.load(json_data)

class State(Resource):
    def get(self):
        with open('/home/pi/EnergyMonitorRAM/state.json') as json_data:
            state = json.load(json_data)
        return state, 200

api.add_resource(State, "/state")

if __name__ == "__main__":
    # Read configuration
    with open('/home/pi/EnergyMonitor/config.json') as json_data:
        config = json.load(json_data)
    
    # Get the current IP
    ip = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
    
    app.run(host=ip,debug=False,port=config["Api"]["Port"])
