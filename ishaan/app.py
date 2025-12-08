from typing import List
import numpy as np
import faiss
from transformers import pipeline
from sentence_transformers import SentenceTransformer

# -------------------------
# NLP MODELS
# -------------------------
skill_model = pipeline("text2text-generation", model="google/flan-t5-base", device=-1)
embed_model = SentenceTransformer("BAAI/bge-m3", device="cpu")

# -------------------------
# FAISS INDEX FOR SKILL EMBEDDINGS (optional)
# -------------------------
EMBED_DIM = 1024
skill_index = faiss.IndexFlatL2(EMBED_DIM)
skill_data = []

# -------------------------
# TECHNICAL SKILLS
# -------------------------
TECHNICAL_KEYWORDS = {
    'python', 'java', 'c++', 'javascript', 'aws', 'azure', 'docker', 'kubernetes', 
    'lambda', 'tensorflow', 'sagemaker', 'sql', 'git', 'hadoop', 'spark', 
    'google cloud', 'react', 'node.js', 'scala', 'devops', 'jenkins', 
    'terraform', 'cicd', 'microservices', 'spring boot', 'golang'
}

# -------------------------
# HELPER FUNCTIONS
# -------------------------
def extract_skills(job_description: str, top_k: int = 10, use_faiss: bool = False) -> List[str]:
    """
    Extract ONLY technical skills from a job description.
    - Returns unique, comma-separated technical skills.
    - Multi-line safe.
    - Optionally embed and store skills in FAISS for semantic search.
    """
    prompt = (
        f"Extract the top {top_k} unique technical skills and programming languages "
        f"from the following job description. Return only comma-separated skill names.\n\n"
        f"{job_description}\n\nSkills:"
    )

    out = skill_model(prompt, max_length=128, num_return_sequences=1)
    skills_text = out[0]["generated_text"].split("Skills:")[-1].replace("\n", ",")
    
    skills_list = [s.strip().lower() for s in skills_text.split(",") if s.strip()]
    filtered_skills = [s for s in skills_list if s in TECHNICAL_KEYWORDS]
    
    if not filtered_skills:
        filtered_skills = ["python"]  # fallback default

    # Optional: Embed and add to FAISS
    if use_faiss:
        for skill in filtered_skills:
            vec = np.array(embed_model.encode(skill, normalize_embeddings=True), dtype="float32")
            skill_index.add(vec.reshape(1, -1))
            skill_data.append(skill)

    return list(dict.fromkeys(filtered_skills))

def search_skills(query_skills: List[str], top_k: int = 5) -> List[str]:
    """Search top-K most similar skills in FAISS index"""
    if not skill_data or skill_index.ntotal == 0:
        raise ValueError("FAISS index is empty. Run extract_skills with use_faiss=True first.")
    
    query_vecs = np.array([embed_model.encode(s, normalize_embeddings=True) for s in query_skills], dtype="float32")
    distances, indices = skill_index.search(query_vecs, top_k)
    results = []
    for idx_list in indices:
        results.extend([skill_data[i] for i in idx_list])
    return list(dict.fromkeys(results))