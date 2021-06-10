
flaskInst = __import__("flask").Flask("evalsr")
__import__("flask_cors").CORS(flaskInst)
