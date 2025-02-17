#python modules
import os
from statistics import mean
from datetime import datetime
from collections import defaultdict
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, cast, String,func
from flask import Flask, render_template, request, redirect, url_for, session, jsonify,flash

app = Flask(__name__)
app.secret_key = os.urandom(24)

#database configuration 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#database models
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100), nullable=True)
    dob = db.Column(db.Date, nullable=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.String(10), nullable=False)
    remarks = db.Column(db.Text, nullable=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, default=datetime.now())
    total_scored = db.Column(db.Integer, nullable=False)

#inializing database when application starts
def init_db():
    with app.app_context():
        db.create_all()
        if not Admin.query.filter_by(username="admin").first():
            admin = Admin(username="admin", password="admin123")
            db.session.add(admin)
            db.session.commit()

#home route
@app.route('/')
def home():
    return render_template('index.html')

#login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin':
            admin = Admin.query.filter_by(username=username, password=password).first()
            if admin:
                session['admin'] = True
                return redirect(url_for('admin_dashboard'))
        else:
            user = User.query.filter_by(username=username, password=password).first()
            if user:
                session['user_id'] = user.id
                return redirect(url_for('user_dashboard'))

        return "Invalid credentials. Please try again."
    return render_template('login.html')

#registration route 
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        qualification = request.form['qualification']
        dob = request.form['dob']

        user = User(username=username, password=password, full_name=full_name, qualification=qualification, dob=datetime.strptime(dob, '%Y-%m-%d'))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

''' Admin Routes:
    [on admin_dashboard page]- search, view_user(view_details), delete_user, chapters(view chapters), edit_subjest, delete_subject,
        add_subject, view_quiz_users(view_users), quiz_history(view_quiz_history),quiz_trends
    [on subject's page]- chapter_quizzes(view quizzes), create_quiz, edit_chapter, delete_chapter,add_chapter
    [on chapter's page]- quiz_questions(view questions), edit_quiz,delete_quiz,create_quiz
    [on a quizzes page]- edit_question, delete_question,add_question
'''

#Below  are all Admin's Routes
##admin's dashboard page routes
###admin dashboard route
@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('login'))
    
    subjects = Subject.query.all()
    users = User.query.all()

    total_quizzes_attempted = db.session.query(func.count(Score.id)).scalar()
    users_per_quiz = db.session.query(Quiz.id, func.count(func.distinct(Score.user_id))).join(Score).group_by(Quiz.id).all()
    quiz_user_attempts = {quiz_id: count for quiz_id, count in users_per_quiz}

    quiz_attempts_per_subject = db.session.query(
        Subject.name, func.count(Score.id)
    ).join(Chapter, Chapter.subject_id == Subject.id
    ).join(Quiz, Quiz.chapter_id == Chapter.id
    ).join(Score, Score.quiz_id == Quiz.id
    ).group_by(Subject.name).all()

    users_per_quiz = db.session.query(
        Quiz.id, Quiz.chapter_id, Chapter.name, func.count(func.distinct(Score.user_id))
    ).join(Chapter, Chapter.id == Quiz.chapter_id
    ).join(Score, Score.quiz_id == Quiz.id
    ).group_by(Quiz.id, Chapter.name).all()

    quiz_user_attempts = [{
        "quiz_id": quiz_id,
        "chapter_name": chapter_name,
        "user_count": count
    } for quiz_id, chapter_id, chapter_name, count in users_per_quiz]

    quiz_attempts_per_chapter = db.session.query(
        Chapter.name, func.count(Score.id)
    ).join(Quiz, Quiz.chapter_id == Chapter.id
    ).join(Score, Score.quiz_id == Quiz.id
    ).group_by(Chapter.name).all()

    return render_template(
        'admin_dashboard.html',
        subjects=subjects,
        users=users,
        total_quizzes_attempted=total_quizzes_attempted,
        quiz_user_attempts=quiz_user_attempts,
        quiz_attempts_per_subject=quiz_attempts_per_subject,
        quiz_attempts_per_chapter=quiz_attempts_per_chapter
    )

###searching route
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return render_template('admin_dashboard.html', subjects=[], users=[], quizzes=[], chapters=[])

    users = User.query.filter(User.username.ilike(f"%{query}%") | User.full_name.ilike(f"%{query}%")).all()
    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%") | Subject.description.ilike(f"%{query}%")).all()
    quizzes = (
    db.session.query(Quiz)
    .join(Chapter, Quiz.chapter_id == Chapter.id)
    .join(Subject, Chapter.subject_id == Subject.id)
    .filter(
        or_(
            Quiz.remarks.ilike(f"%{query}%"),
            Chapter.name.ilike(f"%{query}%"),
            Subject.name.ilike(f"%{query}%"),
            cast(Quiz.date_of_quiz, String).ilike(f"%{query}%"),  
            Quiz.time_duration.ilike(f"%{query}%") 
        )
    )
    .all()
)
    return render_template('search_results.html', users=users, subjects=subjects, quizzes=quizzes)

##--to check info of saerched quiz
@app.route('/view_quiz/<int:quiz_id>')
def view_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    chapter = Chapter.query.get(quiz.chapter_id)
    subject = Subject.query.get(chapter.subject_id)
    return render_template('view/view_quiz.html', quiz=quiz, chapter=chapter, subject=subject)

##--to check info of searched subject
@app.route('/view_subject/<int:subject_id>')
def view_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return render_template('view/view_subject.html', subject=subject)

###to view user details 
@app.route('/view_user/<int:user_id>')
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('view/view_user.html', user=user)

###to delete user 
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect('/admin_dashboard')

###to view chapters 
@app.route('/chapters/<int:subject_id>')
def chapters(subject_id):
    subject = Subject.query.get(subject_id)
    if subject:
        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        return render_template('chapters.html', subject=subject, chapters=chapters)
    return redirect(url_for('admin_dashboard'))

###to edit subjects 
@app.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    if not session.get('admin'):
        return redirect(url_for('login'))

    subject = Subject.query.get_or_404(subject_id)

    if request.method == 'POST':
        subject.name = request.form['name']
        subject.description = request.form['description']

        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('edit/edit_subject.html', subject=subject)

###to delete subject 
@app.route('/delete_subject/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    if not session.get('admin'):
        return redirect(url_for('login'))

    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()

    return redirect(url_for('admin_dashboard'))

###to add new subject
@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()

        return redirect(url_for('admin_dashboard'))

    return render_template('add/add_subject.html')

###to check quiz attempted users
@app.route('/view_quiz_users/<int:quiz_id>')
def view_quiz_users(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return "Quiz not found", 404
    chapter = Chapter.query.get(quiz.chapter_id)

    users = db.session.query(User.full_name, User.username).join(Score, User.id == Score.user_id).filter(Score.quiz_id == quiz_id).all()

    return render_template('/view/view_quiz_users.html', quiz=quiz, chapter=chapter, users=users)

###to check history of attempted quiz
@app.route('/quiz_history')
def quiz_history():
    quiz_attempts = db.session.query(Score, User, Quiz, Chapter, Subject).join(User).join(Quiz).join(Chapter).join(Subject).all()
    history = []
    for score, user, quiz, chapter, subject in quiz_attempts:
        history.append({
            'username': user.username,
            'full_name': user.full_name,
            'quiz_date': quiz.date_of_quiz,
            'quiz_id': quiz.id,
            'time_of_attempt': score.time_stamp_of_attempt,
            'score': score.total_scored,
            'subject_name': subject.name,
            'chapter_name': chapter.name
        })

    return render_template('quiz_history.html', history=history)

##for summary: quiz trends
@app.route('/quiz_trends')
def quiz_trends():
    today = datetime.today().date()

    quiz_attempts_per_chapter_day = db.session.query(
        Chapter.name, func.count(Score.id)
    ).join(Quiz, Quiz.chapter_id == Chapter.id
    ).join(Score, Score.quiz_id == Quiz.id
    ).filter(func.date(Score.time_stamp_of_attempt) == today).group_by(Chapter.name).all()

    return jsonify({
        "chapters_day": [{"name": c, "attempts": a} for c, a in quiz_attempts_per_chapter_day]
    })

##particular subjects page (having chapters) routes
###view current chapters available quizzes
@app.route('/chapter_quizzes/<int:chapter_id>')
def chapter_quizzes(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    return render_template('chapter_quizzes.html', chapter=chapter, quizzes=quizzes)

###to create new quiz 
@app.route('/create_quiz/<int:chapter_id>')
def create_quiz(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    return render_template('create_quiz.html', chapter=chapter)

###to edit chapters details 
@app.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if request.method == 'POST':
        chapter.name = request.form['name']
        chapter.description = request.form.get('description')
        db.session.commit()
        return redirect(url_for('chapters', subject_id=chapter.subject_id))
    return render_template('edit/edit_chapter.html', chapter=chapter)

###to delete a chapter
@app.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
def delete_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    subject_id = chapter.subject_id
    db.session.delete(chapter)
    db.session.commit()
    return redirect(url_for('chapters', subject_id=subject_id))

###to add new chapter
@app.route('/add_chapter/<int:subject_id>', methods=['GET', 'POST'])
def add_chapter(subject_id):
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description')
        new_chapter = Chapter(subject_id=subject_id, name=name, description=description)
        db.session.add(new_chapter)
        db.session.commit()
        return redirect(url_for('chapters', subject_id=subject_id))
    return render_template('add/add_chapter.html', subject_id=subject_id)

##particular chapters page (having quizzes) routes
###to check quizzes questions
@app.route('/quiz_questions/<int:quiz_id>')
def quiz_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('quiz_questions.html', quiz=quiz, questions=questions)

###to edit created quiz
@app.route('/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'POST':
        date_of_quiz_str = request.form['date_of_quiz']
        time_duration = request.form['time_duration']
        remarks = request.form['remarks']
        date_of_quiz = datetime.strptime(date_of_quiz_str, '%Y-%m-%d').date()
        quiz.date_of_quiz = date_of_quiz
        quiz.time_duration = time_duration
        quiz.remarks = remarks
        db.session.commit()
        return redirect(url_for('chapter_quizzes', chapter_id=quiz.chapter_id, subject_id=quiz.chapter_id))

    return render_template('edit/edit_quiz.html', quiz=quiz)

###to delete created quiz
@app.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    return redirect(f'/chapter_quizzes/{quiz.chapter_id}')

##particular quiz's page (having questions) routes
###to edit created question
@app.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)

    if request.method == 'POST':
        question.question_statement = request.form['question_statement']
        question.option1 = request.form['option1']
        question.option2 = request.form['option2']
        question.option3 = request.form['option3']
        question.option4 = request.form['option4']
        question.correct_option = int(request.form['correct_option'])

        db.session.commit()
        return redirect(url_for('quiz_questions', quiz_id=question.quiz_id))

    return render_template('edit/edit_question.html', question=question)

###to delete a question in a quiz
@app.route('/delete_question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('quiz_questions', quiz_id=quiz_id))

###to add a question in a quiz
@app.route('/add_question/<int:quiz_id>', methods=['GET', 'POST'])
def add_question(quiz_id):
    if request.method == 'POST':
        question_statement = request.form['question_statement']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_option = int(request.form['correct_option'])
        
        question = Question(quiz_id=quiz_id, question_statement=question_statement, option1=option1, option2=option2, option3=option3, option4=option4, correct_option=correct_option)
        db.session.add(question)
        db.session.commit()
        return redirect(f'/quiz_questions/{quiz_id}')
    return render_template('add/add_question.html', quiz_id=quiz_id)

###to save quiz after creating a quiz
@app.route('/save_quiz/<int:chapter_id>', methods=['POST'])
def save_quiz(chapter_id):
    date_of_quiz = request.form['date_of_quiz']
    time_duration = request.form['time_duration']
    remarks = request.form['remarks']
 
    new_quiz = Quiz(
        chapter_id=chapter_id,
        date_of_quiz=datetime.strptime(date_of_quiz, '%Y-%m-%d').date(),
        time_duration=time_duration,
        remarks=remarks
    )
    
    db.session.add(new_quiz)
    db.session.commit()
    
    return redirect(url_for('chapter_quizzes', chapter_id=chapter_id,subject_id=chapter_id))


'''User Routes
    [user dashboard]- attempt_quiz
    [quiz page]- submit_quiz
'''

#Below are all User's routes
##user's dashboard page routes
##user dashboard route
@app.route('/user_dashboard')
def user_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    quizzes = Quiz.query.all()
    scores = Score.query.filter_by(user_id=user_id).all()

    enriched_scores = []
    scores_by_date = defaultdict(list)
    
    dates = []
    scores_data = []
    
    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        chapter = Chapter.query.get(quiz.chapter_id)
        subject = Subject.query.get(chapter.subject_id)
        date = score.time_stamp_of_attempt.date()  
        scores_by_date[date].append(score.total_scored)

        enriched_scores.append({
            'score': score,
            'quiz': quiz,
            'chapter': chapter,
            'subject': subject
        })

        dates.append(date)
        scores_data.append(score.total_scored)

    avg_scores = {date: mean(scores_by_date[date]) for date in scores_by_date}
    
    unique_dates = sorted(set(dates))
    attempts_data = [dates.count(date) for date in unique_dates]
    avg_scores_data = [avg_scores[date] for date in unique_dates]

   
    subjects_data = {}
    for score in scores:
        quiz = Quiz.query.get(score.quiz_id)
        chapter = Chapter.query.get(quiz.chapter_id)
        subject = Subject.query.get(chapter.subject_id)
        subjects_data[subject.name] = subjects_data.get(subject.name, 0) + 1

    summary_data = {
        'dates': [date.strftime('%Y-%m-%d') for date in unique_dates], 
        'scores': scores_data,
        'avg_scores': avg_scores_data,
        'attempts': attempts_data,
        'subjects': list(subjects_data.keys()),
        'subjectAttempts': list(subjects_data.values())
    }

    user=User.query.filter_by(id=user_id).first()
    user_name=user.full_name

    return render_template(
        'user_dashboard.html',
        subjects=subjects,
        chapterss=chapters,
        quizzes=quizzes,
        scores=enriched_scores,
        user_name=user_name,
        summaryData=summary_data
    )

###to attempt a quiz
@app.route('/attempt_quiz/<int:quiz_id>', methods=['GET'])
def attempt_quiz(quiz_id):
    if 'user_id' not in session:
        flash('Please log in to attempt the quiz.', 'danger')
        return redirect(url_for('login'))

    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('attempt_quiz.html', quiz=quiz, questions=questions)

###to check user score
    

##particular quiz page (quiz page)
###to submit quiz
@app.route('/submit_quiz/<int:quiz_id>', methods=['POST'])
def submit_quiz(quiz_id):
    if 'user_id' not in session:
        flash('Please log in to submit the quiz.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    score = 0

    for question in questions:
        selected_option = request.form.get(f'question_{question.id}')
        if selected_option and int(selected_option) == question.correct_option:
            score += 1

    total_questions = len(questions)
    percentage = f"{(score / total_questions) * 100:.2f}"

    new_score = Score(
        quiz_id=quiz_id,
        user_id=user_id, 
        time_stamp_of_attempt=datetime.now().replace(microsecond=0),
        total_scored=percentage
    )
    db.session.add(new_score)
    db.session.commit()

    return redirect(url_for('user_dashboard'))

#to logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

#to execute and run db
if __name__ == '__main__':
    init_db()
    app.run(debug=True)