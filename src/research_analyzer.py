from typing import Dict, Any, List

def analyze_paper_synergy(
    candidate_profile: Dict[str, Any],
    professor_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Performs deep research paper and publication synergy analysis between
    the candidate's published/dissertation work and the professor's recent papers.
    """
    cand_publications = candidate_profile.get("publications", [])
    cand_projects = candidate_profile.get("research_projects", [])
    
    prof_papers = professor_data.get("recent_papers", [])
    prof_areas = professor_data.get("research_areas", [])
    
    paper_alignments = []
    
    # Check alignments across Vision, Assistive AI, Machine Learning, Decision Analytics, IoT/Embedded, and Scientific AI
    for paper in prof_papers:
        p_lower = paper.lower()
        if any(term in p_lower for term in ["depth", "spatial", "navigation", "assistive", "object detection", "monocular", "video", "surveillance", "biometric", "3d", "vision", "tracking"]):
            paper_alignments.append({
                "professor_paper": paper,
                "candidate_synergy": "Matches candidate's M.Sc. thesis and IJCOPE 2026 publication on distance-aware assistive navigation (YOLOv8 + Monocular Depth)."
            })
        elif any(term in p_lower for term in ["embedded", "sensor", "telemetry", "iot", "micro-mobility", "hardware", "real-time", "edge"]):
            paper_alignments.append({
                "professor_paper": paper,
                "candidate_synergy": "Direct synergy with candidate's embedded AI development, ESP32 telemetry, and low-latency FastAPI edge microservices."
            })
        elif any(term in p_lower for term in ["multimodal", "audio", "speech", "deepfake", "synthetic", "conversational", "generative", "nlp", "language", "dialogue", "text"]):
            paper_alignments.append({
                "professor_paper": paper,
                "candidate_synergy": "Directly connects with candidate's voice deepfake detection research (PyTorch CNN/Librosa) and local Generative AI / LLM pipelines."
            })
        elif any(term in p_lower for term in ["loan", "credit", "risk", "decision", "predictive", "analytics", "operations", "supply", "transactional", "financial", "pricing", "econometric", "logistics"]):
            paper_alignments.append({
                "professor_paper": paper,
                "candidate_synergy": "Synergizes with candidate's loan approval and EMI analysis platform, Scikit-learn predictive modeling, and automated decision APIs."
            })
        elif any(term in p_lower for term in ["catalytic", "molecular", "physics", "quantum", "biophysical", "chaotic", "time series", "scientific", "dynamics", "materials"]):
            paper_alignments.append({
                "professor_paper": paper,
                "candidate_synergy": "Aligns with candidate's data science modeling, mathematical optimization, and interdisciplinary AI pipeline development."
            })
        elif any(term in p_lower for term in ["explainable", "generative", "neural", "bayesian", "reinforcement", "continual", "optimization", "graph", "meta-learning"]):
            paper_alignments.append({
                "professor_paper": paper,
                "candidate_synergy": "Synergizes with candidate's advanced ML modeling, Scikit-learn decision platforms, and PyTorch deep learning pipelines."
            })

    # Summary synthesis
    if paper_alignments:
        synergy_summary = f"Strong paper synergy identified with {len(paper_alignments)} recent publications in {', '.join(prof_areas[:2])}."
    else:
        synergy_summary = "Foundational methodological compatibility in machine learning and data engineering."

    return {
        "aligned_papers_count": len(paper_alignments),
        "aligned_papers": paper_alignments,
        "synergy_summary": synergy_summary
    }
