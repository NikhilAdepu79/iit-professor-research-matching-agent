import os
import json
import httpx
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from src.gmail_sender import load_env_file

def send_discord_embed(
    title: str,
    description: str,
    color: int = 0x2563eb,
    fields: Optional[List[Dict[str, Any]]] = None,
    webhook_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sends a rich formatted card embed to a Discord channel via Webhook.
    Colors:
      - Green: 0x16a34a (Positive / Reply)
      - Yellow: 0xca8a04 (OOO / On Leave)
      - Orange: 0xd97706 (Follow-Up Due / Sent)
      - Red: 0xdc2626 (Bounce / Invalid)
      - Blue: 0x2563eb (Outreach / Sent)
    """
    load_env_file()
    url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL", "").strip()
    
    if not url:
        return {
            "status": "skipped",
            "message": "DISCORD_WEBHOOK_URL not configured in .env. Skipping Discord notification."
        }
        
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "footer": {
            "text": "National AI Research Outreach & Matching Agent • Adepu Nikhil"
        }
    }
    
    if fields:
        embed["fields"] = fields
        
    payload = {
        "username": "Research Outreach Agent",
        "avatar_url": "https://img.icons8.com/color/96/artificial-intelligence.png",
        "embeds": [embed]
    }
    
    try:
        res = httpx.post(url, json=payload, timeout=10.0)
        if res.status_code in [200, 204]:
            return {"status": "sent", "message": "Discord embed dispatched successfully."}
        else:
            return {"status": "error", "message": f"Discord Webhook error ({res.status_code}): {res.text}"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to send Discord alert: {str(e)}"}

def notify_professor_reply(professor_name: str, institution: str, email_addr: str, snippet: str, status: str = "Replied") -> Dict[str, Any]:
    """Dispatches a rich green notification card when a professor replies."""
    is_interested = (status == "Interested")
    color = 0x16a34a if is_interested else 0x0891b2
    title = f"🟢 {'INTERESTED LEAD' if is_interested else 'PROFESSOR RESPONSE'}: {professor_name}"
    description = f"**{professor_name}** from **{institution}** has responded to your research internship application!"
    
    fields = [
        {"name": "🏛️ Institution", "value": institution, "inline": True},
        {"name": "📧 Email", "value": f"`{email_addr}`", "inline": True},
        {"name": "💬 Message Preview", "value": f"```{snippet[:350]}```", "inline": False},
        {"name": "🔗 Action", "value": "[Open Gmail to Reply](https://mail.google.com/)", "inline": False}
    ]
    return send_discord_embed(title=title, description=description, color=color, fields=fields)

def notify_ooo_detected(professor_name: str, institution: str, email_addr: str, return_date: str, snippet: str) -> Dict[str, Any]:
    """Dispatches a yellow notification card when Out-of-Office is detected with return date."""
    title = f"🟡 OUT-OF-OFFICE SCHEDULED: {professor_name}"
    description = f"**{professor_name}** ({institution}) is currently on leave and will return on **{return_date}**."
    
    fields = [
        {"name": "🏛️ Institution", "value": institution, "inline": True},
        {"name": "📅 Return Date", "value": f"**{return_date}**", "inline": True},
        {"name": "⏰ Scheduled Action", "value": f"Follow-up automatically paused until **{return_date}**.", "inline": False},
        {"name": "💬 OOO Auto-Reply Text", "value": f"```{snippet[:250]}```", "inline": False}
    ]
    return send_discord_embed(title=title, description=description, color=0xca8a04, fields=fields)

def notify_followup_dispatched(professor_name: str, institution: str, email_addr: str, days_elapsed: int, is_ooo_return: bool = False) -> Dict[str, Any]:
    """Dispatches an orange notification card when a 10-day follow-up email is sent."""
    title = f"⏰ FOLLOW-UP SENT: {professor_name}"
    reason = "Returned from travel" if is_ooo_return else f"10 days elapsed since initial email ({days_elapsed} days)"
    description = f"Polite academic follow-up (`Re: Application...`) sent to **{professor_name}** ({institution})."
    
    fields = [
        {"name": "🏛️ Institution", "value": institution, "inline": True},
        {"name": "📧 Email", "value": f"`{email_addr}`", "inline": True},
        {"name": "⏳ Trigger Reason", "value": reason, "inline": False}
    ]
    return send_discord_embed(title=title, description=description, color=0xd97706, fields=fields)

def notify_bounce_quarantined(email_addr: str, reason: str = "Invalid Domain / Mailbox Not Found") -> Dict[str, Any]:
    """Dispatches a red notification card when a delivery failure occurs and address is quarantined."""
    title = f"🔴 EMAIL QUARANTINED: {email_addr}"
    description = f"Delivery to `{email_addr}` failed and has been permanently quarantined to avoid wasted retries."
    
    fields = [
        {"name": "📧 Failed Address", "value": f"`{email_addr}`", "inline": True},
        {"name": "⚠️ Reason", "value": reason, "inline": True}
    ]
    return send_discord_embed(title=title, description=description, color=0xdc2626, fields=fields)
