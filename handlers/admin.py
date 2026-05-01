# handlers/admin.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from database import (
    get_portfolio_projects, add_portfolio_project, update_portfolio_project, delete_portfolio_project, get_portfolio_project,
    get_all_users, get_user_count
)
from keyboards.reply_keyboards import get_admin_keyboard, get_main_menu_keyboard
from config import ADMIN_IDS

logger = logging.getLogger(__name__)

# States
(ADD_NAME, ADD_DESCRIPTION, ADD_LINK, EDIT_SELECT, EDIT_NAME, EDIT_DESCRIPTION, EDIT_LINK, DELETE_CONFIRM) = range(8)
ADMIN_MENU = 100
(ASK_PHOTO, ASK_CAPTION, ASK_BUTTONS, CONFIRM_ANNOUNCEMENT) = range(200, 204)

# ----------------------------------------------------------------------
# Admin entry point
# ----------------------------------------------------------------------
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ You are not authorized.")
        return ConversationHandler.END
    await update.message.reply_text("👑 *Admin Panel*", parse_mode='Markdown', reply_markup=get_admin_keyboard())
    return ADMIN_MENU

# ----------------------------------------------------------------------
# Admin menu handler (reply buttons)
# ----------------------------------------------------------------------
async def admin_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Access denied.")
        return ConversationHandler.END
    text = update.message.text
    if text == "🔙 Back to User Menu":
        await update.message.reply_text("Returning to user menu.", reply_markup=get_main_menu_keyboard(user_id=user_id))
        return ConversationHandler.END
    elif text == "📂 Manage Portfolio":
        projects = get_portfolio_projects()
        msg = "*Current Portfolio Projects:*\n\n" if projects else "No projects yet."
        for p in projects:
            msg += f"`{p['id']}` – *{p['name']}*\n"
        keyboard = [
            [InlineKeyboardButton("➕ Add New Project", callback_data="admin_add_project")],
            [InlineKeyboardButton("✏️ Edit Project", callback_data="admin_edit_project")],
            [InlineKeyboardButton("🗑 Delete Project", callback_data="admin_delete_project")],
            [InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_back")]
        ]
        await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return ADMIN_MENU
    elif text == "👥 View Users":
        users = get_all_users()
        total = len(users)
        msg = f"*Total Users:* {total}\n\n"
        for u in users[:20]:
            username = f"@{u['username']}" if u['username'] else "No username"
            msg += f"• {u['first_name']} {u['last_name'] or ''} ({username})\n  ID: `{u['user_id']}`\n  Joined: {u['joined_date'][:10]}\n\n"
        if total > 20:
            msg += f"... and {total-20} more."
        await update.message.reply_text(msg, parse_mode='Markdown')
        await update.message.reply_text("Admin Menu:", reply_markup=get_admin_keyboard())
        return ADMIN_MENU
    elif text == "📢 Send Announcement":
        keyboard = [
            [InlineKeyboardButton("📷 Include Photo", callback_data="announcement_yes")],
            [InlineKeyboardButton("🚫 No Photo", callback_data="announcement_no")]
        ]
        await update.message.reply_text("Do you want to include a photo?", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return ASK_PHOTO
    else:
        await update.message.reply_text("Unknown option.", reply_markup=get_admin_keyboard())
        return ADMIN_MENU

# ----------------------------------------------------------------------
# Announcement conversation (inline buttons, photo, buttons)
# ----------------------------------------------------------------------
async def ask_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "announcement_yes":
        context.user_data['announcement_has_photo'] = True
        await query.edit_message_text("Send the photo (or click 'Skip')", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏩ Skip", callback_data="announcement_skip_photo")]]))
        return ASK_CAPTION
    else:
        context.user_data['announcement_has_photo'] = False
        await query.edit_message_text("Now send the announcement text (Markdown allowed).")
        return ASK_BUTTONS

async def ask_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        if query.data == "announcement_skip_photo":
            context.user_data['announcement_has_photo'] = False
            await query.edit_message_text("Now send the announcement text (Markdown allowed).")
            return ASK_BUTTONS
        return ASK_CAPTION
    if update.message.photo:
        context.user_data['announcement_photo'] = update.message.photo[-1].file_id
        await update.message.reply_text("Photo received. Now send the caption (text).")
        return ASK_BUTTONS
    else:
        await update.message.reply_text("Please send a photo or use 'Skip'.")
        return ASK_CAPTION

async def ask_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('announcement_has_photo'):
        context.user_data['announcement_caption'] = update.message.text
    else:
        context.user_data['announcement_text'] = update.message.text
    await update.message.reply_text(
        "Add inline buttons (optional). Send each as `Text | URL` (one per line).\nExample:\n`Get Started | https://t.me/...`\n\nWhen done, click 'Done'.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Done", callback_data="announcement_done")],
            [InlineKeyboardButton("⏩ Skip (no buttons)", callback_data="announcement_skip_buttons")]
        ])
    )
    context.user_data['announcement_buttons'] = []
    return CONFIRM_ANNOUNCEMENT

async def collect_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        data = query.data
        if data == "announcement_done":
            return await preview_announcement(update, context)
        elif data == "announcement_skip_buttons":
            context.user_data['announcement_buttons'] = []
            return await preview_announcement(update, context)
        return CONFIRM_ANNOUNCEMENT
    # User sent text button line
    text = update.message.text
    lines = text.split('\n')
    for line in lines:
        if '|' not in line:
            continue
        btn_text, btn_url = line.split('|', 1)
        btn_text = btn_text.strip()
        btn_url = btn_url.strip()
        if btn_text and btn_url.startswith(('http://', 'https://', 'tg://')):
            context.user_data['announcement_buttons'].append((btn_text, btn_url))
    await update.message.reply_text(f"✅ Added buttons. Send more or click 'Done'.")
    return CONFIRM_ANNOUNCEMENT

async def preview_announcement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        msg = query.message
    else:
        msg = update.message
    has_photo = context.user_data.get('announcement_has_photo', False)
    buttons = context.user_data.get('announcement_buttons', [])
    reply_markup = None
    if buttons:
        keyboard = [[InlineKeyboardButton(btn[0], url=btn[1])] for btn in buttons]
        reply_markup = InlineKeyboardMarkup(keyboard)
    if has_photo:
        caption = context.user_data.get('announcement_caption', '')
        await msg.reply_photo(photo=context.user_data['announcement_photo'], caption=caption, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        text = context.user_data.get('announcement_text', '')
        await msg.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    confirm_keyboard = [[InlineKeyboardButton("✅ Confirm & Send", callback_data="announcement_confirm")], [InlineKeyboardButton("❌ Cancel", callback_data="announcement_cancel")]]
    await msg.reply_text("Send this announcement?", reply_markup=InlineKeyboardMarkup(confirm_keyboard))
    return CONFIRM_ANNOUNCEMENT

async def send_announcement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "announcement_confirm":
        has_photo = context.user_data.get('announcement_has_photo', False)
        buttons = context.user_data.get('announcement_buttons', [])
        reply_markup = None
        if buttons:
            keyboard = [[InlineKeyboardButton(btn[0], url=btn[1])] for btn in buttons]
            reply_markup = InlineKeyboardMarkup(keyboard)
        users = get_all_users()
        sent = 0
        failed = 0
        for user in users:
            try:
                if has_photo:
                    await context.bot.send_photo(chat_id=user['user_id'], photo=context.user_data['announcement_photo'], caption=context.user_data.get('announcement_caption', ''), parse_mode='Markdown', reply_markup=reply_markup)
                else:
                    await context.bot.send_message(chat_id=user['user_id'], text=context.user_data.get('announcement_text', ''), parse_mode='Markdown', reply_markup=reply_markup)
                sent += 1
            except:
                failed += 1
        await query.edit_message_text(f"✅ Sent to {sent} users. Failed: {failed}.")
    else:
        await query.edit_message_text("Announcement cancelled.")
    for key in ['announcement_has_photo', 'announcement_photo', 'announcement_caption', 'announcement_text', 'announcement_buttons']:
        context.user_data.pop(key, None)
    await query.message.reply_text("Admin Panel:", reply_markup=get_admin_keyboard())
    return ADMIN_MENU

# ----------------------------------------------------------------------
# Portfolio management functions (add/edit/delete)
# ----------------------------------------------------------------------
async def add_project_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Enter project name:")
    return ADD_NAME

async def add_project_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_name'] = update.message.text.strip()
    await update.message.reply_text("Now enter description:")
    return ADD_DESCRIPTION

async def add_project_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_desc'] = update.message.text.strip()
    await update.message.reply_text("Finally, enter the link (URL):")
    return ADD_LINK

async def add_project_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_portfolio_project(context.user_data['new_name'], context.user_data['new_desc'], update.message.text.strip())
    await update.message.reply_text("✅ Project added!")
    await update.message.reply_text("Admin Panel:", reply_markup=get_admin_keyboard())
    return ADMIN_MENU

async def edit_project_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    projects = get_portfolio_projects()
    if not projects:
        await query.edit_message_text("No projects.")
        return ADMIN_MENU
    keyboard = [[InlineKeyboardButton(p['name'], callback_data=f"edit_{p['id']}")] for p in projects]
    keyboard.append([InlineKeyboardButton("🔙 Cancel", callback_data="admin_back")])
    await query.edit_message_text("Select project to edit:", reply_markup=InlineKeyboardMarkup(keyboard))
    return EDIT_SELECT

async def edit_project_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    project_id = int(query.data.split('_')[1])
    context.user_data['edit_id'] = project_id
    project = get_portfolio_project(project_id)
    await query.edit_message_text(f"Editing *{project['name']}*\nSend new name (or /skip):", parse_mode='Markdown')
    return EDIT_NAME

async def edit_project_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == '/skip':
        context.user_data['edit_name'] = None
    else:
        context.user_data['edit_name'] = update.message.text.strip()
    await update.message.reply_text("Send new description (or /skip):")
    return EDIT_DESCRIPTION

async def edit_project_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == '/skip':
        context.user_data['edit_desc'] = None
    else:
        context.user_data['edit_desc'] = update.message.text.strip()
    await update.message.reply_text("Send new link (or /skip):")
    return EDIT_LINK

async def edit_project_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == '/skip':
        context.user_data['edit_link'] = None
    else:
        context.user_data['edit_link'] = update.message.text.strip()
    project = get_portfolio_project(context.user_data['edit_id'])
    new_name = context.user_data['edit_name'] if context.user_data['edit_name'] else project['name']
    new_desc = context.user_data['edit_desc'] if context.user_data['edit_desc'] else project['description']
    new_link = context.user_data['edit_link'] if context.user_data['edit_link'] else project['link']
    update_portfolio_project(context.user_data['edit_id'], new_name, new_desc, new_link)
    await update.message.reply_text("✅ Project updated!")
    await update.message.reply_text("Admin Panel:", reply_markup=get_admin_keyboard())
    return ADMIN_MENU

async def delete_project_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    projects = get_portfolio_projects()
    if not projects:
        await query.edit_message_text("No projects.")
        return ADMIN_MENU
    keyboard = [[InlineKeyboardButton(p['name'], callback_data=f"del_{p['id']}")] for p in projects]
    keyboard.append([InlineKeyboardButton("🔙 Cancel", callback_data="admin_back")])
    await query.edit_message_text("Select project to delete:", reply_markup=InlineKeyboardMarkup(keyboard))
    return DELETE_CONFIRM

async def delete_project_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    project_id = int(query.data.split('_')[1])
    keyboard = [[InlineKeyboardButton("✅ Yes", callback_data=f"confirm_del_{project_id}")], [InlineKeyboardButton("❌ No", callback_data="admin_back")]]
    await query.edit_message_text("Are you sure?", reply_markup=InlineKeyboardMarkup(keyboard))
    return DELETE_CONFIRM

async def delete_project_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    project_id = int(query.data.split('_')[2])
    delete_portfolio_project(project_id)
    await query.edit_message_text("✅ Project deleted.")
    await query.message.reply_text("Admin Panel:", reply_markup=get_admin_keyboard())
    return ADMIN_MENU

async def admin_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Admin Panel:")
    await query.message.reply_text("Choose an option:", reply_markup=get_admin_keyboard())
    return ADMIN_MENU

# Conversation handler
admin_conv = ConversationHandler(
    entry_points=[CommandHandler('admin', admin_panel), MessageHandler(filters.Regex('^👑 Admin Panel$'), admin_panel)],
    states={
        ADMIN_MENU: [
            MessageHandler(filters.Regex('^(📂 Manage Portfolio|👥 View Users|📢 Send Announcement|🔙 Back to User Menu)$'), admin_menu_handler),
            CallbackQueryHandler(add_project_start, pattern='^admin_add_project$'),
            CallbackQueryHandler(edit_project_select, pattern='^admin_edit_project$'),
            CallbackQueryHandler(delete_project_select, pattern='^admin_delete_project$'),
            CallbackQueryHandler(admin_back_callback, pattern='^admin_back$')
        ],
        ADD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_project_name)],
        ADD_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_project_description)],
        ADD_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_project_link)],
        EDIT_SELECT: [CallbackQueryHandler(edit_project_chosen, pattern='^edit_\\d+$')],
        EDIT_NAME: [MessageHandler(filters.TEXT, edit_project_name)],
        EDIT_DESCRIPTION: [MessageHandler(filters.TEXT, edit_project_description)],
        EDIT_LINK: [MessageHandler(filters.TEXT, edit_project_link)],
        DELETE_CONFIRM: [
            CallbackQueryHandler(delete_project_confirm, pattern='^del_\\d+$'),
            CallbackQueryHandler(delete_project_execute, pattern='^confirm_del_\\d+$')
        ],
        ASK_PHOTO: [CallbackQueryHandler(ask_photo, pattern='^(announcement_yes|announcement_no)$')],
        ASK_CAPTION: [CallbackQueryHandler(ask_caption, pattern='^announcement_skip_photo$'), MessageHandler(filters.PHOTO, ask_caption)],
        ASK_BUTTONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_buttons)],
        CONFIRM_ANNOUNCEMENT: [
            CallbackQueryHandler(collect_buttons, pattern='^(announcement_done|announcement_skip_buttons)$'),
            CallbackQueryHandler(send_announcement, pattern='^(announcement_confirm|announcement_cancel)$'),
            MessageHandler(filters.TEXT & ~filters.COMMAND, collect_buttons)
        ]
    },
    fallbacks=[CommandHandler('cancel', admin_panel)],
    name="admin_conversation",
    allow_reentry=True
)