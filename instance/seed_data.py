from quiz_master import db
from quiz_master.models import Subject, Chapter, Quiz, Question
from datetime import date, timedelta
import random
from faker import Faker

fake = Faker()

# Create and add subjects
subjects = []
for i in range(1, 26):
    subject = Subject(
        name=f"Subject {i}",
        description=fake.text(max_nb_chars=200)
    )
    db.session.add(subject)
    subjects.append(subject)

db.session.commit()

# Create and add chapters
chapters = []
for subject in subjects:
    for j in range(1, 6):  # 5 chapters per subject
        chapter = Chapter(
            subject_id=subject.id,
            name=f"Chapter {j} of {subject.name}",
            description=fake.text(max_nb_chars=200)
        )
        db.session.add(chapter)
        chapters.append(chapter)

db.session.commit()

# Create and add quizzes and questions
for chapter in chapters:
    for _ in range(5):  # 5 quizzes per chapter
        quiz = Quiz(
            chapter_id=chapter.id,
            date_of_quiz=date.today() - timedelta(days=random.randint(1, 365)),
            time_duration=f"{random.choice([15, 30, 45, 60])} min",
            remarks=fake.sentence()
        )
        db.session.add(quiz)
        db.session.commit()  # To get quiz.id

        # Add 10 questions to the quiz
        for _ in range(10):
            correct_option = random.randint(1, 4)
            question = Question(
                quiz_id=quiz.id,
                question_statement=fake.sentence(nb_words=10),
                option1=fake.word(),
                option2=fake.word(),
                option3=fake.word(),
                option4=fake.word(),
                correct_option=correct_option
            )
            db.session.add(question)

        db.session.commit()

