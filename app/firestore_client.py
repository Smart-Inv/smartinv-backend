import firebase_admin
from firebase_admin import firestore
from dotenv import load_dotenv
import os

load_dotenv()

if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client()
