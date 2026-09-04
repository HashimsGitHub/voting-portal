"""
Configuration
Centralized access to environment-backed settings
"""
import os

MONGODB_CONNECTION_STRING = os.getenv('MONGODB_CONNECTION_STRING')
JWT_SECRET = os.getenv('JWT_SECRET')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AzureWebJobsStorage') or os.getenv('AZURE_STORAGE_CONNECTION_STRING')
