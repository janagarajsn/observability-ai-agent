import os
import json
import random
import datetime
import logging
import uuid
from pathlib import Path
from log_generator import APPLICATIONS, NAMESPACES, NODES  # reuse constants

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s")
logger = logging.getLogger(__name__)

TICKET_DIR = "tickets"
os.makedirs(TICKET_DIR, exist_ok=True)

TICKET_TYPES = ["DatabaseTimeout", "HighCPU", "HighMemory", "PodCrash", "AuthFailure"]

def generate_ticket(i: int, timestamp=None):
    """Generate a synthetic ticket aligned with logs."""
    if timestamp is None:
        timestamp = datetime.datetime.utcnow()

    namespace = random.choice(NAMESPACES)
    app = random.choice(APPLICATIONS)
    pod = f"{app}-pod-{random.randint(1,5)}"
    node = random.choice(NODES)
    ticket_type = random.choice(TICKET_TYPES)

    # Map ticket_type to message and resolution
    if ticket_type == "DatabaseTimeout":
        message = f"Database connection timeout in {namespace} for {app}"
        resolution = "Check DB connectivity and restart DB pods if necessary."
    elif ticket_type == "HighCPU":
        message = f"High CPU usage detected on {node} in {namespace}"
        resolution = "Investigate running pods, consider scaling node pool."
    elif ticket_type == "HighMemory":
        message = f"High memory usage detected on {pod} in {namespace}"
        resolution = "Investigate memory leaks, restart pods, consider scaling memory limits."
    elif ticket_type == "PodCrash":
        message = f"{pod} crashed in {namespace}"
        resolution = "Check pod logs and redeploy if necessary."
    elif ticket_type == "AuthFailure":
        message = f"Multiple failed login attempts in {namespace}"
        resolution = "Investigate security issues and reset affected credentials."

    ticket = {
        "ticketId": f"INC{i:09d}",
        "timestamp": timestamp.isoformat() + "Z",
        "namespace": namespace,
        "pod": pod,
        "application": app,
        "node": node,
        "ticketType": ticket_type,
        "message": message,
        "suggestedAction": resolution,
        "traceId": str(uuid.uuid4())  # optional: fake link to a log trace
    }

    return ticket

def generate_batch(num=10, date_str=None):
    """Generate a batch of tickets and save to a daily JSON file."""
    if date_str is None:
        date_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")

    tickets = []
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    for i in range(1, num + 1):
        seconds_offset = int((86400 / num) * i)
        timestamp = date + datetime.timedelta(seconds=seconds_offset)
        tickets.append(generate_ticket(i, timestamp=timestamp))

    output_file = os.path.join(TICKET_DIR, f"tickets_{date_str}.json")
    with open(output_file, "w") as f:
        json.dump(tickets, f, indent=2)

    logger.info(f"Generated {len(tickets)} tickets for {date_str} -> {output_file}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ticket Generator aligned to logs")
    parser.add_argument("--num", type=int, default=10, help="Number of tickets to generate")
    parser.add_argument("--date", type=str, help="Date for file name (YYYY-MM-DD)")
    args = parser.parse_args()

    generate_batch(args.num, date_str=args.date)
