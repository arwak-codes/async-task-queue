\# Route Mobile Python Developer Assessment

\## Tech Stack
\- Python 3.10+
\- Flask (REST API)
\- RabbitMQ (Message Broker)
\- Celery (Background Worker)
\- SQLite (Database)
\- Python Threading (Concurrent Requests)

\---

\## Prerequisites

Before running the project, make sure the following are installed and running:

1\. Python 3.10 or above
2\. RabbitMQ Server running on localhost:5672
	- Management UI available at http://localhost:15672
	- Default credentials: guest / guest

\---

\## Project Structure

route\_assessment/
├── app.py           → Flask API (POST /item and GET /concurrent)
├── worker.py        → Celery consumer (processes RabbitMQ messages)
├── db.py            → SQLite database setup and helper functions
├── config.py        → All configuration (RabbitMQ, DB, queue names)
├── items.db         → SQLite database (auto-created on first run)
├── .gitignore       → Ignored files/folders for Git
├── requirements.txt → All Python dependencies
├── README.md        → Setup and run instructions
└── RouteAssessment.postman_collection.json → Postman collection

\---

\## Setup Instructions

\### Step 1 — Clone the project
```bash
cd route_assessment
```

\### Step 2 — Create and activate virtual environment
```bash
python -m venv venv
```

\# For Windows:
venv\Scripts\activate


\# For Mac/Linux:
source venv/bin/activate


\### Step 3 — Install all dependencies
```bash
pip install -r requirements.txt
```

\### Step 4 — Initialise the database
```bash
python db.py
```
This creates the `items.db` SQLite database and the `items` table automatically.


\### Step 5 — Ensure RabbitMQ is running

Make sure RabbitMQ is running on `localhost:5672` before proceeding.
You can verify at http://localhost:15672 (guest/guest).

\---


\## Running the Project

Open \*\*3 separate terminals\*\* and activate venv in each one.


\### Terminal 1 — Start Flask API
```bash
python app.py
```

Flask will run on: http://127.0.0.1:5000


\### Terminal 2 — Start Celery Worker
```bash
python worker.py
```

Worker will start listening for messages from RabbitMQ queue.


\### Terminal 3 — Test endpoints
Use the provided Postman collection or curl commands below.


\## API Endpoints

\### 1. POST /item

Accepts an item name, inserts into DB with `status=pending`, publishes to RabbitMQ. 
Celery worker automatically updates status to `completed`.


\*\*Request:\*\*
```bash
curl -i -X POST http://127.0.0.1:5000/item -H "Content-Type: application/json" -d "{\"item\": \"book\"}"
```

\*\*Response:\*\* `202 ACCEPTED`
```json
{}
```

\*\*DB flow:\*\*

Before worker processes: id=1  item=book  status=pending

After worker processes: id=1  item=book  status=completed


\---


\### 2. GET /concurrent

Fires 5 concurrent HTTP requests to `https://httpbin.org/delay/{delay\_value}`using Python Threading and returns total time taken.

\*\*Request:\*\*
```bash
curl "http://127.0.0.1:5000/concurrent?delay_value=3"
```

\*\*Response:\*\* `200 OK`
```json
{"time_taken": 7.15}
```

Note: Response time includes network latency to httpbin.org servers.


\---


\## Testing with Postman

1\. Open Postman
2\. Click \*\*Import\*\*
3\. Select `RouteAssessment.postman_collection.json`
4\. Both endpoints are pre-configured and ready to test


\---


\## Verify DB directly

To check the database at any point:
```bash
python -c "import sqlite3; conn = sqlite3.connect('items.db'); rows = conn.execute('SELECT * FROM items').fetchall(); print(rows); conn.close()"
```