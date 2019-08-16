#! /usr/bin/python3
import json
import socket
import time
from flask import Flask, request
from flask_restful import Resource, reqparse ,Api

# Read configuration
with open('/home/pi/EnergyMonitor/config.json') as json_data:
    config = json.load(json_data)

app = Flask(__name__)
api = Api(app)

statedata = []
volumedata = []
volumestart = time.time() DIV config["Api"]["VolumeDataSeconds"] * config["Api"]["VolumeDataSeconds"]
volumeend = volumestart + config["Api"]["VolumeDataSeconds"]

class State(Resource):
    def get(self, point):
        for pointdata in statedata:
            if(point == pointdata["point"]):
                return pointdata, 200
        return "point not found", 404
    def put(self, point):
        # fetch the values from the post data
        newpointdata = json.loads(request.data.decode('ascii'))
        
        # update in case the point already exists
        for pointdata in statedata:
            if(point == pointdata["point"]):
                pointdata["time"] = newpointdata["time"]
                pointdata["l1_current"] = newpointdata["l1_current"]
                pointdata["l1_voltage"] = newpointdata["l1_voltage"]
                pointdata["l1_power"] = newpointdata["l1_power"]
                pointdata["l2_current"] = newpointdata["l2_current"]
                pointdata["l2_voltage"] = newpointdata["l2_voltage"]
                pointdata["l2_power"] = newpointdata["l2_power"]
                pointdata["l3_current"] = newpointdata["l3_current"]
                pointdata["l3_voltage"] = newpointdata["l3_voltage"]
                pointdata["l3_power"] = newpointdata["l3_power"]
                pointdata["total_current"] = newpointdata["total_current"]
                pointdata["total_voltage"] = newpointdata["total_voltage"]
                pointdata["total_power"] = newpointdata["total_power"]
                return pointdata, 200
                
        # insert in case the point doesn't already exist
        statedata.append(newpointdata)
        return pointdata, 201
                
api.add_resource(State, "/state/<string:point>")

if __name__ == "__main__":
    # Get the current IP
    ip = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
    
    app.run(host=ip,debug=False,port=config["Api"]["Port"])
