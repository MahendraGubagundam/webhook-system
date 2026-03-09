# Multi-User Webhook Delivery System

A reliable webhook delivery platform where users can register HTTP endpoints, subscribe to events, and receive real-time payloads when those events occur.

This project was built as part of the **Atomicwork DevOps Intern Assignment**.

---

# Architecture Overview

The system architecture:


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
Processes queued jobs and delivers webhooks.

**Mock Receiver**  
Simulates an external webhook endpoint for testing.

**Docker Compose**  
Runs the entire system with one command.

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

### Register Webhook


POST /webhooks


Registers a webhook endpoint with selected event subscriptions.

Example request:

json
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

Example request:

{
  "user_id": "user1",
  "event_type": "request.created",
  "payload": {
    "id": "123"
  }
}

The system finds all active webhooks subscribed to the event and queues delivery jobs.

Webhook Delivery

The worker service processes queued jobs and sends HTTP POST requests to webhook endpoints.

A delivery is considered successful when the receiver responds with a 2xx HTTP status code.

Failed deliveries are logged.

Retry logic is intentionally omitted as specified in the assignment.

Rate Limiting Strategy (Part B)

Webhook deliveries are rate-limited using a global delivery rate.

Implementation:

A configurable limit defines deliveries per second

The worker enforces this limit using Redis

Excess deliveries remain queued until capacity becomes available

This ensures no deliveries are dropped.

Multi-User Fairness Strategy (Part C)

To prevent one user from blocking others:

Jobs are separated into per-user queues

Worker processes queues using round-robin scheduling

Example:

User A publishes 1000 events
User B publishes 1 event

User B’s delivery is processed quickly instead of waiting behind User A’s backlog.

Running the System

Clone the repository:

git clone https://github.com/MahendraGubagundam/webhook-system.git
cd webhook-system

Start all services:

docker compose up --build

This will start:

API service

Redis

PostgreSQL

Worker

Mock receiver

Testing the System

Open FastAPI documentation:

http://localhost:8000/docs

Steps:

Register a webhook

Publish an event

Worker processes queue

Mock receiver receives webhook

Check received events:

http://localhost:9000/events
Example Workflow

Register webhook

Publish event

API enqueues delivery job

Worker processes queue

Mock receiver receives webhook payload

Project Structure
'''
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
'''
Commit History

The repository includes meaningful commits representing incremental development:

Project setup

API implementation

Worker implementation

Mock receiver

Docker infrastructure

Author

Mahendra Gubagundam
