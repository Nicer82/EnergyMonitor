#! /usr/bin/python3
import json
import socket
from flask import Flask, request
from flask_restful import Resource, reqparse ,Api

app = Flask(__name__)
api = Api(app)

statedata = []

class State(Resource):
    def get(self, point):
        for pointdata in statedata:
            if(point == pointdata["point"]):
                return pointdata, 200
        return "point not found", 404
        #with open('/home/pi/EnergyMonitorRAM/state.json') as json_data:
        #    state = json.load(json_data)
        #return state, 200
    def put(self, point):
        # fetch the values from the post data
        
        newpointdata = json.loads(request.data)
        print(newpointdata)
        
        parser = reqparse.RequestParser()
        parser.add_argument("point")
        parser.add_argument("time")
        parser.add_argument("l1_current")
        parser.add_argument("l1_voltage")
        parser.add_argument("l1_power")
        parser.add_argument("l2_current")
        parser.add_argument("l2_voltage")
        parser.add_argument("l2_power")
        parser.add_argument("l3_current")
        parser.add_argument("l3_voltage")
        parser.add_argument("l3_power")
        parser.add_argument("total_current")
        parser.add_argument("total_voltage")
        parser.add_argument("total_power")
        args = parser.parse_args()
        
        # update in case the point already exists
        for pointdata in statedata:
            if(point == pointdata["point"]):
                pointdata["time"] = args["time"]
                pointdata["l1_current"] = args["l1_current"]
                pointdata["l1_voltage"] = args["l1_voltage"]
                pointdata["l1_power"] = args["l1_power"]
                pointdata["l2_current"] = args["l2_current"]
                pointdata["l2_voltage"] = args["l2_voltage"]
                pointdata["l2_power"] = args["l2_power"]
                pointdata["l3_current"] = args["l3_current"]
                pointdata["l3_voltage"] = args["l3_voltage"]
                pointdata["l3_power"] = args["l3_power"]
                pointdata["total_current"] = args["total_current"]
                pointdata["total_voltage"] = args["total_voltage"]
                pointdata["total_power"] = args["total_power"]
                return pointdata, 200
                
        # insert in case the point doesn't already exist
        pointdata = {
            "point": point,
            "time": args["time"],
            "l1_current": args["l1_current"],
            "l1_voltage": args["l1_voltage"],
            "l1_power": args["l1_power"],
            "l2_current": args["l2_current"],
            "l2_voltage": args["l2_voltage"],
            "l2_power": args["l2_power"],
            "l3_current": args["l3_current"],
            "l3_voltage": args["l3_voltage"],
            "l3_power": args["l3_power"],
            "total_current": args["total_current"],
            "total_voltage": args["total_voltage"],
            "total_power": args["total_power"]
        }
        statedata.append(pointdata)
        return pointdata, 201
                
api.add_resource(State, "/state/<string:point>")

if __name__ == "__main__":
    # Read configuration
    with open('/home/pi/EnergyMonitor/config.json') as json_data:
        config = json.load(json_data)
    
    # Get the current IP
    ip = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
    
    app.run(host=ip,debug=False,port=config["Api"]["Port"])
