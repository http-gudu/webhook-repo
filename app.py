from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from datetime import datetime
from bson.json_util import dumps

app = Flask(__name__)

# MongoDB Atlas URI
app.config["MONGO_URI"] = "mongodb+srv://dibendrabehera96:password@cluster0.voy4n.mongodb.net/github_webhooks?retryWrites=true&w=majority&appName=Cluster0"

# Initialize MongoDB
mongo = PyMongo(app)
events_collection = mongo.db.events

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        print("✅ Webhook triggered")

        event_type = request.headers.get("X-GitHub-Event")
        print("🟡 Event type:", event_type)

        payload = request.get_json()
        print("📦 Payload received")

        event_data = {
            "author": None,
            "action": None,
            "source": None,
            "target": None,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        if event_type == "push":
            event_data["author"] = payload["pusher"]["name"]
            event_data["action"] = "pushed"
            event_data["source"] = payload["ref"].split("/")[-1]
            event_data["target"] = "main"

        elif event_type == "pull_request":
            event_data["author"] = payload["pull_request"]["user"]["login"]
            event_data["action"] = f'{payload["action"]} pull request'
            event_data["source"] = payload["pull_request"]["head"]["ref"]
            event_data["target"] = payload["pull_request"]["base"]["ref"]
            event_data["timestamp"] = payload["pull_request"]["created_at"]

        else:
            print("⚠️ Unhandled event type:", event_type)
            return jsonify({"message": f"{event_type} not handled"}), 200

        # Store in MongoDB
        events_collection.insert_one(event_data)
        print("✅ Event stored in MongoDB:", event_data)

        return jsonify({"message": "Event stored"}), 201

    except Exception as e:
        print("❌ Error in webhook handler:", str(e))
        return jsonify({"error": str(e)}), 400

@app.route("/get-events", methods=["GET"])
def get_events():
    try:
        events = list(events_collection.find().sort("timestamp", -1))
        return dumps(events), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
