from flask_wtf import FlaskForm
from wtforms.fields.datetime import DateField
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired


class AddTaskForm(FlaskForm):
    text = StringField(label='Task description:', validators=[DataRequired()])
    date_end = DateField(label='Task deadline:', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField(label='Add task!')
