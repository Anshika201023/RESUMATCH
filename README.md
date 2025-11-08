# RESUMATCH
An AI-powered resume–job matcher that parses resumes, analyzes job descriptions, and calculates skill match percentage using NLP and semantic similarity.

ResuMatch is an intelligent web application that helps recruiters and job seekers instantly compare resumes against job descriptions. It uses Natural Language Processing (NLP) and semantic similarity models to identify matching and missing skills, providing a clear match percentage between a candidate’s profile and a job role.

**FEATURES**
1. Resume Parsing – Automatically extracts candidate details such as name, email, education, experience, and skills from PDF or DOCX resumes using pyresparser.
2. Skill Matching – Compares extracted resume skills with the job description using Sentence Transformers (all-MiniLM-L6-v2) and cosine similarity.
3. Match Score – Displays a percentage score representing how well a resume fits the job description.
4. Keyword Insights – Highlights matched and missing keywords between the resume and JD.
5. History Tracking – Saves parsed resumes and past matches locally for quick reference.
6. User-friendly Interface – Built with Bootstrap 5 for a clean, responsive design.
7. Dockerized Setup – Frontend (Nginx) and Backend (Flask + Gunicorn) run seamlessly via Docker Compose.

**WORKING**
1. Upload Resume - The backend parses and extracts key information using NLP.
2. Enter Job Description - The user inputs a job title and description.
3. Match Results - The system compares both, computes a semantic similarity score, and displays matched/missing skills along with a match percentage.
4. History View - Users can view previously uploaded resumes and match results anytime.

**OUTPUT**

<img width="1919" height="926" alt="image" src="https://github.com/user-attachments/assets/6815f5f1-d895-4ed5-a831-39ec4e3ef9be" />

<img width="1595" height="598" alt="image" src="https://github.com/user-attachments/assets/90dca0e0-42fc-49f5-b77a-20422e8b314f" />

<img width="1918" height="928" alt="image" src="https://github.com/user-attachments/assets/f816ab99-2f4d-4c2a-9cc4-0f087dec0ef9" />

<img width="1912" height="930" alt="image" src="https://github.com/user-attachments/assets/ae757b4e-cd13-45b7-aece-369ebc42a240" />

<img width="1909" height="929" alt="image" src="https://github.com/user-attachments/assets/89293953-51a5-4506-b306-8e9e30487eb2" />

