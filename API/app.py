import flask_cors, requests, mysql 
from flask import request, jsonify, make_response, Flask
from modelexecution import SVC, clean_df, filter_by_date

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

@app.route("/api/v1/models/svc/", methods=["GET"])
def model():
    # setup for verification of response
    args = request.args.to_dict()
    accepted_params = {
        "kernel" : {"default" : "linear", "accepted" : ["linear", "poly", "rbf", "sigmoid", "precomputed"]},
        "gamma" : {"default": "auto", "accepted" : ["scale", "auto"]}
    }

    valid_provided_params = [param for param in args.keys() if param in list(accepted_params.keys())]
    valid_provided_kernel = [val for val in accepted_params.get("kernel").get("accepted") if val == args.get("kernel")]
    valid_provided_gamma = [val for val in accepted_params.get("gamma").get("accepted") if val == args.get("gamma")] 

    if len(args) == 0:
        return make_response(jsonify(
            {
                "Warning" : "No parameters were specified. The accepted params are Gamma and Kernel. If neither are specified, their default values are used.",
                "Accuracy": round(SVC(df = clean_df), 3)*100
            }
        ), 200)
    elif len(valid_provided_gamma) == 0 and len(valid_provided_kernel) == 0:
           return make_response(jsonify({
                "Warning" : "The parameters specified for Gamma and/or Kernel were incorrect.",
                "Accuracy": round(SVC(df = clean_df), 3)*100
            }), 200) 

    # custom warning for incorrect gamma
    elif len(valid_provided_gamma) == 0:
        return make_response(jsonify({
                "Warning" : "Gamma was not correctly specified. The default value parameter for Gamma, 'auto,' was used.",
                "Accuracy": round(SVC(df = clean_df), 3)*100
            }), 200)

    elif len(valid_provided_kernel) == 0:
           return make_response(jsonify({
                "Warning" : "Kernel was not correctly specified. The default value Kernel, 'linear,' was used.",
                "Accuracy": round(SVC(df = clean_df), 3)*100
            }), 200) 

    elif len(args) == len(accepted_params):
        return make_response(jsonify({
            "Accuracy" : round(SVC(df = clean_df, params = args), 3),
            "Params" : \
                f"{valid_provided_params[0]}: {valid_provided_gamma[0]},"\
                f" {valid_provided_params[1]}: {valid_provided_kernel[0]}"
        }), 200)
    elif len(args) > 2:
        return make_response(jsonify({
                    "error" : "The only accetable parameters are Gamma and Kernel. You can specify one, both, or none."
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port = "80")