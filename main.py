###############################################
#              Import Packages                #
###############################################
from flask import Flask, request, render_template, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length
import email_validator
import sendgrid

###############################################
#              Access Secrets                 #
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
    sg = sendgrid.SendGridAPIClient(access_secret('Sendgrid'))
    form = ContactForm()
    if request.method == 'POST':
        data = {
            "from": {
                "email": "noreply@jpoirierlavoie.ca",
                "name": request.form["first_name"] + " " + request.form["last_name"]
            },
            "reply_to": {
                "email": request.form["email"],
                "name": request.form["first_name"] + " " + request.form["last_name"]
            },
            "content": [
                {
                    "type": "text/plain",
                    "value": request.form["message"]
                }
            ],
            "personalizations": [
                {
                    "to": [
                        {
                            "email": "jpoirierlavoie@gmail.com",
                            "name": "Jason Poirier Lavoie"
                        }
                    ],
                    "subject": "Contact Form: " + request.form["subject"]
                }
            ]
        }
        response = sg.client.mail.send.post(request_body=data)
        if response.status_code == 202:
            return ("Email sent successfully.", 200)
        return ("Something went wrong. Status Code: " + str(response.status_code))
    else:
        return render_template('index.html', form=form)

###############################################
#             Development Server              #
###############################################
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
