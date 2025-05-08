🧠 AI-Powered Interview Assistant
This project is a Streamlit-based AI interview automation system that uses Groq's LLaMA 3.3 model to dynamically generate personalized interview questions and assess candidate responses. It supports PDF resume parsing, adaptive question generation, voice-based interaction, and automated evaluation of answers with visual feedback.

🚀 Features
📄 Resume Parsing
Upload a resume (PDF format).

The system extracts text using PyPDF2 for context-aware question generation.

❓ Dynamic Question Generation
Uses Groq's LLaMA 3.3 via API (model.py) to create:

Technical questions based on resume content.

Behavioral questions to assess soft skills.

Adapts follow-up questions based on previous answers.

🗣️ Voice-Based Interaction
Uses speech_recognition for capturing voice answers.

Delivers questions using pyttsx3 text-to-speech.

Handles ambient noise and errors gracefully (speech_handler.py).

🧠 AI Answer Evaluation
Each answer is scored for relevance using:

Directness, completeness, specificity, relevance, and technical accuracy.

Uses a combination of BLEU score and LLM-based JSON feedback for precise scoring (answer_evaluator.py).

📊 Visual Feedback & Reports
Generates:

Gauge meters and bar charts for individual and average scores.

Final interview assessment including strengths, weaknesses, and improvement tips.

Saves results in JSON format for future reference (main.py, visualization.py).

🛠️ Tech Stack
Frontend: Streamlit

LLM: Groq’s LLaMA 3.3 (via API)

Speech: pyttsx3 (TTS), SpeechRecognition (STT)

Parsing: PyPDF2

Evaluation: BLEU Score, LLM scoring logic

Visualization: Custom HTML/CSS charts + Streamlit components



📁 File Structure
main.py – UI and control flow

resume_parser.py – Resume extraction

question_generator.py – Initial + adaptive question generation

answer_evaluator.py – LLM-based answer assessment

speech_handler.py – Voice input/output logic

visualization.py – Score graphs and summaries

model.py – Groq API integration and retry logic
