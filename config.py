# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration - REPLACE WITH YOUR ACTUAL TOKEN
BOT_TOKEN = os.getenv('BOT_TOKEN', '8652210142:AAHo-ITqN6Q8OEIqHwDMOXz4UPrNStMNGGg')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '1850435445')

ADMIN_IDS = [int(ADMIN_CHAT_ID)]  # list of admin user IDs
BOT_USERNAME = "@AutogramLab_bot"

# Conversation states
(SERVICE_SELECTION, BOT_NAME, BOT_DESCRIPTION, 
 BUDGET_SELECTION, DEADLINE) = range(5)

# Service types
SERVICE_TYPES = {
    'telegram_bot': 'Telegram Bot',
    'telegram_mini_app': 'Telegram Mini App',
    'website': 'Website',
    'automation_tool': 'Automation Tool'
}

# Budget ranges (no longer used for dropdown but kept for compatibility)
BUDGET_RANGES = {
    'budget_1': '$50–$150',
    'budget_2': '$150–$500',
    'budget_3': '$500+'
}