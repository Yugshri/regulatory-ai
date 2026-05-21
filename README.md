RegAI — Agentic Regulatory Intelligence & Compliance
RegAI transforms RBI and SEBI circulars into structured, department-assigned action points — automatically. No manual reading. No missed deadlines.

The Problem
Indian banks receive hundreds of regulatory circulars every year. Compliance teams read them manually, interpret what needs to be done, figure out which department is responsible, and track completion in spreadsheets. This process is slow, error-prone, and unauditable.

The Solution
Upload a circular. RegAI reads it, extracts every actionable requirement, assigns each one to the correct department, and gives your team a live dashboard to track progress — with a built-in AI assistant to answer questions about the circular at any time.

Features
PDF Upload — Drop any RBI or SEBI circular PDF directly into the app
AI Extraction — Gemini 2.5 Flash reads the circular and outputs structured Measurable Action Points (MAPs)
Auto Department Assignment — Each MAP is assigned to Compliance, IT, AML, HR, Operations, Risk, Legal, or Internal Audit
Live Dashboard — Filter by department or priority, track status in real time
AI Compliance Chatbot — Ask anything about the loaded circular and get instant answers
Audit Trail — Every status change is logged with a timestamp
Export — Download all MAPs as Excel or JSON
Tech Stack
Layer	Technology
UI	Streamlit
AI	Google Gemini 2.5 Flash
Database	SQLite
PDF Parsing	PyPDF
Language	Python 3.12
Project Structure
regulatory-ai/
├── app.py            UI and layout
├── ai_engine.py      MAP extraction and completion validation
├── extractor.py      PDF parsing and circular validation  
├── database.py       SQLite operations and audit logging
├── models.py         MAP and CircularSession classes
├── config.py         API keys, model config, department list
└── utils.py          Excel export and summary statistics
Getting Started
Prerequisites

Python 3.10 or higher
A Google Gemini API key — get one free at aistudio.google.com
Installation

bash
git clone https://github.com/Yugshri/regulatory-ai.git
cd regulatory-ai
pip install streamlit google-genai pypdf pandas openpyxl python-dotenv
Configuration

Create a .env file in the root directory:

GEMINI_API_KEY=your_api_key_here
Run

bash
streamlit run app.py
The app opens at http://localhost:8501

How to Use
Open the app and go to the Upload PDF tab
Upload any RBI or SEBI circular in PDF format
Click Extract Action Points
View extracted MAPs on the dashboard — filter by department or priority
Update the status of each MAP as your team works through them
Use the AI Compliance Assistant on the right to ask questions about the circular
Download all MAPs as Excel or JSON when done
Example
Upload an RBI KYC circular and RegAI will output something like:

MAP	Department	Deadline	Priority
Complete re-KYC for all existing customers	Compliance	Within 6 months	High
Enable Video KYC at all branches	IT & Technology	Q3 2025	High
File suspicious transaction reports within 7 days	AML	Ongoing	High
Update IT systems for new KYC data fields	IT & Technology	December 2025	Medium
Developer
Yug Shrivastav Final Year — Internet Of Things, MITS Gwalior GitHub

