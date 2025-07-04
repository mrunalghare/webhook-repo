from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# MongoDB Atlas connection
client = MongoClient("mongodb+srv://mrunalghare7:YgArQ0uu1KC141A4@webhook-cluster.ada12s6.mongodb.net/?retryWrites=true&w=majority&appName=webhook-cluster")
db = client['webhook_db']
collection = db['events']

print("✅ MongoDB Connected Successfully")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/testdb')
def testdb():
    test_data = {
        "author": "Mrunal",
        "event": "test_connection",
        "timestamp": datetime.utcnow()
    }
    collection.insert_one(test_data)
    return "Inserted test data to MongoDB Atlas!"

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
        })

    collection.insert_one(payload)
    return jsonify({"status": "success"}), 200

@app.route('/events', methods=['GET'])
def get_events():
    latest_events = list(collection.find().sort("timestamp", -1).limit(10))
    for e in latest_events:
        e['_id'] = str(e['_id'])
        e['timestamp'] = e['timestamp'].strftime('%d %b %Y - %I:%M %p UTC')
    return jsonify(latest_events)

if __name__ == '__main__':
    print("🔥 Starting Flask...")
    app.run(port=5000, debug=True)
    
    