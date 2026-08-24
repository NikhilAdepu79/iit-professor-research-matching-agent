from typing import Dict, Any, Optional
from datetime import datetime
from src.ollama_client import generate_personalized_alignment

def get_salutation_name(full_name: str) -> str:
    name_clean = full_name.replace("Prof.", "").replace("Dr.", "").strip()
    parts = name_clean.split()
    return f"Prof. {parts[-1]}" if len(parts) > 1 else f"Prof. {name_clean}"

def clean_lab_name(lab_name: Optional[str], salutation_name: str) -> str:
    if not lab_name or lab_name.startswith("http") or "www." in lab_name:
        return f"{salutation_name} Research Group"
    return lab_name.strip()

def generate_application_package_content(candidate_profile: Dict[str, Any], professor_data: Dict[str, Any]) -> Dict[str, Any]:
    candidate_name = candidate_profile.get("name", "Adepu Nikhil")
    candidate_email = candidate_profile.get("email", "adepunikhil79@gmail.com")
    candidate_phone = candidate_profile.get("phone", "+91 7981340358")
    candidate_location = candidate_profile.get("location", "Hyderabad, Telangana, India")

    prof_name = professor_data.get("name", "Professor")
    salutation_name = get_salutation_name(prof_name)
    institution = professor_data.get("institution", professor_data.get("iit", "Institute"))
    full_institution_name = professor_data.get("full_institution_name", institution)
    department = professor_data.get("department", "Department of Computer Science & Engineering")
    location = professor_data.get("location", "India")
    
    raw_lab_name = professor_data.get("lab_name")
    lab_name = clean_lab_name(raw_lab_name, salutation_name)
    
    prof_areas = professor_data.get("research_areas", [])
    primary_area = prof_areas[0] if isinstance(prof_areas, list) and prof_areas else "Machine Learning & AI"
    areas_str = ", ".join(prof_areas[:3]) if isinstance(prof_areas, list) else str(prof_areas)

    # 1. Plain Text Email Subject & Body (for Gmail)
    subject = f"Application for Research Internship – {primary_area} – {candidate_name}"

    email_body = f"""Dear {salutation_name},

I hope you are doing well.

My name is {candidate_name}, and I have completed my M.Sc. in Artificial Intelligence and Data Science from the Central University of Andhra Pradesh. I am writing to express my interest in the research activities of the {lab_name}, {institution}, and to inquire whether there may be an opportunity to work as a research intern or research trainee under your guidance.

My academic and project work has focused on machine learning, deep learning, computer vision, and AI-based intelligent systems. For my master's dissertation, I developed a Distance-Aware Real-Time Assistive Navigation System using YOLOv8 and Monocular Depth Estimation, involving real-time object detection, spatial reasoning, FastAPI deployment, and multilingual feedback systems. I also have hands-on experience with Python, Scikit-learn, OpenCV, YOLOv8, FastAPI, and Generative AI tools, and I have co-authored a peer-reviewed publication in the area of computer vision and intelligent navigation.

I am particularly interested in applying machine learning techniques to {areas_str}, and I would be grateful for an opportunity to contribute to the ongoing work in your lab. I have attached my personalized cover letter and resume for your kind consideration.

If there are any current or upcoming opportunities, I would be happy to provide further information or discuss how my background may align with your research group.

Thank you very much for your time and consideration. I look forward to hearing from you.

Sincerely,

{candidate_name}
{candidate_location}
{candidate_phone}
{candidate_email}"""

    # 2. Personalized Cover Letter Payload (with Bold highlights matching template)
    alignment_para = generate_personalized_alignment(candidate_profile, professor_data)
    current_date = datetime.now().strftime("%d %B %Y")

    para1 = (
        f"I am writing to express my sincere interest in the research activities of the {lab_name}, "
        f"{institution} and to seek an opportunity to contribute as a Research Intern / Research "
        f"Trainee under your guidance."
    )

    para2 = (
        "I have recently completed my <b>Master of Science in Artificial Intelligence and Data Science</b> from the "
        "<b>Central University of Andhra Pradesh</b>. My academic background and research interests are "
        "<b>centered on machine learning, deep learning, computer vision, generative AI, and intelligent real-time "
        "systems</b>. During my master’s dissertation, I developed a <b>Distance-Aware Real-Time Assistive "
        "Navigation System using YOLOv8 and Monocular Depth Estimation</b>, where I worked on real-time "
        "object detection, spatial reasoning, FastAPI-based deployment, and multilingual feedback "
        "mechanisms."
    )

    para3 = (
        "I have also gained practical experience through internships in AI and data science, involving the "
        "development of machine learning models, computer vision pipelines, and AI-enabled applications "
        "using <b>Python, Scikit-learn, OpenCV, YOLOv8, FastAPI, and Generative AI tools</b>. In addition, I have "
        "contributed to a peer-reviewed publication related to computer vision and intelligent navigation "
        "systems, which strengthened my interest in research methodology, experimentation, and scientific "
        "problem solving."
    )

    para4 = alignment_para

    para5 = (
        "I have attached my resume for your kind consideration. I would be grateful if my profile could be "
        "considered for any current or upcoming research opportunities in your laboratory."
    )

    cover_letter_data = {
        "candidate_name": candidate_name,
        "candidate_location": candidate_location,
        "candidate_phone": candidate_phone,
        "candidate_email": candidate_email,
        "date": current_date,
        "professor_name": prof_name,
        "salutation_name": salutation_name,
        "lab_name": lab_name,
        "department": department,
        "iit_name": full_institution_name,
        "institute_location": location,
        "subject": "Subject: Expression of Interest for Research Internship / Research Trainee Opportunity",
        "paragraphs": [para1, para2, para3, para4, para5],
        "closing_note": "Thank you very much for your time and consideration. I look forward to the possibility of working with your research group."
    }

    return {
        "subject": subject,
        "email_body": email_body,
        "cover_letter_data": cover_letter_data
    }
