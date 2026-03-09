README.md Template for Your Project
# Multi-User Webhook Delivery System

A reliable webhook delivery platform where users can register HTTP endpoints, subscribe to events, and receive real-time payloads when those events occur.

This project was built as part of the **Atomicwork DevOps Intern Assignment**.

---

# Architecture Overview

The system consists of the following components:

Client / Event Publisher
        |
        v
   FastAPI Backend
        |
        v
      Redis Queue
        |
        v
 Delivery Worker
        |
        v
 Webhook Endpoint (Mock Receiver)

### Components

**API Service (FastAPI)**  
Handles webhook management and event ingestion.

**Redis Queue**  
Stores delivery jobs for asynchronous processing.

**Worker Service**  
Continuously processes queued jobs and delivers webhooks.

**Mock Receiver**  
Simulates an external webhook endpoint for testing.

**Docker Compose**  
Runs all services together with a single command.

---

# Tech Stack

- Python
- FastAPI
- Redis
- PostgreSQL
- Docker
- Docker Compose

---

# Features

## Webhook Management API

Users can manage webhooks through the following endpoints.

### Register Webhook


POST /webhooks


Registers a webhook endpoint with selected event subscriptions.

Example:

```json
{
  "url": "http://mock-receiver:9000/webhook",
  "event_types": ["request.created", "request.updated"]
}
List Webhooks
GET /webhooks

Returns all webhooks for the authenticated user.

Header:

X-User-Id: user1
Delete Webhook
DELETE /webhooks/{webhook_id}

Removes a webhook permanently.

Enable / Disable Webhook
PATCH /webhooks/{webhook_id}/toggle

Disables or re-enables webhook delivery.

Event Publishing

Events are ingested through:

POST /events

Example:

{
  "user_id": "user1",
  "event_type": "request.created",
  "payload": {
    "id": "123"
  }
}

The system finds all active webhooks subscribed to the event and creates delivery jobs.

Webhook Delivery

The worker service processes queued jobs and sends HTTP POST requests to webhook endpoints.

A delivery is considered successful when the receiver responds with a 2xx HTTP status code.

Failed deliveries are logged.

Retry logic is intentionally omitted as per assignment requirements.

Rate Limiting Strategy (Part B)

Webhook deliveries are rate-limited using a global delivery rate.

Implementation approach:

A configurable limit defines maximum deliveries per second.

The worker enforces the rate using Redis-based counters.

If the rate is exceeded, jobs remain queued until capacity becomes available.

This ensures no deliveries are dropped.

Multi-User Fairness Strategy (Part C)

To prevent one user from blocking others:

Each user's jobs are logically separated.

Worker processes jobs in a round-robin scheduling approach.

This ensures users with smaller workloads are not delayed by heavy users.

Example scenario:

User A publishes 1000 events
User B publishes 1 event

User B's webhook delivery is processed quickly instead of waiting behind User A's entire queue.

Running the System

Clone the repository:

git clone https://github.com/MahendraGubagundam/webhook-system.git
cd webhook-system

Start the system:

docker compose up --build

This will start:

API service

Redis queue

PostgreSQL

Worker

Mock receiver

Testing the System

Open FastAPI docs:

http://localhost:8000/docs

Register a webhook.

Publish an event.

The worker will deliver the event to the mock receiver.

Check received events:

http://localhost:9000/events
Example Workflow

Register webhook

Publish event

API enqueues delivery job

Worker processes queue

Mock receiver receives webhook payload

Project Structure
webhook-system
│
├── api
│   └── main.py
│
├── worker
│   └── worker.py
│
├── mock_receiver
│   └── server.py
│
├── Dockerfile
├── Dockerfile.worker
├── docker-compose.yml
├── requirements.txt
└── README.md
Commit History

The repository contains meaningful commits representing incremental development:

Project setup

API implementation

Worker implementation

Mock receiver

Docker infrastructure

Author

Mahendra Gubagundam.
