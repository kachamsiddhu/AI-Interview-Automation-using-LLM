import streamlit as st
from resume_parser import extract_resume
from question_generator import generate_initial_questions, generate_adaptive_questions
from speech_handler import recognize_speech, speak_text
from answer_evaluator import calculate_relevance_score, evaluate_overall_interview
from datetime import datetime
import json
import os
from visualization import display_score_visualization


# Initialize session state
def initialize_session_state():
    if 'interview_state' not in st.session_state:
        st.session_state.interview_state = {
            'current_question': 0,
            'questions': [],
            'answers': [],
            'resume_text': None,
            'interview_complete': False,
            'feedback': {},
            'start_time': None,
            'question_spoken': False,
            'context': {},
            'scores': []  # Add scores list to track relevance scores
        }

# Save interview results
def save_interview_results():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {
        'timestamp': timestamp,
        'resume_text': st.session_state.interview_state['resume_text'],
        'questions': st.session_state.interview_state['questions'],
        'answers': st.session_state.interview_state['answers'],
        'feedback': st.session_state.interview_state['feedback'],
        'context': st.session_state.interview_state['context'],
        'scores': st.session_state.interview_state['scores']  # Include scores in saved results
    }

    os.makedirs('interview_results', exist_ok=True)
    filename = f'interview_results/interview_{timestamp}.json'
    with open(filename, 'w') as f:
        json.dump(results, f, indent=4)
    return filename

# Display interview progress
def display_interview_progress():
    total_questions = len(st.session_state.interview_state['questions'])
    current = st.session_state.interview_state['current_question']
    progress = min(1.0, (current + 1) / 10)
    st.progress(progress)
    st.caption(f"Question {current + 1} of {min(10, total_questions)} (Max: 10)")

# Handle answer submission
def handle_answer_submission():
    with st.spinner("Listening for your response..."):
        answer = recognize_speech()
        if answer:
            st.session_state.interview_state['answers'].append(answer)
            current_q_index = st.session_state.interview_state['current_question']
            current_q = st.session_state.interview_state['questions'][current_q_index]
            
            # Calculate relevance score for this answer
            with st.spinner("Evaluating your answer..."):
                score = calculate_relevance_score(
                    current_q, 
                    answer, 
                    st.session_state.interview_state['resume_text']
                )
                st.session_state.interview_state['scores'].append(score)
            
            current_questions = len(st.session_state.interview_state['questions'])
            
            # Only generate new questions if we haven't reached 15 yet
            if current_questions < 15:
                new_questions = generate_adaptive_questions(
                    answer,
                    st.session_state.interview_state['resume_text'],
                    {
                        'questions': st.session_state.interview_state['questions'],
                        'answers': st.session_state.interview_state['answers']
                    }
                )
                # Add new questions up to the 15-question limit
                remaining_slots = 15 - current_questions
                st.session_state.interview_state['questions'].extend(new_questions[:remaining_slots])

            st.session_state.interview_state['current_question'] += 1
            st.session_state.interview_state['question_spoken'] = False

            # Mark interview complete only if we've asked all 15 questions or run out of questions
            if (st.session_state.interview_state['current_question'] >= 15 or 
                st.session_state.interview_state['current_question'] >= len(st.session_state.interview_state['questions'])):
                
                # Generate overall feedback
                with st.spinner("Generating final interview assessment..."):
                    overall_evaluation = evaluate_overall_interview(
                        st.session_state.interview_state['questions'][:len(st.session_state.interview_state['answers'])],
                        st.session_state.interview_state['answers'],
                        st.session_state.interview_state['resume_text']
                    )
                    st.session_state.interview_state['feedback'] = overall_evaluation
                
                st.session_state.interview_state['interview_complete'] = True

            st.rerun()

# Reset interview
def reset_interview():
    st.session_state.interview_state = {
        'current_question': 0,
        'questions': [],
        'answers': [],
        'resume_text': None,
        'interview_complete': False,
        'feedback': {},
        'start_time': None,
        'question_spoken': False,
        'context': {},
        'scores': []  # Reset scores
    }

# Display answer score and feedback
def display_score_feedback(score, question_index):
    score_value = score.get("relevance_score", 0)
    
    # Color coding based on score
    if score_value >= 80:
        color = "green"
    elif score_value >= 60:
        color = "orange"
    else:
        color = "red"
        
    st.markdown(f"<h4 style='color:{color}'>Relevance Score: {score_value}/100</h4>", unsafe_allow_html=True)
    st.markdown(f"**Feedback:** {score.get('feedback', 'No feedback available')}")
    
    # Display strengths and areas for improvement
    if "strengths" in score and score["strengths"]:
        st.markdown("**Strengths:**")
        for strength in score["strengths"]:
            st.markdown(f"- {strength}")
            
    if "areas_for_improvement" in score and score["areas_for_improvement"]:
        st.markdown("**Areas for Improvement:**")
        for area in score["areas_for_improvement"]:
            st.markdown(f"- {area}")

# Main app
def main():
    initialize_session_state()
    st.title("🚀 AI-Powered Interview Assistant")
    st.markdown("""
        Welcome to the **AI Interviewer**! Upload your resume to start a dynamic interview session. 
        This tool will guide you through technical, project-based, and behavioral questions.
    """)

    uploaded_file = st.file_uploader("📄 Upload your Resume (PDF)", type=["pdf"])
    if uploaded_file:
        with st.spinner("Analyzing your resume..."):
            resume_text = extract_resume(uploaded_file)
            if resume_text:
                st.session_state.interview_state['resume_text'] = resume_text
                st.success("✅ Resume processed successfully!")

                if not st.session_state.interview_state['questions']:
                    if st.button("🎤 Start Interview"):
                        st.session_state.interview_state['start_time'] = datetime.now()
                        with st.spinner("Generating interview questions..."):
                            initial_questions = generate_initial_questions(resume_text)
                            # Ensure we don't exceed 15 questions initially
                            st.session_state.interview_state['questions'] = initial_questions[:15]
                            st.session_state.interview_state['current_question'] = 0
                            st.rerun()

                if st.session_state.interview_state['questions']:
                    display_interview_progress()

                    current_q = st.session_state.interview_state['current_question']
                    if current_q < len(st.session_state.interview_state['questions']):
                        question = st.session_state.interview_state['questions'][current_q]
                        st.info(f"**🤖 Question:** {question}")

                        if not st.session_state.interview_state['question_spoken']:
                            speak_text(question)
                            st.session_state.interview_state['question_spoken'] = True

                        if st.button("🎙️ Record Answer", key=f"record_{current_q}"):
                            handle_answer_submission()

                        if st.session_state.interview_state['interview_complete']:
                           st.success("🎯 Interview Complete!")
                    results_file = save_interview_results()
                    st.write(f"Results saved to: `{results_file}`")

                    # Display score visualizations
                    st.subheader("📊 Score Visualization")
                    display_score_visualization(st.session_state.interview_state['scores'])
                    
                    # Display overall assessment
                    st.subheader("📋 Overall Assessment")
                    # (rest of the code for displaying overall assessment remains the same)

                    # Display overall assessment
                    st.subheader("📊 Overall Assessment")
                    overall_feedback = st.session_state.interview_state['feedback']
                    
                    # Display overall score
                    overall_score = overall_feedback.get('overall_score', 0)
                    st.metric("Overall Relevance Score", f"{overall_score:.1f}/100")
                    
                    # Display overall feedback
                    feedback = overall_feedback.get('feedback', {})
                    if 'overall_assessment' in feedback:
                        st.markdown(f"**Assessment:** {feedback['overall_assessment']}")
                        
                    # Display consistent strengths
                    if 'consistent_strengths' in feedback and feedback['consistent_strengths']:
                        st.markdown("**Consistent Strengths:**")
                        for strength in feedback['consistent_strengths']:
                            st.markdown(f"- {strength}")
                            
                    # Display areas for improvement
                    if 'consistent_areas_for_improvement' in feedback and feedback['consistent_areas_for_improvement']:
                        st.markdown("**Areas for Improvement:**")
                        for area in feedback['consistent_areas_for_improvement']:
                            st.markdown(f"- {area}")
                            
                    # Display recommendations
                    if 'recommendations' in feedback and feedback['recommendations']:
                        st.markdown("**Recommendations:**")
                        for rec in feedback['recommendations']:
                            st.markdown(f"- {rec}")
                    
                    # Display detailed Q&A with scores
                    st.subheader("📋 Interview Details")
                    for i, (q, a, score) in enumerate(zip(
                        st.session_state.interview_state['questions'],
                        st.session_state.interview_state['answers'],
                        st.session_state.interview_state['scores']
                    )):
                        with st.expander(f"Question {i+1}: {q[:50]}..."):
                            st.markdown(f"**Q:** {q}")
                            st.markdown(f"**A:** {a}")
                            display_score_feedback(score, i)
                        st.markdown("---")

                    if st.button("🔄 Start New Interview"):
                        reset_interview()
                        st.rerun()
            else:
                st.error("❌ Failed to extract text. Please upload a valid PDF.")

if __name__ == "__main__":
    main()