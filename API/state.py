#! /usr/bin/python3
import json
from flask import Flask
from flask_restful import Resource, reqparse ,Api

app = Flask(__name__)
@app.route("/")

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
    app.run(host='192.168.1.55',debug=False,port=80)
