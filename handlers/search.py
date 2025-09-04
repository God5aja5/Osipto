import re
import json
import io
import telebot
import utils
import db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS
from typing import Any

# ----- Constants -----
API_MAP = {
    "phone_in": "https://private-9e6q.onrender.com/search/?q={}",
    "phone_pk": "https://allnetworkdata.com/?number={}",
    "ip":       "https://ip-info.bjcoderx.workers.dev/?ip={}",
    "ifsc":     "https://ifsc.razorpay.com/{}",
    "ffuid":    "http://raw.thug4ff.com/info?uid={}",
    "pin":      "https://pincode-info-j4tnx.vercel.app/pincode={}"
}

BANNERS = {
    "phone_in": "📱 Indian Phone",
    "phone_pk": "📱 Pakistan Phone",
    "ip":       "🌐 IP Address",
    "ifsc":     "🏦 IFSC Code",
    "ffuid":    "🎮 Free Fire UID",
    "pin":      "📮 Pin-Code"
}

CREDIT_COST = 5

# ----- Helpers -----
def clean_phone(number: str) -> str:
    return re.sub(r"^(?:\+?91|0+)", "", number.strip())

def escape_md(text: Any) -> str:
    """Escape text for MarkdownV2 safely."""
    if text is None:
        text = ""
    text = str(text)
    # Escape all reserved characters for MarkdownV2
    for c in r"_*[]()~`>#+-=|{}.!":
        text = text.replace(c, "\\" + c)
    return text

def create_separator(length: int = 25) -> str:
    """Create a decorative separator line"""
    return "─" * length

def create_header(title: str, emoji: str = "🔍") -> str:
    """Create a formatted header"""
    return f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n┃ {emoji} {escape_md(title)} ┃\n┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"

def create_field_row(label: str, value: Any, emoji: str = "▫️") -> str:
    """Create a formatted field row"""
    if value is None or str(value).strip() == "":
        value = "N/A"
    return f"{emoji} **{escape_md(label)}:** `{escape_md(value)}`"

def flatten(obj: Any, prefix: str = "") -> dict:
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            out.update(flatten(item, f"{prefix}[{idx}]"))
    else:
        out[prefix] = obj
    return out

# ----- Formatters -----
def format_pin(data: Any) -> str:
    if isinstance(data, list):
        data = data[0] if data else {}
    if not isinstance(data, dict):
        return create_header("PIN DETAILS", "❌") + "\n\n❌ **No data found**"
    
    lines = [create_header("PIN CODE DETAILS", "📮"), ""]
    
    post_offices = data.get("PostOffice", [])
    if not post_offices:
        lines.append("❌ **No post office data available**")
    else:
        for idx, po in enumerate(post_offices):
            if idx > 0:
                lines.append("")  # Add spacing between offices
            
            lines.append(f"📍 **Post Office #{idx + 1}**")
            lines.append("┌─────────────────────────────")
            lines.append(create_field_row("Name", po.get('Name'), "🏤"))
            lines.append(create_field_row("Branch Type", po.get('BranchType'), "🏢"))
            lines.append(create_field_row("Delivery Status", po.get('DeliveryStatus'), "📬"))
            lines.append(create_field_row("District", po.get('District'), "🏘️"))
            lines.append(create_field_row("State", po.get('State'), "🌍"))
            lines.append(create_field_row("PIN Code", po.get('Pincode'), "📮"))
            lines.append("└─────────────────────────────")
    
    return "\n".join(lines)

def format_ffuid(data: Any) -> str:
    if not isinstance(data, dict):
        return create_header("FREE FIRE PLAYER", "❌") + "\n\n❌ **No player data found**"
    
    lines = [create_header("FREE FIRE PLAYER INFO", "🎮"), ""]
    
    # Extract data sections
    basic = data.get("basicInfo", {})
    social = data.get("socialInfo", {})
    clan = data.get("clanBasicInfo", {})
    captain = data.get("captainBasicInfo", {})
    diamond_info = data.get("diamondCostRes", {})
    pet_info = data.get("petInfo", {})
    profile_info = data.get("profileInfo", {})
    
    # Basic Information Section
    if basic:
        lines.append("👤 **BASIC INFORMATION**")
        lines.append("┌─────────────────────────────")
        lines.append(create_field_row("Nickname", basic.get('nickname'), "🎯"))
        lines.append(create_field_row("Account ID", basic.get('accountId'), "🆔"))
        lines.append(create_field_row("Level", basic.get('level'), "📈"))
        lines.append(create_field_row("Rank", basic.get('rank'), "🏆"))
        lines.append(create_field_row("Region", basic.get('region'), "🌍"))
        lines.append(create_field_row("Last Login", basic.get('lastLoginAt'), "🕒"))
        lines.append("└─────────────────────────────")
        lines.append("")
    
    # Social Information Section
    if social:
        lines.append("💫 **SOCIAL STATS**")
        lines.append("┌─────────────────────────────")
        lines.append(create_field_row("Likes Received", social.get('liked'), "❤️"))
        lines.append("└─────────────────────────────")
        lines.append("")
    
    # Game Assets Section
    lines.append("💎 **GAME ASSETS**")
    lines.append("┌─────────────────────────────")
    lines.append(create_field_row("Diamonds", diamond_info.get('diamondCost'), "💎"))
    
    # Pet Information
    pet_id = pet_info.get('id') if pet_info else None
    lines.append(create_field_row("Pet ID", pet_id, "🐾"))
    
    # Equipped Skills/Weapons
    equipped_skills = profile_info.get('equipedSkills', []) if profile_info else []
    if equipped_skills:
        skills_str = ', '.join(map(str, equipped_skills))
        lines.append(create_field_row("Equipped Skills", skills_str, "⚔️"))
    else:
        lines.append(create_field_row("Equipped Skills", "None", "⚔️"))
    
    lines.append("└─────────────────────────────")
    lines.append("")
    
    # Clan Information Section
    if clan and clan.get('clanName'):
        lines.append("🏰 **CLAN INFORMATION**")
        lines.append("┌─────────────────────────────")
        lines.append(create_field_row("Clan Name", clan.get('clanName'), "🏰"))
        lines.append(create_field_row("Members", clan.get('memberNum'), "👥"))
        
        # Captain info
        if captain and captain.get('nickname'):
            lines.append(create_field_row("Captain", captain.get('nickname'), "👑"))
        
        lines.append("└─────────────────────────────")
    
    return "\n".join(lines)

def format_phone_info(data: Any, query: str, country: str = "IN") -> str:
    """Format phone number information"""
    country_flag = "🇮🇳" if country == "IN" else "🇵🇰"
    country_name = "Indian" if country == "IN" else "Pakistani"
    
    lines = [create_header(f"{country_name} PHONE INFO", "📱"), ""]
    
    lines.append("📞 **PHONE DETAILS**")
    lines.append("┌─────────────────────────────")
    lines.append(create_field_row("Number", query, f"{country_flag}"))
    
    if isinstance(data, dict):
        # Common phone info fields
        phone_fields = {
            "name": ("👤", "Name"),
            "cnic": ("🆔", "CNIC"),
            "address": ("🏠", "Address"),
            "district": ("🏘️", "District"),
            "state": ("🌍", "State"),
            "operator": ("📡", "Operator"),
            "circle": ("🔄", "Circle"),
            "type": ("📋", "Type")
        }
        
        flat = flatten(data)
        for key, value in flat.items():
            key_lower = key.lower().split('.')[-1]
            if key_lower in phone_fields:
                emoji, label = phone_fields[key_lower]
                lines.append(create_field_row(label, value, emoji))
            else:
                lines.append(create_field_row(key, value, "▫️"))
    
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            lines.append(create_field_row(f"Result {idx + 1}", item, "📄"))
    else:
        lines.append(create_field_row("Data", data, "📄"))
    
    lines.append("└─────────────────────────────")
    return "\n".join(lines)

def format_ip_info(data: Any, query: str) -> str:
    """Format IP address information"""
    lines = [create_header("IP ADDRESS INFO", "🌐"), ""]
    
    lines.append("🌍 **LOCATION DETAILS**")
    lines.append("┌─────────────────────────────")
    lines.append(create_field_row("IP Address", query, "🌐"))
    
    if isinstance(data, dict):
        ip_fields = {
            "country": ("🇺🇳", "Country"),
            "region": ("🏞️", "Region"),
            "city": ("🏙️", "City"),
            "timezone": ("🕒", "Timezone"),
            "isp": ("🏢", "ISP"),
            "org": ("🏛️", "Organization"),
            "as": ("🔢", "AS Number"),
            "lat": ("📍", "Latitude"),
            "lon": ("📍", "Longitude")
        }
        
        flat = flatten(data)
        for key, value in flat.items():
            key_lower = key.lower().split('.')[-1]
            if key_lower in ip_fields:
                emoji, label = ip_fields[key_lower]
                lines.append(create_field_row(label, value, emoji))
            else:
                lines.append(create_field_row(key, value, "▫️"))
    
    lines.append("└─────────────────────────────")
    return "\n".join(lines)

def format_ifsc_info(data: Any, query: str) -> str:
    """Format IFSC code information"""
    lines = [create_header("BANK DETAILS", "🏦"), ""]
    
    lines.append("🏛️ **BANK INFORMATION**")
    lines.append("┌─────────────────────────────")
    lines.append(create_field_row("IFSC Code", query, "🏦"))
    
    if isinstance(data, dict):
        bank_fields = {
            "bank": ("🏛️", "Bank Name"),
            "branch": ("🏤", "Branch"),
            "address": ("🏠", "Address"),
            "city": ("🏙️", "City"),
            "district": ("🏘️", "District"),
            "state": ("🌍", "State"),
            "contact": ("📞", "Contact"),
            "rtgs": ("💳", "RTGS"),
            "neft": ("💰", "NEFT"),
            "imps": ("⚡", "IMPS")
        }
        
        flat = flatten(data)
        for key, value in flat.items():
            key_lower = key.lower().split('.')[-1]
            if key_lower in bank_fields:
                emoji, label = bank_fields[key_lower]
                lines.append(create_field_row(label, value, emoji))
            else:
                lines.append(create_field_row(key, value, "▫️"))
    
    lines.append("└─────────────────────────────")
    return "\n".join(lines)

def format_generic(typ: str, obj: Any, query: str) -> str:
    """Generic formatter with improved UI"""
    banner = BANNERS.get(typ, typ.upper())
    lines = [create_header(f"{banner} RESULTS", "🔍"), ""]
    
    lines.append(f"🎯 **Query:** `{escape_md(query)}`")
    lines.append("")
    
    if isinstance(obj, list):
        lines.append("📋 **RESULTS LIST**")
        lines.append("┌─────────────────────────────")
        for idx, item in enumerate(obj):
            lines.append(create_field_row(f"Result {idx + 1}", item, "📄"))
        lines.append("└─────────────────────────────")
    elif isinstance(obj, dict):
        lines.append("📊 **DETAILED INFORMATION**")
        lines.append("┌─────────────────────────────")
        flat = flatten(obj)
        for k, v in flat.items():
            lines.append(create_field_row(k, v, "▫️"))
        lines.append("└─────────────────────────────")
    else:
        lines.append("📄 **RAW DATA**")
        lines.append("┌─────────────────────────────")
        lines.append(create_field_row("Data", obj, "📄"))
        lines.append("└─────────────────────────────")
    
    return "\n".join(lines)

# ----- Bot Handlers -----
def register(bot: telebot.TeleBot):
    @bot.callback_query_handler(func=lambda c: c.data.startswith("sr_"))
    def handle_callback(c):
        typ = c.data.split("_", 1)[1]
        bot.send_message(
            c.message.chat.id,
            f"📩 Send the query for **{escape_md(typ.upper())}**",
            parse_mode="MarkdownV2"
        )
        bot.register_next_step_handler_by_chat_id(
            c.message.chat.id,
            lambda m: do_search(m, typ)
        )

    def do_search(m, typ):
        q = m.text.strip()
        uid = m.from_user.id

        if typ == "phone_in":
            q = clean_phone(q)
        elif typ == "phone_pk":
            q = re.sub(r"\D", "", q)

        if not q:
            return bot.reply_to(m, "❌ **Empty query\\.**", parse_mode="MarkdownV2")

        if uid not in ADMIN_IDS and db.get_credits(uid) < CREDIT_COST:
            return bot.reply_to(
                m, f"❌ **Insufficient credits**\nBuy from /plans",
                parse_mode="MarkdownV2"
            )

        prog = bot.send_message(m.chat.id, "⏳ **Searching…**", parse_mode="MarkdownV2")

        try:
            raw = utils.fetch(API_MAP[typ].format(q))
            parsed = {}
            try:
                parsed = json.loads(raw) or {}
            except:
                parsed = {"raw": raw}

            # Clean unwanted fields
            if isinstance(parsed, dict):
                for key in ["dev", "channel"]:
                    parsed.pop(key, None)

            # Format based on type with improved UI
            if typ == "pin":
                formatted = format_pin(parsed)
            elif typ == "ffuid":
                formatted = format_ffuid(parsed)
            elif typ == "phone_in":
                formatted = format_phone_info(parsed, q, "IN")
            elif typ == "phone_pk":
                formatted = format_phone_info(parsed, q, "PK")
            elif typ == "ip":
                formatted = format_ip_info(parsed, q)
            elif typ == "ifsc":
                formatted = format_ifsc_info(parsed, q)
            else:
                formatted = format_generic(typ, parsed, q)

            # Handle long messages
            if len(formatted) > 4096:
                file = io.BytesIO(formatted.encode())
                file.name = f"{typ}_{q}_details.txt"
                bot.edit_message_text(
                    "📄 **Response too long\\. Sent as file\\.**",
                    prog.chat.id,
                    prog.message_id,
                    parse_mode="MarkdownV2"
                )
                bot.send_document(m.chat.id, file, caption="📊 **Full Details**", parse_mode="MarkdownV2")
            else:
                bot.edit_message_text(
                    formatted,
                    prog.chat.id,
                    prog.message_id,
                    parse_mode="MarkdownV2"
                )

            # Deduct credits and log
            if uid not in ADMIN_IDS:
                db.add_credits(uid, -CREDIT_COST)
            db.log_search(uid, q, typ, formatted[:1000])  # Log first 1000 chars

        except Exception as e:
            error_msg = f"❌ **Search Error**\n\n`{escape_md(str(e))}`"
            bot.edit_message_text(
                error_msg,
                prog.chat.id,
                prog.message_id,
                parse_mode="MarkdownV2"
            )
