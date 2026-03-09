import redis
import json
import requests
import time
from collections import deque

# Redis connection
r = redis.Redis(host="redis", port=6379, decode_responses=True)

# Default rate limit
DEFAULT_RATE_LIMIT = 10

# Track active user queues
user_queues = deque()


def get_rate_limit():
    limit = r.get("rate_limit")
    if limit:
        return int(limit)
    return DEFAULT_RATE_LIMIT


def refill_tokens():
    return get_rate_limit()


def deliver_webhook(job):
    url = job["url"]
    event = job["event"]

    try:
        response = requests.post(url, json=event, timeout=5)

        if 200 <= response.status_code < 300:
            print(f"SUCCESS → Delivered to {url}")
        else:
            print(f"FAILED → {url} returned {response.status_code}")

    except Exception as e:
        print(f"ERROR → Delivery to {url} failed: {e}")


def move_jobs_to_user_queues():
    """
    Move jobs from global queue into per-user queues
    """
    job_data = r.rpop("delivery_queue")

    if not job_data:
        return

    job = json.loads(job_data)
    user_id = job["user_id"]

    queue_name = f"user_queue:{user_id}"

    r.lpush(queue_name, json.dumps(job))

    if user_id not in user_queues:
        user_queues.append(user_id)


def get_next_job():
    """
    Round-robin across user queues
    """

    if not user_queues:
        return None

    user_id = user_queues.popleft()

    queue_name = f"user_queue:{user_id}"

    job_data = r.rpop(queue_name)

    if job_data:
        job = json.loads(job_data)

        # If queue still has jobs, keep user in rotation
        if r.llen(queue_name) > 0:
            user_queues.append(user_id)

        return job

    return None


def worker_loop():

    print("Webhook delivery worker started")

    tokens = refill_tokens()
    last_refill = time.time()

    while True:

        # refill tokens every second
        if time.time() - last_refill >= 1:
            tokens = refill_tokens()
            last_refill = time.time()

        # move new jobs into user queues
        move_jobs_to_user_queues()

        if tokens <= 0:
            time.sleep(0.05)
            continue

        job = get_next_job()

        if not job:
            time.sleep(0.1)
            continue

        deliver_webhook(job)

        tokens -= 1


if __name__ == "__main__":
    worker_loop()
