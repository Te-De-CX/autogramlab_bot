from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from keyboards.reply_keyboards import (
    get_service_keyboard, get_main_menu_keyboard, get_back_keyboard
)
from utils.validators import validate_project_name, validate_description
import config
import urllib.parse

async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 *Let's build your project!*\n\n"
        "Step 1: What do you want to build?",
        parse_mode='Markdown',
        reply_markup=get_service_keyboard()
    )
    return config.SERVICE_SELECTION

def get_questions_for_service(service_type):
    questions = {
        "Telegram Bot": {
            "name_question": "🤖 Step 2: What should be the name of your Telegram bot?\n\nPlease enter the bot name:",
            "description_question": "📝 Step 3: What should your bot do?\n\nPlease describe:\n• Main features\n• Commands it should have\n• Target users\n• Any specific functionality"
        },
        "Telegram Mini App": {
            "name_question": "📱 Step 2: What should be the name of your Mini App?\n\nPlease enter the app name:",
            "description_question": "🎨 Step 3: Describe your Mini App idea:\n\nPlease include:\n• Main purpose of the app\n• Key features\n• Design preferences\n• User interactions needed"
        },
        "Website": {
            "name_question": "🌐 Step 2: What should be the name of your website?\n\nPlease enter the website name:",
            "description_question": "💻 Step 3: Tell us about your website:\n\nPlease describe:\n• Type of website (e-commerce, blog, portfolio, business, etc.)\n• Main pages needed (Home, About, Contact, etc.)\n• Key functionality\n• Design preferences (colors, style, references)\n• Target audience"
        },
        "Automation Tool": {
            "name_question": "⚙️ Step 2: What should be the name of your automation tool?\n\nPlease enter the tool name:",
            "description_question": "🔄 Step 3: Describe what you want to automate:\n\nPlease explain:\n• Current manual process\n• What tasks to automate\n• Tools/platforms involved\n• Expected outcomes"
        }
    }
    return questions.get(service_type, {
        "name_question": "Step 2: What should be the name of your project?\n\nPlease enter the name:",
        "description_question": "Step 3: Please describe your project in detail:"
    })

async def handle_service_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    if user_input == "🔙 Back to Main Menu":
        await update.message.reply_text("Returning to main menu...", reply_markup=get_main_menu_keyboard())
        return ConversationHandler.END
    service_map = {
        "Telegram Bot": "Telegram Bot",
        "Telegram Mini App": "Telegram Mini App", 
        "Website": "Website",
        "Automation Tool": "Automation Tool"
    }
    if user_input not in service_map:
        await update.message.reply_text("Please select a valid option:", reply_markup=get_service_keyboard())
        return config.SERVICE_SELECTION
    service_type = service_map[user_input]
    context.user_data['service_type'] = service_type
    questions = get_questions_for_service(service_type)
    context.user_data['questions'] = questions
    await update.message.reply_text(questions["name_question"], reply_markup=get_back_keyboard())
    return config.BOT_NAME

async def handle_bot_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    if user_input == "🔙 Back to Main Menu":
        await update.message.reply_text("Returning to main menu...", reply_markup=get_main_menu_keyboard())
        return ConversationHandler.END
    if not validate_project_name(user_input):
        await update.message.reply_text("Invalid name. Use 3-50 letters, numbers, spaces, hyphens.", reply_markup=get_back_keyboard())
        return config.BOT_NAME
    context.user_data['project_name'] = user_input
    questions = context.user_data.get('questions', get_questions_for_service(context.user_data['service_type']))
    await update.message.reply_text(questions["description_question"], reply_markup=get_back_keyboard())
    return config.BOT_DESCRIPTION

async def handle_bot_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    if user_input == "🔙 Back to Main Menu":
        await update.message.reply_text("Returning to main menu...", reply_markup=get_main_menu_keyboard())
        return ConversationHandler.END
    if not validate_description(user_input):
        await update.message.reply_text("Please provide a more detailed description (min 20 chars).", reply_markup=get_back_keyboard())
        return config.BOT_DESCRIPTION
    context.user_data['description'] = user_input
    await update.message.reply_text("💰 Step 4: Please enter your budget (e.g., $500–$1000 or $750).", reply_markup=get_back_keyboard())
    return config.BUDGET_SELECTION

async def handle_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    if user_input == "🔙 Back to Main Menu":
        await update.message.reply_text("Returning to main menu...", reply_markup=get_main_menu_keyboard())
        return ConversationHandler.END
    context.user_data['budget'] = user_input
    await update.message.reply_text("📅 Step 5: Do you have a deadline?\n(e.g., '2 weeks', '1 month', 'ASAP')", reply_markup=get_back_keyboard())
    return config.DEADLINE

async def send_admin_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = context.user_data
    service_icons = {"Telegram Bot": "🤖", "Telegram Mini App": "📱", "Website": "🌐", "Automation Tool": "⚙️"}
    service_type = user_data.get('service_type', 'Not specified')
    icon = service_icons.get(service_type, "🔔")
    admin_message = (
        f"{icon} *NEW CLIENT REQUEST*\n\n"
        f"*Service:* {service_type}\n"
        f"*Project Name:* {user_data.get('project_name', 'Not specified')}\n"
        f"*Description:* {user_data.get('description', 'Not specified')}\n"
        f"*Budget:* {user_data.get('budget', 'Not specified')}\n"
        f"*Deadline:* {user_data.get('deadline', 'Not specified')}\n\n"
        f"*Client Info:*\n"
        f"• Username: @{user.username if user.username else 'No username'}\n"
        f"• User ID: `{user.id}`\n"
        f"• Name: {user.full_name}\n"
        f"• Language: {user.language_code if user.language_code else 'Not specified'}"
    )
    admin_ids = config.ADMIN_IDS if hasattr(config, 'ADMIN_IDS') else [config.ADMIN_CHAT_ID]
    for admin_id in admin_ids:
        try:
            await context.bot.send_message(chat_id=admin_id, text=admin_message, parse_mode='Markdown')
        except:
            await context.bot.send_message(chat_id=admin_id, text=admin_message.replace('*', '').replace('`', ''))

async def handle_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    if user_input == "🔙 Back to Main Menu":
        await update.message.reply_text("Returning to main menu...", reply_markup=get_main_menu_keyboard())
        return ConversationHandler.END
    context.user_data['deadline'] = user_input
    
    # Store data for quote link
    context.user_data['quote_data'] = {
        'service_type': context.user_data.get('service_type'),
        'project_name': context.user_data.get('project_name'),
        'description': context.user_data.get('description'),
        'budget': context.user_data.get('budget'),
        'deadline': user_input
    }
    
    # 1. Send automatic admin summary
    await send_admin_summary(update, context)
    
    # 2. Create deep link to admin chat with pre‑filled quote
    user = update.effective_user
    user_data = context.user_data['quote_data']
    quote_text = (
        f"New project quote from @{user.username if user.username else 'User'} (ID: {user.id})\n\n"
        f"Service: {user_data['service_type']}\n"
        f"Project: {user_data['project_name']}\n"
        f"Description: {user_data['description']}\n"
        f"Budget: {user_data['budget']}\n"
        f"Deadline: {user_data['deadline']}"
    )
    encoded_text = urllib.parse.quote(quote_text)
    admin_username = config.ADMIN_CONTACT.lstrip('@')
    deep_link = f"https://t.me/{admin_username}?text={encoded_text}"
    
    keyboard = [[InlineKeyboardButton("📩 Send Quote to Admin (opens chat)", url=deep_link)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    service_type = context.user_data.get('service_type', 'project')
    confirmation_messages = {
        "Website": "🌐 *Great! Your website request has been submitted!*",
        "Telegram Bot": "🤖 *Awesome! Your bot request has been submitted!*",
        "Telegram Mini App": "📱 *Excellent! Your Mini App request has been submitted!*",
        "Automation Tool": "⚙️ *Perfect! Your automation tool request has been submitted!*"
    }
    confirmation = confirmation_messages.get(service_type, "✅ *Thank you! Your request has been submitted.*")
    await update.message.reply_text(
        confirmation + "\n\nClick the button below to open a chat with our team and send the quote (the message is pre‑written – just press Send).",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    # End the conversation so that the main menu works normally
    return ConversationHandler.END

async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text("Order cancelled.", reply_markup=get_main_menu_keyboard(user_id=user_id))
    return ConversationHandler.END