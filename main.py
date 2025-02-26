import datetime
import os
import smtplib
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from forms import AddTaskForm, SendMailForm

# done strona we flasku ktora pokazuje zadania tymczasowe i stale odziellnie
# done zadanie tymczasowe- obiekt: status wykonania, tekst,czas wykonania
# done formularz do tworzenia zadan tymczasowych:ma pola test i data, domyslnie ma status wykonania na false(jako radio button)
# done tworzenie listy z zadan tymczaowych po wypelnieniu formlarza
# done wyswietlanie tej listy jako zadan tymczasowych
# done jak mamy ta liste i kliknemy guzik to przjedzie po tych zadaniach tymczasowych ,zapisze je w bazie danych i usunie z temporary
# done wyciagamy zdania z bazy danych i wyswietlamy jako osobna lista ponziej zadan tymczasowych -> potem do oznaczenia jako wykonane i usuwanie
# done przycisk zmiany statusu wykonania zmienia sie w zaleznosci od statusu zdania
# done strona glowna ktora zawiera zadania
# done strona glowna: zawiera forma ktory ma tekst i date do kiedy
# done layout
# done  zmienic debugowanie jesli dziala jak nalezy  strona
# https://github.com/gumissek/webapp_todo_list



FLASK_KEY = os.getenv('FLASK_KEY', '123312')
DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///todo_task.db')
MY_MAIL_SMTP = os.getenv('MY_MAIL_SMTP', 'smtp.gmail.com')
MY_MAIL = os.getenv('MY_MAIL', 'pythonkurskurs@gmail.com')
MY_MAIL_PASSWORD = os.getenv('MY_MAIL_PASSWORD', 'svvbtqswtoxdbchw')

app = Flask(__name__)
bootstrap = Bootstrap5(app)

# CONFIGS
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SECRET_KEY'] = FLASK_KEY


# DATABASE
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)


# TABLES
class Task(db.Model):
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(250), nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    date_start: Mapped[str] = mapped_column(String(250), nullable=False)
    date_end: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()

temporary_tasks = []


@app.route('/', methods=['POST', 'GET'])
def homepage():
    add_task_form = AddTaskForm()
    email_form = SendMailForm()
    saved_tasks = db.session.execute(db.select(Task).order_by(Task.status)).scalars().all()
    if add_task_form.validate_on_submit():
        task_text = request.form['text']
        task_date_end = request.form['date_end']
        new_task = Task(text=task_text, status=False, date_start=datetime.datetime.now().strftime('%Y-%m-%d'),
                        date_end=task_date_end)
        temporary_tasks.append(new_task)
        return redirect(url_for('homepage'))
    if email_form.validate_on_submit():
        msg_body = f'Subject: My To-Do list -> {datetime.datetime.now().strftime('%Y-%m-%d')}\n\n'
        for task in saved_tasks:
            msg_body += f'Task nr: {task.id}\nTask: {task.text}\nTask complete: {task.status}\nTask start date: {task.date_start}\nTask deadline: {task.date_end}\n###############\n'
        with smtplib.SMTP(MY_MAIL_SMTP, port=587) as connection:
            connection.starttls()
            connection.login(user=MY_MAIL, password=MY_MAIL_PASSWORD)
            connection.sendmail(from_addr=MY_MAIL, to_addrs=request.form['email'], msg=msg_body)
        flash('Email has been sent.')
        return redirect(url_for('homepage'))

    return render_template('index.html', addtaskform=add_task_form, email_form=email_form,
                           temporary_tasks=temporary_tasks, saved=saved_tasks)


@app.route('/save', methods=['GET', 'POST'])
def save_temporary():
    for task in temporary_tasks:
        db.session.add(task)
        temporary_tasks.remove(task)
        db.session.commit()

    return redirect(url_for('homepage'))


def send_as_email():
    pass


@app.route('/mark', methods=['POST', 'GET'])
def mark_as_done():
    task_to_mark = db.session.execute(db.select(Task).where(Task.id == request.args.get('task_id'))).scalar()
    if task_to_mark.status:
        task_to_mark.status = False
    else:
        task_to_mark.status = True
    db.session.commit()
    return redirect(url_for('homepage'))


@app.route('/remove', methods=['POST', 'GET'])
def delete_task():
    task_to_remove = db.session.execute(db.select(Task).where(Task.id == request.args.get('delete_id'))).scalar()
    db.session.delete(task_to_remove)
    db.session.commit()
    return redirect(url_for('homepage'))


@app.route('/mark_tmp', methods=['POST', 'GET'])
def mark_as_done_tmp():
    if temporary_tasks[int(request.args.get('index'))].status:
        temporary_tasks[int(request.args.get('index'))].status = False
    else:
        temporary_tasks[int(request.args.get('index'))].status = True
    return redirect(url_for('homepage'))


@app.route('/delete_tmp', methods=['POST', 'GET'])
def delete_task_tmp():
    temporary_tasks.remove(temporary_tasks[int(request.args.get('index'))])

    return redirect(url_for('homepage'))


if __name__ == '__main__':
    app.run(debug=False, port=5001)
