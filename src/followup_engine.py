from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from src.database import get_connection
from src.email_generator import get_salutation_name
from src.gmail_sender import send_application_email
from src.notifier import notify_followup_dispatched

def is_academic_research_target(email_addr: str, subject: str) -> bool:
    """Strict verification: Only allows follow-ups for verified research applications to academic institutes."""
    e = email_addr.lower().strip()
    s = subject.lower().strip()
    
    # Must be an academic or research domain
    academic_endings = [".ac.in", ".edu", ".ernet.in", ".res.in", ".org.in", "iisc.ac.in", "iiit.ac.in", "isb.edu", "iim"]
    if not any(dom in e for dom in academic_endings):
        return False
        
    # Block list for non-academic/personal
    blocked = ["zepto", "techmahindra", "visys", "zorvyn", "gmail.com", "yahoo", "support", "no-reply", "careers"]
    if any(b in e for b in blocked):
        return False
        
    # Subject must be research internship application
    if "research internship" not in s and "application for research" not in s:
        return False
        
    return True

def check_pending_followups(days_threshold: int = 10, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Identifies applications eligible for follow-up:
    1. Sent >= days_threshold days ago with status 'Sent' or 'Waiting'.
    2. OOO faculty whose return date (available_after) has arrived.
    STRICTLY filters only academic research applications for this project.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT a.id as app_id, a.subject, a.sent_at, a.status, a.available_after,
           p.id as prof_id, p.name as prof_name, p.iit as institution, p.department, p.email as prof_email
    FROM applications a
    JOIN professors p ON a.professor_id = p.id
    WHERE a.status IN ('Sent', 'Waiting', 'Follow-up Required') OR a.status LIKE 'OOO%'
    """)
    rows = cursor.fetchall()
    
    now = datetime.now()
    eligible_followups = []
    
    for r in rows:
        prof_email = r["prof_email"] or ""
        subj = r["subject"] or ""
        
        # Strict validation: Ignore non-research emails
        if not is_academic_research_target(prof_email, subj):
            continue
            
        avail_str = r["available_after"]
        is_ooo_return_due = False
        if avail_str:
            try:
                avail_dt = datetime.strptime(avail_str.split(" ")[0], "%Y-%m-%d")
                if now.date() >= avail_dt.date():
                    is_ooo_return_due = True
                else:
                    continue
            except Exception:
                pass
                
        sent_at_str = r["sent_at"]
        if not sent_at_str:
            continue
            
        try:
            sent_time = datetime.fromisoformat(sent_at_str.replace(" ", "T"))
        except Exception:
            try:
                sent_time = datetime.strptime(sent_at_str, "%Y-%m-%d %H:%M:%S")
            except Exception:
                continue
                
        elapsed_days = (now - sent_time).days
        if elapsed_days >= days_threshold or is_ooo_return_due:
            cursor.execute("UPDATE applications SET status = 'Follow-up Required' WHERE id = ?", (r["app_id"],))
            eligible_followups.append({
                "application_id": r["app_id"],
                "professor_name": r["prof_name"],
                "institution": r["institution"],
                "email": r["prof_email"],
                "subject": r["subject"],
                "sent_at": sent_at_str,
                "days_elapsed": elapsed_days,
                "is_ooo_return": is_ooo_return_due
            })
            
    conn.commit()
    conn.close()
    return eligible_followups

def generate_followup_email(
    candidate_name: str,
    prof_name: str,
    original_subject: str,
    sent_date_str: str,
    is_ooo_return: bool = False
) -> Dict[str, str]:
    """
    Generates a polite, respectful, and concise academic follow-up email.
    """
    salutation = get_salutation_name(prof_name)
    followup_subject = f"Re: {original_subject}" if not original_subject.startswith("Re:") else original_subject
    
    if is_ooo_return:
        opening = "I hope you had a restful trip and are having a productive week."
    else:
        opening = "I hope you are having a productive week."
        
    body = f"""Dear {salutation},

{opening}

I am writing to respectfully follow up on my previous email regarding my interest in research internship opportunities under your guidance. I understand that you have a demanding schedule, and I wanted to gently reiterate my enthusiasm for contributing to your research group.

My academic resume and personalized cover letter remain available for your review, and I would be very glad to discuss how my background in machine learning and computer vision could support your ongoing projects whenever convenient.

Thank you once again for your time and consideration.

Sincerely,

{candidate_name}"""

    return {
        "subject": followup_subject,
        "email_body": body
    }

def execute_due_followups(candidate_name: str = "Adepu Nikhil", days_threshold: int = 10) -> Dict[str, Any]:
    """
    Automatically sends polite academic follow-ups ONLY for verified research applications sent >= days_threshold days ago.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT a.*, p.name as prof_name, p.email as prof_email, p.iit as institution
    FROM applications a
    JOIN professors p ON a.professor_id = p.id
    WHERE a.status IN ('Sent', 'Waiting', 'Follow-up Required') OR a.status LIKE 'OOO%'
    """)
    rows = cursor.fetchall()
    
    now = datetime.now()
    sent_followups = []
    
    for r in rows:
        prof_email = r["prof_email"] or ""
        subj = r["subject"] or ""
        
        # STRICT FILTER: Never touch personal or non-research emails
        if not is_academic_research_target(prof_email, subj):
            continue
            
        avail_str = r["available_after"]
        is_ooo_return = False
        if avail_str:
            try:
                avail_dt = datetime.strptime(avail_str.split(" ")[0], "%Y-%m-%d")
                if now.date() >= avail_dt.date():
                    is_ooo_return = True
                else:
                    continue
            except Exception:
                pass
                
        sent_at_str = r["sent_at"]
        if not sent_at_str:
            continue
        try:
            sent_time = datetime.fromisoformat(sent_at_str.replace(" ", "T"))
        except Exception:
            try:
                sent_time = datetime.strptime(sent_at_str, "%Y-%m-%d %H:%M:%S")
            except Exception:
                continue
                
        elapsed_days = (now - sent_time).days
        if elapsed_days >= days_threshold or is_ooo_return:
            followup_content = generate_followup_email(
                candidate_name=candidate_name,
                prof_name=r["prof_name"],
                original_subject=r["subject"],
                sent_date_str=sent_at_str,
                is_ooo_return=is_ooo_return
            )
            
            cover_path = r["cover_letter_path"]
            resume_path = r["resume_path"]
            attachments = [p for p in [cover_path, resume_path] if p]
            
            dispatch = send_application_email(
                to_email=r["prof_email"],
                subject=followup_content["subject"],
                body=followup_content["email_body"],
                attachment_paths=attachments
            )
            
            if dispatch.get("status") in ["sent", "dry_run_success"]:
                cursor.execute("""
                UPDATE applications
                SET status = 'Followed Up', followup_date = CURRENT_TIMESTAMP
                WHERE id = ?
                """, (r["id"],))
                
                notify_followup_dispatched(
                    professor_name=r["prof_name"],
                    institution=r["institution"],
                    email_addr=r["prof_email"],
                    days_elapsed=elapsed_days,
                    is_ooo_return=is_ooo_return
                )
                
                sent_followups.append({
                    "application_id": r["id"],
                    "professor_name": r["prof_name"],
                    "institution": r["institution"],
                    "email": r["prof_email"],
                    "status": "Followed Up",
                    "days_elapsed": elapsed_days,
                    "is_ooo_return": is_ooo_return
                })
            
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "total_followups_sent": len(sent_followups),
        "followups": sent_followups,
        "message": f"Processed {len(sent_followups)} verified academic research follow-ups."
    }
