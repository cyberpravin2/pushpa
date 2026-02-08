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

import time
import psutil
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import START_TIME, BOT_NAME
from baka.utils import stylize_text

def get_readable_time(seconds: int) -> str:
    count = 0
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        time_list.pop()

    time_list.reverse()
    return ":".join(time_list)

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Checks API Latency and System Stats."""
    if not update.message: return
    
    try:
        start_time = time.time()
        msg = await update.message.reply_text(f"⚡ <b>{stylize_text('Pinging')}...</b>", parse_mode=ParseMode.HTML)
        end_time = time.time()
        latency = round((end_time - start_time) * 1000)
        
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton(f"📡 {stylize_text('System Stats')}", callback_data="sys_stats")
        ]])
        
        await msg.edit_text(
            f"🏓 <b>{stylize_text('Pong')}!</b>\n\n"
            f"📶 <b>{stylize_text('Latency')}:</b> <code>{latency}ms</code>\n"
            f"🤖 <b>{stylize_text('Status')}:</b> 🟢 σηʟɪηє\n"
            f"<i>{stylize_text('Click below for server details!')}</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=kb
        )
    except Exception as e:
        print(f"Ping Error: {e}")

async def ping_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data != "sys_stats": return
    
    try:
        uptime = get_readable_time(int(time.time() - START_TIME))
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage(os.getcwd()).percent
        
        # Unicode Fonts work in Popups!
        text = (
            f"📊 {stylize_text(f'{BOT_NAME} Stats')} 📊\n\n"
            f"⏰ {stylize_text('Uptime')}: {uptime}\n"
            f"🧠 {stylize_text('RAM')}: {ram}%\n"
            f"⚙️ {stylize_text('CPU')}: {cpu}%\n"
            f"💾 {stylize_text('Disk')}: {disk}%"
        )
        
        await query.answer(text, show_alert=True)
    except:
        await query.answer("❌ Error fetching stats", show_alert=True)