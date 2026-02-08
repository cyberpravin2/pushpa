# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Location: Supaul, Bihar 
#
# All rights reserved.
#
# This code is the intellectual property of @WTF_Phantom.
# You are not allowed to copy, modify, redistribute, or use this
# code for commercial or personal projects without explicit permission.
# Contact for permissions:
# Email: king25258069@gmail.com

from pymongo import MongoClient
import certifi
from baka.config import MONGO_URI

# Initialize Connection
RyanBaka = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = RyanBaka["bakabot_db"]

# --- DEFINING COLLECTIONS ---
users_collection = db["users"]       # Stores balance, inventory, waifus, stats
groups_collection = db["groups"]     # Tracks group settings (welcome, claim status)
sudoers_collection = db["sudoers"]   # Stores admin IDs
chatbot_collection = db["chatbot"]   # Stores AI chat history per group/user
riddles_collection = db["riddles"]   # Stores active riddles and answers
