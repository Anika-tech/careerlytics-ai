LEARNING_TOPICS = {
    "python": ["Core syntax", "Object-oriented programming", "Pandas and NumPy"],
    "sql": ["Joins", "Subqueries", "Indexes", "Query optimization"],
    "machine learning": ["Supervised learning", "Model evaluation", "Feature engineering"],
    "deep learning": ["Neural networks", "CNNs", "RNNs", "PyTorch or TensorFlow"],
    "aws": ["Cloud foundations", "EC2", "S3", "IAM"],
    "docker": ["Containers", "Dockerfiles", "Images", "Docker Compose"],
    "kubernetes": ["Pods", "Deployments", "Services", "Cluster basics"],
    "react": ["Components", "Hooks", "State management", "Routing"],
    "git": ["Branching", "Pull requests", "Merge conflicts", "Rebasing"],
    "java": ["Collections", "Concurrency", "Spring", "JVM fundamentals"],
}


def calculate_skill_gap(candidate_skills, required_skills):
    candidate = {str(skill).lower() for skill in candidate_skills}
    required = {str(skill).lower() for skill in required_skills}
    matching = sorted(candidate & required)
    missing = sorted(required - candidate)
    return {
        "matching": matching,
        "missing": missing,
        "suggestions": [
            {"skill": skill, "topics": LEARNING_TOPICS.get(skill, [f"{skill.title()} fundamentals", "Practice projects", "Documentation"])}
            for skill in missing
        ],
    }
