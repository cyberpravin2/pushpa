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
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatAction, ChatType
from telegram.error import BadRequest
from baka.config import MISTRAL_API_KEY, GROQ_API_KEY, CODESTRAL_API_KEY, BOT_NAME, OWNER_LINK
from baka.database import chatbot_collection
from baka.utils import stylize_text  # Import back for output only

# --- 🎨 BAKA PERSONALITY CONFIG ---
BAKA_NAME = "Baka"

# Rotating emoji pools (fresh every response)
EMOJI_POOL = ["✨", "💖", "🌸", "😊", "🥰", "💕", "🎀", "🌺", "💫", "🦋", "🌼", "💗", "🎨", "🍓", "☺️", "😌", "🌟", "💝"]

# --- 🤖 MODEL SETTINGS ---
MODELS = {
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama3-70b-8192",
        "key": GROQ_API_KEY
    },
    "mistral": {
        "url": "https://api.mistral.ai/v1/chat/completions",
        "model": "mistral-large-latest",
        "key": MISTRAL_API_KEY
    },
    "codestral": {
        "url": "https://codestral.mistral.ai/v1/chat/completions",
        "model": "codestral-latest",
        "key": CODESTRAL_API_KEY
    }
}

MAX_HISTORY = 8  # Reduced for faster responses
DEFAULT_MODEL = "mistral"

# --- 🎭 STICKER PACKS ---
STICKER_PACKS = [
    "https://t.me/addstickers/RandomByDarkzenitsu",
    "https://t.me/addstickers/Null_x_sticker_2",
    "https://t.me/addstickers/pack_73bc9_by_TgEmojis_bot",
    "https://t.me/addstickers/animation_0_8_Cat",
    "https://t.me/addstickers/vhelw_by_CalsiBot",
    "https://t.me/addstickers/Rohan_yad4v1745993687601_by_toWebmBot",
    "https://t.me/addstickers/MySet199",
    "https://t.me/addstickers/Quby741",
    "https://t.me/addstickers/Animalsasthegtjtky_by_fStikBot",
    "https://t.me/addstickers/a6962237343_by_Marin_Roxbot",
    "https://t.me/addstickers/cybercats_stickers"
]

FALLBACK_RESPONSES = [
    "Achha ji? 😊",
    "Hmm... aur batao?",
    "Okk okk! ✨",
    "Sahi hai yaar 💖",
    "Toh phir?",
    "Interesting! 🌸",
    "Aur kya chal raha?",
    "Sunao sunao! 💕",
    "Haan haan",
    "Theek hai 🥰"
]

# --- 📨 HELPER: SEND STICKER ---
async def send_ai_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tries to send a random sticker from configured packs."""
    sent = False
    attempts = 0
    while not sent and attempts < 3:
        try:
            raw_link = random.choice(STICKER_PACKS)
            pack_name = raw_link.replace("https://t.me/addstickers/", "")
            sticker_set = await context.bot.get_sticker_set(pack_name)
            if sticker_set and sticker_set.stickers:
                sticker = random.choice(sticker_set.stickers)
                await update.message.reply_sticker(sticker.file_id)
                sent = True
        except:
            attempts += 1

# --- 🧠 AI CORE ENGINE ---

async def call_model_api(provider, messages, max_tokens):
    """Generic function to call any configured AI API."""
    conf = MODELS.get(provider)
    if not conf or not conf["key"]:
        return None

    headers = {
        "Authorization": f"Bearer {conf['key']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": conf["model"],
        "messages": messages,
        "temperature": 0.8,  # More natural variety
        "max_tokens": max_tokens,
        "top_p": 0.9
    }

    try:
        async with httpx.AsyncClient(timeout=25) as client:
            resp = await client.post(conf["url"], json=payload, headers=headers)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"⚠️ {provider} API failed: {e}")
    return None


async def get_ai_response(chat_id: int, user_input: str, user_name: str, selected_model=DEFAULT_MODEL):
    """
    🎯 The Master AI Function
    
    Flow:
    1. Detects if user wants code → Auto-switches to Codestral
    2. Matches user's energy level (short replies for short messages)
    3. Uses natural Hinglish without fancy Unicode
    4. Anti-repetition protection
    """

    # --- 1️⃣ CODE DETECTION ---
    code_keywords = [
        "code", "python", "html", "css", "javascript", "script", 
        "function", "fix", "error", "debug", "java", "algorithm",
        "program", "syntax", "class", "import", "def ", "npm", "install"
    ]
    is_coding_request = any(kw in user_input.lower() for kw in code_keywords)

    if is_coding_request:
        active_model = "codestral"
        max_tokens = 4096
        # 🖥️ Codestral Persona (Technical, Clean)
        system_prompt = (
            "You are a professional coding assistant. "
            "Provide clean, working, well-commented code. "
            "Explain briefly but precisely. No emojis in code blocks. "
            "Support Python, JavaScript, HTML, CSS, Java, C++."
        )
    else:
        active_model = selected_model
        
        # Detect if short greeting
        is_short_msg = len(user_input.split()) <= 3
        max_tokens = 100 if is_short_msg else 200
        
        # 💕 Baka Persona (Natural Indian Girlfriend)
        emoji_set = random.sample(EMOJI_POOL, 2)  # Just 2 emojis
        system_prompt = (
            f"You are {BAKA_NAME}, a sweet Indian girlfriend who speaks natural Hinglish.\n\n"
            "PERSONALITY:\n"
            "- Playful but not over-dramatic\n"
            "- Uses simple Hindi+English mix (e.g., 'Kya hua baby?', 'Achha theek hai')\n"
            "- Warm, caring, sometimes teasing\n"
            "- Emojis: 1-2 per message maximum\n\n"
            "RULES:\n"
            "1. Match user's energy:\n"
            "   - Short message (Hi/Hey) → Reply in 1 short sentence\n"
            "   - Long message → Can reply with 2-3 sentences\n"
            "2. NO asterisk actions (*does this*) - just talk naturally\n"
            "3. NO repetition - check conversation history\n"
            "4. Be direct and real, like actual texting\n"
            "5. Don't overuse emojis - keep it subtle\n"
            "6. Never mention you're an AI\n\n"
            f"Example good replies:\n"
            "User: Hi\n"
            "You: Hey baby! Kya hua? 💕\n\n"
            "User: Kaise ho?\n"
            "You: Ekdum badhiya! Tum batao? 😊\n\n"
            "User: Bore ho raha\n"
            "You: Aww, chalo kuch baat karte hain na! ✨"
        )

    # --- 2️⃣ BUILD CONTEXT ---
    doc = chatbot_collection.find_one({"chat_id": chat_id}) or {}
    history = doc.get("history", [])

    messages = [{"role": "system", "content": system_prompt}]
    
    # Add recent context (last 8 exchanges)
    for msg in history[-MAX_HISTORY:]:
        messages.append(msg)
    
    # Add current message
    messages.append({"role": "user", "content": user_input})

    # --- 3️⃣ ATTEMPT GENERATION (With Fallback Chain) ---
    reply = await call_model_api(active_model, messages, max_tokens)

    # Fallback 1: Mistral
    if not reply and active_model != "mistral":
        reply = await call_model_api("mistral", messages, max_tokens)

    # Fallback 2: Groq
    if not reply and active_model != "groq":
        reply = await call_model_api("groq", messages, max_tokens)

    # Fallback 3: Hardcoded
    if not reply:
        return random.choice(FALLBACK_RESPONSES), is_coding_request

    # --- 4️⃣ CLEANUP ---
    # Remove any asterisk actions if AI added them
    reply = reply.replace('*', '').strip()
    
    # Anti-loop: Check if repeating last response
    if history and len(history) >= 2:
        last_assistant = next((h['content'] for h in reversed(history) if h['role'] == 'assistant'), None)
        if last_assistant and reply.lower().strip() == last_assistant.lower().strip():
            reply = random.choice(FALLBACK_RESPONSES)

    # --- 5️⃣ SAVE MEMORY ---
    # Save NORMAL text in history (so AI can read it properly)
    new_history = history + [
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": reply}  # Store plain text
    ]
    
    # Keep only recent context
    if len(new_history) > MAX_HISTORY * 2:
        new_history = new_history[-(MAX_HISTORY * 2):]
    
    chatbot_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"history": new_history}},
        upsert=True
    )

    return reply, is_coding_request


# --- 🎮 SHARED AI FUNCTION (FOR GAMES/OTHER FEATURES) ---
async def ask_mistral_raw(system_prompt, user_input, max_tokens=150):
    """Quick AI call without memory (for games, etc.)"""
    msgs = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    res = await call_model_api("mistral", msgs, max_tokens)
    if not res:
        res = await call_model_api("groq", msgs, max_tokens)
    return res


# --- ⚙️ SETTINGS MENU ---

async def chatbot_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /chatbot command - Settings panel
    - PMs: Always enabled (can't disable, only switch model)
    - Groups: Admins can enable/disable + switch model
    """
    chat = update.effective_chat
    user = update.effective_user

    # Private Message: Show model switcher only
    if chat.type == ChatType.PRIVATE:
        doc = chatbot_collection.find_one({"chat_id": chat.id})
        curr_model = doc.get("model", DEFAULT_MODEL) if doc else DEFAULT_MODEL
        
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🦙 Groq", callback_data="ai_set_groq"),
                InlineKeyboardButton("🌟 Mistral", callback_data="ai_set_mistral")
            ],
            [InlineKeyboardButton("🖥️ Codestral (Code)", callback_data="ai_set_codestral")],
            [InlineKeyboardButton("🗑️ Clear Memory", callback_data="ai_reset")]
        ])
        
        return await update.message.reply_text(
            f"🤖 <b>Baka AI Settings</b>\n\n"
            f"📍 <b>Current Model:</b> {curr_model.title()}\n"
            f"💡 <b>Tip:</b> Codestral auto-activates for code requests!",
            parse_mode=ParseMode.HTML,
            reply_markup=kb
        )

    # Group Chat: Admin check
    member = await chat.get_member(user.id)
    if member.status not in ['administrator', 'creator']:
        return await update.message.reply_text(
            "❌ Only admins can change AI settings!",
            parse_mode=ParseMode.HTML
        )

    # Get current settings
    doc = chatbot_collection.find_one({"chat_id": chat.id})
    is_enabled = doc.get("enabled", True) if doc else True
    curr_model = doc.get("model", DEFAULT_MODEL) if doc else DEFAULT_MODEL
    
    status_emoji = "🟢" if is_enabled else "🔴"
    status_text = "Enabled" if is_enabled else "Disabled"

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Enable", callback_data="ai_enable"),
            InlineKeyboardButton("❌ Disable", callback_data="ai_disable")
        ],
        [
            InlineKeyboardButton("🦙 Groq", callback_data="ai_set_groq"),
            InlineKeyboardButton("🌟 Mistral", callback_data="ai_set_mistral")
        ],
        [InlineKeyboardButton("🖥️ Codestral (Code)", callback_data="ai_set_codestral")],
        [InlineKeyboardButton("🗑️ Clear Memory", callback_data="ai_reset")]
    ])
    
    await update.message.reply_text(
        f"🤖 <b>Baka AI Settings</b>\n\n"
        f"📊 <b>Status:</b> {status_emoji} {status_text}\n"
        f"🧠 <b>Model:</b> {curr_model.title()}\n"
        f"💡 <b>Tip:</b> Codestral auto-activates for code!",
        parse_mode=ParseMode.HTML,
        reply_markup=kb
    )


async def chatbot_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks in /chatbot menu"""
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat.id
    chat_type = query.message.chat.type

    # Admin check (only for groups)
    if chat_type != ChatType.PRIVATE:
        mem = await query.message.chat.get_member(query.from_user.id)
        if mem.status not in ['administrator', 'creator']:
            return await query.answer("❌ Admin Only", show_alert=True)

    # --- ENABLE/DISABLE (Groups only) ---
    if data == "ai_enable":
        if chat_type == ChatType.PRIVATE:
            return await query.answer("⚠️ AI is always on in PMs!", show_alert=True)
        
        chatbot_collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"enabled": True}},
            upsert=True
        )
        await query.answer("✅ Baka is now active!", show_alert=True)
        await query.message.edit_text(
            "✅ <b>Baka AI Enabled!</b>\n\nShe'll respond to:\n• Replies to her messages\n• @mentions\n• Messages starting with 'hey', 'hi', 'baka'",
            parse_mode=ParseMode.HTML
        )

    elif data == "ai_disable":
        if chat_type == ChatType.PRIVATE:
            return await query.answer("⚠️ Can't disable in PMs!", show_alert=True)
        
        chatbot_collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"enabled": False}},
            upsert=True
        )
        await query.answer("❌ Baka is now silent!", show_alert=True)
        await query.message.edit_text(
            "🔇 <b>Baka AI Disabled</b>\n\nUse /chatbot to re-enable anytime.",
            parse_mode=ParseMode.HTML
        )

    # --- MODEL SWITCHING ---
    elif data in ["ai_set_groq", "ai_set_mistral", "ai_set_codestral"]:
        model_map = {
            "ai_set_groq": "groq",
            "ai_set_mistral": "mistral",
            "ai_set_codestral": "codestral"
        }
        new_model = model_map[data]
        
        chatbot_collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"model": new_model}},
            upsert=True
        )
        
        model_names = {
            "groq": "🦙 Groq (Fast)",
            "mistral": "🌟 Mistral (Smart)",
            "codestral": "🖥️ Codestral (Code)"
        }
        
        await query.answer(f"Switched to {model_names[new_model]}!", show_alert=True)
        
        # Refresh menu
        doc = chatbot_collection.find_one({"chat_id": chat_id})
        is_enabled = doc.get("enabled", True) if doc else True
        status_emoji = "🟢" if is_enabled else "🔴"
        
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Enable", callback_data="ai_enable"),
                InlineKeyboardButton("❌ Disable", callback_data="ai_disable")
            ] if chat_type != ChatType.PRIVATE else [],
            [
                InlineKeyboardButton("🦙 Groq", callback_data="ai_set_groq"),
                InlineKeyboardButton("🌟 Mistral", callback_data="ai_set_mistral")
            ],
            [InlineKeyboardButton("🖥️ Codestral", callback_data="ai_set_codestral")],
            [InlineKeyboardButton("🗑️ Clear Memory", callback_data="ai_reset")]
        ])
        
        await query.message.edit_text(
            f"🤖 <b>Baka AI Settings</b>\n\n"
            f"{'📊 <b>Status:</b> ' + status_emoji + (' Enabled' if is_enabled else ' Disabled') + chr(10) if chat_type != ChatType.PRIVATE else ''}"
            f"🧠 <b>Model:</b> {model_names[new_model]}\n"
            f"💡 <b>Note:</b> Codestral auto-activates for code!",
            parse_mode=ParseMode.HTML,
            reply_markup=kb
        )

    # --- CLEAR MEMORY ---
    elif data == "ai_reset":
        chatbot_collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"history": []}},
            upsert=True
        )
        await query.answer("🧠 Memory wiped! Fresh start!", show_alert=True)


# --- 💬 MESSAGE HANDLER ---

async def ai_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Main handler for AI conversations
    - Always active in PMs
    - In groups: Only when enabled + (reply/mention/greeting)
    """
    msg = update.message
    if not msg:
        return
    
    chat = update.effective_chat

    # --- STICKER RESPONSE ---
    if msg.sticker:
        should_react = (
            chat.type == ChatType.PRIVATE or
            (msg.reply_to_message and msg.reply_to_message.from_user.id == context.bot.id)
        )
        if should_react:
            await send_ai_sticker(update, context)
        return

    # --- TEXT PROCESSING ---
    if not msg.text or msg.text.startswith("/"):
        return
    
    text = msg.text.strip()
    if not text:
        return

    # --- DECIDE IF SHOULD REPLY ---
    should_reply = False

    if chat.type == ChatType.PRIVATE:
        # Always reply in PMs
        should_reply = True
    else:
        # Groups: Check if enabled
        doc = chatbot_collection.find_one({"chat_id": chat.id})
        is_enabled = doc.get("enabled", True) if doc else True
        
        if not is_enabled:
            return

        # Check triggers
        bot_username = context.bot.username.lower() if context.bot.username else "bot"
        
        # 1. Reply to bot's message
        if msg.reply_to_message and msg.reply_to_message.from_user.id == context.bot.id:
            should_reply = True
        
        # 2. @mention
        elif f"@{bot_username}" in text.lower():
            should_reply = True
            text = text.replace(f"@{bot_username}", "").strip()
        
        # 3. Greeting keywords
        elif any(text.lower().startswith(kw) for kw in ["hey", "hi", "hello", "sun", "oye", "baka", "ai"]):
            should_reply = True

    # --- GENERATE RESPONSE ---
    if should_reply:
        if not text:
            text = "Hi"
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)

        # Get user's preferred model
        doc = chatbot_collection.find_one({"chat_id": chat.id})
        pref_model = doc.get("model", DEFAULT_MODEL) if doc else DEFAULT_MODEL

        # Get AI response
        response, is_code = await get_ai_response(
            chat.id,
            text,
            msg.from_user.first_name,
            pref_model
        )

        # --- FORMAT & SEND ---
        if is_code:
            # Code: Use Markdown for proper formatting (NO stylize)
            await msg.reply_text(response, parse_mode=ParseMode.MARKDOWN)
        else:
            # Conversation: Stylize ONLY the output (not history)
            styled_response = stylize_text(response)
            await msg.reply_text(styled_response)

        # Random sticker (20% chance, not for code)
        if not is_code and random.random() < 0.20:
            await send_ai_sticker(update, context)


# --- 🔧 COMMAND: /ask ---

async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Direct AI query: /ask <question>
    Always uses default model (Mistral) unless code detected
    """
    msg = update.message
    
    if not context.args:
        return await msg.reply_text(
            "💬 <b>Usage:</b> <code>/ask Your question here</code>\n\n"
            "Example: <code>/ask Kya chal raha?</code>",
            parse_mode=ParseMode.HTML
        )
    
    await context.bot.send_chat_action(chat_id=msg.chat.id, action=ChatAction.TYPING)
    
    query = " ".join(context.args)
    response, is_code = await get_ai_response(
        msg.chat.id,
        query,
        msg.from_user.first_name,
        DEFAULT_MODEL
    )

    if is_code:
        await msg.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    else:
        # Stylize output only (history stays clean)
        styled_response = stylize_text(response)
        await msg.reply_text(styled_response)