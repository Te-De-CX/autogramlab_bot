from telegram import ReplyKeyboardMarkup, KeyboardButton
from config import ADMIN_IDS

def get_main_menu_keyboard(user_id=None):
    keyboard = [
        [KeyboardButton("🚀 Start a project")],
        [KeyboardButton("📂 Our Portfolio")],
        [KeyboardButton("💰 Pricing")],
        [KeyboardButton("📩 Contact Team"), KeyboardButton("❓ Support")]
    ]
    if user_id and user_id in ADMIN_IDS:
        keyboard.append([KeyboardButton("👑 Admin Panel")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_keyboard():
    keyboard = [
        ["📂 Manage Portfolio", "👥 View Users"],
        ["📢 Send Announcement", "🔙 Back to User Menu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_service_keyboard():
    keyboard = [
        [KeyboardButton("Telegram Bot")],
        [KeyboardButton("Telegram Mini App")],
        [KeyboardButton("Website")],
        [KeyboardButton("Automation Tool")],
        [KeyboardButton("🔙 Back to Main Menu")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_budget_keyboard():
    # kept for compatibility, not used now
    keyboard = [
        [KeyboardButton("$50–$150")],
        [KeyboardButton("$150–$500")],
        [KeyboardButton("$500+")],
        [KeyboardButton("🔙 Back to Main Menu")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard():
    keyboard = [["🔙 Back to Main Menu"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)