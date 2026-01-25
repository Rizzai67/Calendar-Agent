# 📅 AI Calendar Agent

An intelligent calendar assistant powered by LangGraph and Groq's Llama 3.3 that helps you manage your Google Calendar through natural language conversations.

## ✨ Features

- **List Events** - View your upcoming calendar events
- **Create Events** - Schedule new events with natural language
- **Update Events** - Modify existing events with fuzzy matching
- **Smart Date/Time Handling** - Understands relative dates like "tomorrow", "next week"
- **Partial Match Search** - Find events even with incomplete titles
- **Conversational Interface** - Natural back-and-forth dialogue

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Calendar API credentials
- Groq API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/calendar-agent.git
cd calendar-agent
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install langchain-groq langgraph python-dotenv google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

4. Set up your environment variables:
Create a `.env` file in the root directory:
```
GROQ_API_KEY=your_groq_api_key_here
```

5. Set up Google Calendar API:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Google Calendar API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download and save as `credentials.json` in the project root

## 📖 Usage

Run the agent:
```bash
python main.py
```

### Example Conversations

**List events:**
```
You: What events do I have tomorrow?
Assistant: You have 3 events tomorrow:
- Team Standup at 2026-01-24T09:00:00
- Lunch with Client at 2026-01-24T12:30:00
- Project Review at 2026-01-24T15:00:00
```

**Create an event:**
```
You: Schedule a dentist appointment tomorrow at 2 PM
Assistant: ✓ Event created successfully!
Title: Dentist Appointment
Start: 2026-01-24T14:00:00
End: 2026-01-24T15:00:00
```

**Update an event:**
```
You: Move the team meeting to 3 PM
Assistant: ✓ Event 'Team Standup' updated successfully!
Changes made:
Start: 2026-01-24T15:00:00
```

## 🏗️ Project Structure

```
calendar-agent/
│
├── main.py              # Main agent code with all tools and logic
├── auth_test.py         # Google Calendar authentication
├── .env                 # Environment variables (not tracked)
├── credentials.json     # Google API credentials (not tracked)
├── token.json          # OAuth token (not tracked)
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## 🛠️ Tech Stack

- **LangGraph** - Agent orchestration and workflow management
- **Groq** - Fast LLM inference (Llama 3.3 70B)
- **LangChain** - Tool integration and prompt management
- **Google Calendar API** - Calendar operations

## 🔧 Configuration

### Timezone
The agent is currently configured for `Asia/Kolkata` timezone. To change it, update the timezone in `main.py`:
```python
'timeZone': 'Your/Timezone'  # e.g., 'America/New_York'
```

### API Permissions
Ensure your Google Calendar API has the following scope enabled:
```python
SCOPES = ['https://www.googleapis.com/auth/calendar']
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by [Groq](https://groq.com/)
- Uses [Google Calendar API](https://developers.google.com/calendar)

## 📧 Contact

**Rishi**
- LinkedIn: [linkedin.com/in/rishi-sujith-922554377](https://www.linkedin.com/in/rishi-sujith-922554377)

- Email: rishisujith07@gmail.com



---

⭐ If you find this project helpful, please give it a star!