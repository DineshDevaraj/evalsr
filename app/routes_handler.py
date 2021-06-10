
from flask import jsonify
from flask import request
from flask import render_template

from app import evaluvator
from app.flask_inst import flaskInst
from app.stock_actions import Recommendation
from app.database_handler import RecommendationCollection
from app.exceptions_definition import ArgumentError

@flaskInst.route("/", methods=["GET", "POST"])
def home_page():

    return render_template("home_page.html")

@flaskInst.route("/api", methods=["GET", "POST"])
def top():

    pass

@flaskInst.route("/api/help", methods=["GET"])
def help():

    return jsonify({
        "/help": "show the list of APIs and their functions"
    })

@flaskInst.route("/api/add_recommendations", methods=["POST"])
def add_recommendations():

    try:
        RecommendationCollection.add(Recommendation(request.form))
        result = {
            "status": "success",
            "message": "recommendation add success"
        }
    except ArgumentError as ex:
        result = {
            "status": "error",
            "message": ex.message
        }

    return jsonify(result)

@flaskInst.route("/api/calculate_profitloss", methods=["POST"])
def calculate_profitloss():

    try:

        symbolSetString = request.form.get("symbolSet", None)
        if symbolSetString is None: symbolSet = set()
        else: symbolSet = symbolSetString.split(";")
        result = evaluvator.calculate_profitloss(symbolSet)
        result["message"] =  "evaluvation run success"
        result["status"] = "success"

    except ArgumentError as ex:
        
        result = {
            "status": "error",
            "message": ex.message
        }

    return jsonify(result)
