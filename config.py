from dotenv import load_dotenv
import os

# .env file se keys load karo
load_dotenv()

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# App settings
APP_NAME = "Agentic Regulatory Intelligence System"
APP_VERSION = "1.0.0"

# AI Model
AI_MODEL = "gemini-2.5-flash"

# Departments list - banks mein ye common hote hain
BANK_DEPARTMENTS = [
    "Compliance",
    "IT & Technology",
    "AML & Financial Crime",
    "Operations",
    "HR & Training",
    "Risk Management",
    "Internal Audit",
    "Finance & Accounts",
    "Legal",
    "Customer Service"
]

# Priority levels
PRIORITY_LEVELS = ["High", "Medium", "Low"]

# Status options
STATUS_OPTIONS = ["Pending", "In Progress", "Completed", "Overdue"]