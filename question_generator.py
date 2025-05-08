from model import infer_with_retry

def extract_resume_topics(resume_text):
    """Extract key topics, skills, and projects from resume"""
    system_prompt = """
    You are an expert resume analyzer. Extract key topics from this resume including:
    1. Technical skills
    2. Projects
    3. Work experiences
    4. Soft skills
    5. Achievements
    
    Format: Return a JSON-like string with categories and items
    """
    
    user_prompt = f"""
    Analyze this resume and extract key topics:
    {resume_text}
    """
    
    try:
        response = infer_with_retry([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        # Use basic parsing since we can't import json
        topics = eval(response) if response else {}
        return topics
    except Exception as e:
        print(f"Error extracting topics: {e}")
        return {}

def generate_initial_questions(resume_text):
    """Generate initial questions covering different aspects of the resume"""
    resume_topics = extract_resume_topics(resume_text)
    
    system_prompt = """
    You are an expert AI interviewer. Generate three diverse initial questions covering different aspects 
    of the candidate's background. Questions should cover different areas like technical skills, 
    projects, and work experience.
    """
    
    user_prompt = f"""
    Based on this resume analysis:
    {resume_topics}
    
    Generate 3 different questions that:
    - Cover different aspects (e.g., one technical, one project-based, one behavioral)
    - Help understand the candidate's background comprehensively
    - Serve as good conversation starters
    
    Format: Return three questions, each starting with Q:
    """
    
    try:
        response = infer_with_retry([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        questions = [q.strip() for q in response.split("\n") if q.strip().startswith("Q:")]
        return questions[:3] if questions else generate_fallback_initial_questions()
    except Exception as e:
        print(f"Error generating initial questions: {e}")
        return generate_fallback_initial_questions()

def generate_adaptive_questions(previous_answer, resume_text, interview_context):
    """Generate follow-up questions based on previous answers and unexplored topics"""
    total_questions = len(interview_context.get('questions', []))
    if total_questions >= 10:
        return []
    
    questions_remaining = 10 - total_questions
    num_to_generate = min(2, questions_remaining)
    
    # Track discussed topics
    discussed_topics = analyze_discussed_topics(interview_context)
    resume_topics = extract_resume_topics(resume_text)
    
    system_prompt = f"""
    You are an expert AI interviewer conducting a comprehensive interview.
    Topics already discussed: {discussed_topics}
    
    Available topics from resume: {resume_topics}
    
    Generate questions that:
    1. Follow up on relevant points from the last answer
    2. Explore unexplored topics from their resume
    3. Connect different aspects of their experience
    """
    
    previous_qa = "\n".join([
        f"Q: {q}\nA: {a}" for q, a in 
        zip(interview_context.get('questions', []), 
            interview_context.get('answers', []))
    ])
    
    user_prompt = f"""
    Resume Context:
    {resume_text[:500]}...

    Interview History:
    {previous_qa}

    Most Recent Answer:
    {previous_answer}

    Generate {num_to_generate} questions that:
    - Follow up on specific points from their last answer
    - Explore unexplored skills or projects from their resume
    - Connect their previous answers to other relevant experience
    - Ensure comprehensive coverage of their background

    Format: Return exactly {num_to_generate} questions, one per line, starting with 'Q: '
    """
    
    try:
        response = infer_with_retry([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        questions = [q.strip() for q in response.split('\n') if q.strip().startswith('Q:')]
        return questions[:num_to_generate] if questions else generate_fallback_questions(previous_answer, discussed_topics)[:num_to_generate]
    except Exception as e:
        print(f"Error generating adaptive questions: {e}")
        return generate_fallback_questions(previous_answer, discussed_topics)[:num_to_generate]

def analyze_discussed_topics(interview_context):
    """Analyze which topics have been discussed in the interview so far"""
    system_prompt = """
    Analyze these interview questions and answers to identify discussed topics.
    Return a list of key topics, skills, and themes that have been covered.
    """
    
    qa_history = "\n".join([
        f"Q: {q}\nA: {a}" for q, a in 
        zip(interview_context.get('questions', []), 
            interview_context.get('answers', []))
    ])
    
    try:
        response = infer_with_retry([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": qa_history}
        ])
        return response.split('\n') if response else []
    except Exception as e:
        print(f"Error analyzing discussed topics: {e}")
        return []

def generate_fallback_initial_questions():
    """Generate default initial questions covering different aspects"""
    return [
        "Q: Could you walk me through your most significant technical project?",
        "Q: What are your core technical skills and how have you applied them?",
        "Q: Tell me about a challenging situation in your work and how you handled it."
    ]

def generate_fallback_questions(answer, discussed_topics=[]):
    """Generate fallback questions considering discussed topics"""
    key_topic = extract_key_topic(answer)
    unused_topics = set(get_common_topics()) - set(discussed_topics)
    
    fallback_questions = [
        f"Q: Could you provide a specific example of how you used {key_topic} in your work?",
        f"Q: What technical challenges did you face while working with {key_topic}?",
        f"Q: How does your experience with {key_topic} relate to your other technical skills?",
        "Q: Could you elaborate on the technical decision-making process?",
        "Q: What were the technical outcomes and metrics of this work?"
    ]
    
    if unused_topics:
        new_topic = unused_topics.pop()
        fallback_questions.append(f"Q: How have you worked with {new_topic} in your projects?")
    
    return fallback_questions

def get_common_topics():
    """Get list of common technical topics for fallback questions"""
    return [
        'python', 'java', 'javascript', 'react', 'node', 'database', 
        'api', 'cloud', 'aws', 'azure', 'docker', 'kubernetes',
        'machine learning', 'ai', 'testing', 'agile', 'project management',
        'leadership', 'development', 'architecture', 'design', 'implementation'
    ]

def extract_key_topic(text):
    """Extract main topic from the answer"""
    text_lower = text.lower()
    for topic in get_common_topics():
        if topic in text_lower:
            return topic
    return "this technical approach"