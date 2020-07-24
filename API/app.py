import flask_cors, requests, mysql 
from flask import request, jsonify, make_response, Flask
from modelexecution import logreg

app = Flask(__name__)
app.config["DEBUG"] = True
flask_cors.CORS(app)

@app.route("/", methods=["GET"])
def home():
    return jsonify(
        {
            "Hello" : "World"
        }
    )

@app.route("/api/v1/models/logreg/", methods=["GET"])
def model():
    args = request.args.to_dict()
    accepted_params = {
        "penalty" : {"default" : "l2"},
        "solver" : {"default": "lbfgs"}
    }
    valid_provided_params = [param for param in args.keys() if param in list(accepted_params.keys())]

    if len(args) == 0:
        response=  make_response(jsonify({"error": "please specify the model."}), 400)
        response.headers["The model must be specified."] = "Acceptable models include Logistic Regression, KNN, and SVC."
        return response

    if len(valid_provided_params) == len(accepted_params):
        return make_response(jsonify({"successful" : "you made a successful response!"}), 200)
    
    
    return jsonify(
        args
    )



if __name__ == "__main__":
    app.run(host="0.0.0.0", port = "80")