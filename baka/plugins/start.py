# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Location: Supaul, Bihar 
#
# All rights reserved.
#
# This code is the intellectual property of @WTF_Phantom.
# You are not allowed to copy, modify, redistribute, or use this
# code for commercial or personal projects without explicit permission.
#
# Allowed:
# - Forking for personal learning
# - Submitting improvements via pull requests
#
# Not Allowed:
# - Claiming this code as your own
# - Re-uploading without credit or permission
# - Selling or using commercially
#
# Contact for permissions:
# Email: king25258069@gmail.com

import html
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatType
from baka.config import BOT_NAME, START_IMG_URL, HELP_IMG_URL, SUPPORT_GROUP, SUPPORT_CHANNEL, OWNER_LINK
from baka.utils import ensure_user_exists, get_mention, track_group, log_to_channel, SUDO_USERS, stylize_text

SUDO_IMG = "https://files.catbox.moe/gyi5iu.jpg"

# --- 🌸 AESTHETIC KEYBOARDS ---
def get_start_keyboard(bot_username):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"🎐 {stylize_text('Updates')}", url=SUPPORT_CHANNEL),
            InlineKeyboardButton(f"☁️ {stylize_text('Support')}", url=SUPPORT_GROUP)
        ],
        [
            InlineKeyboardButton(f"➕ {stylize_text('Add Me Baby')} ➕", url=f"https://t.me/{bot_username}?startgroup=true")
        ],
        [
            InlineKeyboardButton(f"📖 {stylize_text('Diary')}", callback_data="help_main"),
            InlineKeyboardButton(f"👑 {stylize_text('Owner')}", url=OWNER_LINK)
        ]
    ])

def get_help_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"💞 {stylize_text('Social')}", callback_data="help_social"),
            InlineKeyboardButton(f"👛 {stylize_text('Economy')}", callback_data="help_economy")
        ],
        [
            InlineKeyboardButton(f"⚔️ {stylize_text('RPG & War')}", callback_data="help_rpg"),
            InlineKeyboardButton(f"🍥 {stylize_text('AI & Fun')}", callback_data="help_fun")
        ],
        [
            InlineKeyboardButton(f"⛩️ {stylize_text('Group')}", callback_data="help_group"),
            InlineKeyboardButton(f"🔐 {stylize_text('Sudo')}", callback_data="help_sudo")
        ],
        [
            InlineKeyboardButton(f"🔙 {stylize_text('Back')}", callback_data="return_start")
        ]
    ])

def get_back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton(f"🔙 {stylize_text('Back')}", callback_data="help_main")]])

# --- 🚀 COMMANDS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        chat = update.effective_chat
        ensure_user_exists(user)
        track_group(chat, user)
        
        user_link = get_mention(user)
        
        # --- THE ULTRA AESTHETIC CAPTION ---
        caption = (
            f"👋 {stylize_text('Konichiwa')} {user_link}! (⁠≧⁠▽⁠≦⁠)\n"
            f"The {stylize_text('Aesthetic AI-Powered RPG Bot')}! 💞\n\n"
            f"⊚  {stylize_text('Features')}:\n"
            f"⊚  {stylize_text('RPG')}: {stylize_text('Kill, Rob (100%), Protect')}\n"
            f"⊚  {stylize_text('Social')}: {stylize_text('Marry, Couple, Waifu')}\n"
            f"➻  {stylize_text('Economy')}: {stylize_text('Claim, Give, Shop')}\n"
            f"➻  {stylize_text('AI')}: {stylize_text('Sassy Chatbot & Art')}\n\n"
            f"✦ {stylize_text('Need Help?')}\n"
            f"{stylize_text('Click the buttons below!')}"
        )

        bot_un = context.bot.username if context.bot.username else "RyanBakaBot"
        kb = get_start_keyboard(bot_un)

        if update.callback_query:
            try: await update.callback_query.message.edit_media(InputMediaPhoto(media=START_IMG_URL, caption=caption, parse_mode=ParseMode.HTML), reply_markup=kb)
            except: await update.callback_query.message.edit_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=kb)
        else:
            if START_IMG_URL and START_IMG_URL.startswith("http"):
                try: await update.message.reply_photo(photo=START_IMG_URL, caption=caption, parse_mode=ParseMode.HTML, reply_markup=kb)
                except: await update.message.reply_text(caption, parse_mode=ParseMode.HTML, reply_markup=kb)
            else:
                await update.message.reply_text(caption, parse_mode=ParseMode.HTML, reply_markup=kb)

        if chat.type == ChatType.PRIVATE and not update.callback_query:
            await log_to_channel(context.bot, "command", {"user": f"{get_mention(user)} (`{user.id}`)", "action": "Started Bot", "chat": "Private"})
            
    except Exception as e:
        print(f"Start Error: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=HELP_IMG_URL,
        caption=f"📖 <b>{BOT_NAME} {stylize_text('Diary')}</b> 🌸\n\n<i>{stylize_text('Select a category below:')}</i>",
        parse_mode=ParseMode.HTML, reply_markup=get_help_keyboard()
    )

# --- 🖱️ CALLBACK HANDLER ---

async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == "return_start":
        await start(update, context)
        return

    if data == "help_main":
        try: await query.message.edit_media(InputMediaPhoto(media=HELP_IMG_URL, caption=f"📖 <b>{BOT_NAME} {stylize_text('Diary')}</b> 🌸\n\n<i>{stylize_text('Select a category below:')}</i>", parse_mode=ParseMode.HTML), reply_markup=get_help_keyboard())
        except: await query.message.edit_caption(caption=f"📖 <b>{BOT_NAME} {stylize_text('Diary')}</b> 🌸\n\n<i>{stylize_text('Select a category below:')}</i>", parse_mode=ParseMode.HTML, reply_markup=get_help_keyboard())
        return

    target_photo = HELP_IMG_URL
    kb = get_back_keyboard()
    text = ""
    
    if data == "help_social":
        text = (
            f"💍 <b>{stylize_text('Social & Love')}</b>\n\n"
            "<b>/propose @user</b>\n↳ ϻᴧꝛꝛʏ sσϻєσηє (5% ᴛᴧx ᴘєꝛᴋ)\n\n"
            "<b>/marry</b>\n↳ ᴄʜєᴄᴋ sᴛᴧᴛυs\n\n"
            "<b>/divorce</b>\n↳ ʙꝛєᴧᴋ υᴘ (ᴄσsᴛ 2ᴋ)\n\n"
            "<b>/couple</b>\n↳ ϻᴧᴛᴄʜϻᴧᴋɪηɢ ғυη"
        )
    elif data == "help_economy":
        text = (
            f"👛 <b>{stylize_text('Economy & Shop')}</b>\n\n"
            "<b>/bal</b>\n↳ ᴡᴧʟʟєᴛ & Ꝛᴧηᴋ\n\n"
            "<b>/shop</b>\n↳ ʙυʏ ᴡєᴧᴘσηs & ᴧꝛϻσꝛ\n\n"
            "<b>/give [amt] [user]</b>\n↳ ᴛꝛᴧηsғєꝛ (10% ᴛᴧx)\n\n"
            "<b>/claim</b>\n↳ ɢꝛσυᴘ ʙσηυs (2ᴋ)\n\n"
            "<b>/daily</b>\n↳ sᴛꝛєᴧᴋ Ꝛєᴡᴧꝛᴅs"
        )
    elif data == "help_rpg":
        text = (
            f"⚔️ <b>{stylize_text('RPG & War')}</b>\n\n"
            "<b>/kill [user]</b>\n↳ ϻυꝛᴅєꝛ & ʟσσᴛ (50%)\n\n"
            "<b>/rob [amt] [user]</b>\n↳ sᴛєᴧʟ ᴄσɪηs (100% sυᴄᴄєss)\n\n"
            "<b>/protect 1d</b>\n↳ ʙυʏ 24ʜ sʜɪєʟᴅ\n\n"
            "<b>/revive</b>\n↳ ɪηsᴛᴧηᴛ Ꝛєᴠɪᴠє (500ᴄ)"
        )
    elif data == "help_fun":
        text = (
            f"🧠 <b>{stylize_text('AI & Media')}</b>\n\n"
            "<b>/draw [prompt]</b>\n↳ ɢєηєꝛᴧᴛє ᴧηɪϻє ᴧꝛᴛ\n\n"
            "<b>/speak [text]</b>\n↳ ᴄυᴛє ᴧηɪϻє ᴛᴛs\n\n"
            "<b>/chatbot</b>\n↳ ᴧɪ sєᴛᴛɪηɢs\n\n"
            "<b>/riddle</b>\n↳ ᴧɪ ǫυɪᴢ (1ᴋ Ꝛєᴡᴧꝛᴅ)\n\n"
            "<b>/dice | /slots</b>\n↳ ɢᴧϻʙʟɪηɢ"
        )
    elif data == "help_group":
        text = (
            f"⛩️ <b>{stylize_text('Group Settings')}</b>\n\n"
            "<b>/welcome on/off</b>\n↳ ᴡєʟᴄσϻє ɪϻᴧɢєs\n\n"
            "<b>/ping</b>\n↳ sʏsᴛєϻ sᴛᴧᴛυs"
        )
    elif data == "help_sudo":
        if query.from_user.id not in SUDO_USERS: return await query.answer("❌ Baka! Owner Only!", show_alert=True)
        target_photo = SUDO_IMG
        text = (
            f"🔐 <b>{stylize_text('Sudo Panel')}</b>\n\n"
            "<b>/addcoins</b>, <b>/rmcoins</b>\n"
            "<b>/freerevive</b>, <b>/unprotect</b>\n"
            "<b>/broadcast</b>, <b>/cleandb</b>\n"
            "<b>/update</b>, <b>/addsudo</b>"
        )

    try: await query.message.edit_media(InputMediaPhoto(media=target_photo, caption=text, parse_mode=ParseMode.HTML), reply_markup=kb)
    except: await query.message.edit_caption(caption=text, parse_mode=ParseMode.HTML, reply_markup=kb)