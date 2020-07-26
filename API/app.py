import flask_cors, requests, mysql 
from flask import request, jsonify, make_response, Flask
from Models.SVC import SVC
from Models.KNN import KNN
import numpy as np
from Models.Data import X_train, X_test, y_train, y_test

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

def  svc_response(model_params = None):
    """
    Outlines the logic for a api/v1/model/svc/ GET request. The parameters are checked
    in various ways. They 1. Must fit be an acceptable parameter, kernel and / or gamma,
    and 2. Must have accurate values attached to each parameter (e.g. they must be denoted
    as a valid argument by sklearn).
    """
    accepted_params = {
        "kernel" : {"default" : "linear", "accepted" : ["linear", "poly", "rbf", "sigmoid", "precomputed"]},
        "gamma" : {"default": "auto", "accepted" : ["scale", "auto"]}
    }
    valid_provided_params = [param for param in model_params.keys() if param in list(accepted_params.keys())]
    valid_provided_kernel = [val for val in accepted_params.get("kernel").get("accepted") if val == model_params.get("kernel")]
    valid_provided_gamma = [val for val in accepted_params.get("gamma").get("accepted") if val == model_params.get("gamma")] 

    if len(model_params) == 0:
        default = {"kernel" : "linear", "gamma" : "auto"}
        model = SVC(params= default)
        results = model.buildModel(X_train, X_test, y_train, y_test, params= default)
        return make_response(jsonify(
                    {
                        "Warning" : "No parameters were specified. The accepted params are Gamma and Kernel. If neither are specified, their default values are used.",
                        "Results": results
                    }
                ), 200)
    elif len(valid_provided_gamma) == 0 and len(valid_provided_kernel) == 0:
        default = {"kernel" : "linear", "gamma" : "auto"}
        model = SVC(params= default)
        results = model.buildModel(X_train, X_test, y_train, y_test, params= default)
        return make_response(jsonify({
                "Warning" : "The parameters specified for Gamma and Kernel were incorrect.",
                "Results": results
            }), 200) 

    # custom warning for incorrect gamma
    elif len(valid_provided_gamma) == 0:
        default = {"kernel" : "linear", "gamma" : "auto"}
        model = SVC(params= default)
        results = model.buildModel(X_train, X_test, y_train, y_test, params= {"kernel" : " ".join(valid_provided_kernel), "gamma" : accepted_params.get("gamma").get("default")})
        return make_response(jsonify({
                "Warning" : "Gamma was not correctly specified. The default value parameter for Gamma, 'auto,' was used.",
                "Results": results
            }), 200)
    # custom warning for incorrect kernel
    elif len(valid_provided_kernel) == 0:
        model = SVC(params= {"kernel" : accepted_params.get("kernel").get("default"), "gamma" : " ".join(valid_provided_gamma)})
        results = model.buildModel(X_train, X_test, y_train, y_test)
        return make_response(jsonify({
                "Warning" : "Kernel was not correctly specified. The default Kernel value, 'linear,' was used.",
                "Results": results
            }), 200) 

    elif len(model_params) == len(accepted_params):
        model = SVC(params= model_params)
        results = model.buildModel(X_train, X_test, y_train, y_test, params=model_params)
        return make_response(jsonify({
            "Results" : results,
            "Params" : \
                f"{valid_provided_params[0]}: {valid_provided_gamma[0]},"\
                f" {valid_provided_params[1]}: {valid_provided_kernel[0]}"
        }), 200)
    elif len(model_params) > 2:
        return make_response(jsonify({
                    "error" : "The only accetable parameters are Gamma and Kernel. You can specify one, both, or none."
                }))

def knn_response(model_params = None):
    """
    Outlines the logic for a api/v1/model/knn/ GET request. The parameters are checked
    in various ways. They 1. Must fit be an acceptable parameter, kernel and / or gamma,
    and 2. Must have accurate values attached to each parameter (e.g. they must be denoted
    as a valid argument by sklearn).
    """
    accepted_params = {
        "n_neighbors" : {"default" : 5, "accepted" : list(np.arange(0, 25, 1))},
        "algorithm" : {"default" : "auto", "accepted":["kd_tree", "ball_tree", "brute", "auto"]}
    }
    try:
        if model_params.get("n_neighbors"):
            model_params["n_neighbors"] = int(model_params["n_neighbors"])
    except ValueError as e:
        return make_response(jsonify({
            "error" : "n_neighbors must be an integer between 0 and"
        }))
    valid_provided_params = [param for param in model_params.keys() if param in list(accepted_params.keys())]
    valid_provided_neighbors = [val for val in accepted_params.get("n_neighbors").get("accepted") if val == model_params.get("n_neighbors")]
    valid_provided_algo = [val for val in accepted_params.get("algorithm").get("accepted") if val == model_params.get("algorithm")] 

    if len(model_params) == 0:
        default = {"n_neighbors" : 5, "algorithm" : "auto"}
        model = KNN(params= default)
        results = model.buildModel(X_train, X_test, y_train, y_test, params= default)
        return make_response(jsonify(
                    {
                        "Warning" : "No parameters were specified. The accepted params are Gamma and Kernel. If neither are specified, their default values are used.",
                        "Results": results
                    }
                ), 200)
    elif len(valid_provided_neighbors) == 0 and len(valid_provided_algo) == 0:
        default = {"n_neighbors" : 5, "algorithm" : "auto"}
        model = KNN(params= default)
        results = model.buildModel(X_train, X_test, y_train, y_test, params= default)
        return make_response(jsonify({
                "Warning" : "The parameters specified for n_neighbors and algorithm were incorrect.",
                "Results": results
            }), 200) 

    # custom warning for incorrect n_neighbors
    elif len(valid_provided_neighbors) == 0:
        default = {"kernel" : "linear", "gamma" : "auto"}
        model = KNN(params= default)
        results = model.buildModel(X_train, X_test, y_train, y_test, params= {"algorithm" : " ".join(valid_provided_algo), "n_neighbors" : accepted_params.get("n_neighbors").get("default")})
        return make_response(jsonify({
                "Warning" : "n_neighbors was not correctly specified. The default value parameter for n_neighbors, 5, was used.",
                "Results": results
            }), 200)
    # custom warning for incorrect kernel
    elif len(valid_provided_algo) == 0:
        params = {"algorithm" : accepted_params.get("algorithm").get("default"), "n_neighbors" : valid_provided_neighbors[0]}
        model = KNN(params= params)
        results = model.buildModel(X_train, X_test, y_train, y_test, params=params)
        return make_response(jsonify({
                "Warning" : "Algorithm was not correctly specified. The default Algorithm value, 'auto,' was used.",
                "Results": results
            }), 200) 

    elif len(model_params) == len(accepted_params):
        model = KNN(params= model_params)
        results = model.buildModel(X_train, X_test, y_train, y_test, params=model_params)
        return make_response(jsonify({
            "Results" : results,
            "Params" : \
                f"{valid_provided_params[0]}: {valid_provided_neighbors[0]},"\
                f" {valid_provided_params[1]}: {valid_provided_algo[0]}"
        }), 200)
    elif len(model_params) > 2:
        return make_response(jsonify({
                    "error" : "The only accetable parameters are Gamma and Kernel. You can specify one, both, or none."
                }))

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

@app.route("/api/v1/date/", methods=["GET"])
def date():
    acceptable_args = ["day", "month", "year"]
    args = request.args.to_dict()
    valid_args = [arg for arg in acceptable_args if args.get(arg)]

    return jsonify({
        "res" : filter_by_date(day = args.get("day"), month= args.get("month"), year=args.get("year")),
        "args" : args,
        "valid_args" : valid_args
    })

# SENSOR ENDPOINT    
@app.route("/api/v1/sensor/", defaults={"sensor_type" : "..."})
@app.route("/api/v1/sensor/<sensor_type>")
def sensors(sensor_type):
    return jsonify({
        "Hello" : f"Welcome to {sensor_type}"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port = "80")