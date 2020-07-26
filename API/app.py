# import internal modules
from Responses.models import knn_response, svc_response
from Responses.sensors import summary
from Sensors.Photoresistor import Photoresistor
from Sensors.Humidity import Humidity
from Sensors.Temperature import Temperature
from Date.DateFiltering import Filter
# import external packages
import mysql, mysql.connector as connector
import numpy as np
import flask_cors, requests, mysql 
from flask import request, jsonify, make_response, Flask

app = Flask(__name__)
app.config["DEBUG"] = True
flask_cors.CORS(app) # cross-origin resource sharing

@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {
            "Hello" : "World"
        }
    )
# MODEL ENDPOINT
@app.route("/api/v1/model/<model>/", methods=["GET"])
def model(model):
    accepted_models = ["SVC", "KNN"]
    passed_model = model.lower()
    args = request.args.to_dict()

    if passed_model == "svc":
        return svc_response(model_params=args)
    elif passed_model == "knn":
        return knn_response(model_params = args)
    return make_response(jsonify({
        "error" : f"that model is not currently supported. Try: {', '.join(accepted_models)}"
    }))

# DATE ENDPOINT
@app.route("/api/v1/date/", methods=["GET"])
def date():
    acceptable_args = ["day", "month", "year"]
    args = request.args.to_dict()
    valid_args = [arg for arg in acceptable_args if args.get(arg)]

    fil = Filter()
    conn = connector.connect(user = 'root', password = "Dpm#1217", host='127.0.0.1',database='playground')
    res = fil.Date(connection = conn, day = str(args.get("day")), month= args.get("month"), year= str(args.get("year")))    
    return jsonify(res)

# SENSOR ENDPOINT    
@app.route("/api/v1/sensor/", defaults={"sensor_type" : None})
@app.route("/api/v1/sensor/<sensor_type>/")
def sensors(sensor_type):
    conn = connector.connect(user = 'root', password = "Dpm#1217",\
                        host='127.0.0.1',database='playground')

    # handle photoresistor
    if sensor_type.lower() == "photoresistor":
        return summary(connection = conn, sensor = Photoresistor(connection=conn), col="photoresistor")

    # handle temp
    elif sensor_type.lower() == "temp" or sensor_type.lower() == "temperature":
        return summary(connection=conn, sensor = Temperature(connection=conn), col="temp") 

    # handle humidity
    elif sensor_type.lower() == "humidity":
        return summary(connection=conn, sensor = Humidity(connection=conn), col="humidity")

    # otherwise
    return make_response(jsonify({
        "error" : "The only supported sensors for V1 are photoresistor, temperature, humidity."
    }))

@app.route("/api/v1/docs/")
def documentation():
    return "<h1>Documentation</h1>"
if __name__ == "__main__":
    app.run(host="0.0.0.0", port = "80")