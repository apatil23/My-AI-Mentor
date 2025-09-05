# AI Learning Mentor

AI Learning Mentor is a personalized, AI-powered learning companion built with Streamlit. It helps users discover project ideas, create custom learning roadmaps, chat with an AI mentor, and track their progress—all in one place.

---

## 🚀 Features

- **User Authentication:** Secure email/password login and registration.
- **Profile Setup:** Capture experience, interests, skills, learning style, and goals.
- **AI Project Suggestions:** Get diverse, personalized project ideas powered by Google Gemini.
- **Learning Roadmaps:** Generate and manage step-by-step learning plans tailored to your goals.
- **AI Chatbot Mentor:** 24/7 AI mentor for coding help, career advice, and learning support.
- **Progress Tracking:** Log achievements, skills gained, and visualize your learning journey.
- **Data Persistence:** All user data, interactions, and progress are stored in CSV files for easy management.

---

## 🏗️ System Architecture

- **Frontend:** Streamlit multi-page app with responsive UI and custom styling.
- **Backend:** 
  - Google Gemini API for AI-powered suggestions and chat.
  - Pandas for data manipulation and CSV storage.
  - Custom authentication with SHA256 password hashing.
- **Data Storage:** Local CSV files for users, roadmaps, interactions, chat history, and progress.

---

## 📂 Project Structure

```
.
├── app.py
├── pages/
│   ├── 1_Login.py
│   ├── 2_Profile_Setup.py
│   ├── 3_Project_Suggestions.py
│   ├── 4_Learning_Roadmap.py
│   ├── 5_Chatbot_Mentor.py
│   └── 6_Progress_Tracking.py
├── utils/
│   ├── auth.py
│   ├── gemini_client.py
│   └── data_manager.py
├── data/
│   ├── users.csv
│   ├── roadmaps.csv
│   ├── interactions.csv
│   ├── chat_history.csv
│   └── progress.csv
├── .streamlit/
│   └── config.toml
├── pyproject.toml
└── replit.md
```

---

## ⚡ Getting Started

### 1. **Install Dependencies**

```sh
pip install -r requirements.txt
# or, if using pyproject.toml:
pip install .
```

### 2. **Set Up Environment Variables**

Set your Google Gemini API key:

```sh
export GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. **Run the App**

```sh
streamlit run app.py --server.port 5000
```

The app will be available at [http://localhost:5000](http://localhost:5000).

---

## 🛠️ Configuration

- **Streamlit config:** See [.streamlit/config.toml](.streamlit/config.toml)
- **AI API:** Uses Google Gemini via the `google-genai` Python package.
- **Data files:** All persistent data is stored in the `data/` directory as CSV files.

---

## 🤖 AI Services

- **Project Suggestions, Roadmaps, and Chat:** Powered by Google Gemini API.
- **API Key Management:** Set via the `GEMINI_API_KEY` environment variable.

---

## 📊 Data Storage

- `users.csv` — User profiles and authentication
- `roadmaps.csv` — Learning roadmaps
- `interactions.csv` — User activity logs
- `chat_history.csv` — AI mentor conversations
- `progress.csv` — Progress and achievements

---

## 📄 License

This project is for educational and personal use. See [LICENSE](LICENSE) for details.

---

## 🙌 Credits

- Built with [Streamlit](https://streamlit.io/)
- AI powered by [Google Gemini](https://ai.google.dev/)
- Data managed with [pandas](https://pandas.pydata.org/)

---

## 💡 Contributing

Pull requests and suggestions are welcome! Please open an issue to discuss your ideas.

---

## 📬 Contact

For questions or support, open an issue or contact the
