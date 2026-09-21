import logging
import time
import json
import os
from functools import wraps
from datetime import datetime

# Ensure logs directory exists
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Configure standard python logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "system.log")),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("DealForgeAI")

def log_audit_trail(action: str, details: dict):
    """
    Logs critical business decisions (like human approvals, budget changes)
    to a structured JSONL audit trail for compliance purposes.
    """
    audit_file = os.path.join(LOG_DIR, "audit_trail.jsonl")
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "details": details
    }
    with open(audit_file, "a") as f:
        f.write(json.dumps(entry) + "\n")
    logger.info(f"AUDIT ACTION RECORDED: {action}")
