from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, validators


class NewThreadForSectionForm(FlaskForm):
    title = StringField('Title', [validators.Required(message='You must give a title'),
                                  validators.Length(min=4, max=50)])
    message = StringField('Message', [validators.Required(message='Won\'t you write anything my dear.'),
                                  validators.Length(min=5, max=1000)])
    section_only = BooleanField('Section only?')
    submit = SubmitField('Submit')


class NewThreadForCourseForm(FlaskForm):
    title = StringField('Title', [validators.Required(message='You must give a title'),
                                  validators.Length(min=4, max=5)])
    message = StringField('Message', [validators.Required(message='Won\'t you write anything my dear.'),
                                  validators.Length(min=5, max=1000)])
    submit = SubmitField('Submit')

class NewMessageForm(FlaskForm):
    message = StringField('Message', [validators.Required(message='Won\'t you write anything my dear.'),
                                  validators.Length(min=5, max=1000)])
    submit = SubmitField('Submit')
