###############################################
#              Import Packages                #
###############################################
from flask import Flask, request, render_template, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length

import email_validator

###############################################
#              Import Secrets                 #
###############################################
def access_secret(secret_id):
    from google.cloud import secretmanager
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/149647873417/secrets/{secret_id}/versions/1"
    response = client.access_secret_version(request={'name': name})
    payload = response.payload.data.decode('UTF-8')
    return payload

###############################################
#              Define flask app               #
###############################################
app = Flask(__name__)
app.secret_key = access_secret('Flask-WTF')

###############################################
#                  Routes                     #
###############################################     

class ContactForm(FlaskForm):
    first_name = StringField('First Name',[DataRequired()])
    last_name = StringField('Last Name',[DataRequired()])
    email = StringField('Email',[Email(message=('Not a valid email address.')),DataRequired()])
    subject = StringField('Subject',[DataRequired()])
    subject = StringField('Subject',[DataRequired()])
    message = TextAreaField('Message',[DataRequired(),Length(min=20,message=('Your message is too short.'))])
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def home():
    form = ContactForm()
    if request.method == 'POST':
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]
        
    else:
        return render_template('index.html', form=form)
    
@app.route('/manifest.webmanifest')
def manifest():
    return app.send_static_file('manifest.webmanifest'), 200, {'Content-Type': 'application/manifest+json'}

@app.route('/robots.txt')
def crawler():
    return app.send_static_file('robots.txt'), 200, {}

@app.route('/sitemap.xml')
def sitemap():
    return app.send_static_file('sitemap.xml'), 200, {'Content-Type': 'text/xml; charset=utf-8'}

###############################################
#             Development Server              #
###############################################
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
