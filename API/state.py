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

class State(Resource):
    def get(self, point):
        for statepointdata in statedata:
            if(point == statepointdata["point"]):
                return statepointdata, 200
        return "point not found", 404
    def put(self, point):
        # fetch the values from the post data
        newstatepointdata = json.loads(request.data.decode('ascii'))
        return self.registerState(point,newstatepointdata)
    def registerState(self, point, newstatepointdata):
        # update in case the point already exists
        for statepointdata in statedata:
            if(point == statepointdata["point"]):
                print("{}-{}".format(newstatepointdata["time"],statepointdata["time"]))
                self.updatevolume(newstatepointdata, statepointdata["time"])
                statepointdata["time"] = newstatepointdata["time"]
                statepointdata["l1_current"] = newstatepointdata["l1_current"]
                statepointdata["l1_voltage"] = newstatepointdata["l1_voltage"]
                statepointdata["l1_power"] = newstatepointdata["l1_power"]
                statepointdata["l2_current"] = newstatepointdata["l2_current"]
                statepointdata["l2_voltage"] = newstatepointdata["l2_voltage"]
                statepointdata["l2_power"] = newstatepointdata["l2_power"]
                statepointdata["l3_current"] = newstatepointdata["l3_current"]
                statepointdata["l3_voltage"] = newstatepointdata["l3_voltage"]
                statepointdata["l3_power"] = newstatepointdata["l3_power"]
                statepointdata["total_current"] = newstatepointdata["total_current"]
                statepointdata["total_voltage"] = newstatepointdata["total_voltage"]
                statepointdata["total_power"] = newstatepointdata["total_power"]
                return statepointdata, 200
                
        # insert in case the point doesn't already exist
        statedata.append(newstatepointdata)
        print("initialized statedata")
        return newstatepointdata, 201
    def updatevolume(self, statepointdata, prevtime):
        # Calculate the volume data for the current state (part 1)
        volumestartfromprevstate =  prevtime // config["Api"]["VolumeDataSeconds"] * config["Api"]["VolumeDataSeconds"]
        volumestartfromcurstate = statepointdata["time"] // config["Api"]["VolumeDataSeconds"] * config["Api"]["VolumeDataSeconds"]
        print("{} --> {}".format(prevtime, volumestartfromprevstate))
        print("{} --> {}".format(statepointdata["time"], volumestartfromcurstate))
        if(volumestartfromcurstate != volumestartfromprevstate):
            newvolumepointdata = self.calcvolumepointdatafromstatepointdata(statepointdata,volumestartfromprevstate,(volumestartfromcurstate-prevtime))
        else:
            newvolumepointdata = self.calcvolumepointdatafromstatepointdata(statepointdata,volumestartfromprevstate,(statepointdata["time"]-prevtime))
        
        # update the already collected volume data with the current state
        updatedvolumepointdata = {}
        for volumepointdata in volumedata:
            if(statepointdata["point"] == volumepointdata["Point"]):
                volumepointdata["NumReads"] += 1
                volumepointdata["SupplyWh"] += newvolumepointdata["SupplyWh"]
                volumepointdata["SupplyMaxW"] = max([volumepointdata["SupplyMaxW"],newvolumepointdata["SupplyMaxW"]])
                volumepointdata["SupplyMinW"] = min([volumepointdata["SupplyMinW"],newvolumepointdata["SupplyMinW"]])
                volumepointdata["UsageWh"] += newvolumepointdata["UsageWh"]
                volumepointdata["UsageMaxW"] = max([volumepointdata["UsageMaxW"],newvolumepointdata["UsageMaxW"]])
                volumepointdata["UsageMinW"] = min([volumepointdata["UsageMinW"],newvolumepointdata["UsageMinW"]])
                updatedvolumepointdata = volumepointdata
                break
                
        # in case no volume was available for the point, add it
        if(updatedvolumepointdata == {}):
            volumedata.append(newvolumepointdata)
            updatedvolumepointdata = newvolumepointdata

        # Write the volume data to the backend if it is complete
        if(volumestartfromcurstate != volumestartfromprevstate):
            self.writevolume(volumepointdata)
            
            # Calculate the volume data for the current state (part 2)
            newvolumepointdata = self.calcvolumepointdatafromstatepointdata(statepointdata,volumestartfromprevstate,(statepointdata["time"]-volumestartfromcurstate))
        
            # overwrite the previous volume data with the current state (part 2)
            for volumepointdata in volumedata:
                if(statepointdata["point"] == volumepointdata["Point"]):
                    volumepointdata["VolumeStart"] = volumestartfromcurstate
                    volumepointdata["NumReads"] = newvolumepointdata["NumReads"]
                    volumepointdata["SupplyWh"] = newvolumepointdata["SupplyWh"]
                    volumepointdata["SupplyMaxW"] = newvolumepointdata["SupplyMaxW"]
                    volumepointdata["SupplyMinW"] = newvolumepointdata["SupplyMinW"]
                    volumepointdata["SupplyAvgW"] = 0
                    volumepointdata["UsageWh"] = newvolumepointdata["UsageWh"]
                    volumepointdata["UsageMaxW"] = newvolumepointdata["UsageMaxW"]
                    volumepointdata["UsageMinW"] = newvolumepointdata["UsageMinW"]
                    volumepointdata["UsageAvgW"] = 0
                    break
        return
    def calcvolumepointdatafromstatepointdata(self, statepointdata, volumestart, readtime):
        statevolumewh = statepointdata["total_power"] * (readtime) / 3600
        if(statevolumewh < 0):
            statevolumesupplywh = 0
            statevolumeusagewh = abs(statevolumewh)
        else:
            statevolumesupplywh = statevolumewh
            statevolumeusagewh = 0
        newvolumepointdata = {
            "VolumeStart": volumestart,
            "Point": statepointdata["point"],
            "NumReads": 1,
            "SupplyWh": statevolumesupplywh,
            "SupplyMaxW": statevolumesupplywh,
            "SupplyMinW": statevolumesupplywh,
            "UsageWh": statevolumeusagewh,
            "UsageMaxW": statevolumeusagewh,
            "UsageMinW": statevolumeusagewh
        }
        return newvolumepointdata     
    def writevolume(self, volumepointdata):
        volumepointdata["SupplyAvgW"] = volumepointdata["SupplyWh"] / config["Api"]["VolumeDataSeconds"] * 3600
        volumepointdata["UsageAvgW"] = volumepointdata["UsageWh"] / config["Api"]["VolumeDataSeconds"] * 3600
        print(volumepointdata)
        return
                        
api.add_resource(State, "/state/<string:point>")

if __name__ == "__main__":
    # Get the current IP
    ip = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
    
    app.run(host=ip,debug=False,port=config["Api"]["Port"])
