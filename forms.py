from flask_wtf import FlaskForm
from wtforms.fields.datetime import DateField
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired


class AddTaskForm(FlaskForm):
    text = StringField(label='Podaj tresc zadania', validators=[DataRequired()])
    date_end = DateField(label='Podaj czas zakonczenia zadania', validators=[DataRequired()])
    submit = SubmitField(label='Dodaj zadanie')
