
# 📚 Quiz Master

**Quiz Master** is a Flask-based web application for creating, managing, and taking quizzes. It features a clean UI with Bootstrap, light/dark theme toggle, user and admin dashboards, quiz management, and database-backed subject/chapter/quiz/question support.

---

## 🚀 Features

- 🔐 User registration and login
- 🌓 Light/Dark theme toggle (persisted across pages)
- 🧑‍🏫 Admin dashboard to manage users, quizzes, subjects, and chapters
- 🧑‍🎓 User dashboard with quiz history and available quizzes
- 🧠 Quiz-taking interface with time duration
- 📊 Result and progress tracking
- 📦 Flask + SQLAlchemy + Bootstrap

---

## 🛠️ Tech Stack

- **Backend**: Flask, SQLAlchemy, SQLite/MySQL/PostgreSQL
- **Frontend**: HTML, CSS, Bootstrap 5, JavaScript
- **Other**: Flask-Login, Jinja2, WTForms

---

## 📁 Project Structure

```plaintext
quiz_master/
├── instance/
│   └── quiz_master.db
├── templates/
│   ├── add/
│   │   ├── add_chapter.html
│   │   ├── add_question.html
│   │   └── add_subject.html
│   ├── edit/
│   │   ├── edit_chapter.html
│   │   ├── edit_question.html
│   │   ├── edit_quiz.html
│   │   └── edit_subject.html
│   ├── view/
│   │   ├── admin_dashboard.html
│   │   ├── attempt_quiz.html
│   │   ├── chapter_quizzes.html
│   │   ├── chapters.html
│   │   └── create_quiz.html
│   ├── index.html
│   ├── login.html
│   ├── quiz_history.html
│   ├── quiz_questions.html
│   ├── register.html
│   ├── search_results.html
│   └── user_dashboard.html
```

---

## ⚙️ Setup Instructions

1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/quiz_master.git
   cd quiz_master
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file with:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///quiz_master.db
   ```

5. **Initialize the database**
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. **Run the app**
   ```bash
   flask run
   ```

---

## 👨‍🔧 Gunicorn Deployment (example)

```bash
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
