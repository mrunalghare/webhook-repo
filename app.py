from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

#  MongoDB Atlas connection
client = MongoClient("mongodb+srv://mrunalghare7:YgArQ0uu1KC141A4@webhook-cluster.ada12s6.mongodb.net/?retryWrites=true&w=majority&appName=webhook-cluster")
db = client['webhook_db']
collection = db['events']

print(" MongoDB Connected Successfully")

#  Homepage
@app.route('/')
def home():
    return render_template('index.html')

#  Test MongoDB manually
@app.route('/testdb')
def testdb():
    test_data = {
        "author": "Mrunal",
        "event": "test_connection",
        "timestamp": datetime.utcnow()
    }
    collection.insert_one(test_data)
    return "Inserted test data to MongoDB Atlas!"

#  GitHub Webhook Endpoint
@app.route('/webhook', methods=['POST'])
def github_webhook():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')

    payload = {
        "event": event_type,
        "timestamp": datetime.utcnow()
    }

    if event_type == "push":
        payload.update({
            "author": data['pusher']['name'],
            "to_branch": data['ref'].split('/')[-1],
        })

    elif event_type == "pull_request":
        payload.update({
            "author": data['pull_request']['user']['login'],
            "from_branch": data['pull_request']['head']['ref'],
            "to_branch": data['pull_request']['base']['ref'],
            "action": data['action']
        })

        #  Handle Merge (inside pull_request)
        if data['action'] == 'closed' and data['pull_request']['merged']:
            payload['event'] = 'merge'
            payload['merged_by'] = data['pull_request']['merged_by']['login']

    # Save to MongoDB
    collection.insert_one(payload)
    return jsonify({"status": "success"}), 200

#  View Latest Events

@app.route('/events', methods=['GET'])
def get_events():
    try:
        latest_events = list(collection.find().sort("timestamp", -1).limit(10))
        cleaned_events = []
        for e in latest_events:
            event = {
                "event": e.get("event", "unknown"),
                "timestamp": e.get("timestamp", "").strftime('%d %b %Y - %I:%M %p UTC') if isinstance(e.get("timestamp"), datetime) else str(e.get("timestamp")),
                "author": e.get("author", None),
                "to_branch": e.get("to_branch", None),
                "from_branch": e.get("from_branch", None),
                "merged_by": e.get("merged_by", None),
                "action": e.get("action", None),
            }
            cleaned_events.append(event)
        return jsonify(cleaned_events), 200
    except Exception as e:
        print(f"ERROR in /events route: {e}")
        return jsonify({"error": "Internal Server Error. Could not fetch events."}), 500

    
#  Run the Flask app (for local testing)
if __name__ == '__main__':
    print(" Starting Flask...")
    app.run(port=5000, debug=True)

    