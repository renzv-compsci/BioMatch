from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "BioMatch Flask server is running!"})

@app.route('/ping')
def ping():
    return jsonify({"status": "ok", "message": "pong"})

if __name__ == '__main__':
    app.run(debug=True)
