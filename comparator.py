import cohere
import re
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
co = cohere.Client(api_key)

def compare_resume_with_jd(resume_text, jd_text):
    try:
        response = co.embed(texts=[resume_text[:1000], jd_text[:1000]], model='embed-english-light-v2.0')
        embeddings = np.array(response.embeddings)
        similarity = np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))
        match_score = similarity * 100
        
        skills_pattern = r'\b(?:python|java|javascript|js|react|node|sql|mysql|postgresql|mongodb|aws|azure|gcp|docker|kubernetes|git|html|css|angular|vue|django|flask|spring|tensorflow|pytorch|pandas|numpy|scikit-learn|tableau|powerbi|jenkins|ci/cd|agile|scrum|jira|confluence|restapi|api|json|xml|linux|windows|mac|photoshop|illustrator|figma|sketch|unity|c\+\+|c#|php|ruby|go|rust|swift|kotlin|scala|r|matlab|excel|powerpoint|word|outlook|salesforce|hubspot|google analytics|seo|sem|ppc|social media|marketing|project management|leadership|communication|teamwork|problem solving|analytical|creative|detail oriented|time management|multitasking|adaptable|self motivated|customer service|sales|negotiation|presentation|training|mentoring|coaching|budgeting|forecasting|data analysis|machine learning|artificial intelligence|deep learning|nlp|computer vision|blockchain|cybersecurity|devops|microservices|serverless|cloud computing|big data|data science|business intelligence|etl|data warehouse|nosql|graphql|containerization|orchestration|monitoring|logging|testing|automation|performance optimization|scalability|security|compliance|gdpr|hipaa|sox|pci|iso|itil|six sigma|lean|kanban|waterfall|prince2|pmp|csm|aws certified|azure certified|google cloud certified|oracle certified|microsoft certified|cisco certified|comptia|cissp|ceh|cisa|cism|crisc|cgeit|cobit|togaf|zachman|sabsa|nist|iso 27001|iso 20000|iso 9001)\b'
        
        resume_skills = set(re.findall(skills_pattern, resume_text.lower(), re.IGNORECASE))
        jd_skills = set(re.findall(skills_pattern, jd_text.lower(), re.IGNORECASE))
        
        try:
            resume_ai_response = co.generate(model='command-light', prompt=f"List only technical skills, tools, and technologies mentioned in this text. Format as comma-separated values: {resume_text[:400]}", max_tokens=30)
            ai_resume_skills = [s.strip().lower() for s in resume_ai_response.generations[0].text.replace('\n', ',').split(',') if s.strip()]
            resume_skills.update(ai_resume_skills)
            
            jd_ai_response = co.generate(model='command-light', prompt=f"List only technical skills, tools, and technologies mentioned in this job description. Format as comma-separated values: {jd_text[:400]}", max_tokens=30)
            ai_jd_skills = [s.strip().lower() for s in jd_ai_response.generations[0].text.replace('\n', ',').split(',') if s.strip()]
            jd_skills.update(ai_jd_skills)
        except:
            pass
        
        resume_skills = {skill for skill in resume_skills if len(skill) > 1 and skill not in ['and', 'or', 'the', 'with', 'for', 'in', 'on', 'at', 'to', 'of', 'a', 'an']}
        jd_skills = {skill for skill in jd_skills if len(skill) > 1 and skill not in ['and', 'or', 'the', 'with', 'for', 'in', 'on', 'at', 'to', 'of', 'a', 'an']}
        
        matched_skills = list(resume_skills & jd_skills)
        missing_skills = list(jd_skills - resume_skills)
        skill_match_percentage = (len(matched_skills) / len(jd_skills)) * 100 if jd_skills else 0
        
        summary_response = co.generate(model='command-light', prompt=f"Summarize this job description. Extract key requirements and responsibilities: {jd_text[:800]}", max_tokens=100)
        
        return {
            "match_score": round(match_score, 2),
            "skill_match_percentage": round(skill_match_percentage, 2),
            "matched_skills": matched_skills[:10],
            "missing_skills": missing_skills[:10],
            "total_jd_skills": len(jd_skills),
            "jd_summary": {"requirements": [summary_response.generations[0].text], "responsibilities": []},
            "suggestions": [
                f"Focus on these missing skills: {', '.join(missing_skills[:3])}" if missing_skills else "Good skill match!",
                "Tailor your resume keywords to match the job description better" if match_score < 70 else "Strong resume match!"
            ]
        }
    except Exception as e:
        return fallback_analysis(resume_text, jd_text)

def fallback_analysis(resume_text, jd_text):
    skills_pattern = r'\b(?:python|java|javascript|react|node|sql|aws|docker|git|html|css|angular|vue|django|flask|mongodb|kubernetes|jenkins|agile|scrum|tableau|powerbi|azure|gcp)\b'
    resume_skills = set(re.findall(skills_pattern, resume_text.lower()))
    jd_skills = set(re.findall(skills_pattern, jd_text.lower()))
    matched = list(resume_skills & jd_skills)
    missing = list(jd_skills - resume_skills)
    
    return {
        "match_score": len(matched) / max(len(jd_skills), 1) * 100,
        "matched_skills": matched,
        "missing_skills": missing,
        "jd_summary": {"requirements": [], "responsibilities": []},
        "suggestions": ["API unavailable - using basic comparison"]
    }