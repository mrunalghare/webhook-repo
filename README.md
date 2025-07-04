# GitHub Webhook Integration with Flask and MongoDB

This project demonstrates how to receive GitHub webhook events (Push, Pull Request, and Merge) using a Flask server,
store the events in MongoDB, and display them on a web UI that updates every 15 seconds.

## 🔧 Features

- Receives webhook events from GitHub (`push`, `pull_request`, `merge`)
- Parses and stores the event data in MongoDB Atlas
- Frontend UI built with HTML + JavaScript
- UI polls the backend every 15 seconds to display the latest events
- Clean and minimal design

## 🛠️ Tech Stack

- **Python** + **Flask** Backend server
- **MongoDB Atlas** NoSQL database
- **HTML + JS**  Frontend UI
- **GitHub Webhooks** Triggering events

##  Folder Structure
webhook-repo/
├── app.py # Flask backend
├── templates/
│ └── index.html # Frontend UI
└── README.md # Project info