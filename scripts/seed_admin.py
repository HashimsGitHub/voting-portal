#!/usr/bin/env python3
"""
Seed Admin User Script
Creates the initial admin user for the voting portal
"""

import os
import sys
import secrets
import logging
from pymongo import MongoClient
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))
from shared.password_utils import hash_password  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

MONGODB_CONNECTION_STRING = os.getenv('MONGODB_CONNECTION_STRING')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@nustalumni.org')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')


def seed_admin():
    """Create the admin account if it doesn't already exist"""
    if not MONGODB_CONNECTION_STRING:
        logger.error("MONGODB_CONNECTION_STRING not found in environment variables")
        return False

    password = ADMIN_PASSWORD
    if not password:
        password = secrets.token_urlsafe(12)
        logger.warning(
            "ADMIN_PASSWORD not set; generated a one-time random password. "
            "Save it now, it will not be shown again."
        )

    client = MongoClient(MONGODB_CONNECTION_STRING)
    try:
        db = client['voting_portal']
        users = db['users']
        users.create_index("email", unique=True)

        if users.find_one({"email": ADMIN_EMAIL}):
            logger.info(f"Admin user '{ADMIN_EMAIL}' already exists, skipping")
            return True

        users.insert_one({
            "email": ADMIN_EMAIL,
            "password_hash": hash_password(password),
            "name": "Administrator",
            "role": "admin"
        })

        logger.info(f"✅ Admin user created: {ADMIN_EMAIL}")
        if not ADMIN_PASSWORD:
            logger.info(f"Generated password: {password}")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to seed admin user: {str(e)}")
        return False
    finally:
        client.close()


if __name__ == '__main__':
    success = seed_admin()
    sys.exit(0 if success else 1)
