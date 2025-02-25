import datetime
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from forms import AddTaskForm

#TODO
#todo strona we flasku ktora pokazuje zadania tymczasowe i stale odziellnie
#todo zadanie tymczasowe- obiekt: status wykonania, tekst,czas wykonania
#todo formularz do tworzenia zadan tymczasowych:ma pola test i data, domyslnie ma status wykonania na false(jako radio button)
# todo tworzenie listy z zadan tymczaowych po wypelnieniu formlarza
#todo wyswietlanie tej listy jako zadan tymczasowych
#todo jak mamy ta liste i kliknemy guzik to przjedzie po tych zadaniach tymczasowych i zapisze je w bazie danych jako zadania na stale
#todo wyciagamy zdania z bazy danych i wyswietlamy jako osobna lista ponziej zadan tymczasowych -> potem


#todo strona glowna ktora zawiera zadania
#todo strona glowna: zawiera forma ktory ma tekst i date do kiedy


#todo layout
#todo zmienic debugowanie jak dziala strona

FLASK_KEY=os.getenv('FLASK_KEY','123312')
DATABASE_URI=os.getenv('DATABASE_URI','sqlite:///todo_task.db')


app=Flask(__name__)
bootstrap=Bootstrap5(app)

#CONFIGS
app.config['SQLALCHEMY_DATABASE_URI']= DATABASE_URI
app.config['SECRET_KEY']=FLASK_KEY


#DATABASE
class Base(DeclarativeBase):
    pass

db=SQLAlchemy(model_class=Base)
db.init_app(app)

#TABLES
class Task(db.Model):
    __tablename__= 'tasks'
    id : Mapped[int] = mapped_column(Integer,primary_key=True)
    text : Mapped[str] = mapped_column(String(250),nullable=False)
    status : Mapped[bool] = mapped_column(Boolean,nullable=False)
    date_start : Mapped[str] = mapped_column(String(250),nullable=False)
    date_end : Mapped[str] = mapped_column(String(250),nullable=False)

with app.app_context():
    db.create_all()


temporary_tasks = []


@app.route('/',methods=['POST','GET'])
def homepage():
    add_task_form=AddTaskForm()
    saved_tasks=db.session.execute(db.select(Task)).scalars().all()
    if add_task_form.validate_on_submit():
        task_text=request.form['text']
        task_date_end = request.form['date_end']
        new_task=Task(text=task_text,status=False,date_start=datetime.datetime.now().strftime('%d-%m-%Y'),date_end=task_date_end)
        temporary_tasks.append(new_task)
        return redirect(url_for('homepage'))

    return render_template('index.html', addtaskform=add_task_form,temporary_tasks=temporary_tasks,saved=saved_tasks)


@app.route('/save',methods=['GET','POST'])
def save_temporary():
    for task in temporary_tasks:
        db.session.add(task)
        temporary_tasks.remove(task)

    db.session.commit()
    return redirect(url_for('homepage'))


@app.route('/mark',methods=['POST','GET'])
def mark_done():
    task_to_mark=db.session.execute(db.select(Task).where(Task.id==request.args.get('task_id'))).scalar()
    if task_to_mark.status:
        task_to_mark.status=False
    else:
        task_to_mark.status=True
    db.session.commit()
    return redirect(url_for('homepage'))

if __name__=='__main__':
    app.run(debug=True,port=5001)

