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

import httpx
import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.utils import ensure_user_exists, resolve_target, get_mention, stylize_text, format_money
from baka.database import users_collection
from baka.config import WAIFU_PROPOSE_COST
from baka.plugins.chatbot import ask_mistral_raw

API_URL = "https://api.waifu.pics"
SFW_ACTIONS = ["kick", "happy", "wink", "poke", "dance", "cringe", "kill", "waifu", "neko", "shinobu", "bully", "cuddle", "cry", "hug", "awoo", "kiss", "lick", "pat", "smug", "bonk", "yeet", "blush", "smile", "wave", "highfive", "handhold", "nom", "bite", "glomp", "slap"]

async def waifu_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmd = update.message.text.split()[0].replace("/", "")
    if cmd not in SFW_ACTIONS: return

    target, _ = await resolve_target(update, context)
    user = update.effective_user
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{API_URL}/sfw/{cmd}")
            url = resp.json()['url']
    except: return

    s_link = get_mention(user)
    t_link = get_mention(target) if target else "the air"
    caption = f"{s_link} {cmd}s {t_link}!"
    if cmd == "kill": caption = f"{s_link} murdered {t_link} 💀"
    if cmd == "kiss": caption = f"{s_link} kissed {t_link} 💋"

    await update.message.reply_animation(animation=url, caption=caption, parse_mode=ParseMode.HTML)

async def wpropose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Propose to a Waifu (Uses Gold)."""
    user = ensure_user_exists(update.effective_user)
    
    if user['balance'] < WAIFU_PROPOSE_COST:
        return await update.message.reply_text(f"❌ <b>Poor!</b> Need {format_money(WAIFU_PROPOSE_COST)}.", parse_mode=ParseMode.HTML)

    users_collection.update_one({"user_id": user['user_id']}, {"$inc": {"balance": -WAIFU_PROPOSE_COST}})
    
    success = random.random() < 0.3
    
    if success:
        # Celestial Waifu
        async with httpx.AsyncClient() as client:
            r = await client.get("https://api.waifu.im/search?tags=waifu")
            img_url = r.json()['images'][0]['url']
            
        waifu_data = {"name": "Celestial Queen", "rarity": "Celestial", "date": datetime.utcnow()}
        users_collection.update_one({"user_id": user['user_id']}, {"$push": {"waifus": waifu_data}})
        
        await update.message.reply_photo(img_url, caption=f"💍 <b>YES!</b>\n\nYou married a <b>CELESTIAL WAIFU</b>!", parse_mode=ParseMode.HTML)
    else:
        prompt = "Roast a user named 'Player' who got rejected by an anime girl. Hinglish."
        roast = await ask_mistral_raw("Savage Roaster", prompt)
        fail_gifs = ["https://media.giphy.com/media/pSpmPXdHQWZrcuJRq3/giphy.gif"]
        
        await update.message.reply_animation(
            random.choice(fail_gifs),
            caption=f"💔 <b>REJECTED!</b>\n\n🗣️ <i>{stylize_text(roast or 'Lol loser.')}</i>",
            parse_mode=ParseMode.HTML
        )

async def wmarry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = ensure_user_exists(update.effective_user)
    last = user.get("last_wmarry")
    if last and (datetime.utcnow() - last) < timedelta(hours=2):
        return await update.message.reply_text(f"⏳ <b>Cooldown!</b> Wait.", parse_mode=ParseMode.HTML)

    async with httpx.AsyncClient() as client:
        r = await client.get("https://api.waifu.pics/sfw/waifu")
        url = r.json()['url']

    waifu_data = {"name": "Random Waifu", "rarity": "Rare", "date": datetime.utcnow()}
    users_collection.update_one({"user_id": user['user_id']}, {"$push": {"waifus": waifu_data}, "$set": {"last_wmarry": datetime.utcnow()}})

    await update.message.reply_photo(url, caption="💍 <b>Married!</b>\nAdded <b>Rare Waifu</b> to collection.", parse_mode=ParseMode.HTML)
