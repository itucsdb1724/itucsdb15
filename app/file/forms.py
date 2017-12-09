from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, validators
from flask_wtf.file import FileField, FileRequired


class NewFileForSectionForm(FlaskForm):
    title = StringField('Title', [validators.Required(message='You must give a title'),
                                  validators.Length(min=4, max=50)])
    file = FileField(validators=[FileRequired()])
    section_only = BooleanField('Section only?')
    submit = SubmitField('Submit')
