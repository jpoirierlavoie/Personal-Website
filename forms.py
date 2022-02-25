from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, TextField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class ContactForm(FlaskForm):
    first_name = StringField('First Name',[DataRequired()])
    last_name = StringField('Last Name',[DataRequired()])
    email = StringField('Email',[Email(message=('Not a valid email address.')),DataRequired()])
    subject = StringField('Subject',[DataRequired()])
    subject = StringField('Subject',[DataRequired()])
    message = TextField('Message',[DataRequired(),Length(min=20,message=('Your message is too short.'))])
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    title = StringField('Title',[DataRequired()])
    category = StringField('Category',[DataRequired()])
    article = TextAreaField('Article',[DataRequired(),Length(min=4,message=('Your message is too short.'))])
    submit = SubmitField('Submit')
