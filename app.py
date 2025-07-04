from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import certifi

app = Flask(__name__)

# ✅ MongoDB Atlas connection
client = MongoClient(
    "mongodb+srv://mrunalghare7:YgArQ0uu1KC141A4@webhook-cluster.ada12s6.mongodb.net/?retryWrites=true&w=majority&appName=webhook-cluster",
    tls=True,
    tlsCAFile=certifi.where()
)
db = client['webhook_db']
collection = db['events']

print("✅ MongoDB Connected Successfully")

# ✅ Home route
@app.route('/')
def home():
    return render_template('index.html')

# ✅ Test MongoDB connection
@app.route('/testdb')
def testdb():
    test_data = {
        "author": "Mrunal",
        "event": "test_connection",
        "timestamp": datetime.utcnow()
    }
    collection.insert_one(test_data)
    return "Inserted test data to MongoDB Atlas!"

# ✅ Webhook receiver route
@app.route('/webhook', methods=['POST'])
def github_webhook():
    try:
        data = request.json or {}
        event_type = request.headers.get('X-GitHub-Event', 'unknown')

        payload = {
            "event": event_type,
            "timestamp": datetime.utcnow()
        }

        if event_type == "push":
            payload.update({
                "author": data.get('pusher', {}).get('name', 'unknown'),
                "to_branch": data.get('ref', '').split('/')[-1]
            })

        elif event_type == "pull_request":
            payload.update({
                "author": data.get('pull_request', {}).get('user', {}).get('login', 'unknown'),
                "from_branch": data.get('pull_request', {}).get('head', {}).get('ref', ''),
                "to_branch": data.get('pull_request', {}).get('base', {}).get('ref', ''),
                "action": data.get("action", "")
            })

            if data.get("action") == "closed" and data.get("pull_request", {}).get("merged"):
                payload["event"] = "merge"
                payload["merged_by"] = data.get("pull_request", {}).get("merged_by", {}).get("login", "unknown")

        collection.insert_one(payload)
        return jsonify({"status": "received"}), 200

    except Exception as e:
        print(f"❌ Webhook Error: {e}")
        return jsonify({"error": "Webhook processing failed"}), 500

# ✅ Ping health check
@app.route('/ping')
def ping():
    return "pong", 200

# ✅ Display recent GitHub events
@app.route('/events', methods=['GET'])
def get_events():
    try:
        latest_events = list(collection.find().sort("timestamp", -1).limit(10))
        cleaned_events = []

        for e in latest_events:
            timestamp = e.get("timestamp", datetime.utcnow())
            if not isinstance(timestamp, datetime):
                timestamp = datetime.utcnow()

            event = {
                "event": e.get("event", "unknown"),
                "timestamp": timestamp.strftime('%d %b %Y - %I:%M %p UTC'),
                "author": e.get("author", "N/A"),
                "to_branch": e.get("to_branch", "N/A"),
                "from_branch": e.get("from_branch", "N/A"),
                "merged_by": e.get("merged_by", None),
                "action": e.get("action", None)
            }
            cleaned_events.append(event)

        return jsonify(cleaned_events), 200

    except Exception as e:
        print(f"❌ Error in /events route: {e}")
        return jsonify({"error": "Could not fetch events"}), 500

# ✅ Start Flask server
if __name__ == '__main__':
    print("🔥 Starting Flask server...")
    app.run(port=5000, debug=True)