import os
import imaplib
import email
from email.header import decode_header
from datetime import datetime
from typing import Dict, Any, List, Optional

from src.database import get_connection, insert_or_update_professor
from src.gmail_sender import load_env_file

def decode_header_str(raw: Optional[str]) -> str:
    if not raw:
        return ""
    parts = decode_header(raw)
    res = []
    for part, enc in parts:
        if isinstance(part, bytes):
            res.append(part.decode(enc or "utf-8", errors="ignore"))
        else:
            res.append(str(part))
    return " ".join(res)

def extract_email_address(raw_addr: str) -> str:
    if "<" in raw_addr and ">" in raw_addr:
        return raw_addr.split("<")[-1].split(">")[0].strip().lower()
    return raw_addr.strip().lower()

def is_valid_academic_research_email(subject: str, recipient: str) -> bool:
    """
    STRICT FILTER: Only syncs emails that are SPECIFICALLY research internship applications
    for this project sent to academic/research institutions.
    """
    subj_clean = subject.strip().lower()
    recip_clean = recipient.strip().lower()
    
    # 1. Subject MUST be a research application for this project
    valid_subject_keywords = [
        "application for research internship",
        "research internship opportunity",
        "expression of interest for research",
        "research trainee"
    ]
    if not any(kw in subj_clean for kw in valid_subject_keywords):
        return False
        
    # 2. Recipient MUST be an academic / research institution domain (or recognized institute)
    academic_domains = [
        ".ac.in", ".edu", ".ernet.in", ".res.in", ".org.in",
        "iisc.ac.in", "iiit.ac.in", "iitb.ac.in", "iitd.ac.in",
        "iitm.ac.in", "iitk.ac.in", "iitkgp.ac.in", "iitr.ac.in",
        "iitg.ac.in", "iith.ac.in", "isb.edu", "iimb.ac.in"
    ]
    if not any(recip_clean.endswith(dom) or dom in recip_clean for dom in academic_domains):
        return False
        
    # 3. Explicit blacklist for non-professors / services
    blacklist = ["zepto.com", "techmahindra.com", "visyscloudtech.com", "zorvyn.org", "gmail.com", "yahoo.com", "outlook.com", "support", "no-reply", "noreply", "careers"]
    if any(bl in recip_clean for bl in blacklist):
        return False
        
    return True

def sync_sent_history_from_gmail() -> Dict[str, Any]:
    """
    Connects to Gmail IMAP to inspect sent emails.
    STRICTLY syncs ONLY research internship application emails for this project.
    """
    load_env_file()
    user_email = os.getenv("GMAIL_USER", "adepunikhil79@gmail.com")
    raw_pass = os.getenv("GMAIL_APP_PASSWORD", "")
    secret_pass = raw_pass.replace(" ", "").strip()
    
    if not secret_pass:
        return {
            "status": "skipped",
            "message": "GMAIL_APP_PASSWORD not set. Cannot sync live Gmail history.",
            "synced_count": 0
        }
        
    conn = get_connection()
    cursor = conn.cursor()
    synced_records = []
    
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(user_email, secret_pass)
        
        sent_folder = '[Gmail]/Sent Mail'
        status, folders = mail.list()
        if status == 'OK':
            for f in folders:
                folder_str = f.decode('utf-8', errors='ignore')
                if '\\Sent' in folder_str or 'Sent Mail' in folder_str:
                    parts = folder_str.split(' "/" ')
                    if len(parts) > 1:
                        sent_folder = parts[-1].strip('"')
                        break
                        
        mail.select(f'"{sent_folder}"' if ' ' in sent_folder else sent_folder)
        
        status, search_data = mail.search(None, "ALL")
        if status == 'OK' and search_data[0]:
            msg_ids = search_data[0].split()
            for msg_id in msg_ids[-100:]:
                res, data = mail.fetch(msg_id, "(BODY.PEEK[HEADER.FIELDS (TO SUBJECT DATE)])")
                if res != 'OK' or not data or not data[0]:
                    continue
                    
                raw_header = data[0][1]
                msg = email.message_from_bytes(raw_header)
                
                to_hdr = decode_header_str(msg.get("To"))
                subject_hdr = decode_header_str(msg.get("Subject"))
                date_hdr = msg.get("Date")
                
                recipient = extract_email_address(to_hdr)
                if not recipient or recipient == user_email.lower():
                    continue
                    
                # STRICT VALIDATION: Ignore non-research, non-academic emails
                if not is_valid_academic_research_email(subject_hdr, recipient):
                    continue
                    
                sent_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if date_hdr:
                    try:
                        sent_dt = email.utils.parsedate_to_datetime(date_hdr)
                        sent_time_str = sent_dt.strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        pass
                        
                cursor.execute("SELECT id FROM professors WHERE email = ?", (recipient,))
                prof_row = cursor.fetchone()
                if prof_row:
                    prof_id = prof_row["id"]
                else:
                    prof_id = insert_or_update_professor({
                        "name": to_hdr.split("<")[0].strip() or recipient.split("@")[0].title(),
                        "institution": "Academic Institute",
                        "department": "Department",
                        "designation": "Professor",
                        "email": recipient,
                        "research_areas": ["Artificial Intelligence", "Machine Learning"],
                        "research_summary": "Academic researcher in national directory."
                    }, conn=conn)
                    
                cursor.execute("SELECT id, status FROM applications WHERE professor_id = ?", (prof_id,))
                app_row = cursor.fetchone()
                
                if app_row:
                    if app_row["status"] not in ["Replied", "Interested", "Followed Up"]:
                        cursor.execute("""
                        UPDATE applications
                        SET status = 'Sent', sent_at = COALESCE(sent_at, ?), subject = COALESCE(subject, ?)
                        WHERE id = ?
                        """, (sent_time_str, subject_hdr, app_row["id"]))
                else:
                    cursor.execute("""
                    INSERT INTO applications (professor_id, subject, status, drafted_at, approved_at, sent_at)
                    VALUES (?, ?, 'Sent', ?, ?, ?)
                    """, (prof_id, subject_hdr, sent_time_str, sent_time_str, sent_time_str))
                    
                synced_records.append({
                    "recipient": recipient,
                    "subject": subject_hdr,
                    "sent_at": sent_time_str
                })
                
        mail.close()
        mail.logout()
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "message": f"Successfully synchronized {len(synced_records)} verified research application emails.",
            "synced_count": len(synced_records),
            "records": synced_records
        }
    except Exception as e:
        conn.close()
        return {
            "status": "error",
            "message": f"Gmail sent history sync failed: {str(e)}",
            "synced_count": 0
        }
