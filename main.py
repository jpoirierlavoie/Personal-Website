###############################################
#              Import Packages                #
###############################################

from flask import Flask, request, render_template, url_for, redirect
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from flask_talisman import Talisman
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
#      Define and Configure Application       #
###############################################

app = Flask(__name__)
app.config['SECRET_KEY'] = access_secret('Flask')
app.config['RECAPTCHA_PUBLIC_KEY'] = access_secret('Recaptcha-Key')
app.config['RECAPTCHA_PRIVATE_KEY']= access_secret('Recaptcha-Secret')

###############################################
#             Secure Application              #
###############################################

talisman = Talisman(
    app,
    content_security_policy_nonce_in=['script-src'],
    content_security_policy = {
        'default-src': "'none'",
        'img-src': [
            "'self'",
            'https://www.google.com',
            'https://www.google.ca',
            'https://www.google-analytics.com'
        ],
        'script-src': [
            "'self'",
            'https://www.googletagmanager.com',
            'https://www.google.com',
            'https://code.jquery.com',
            'https://cdn.jsdelivr.net',
            'https://www.google-analytics.com',
            'https://www.gstatic.com',
            'https://unpkg.com'
        ],
        'style-src': [
            "'self'",
            'https://fonts.googleapis.com',
            'https://cdn.jsdelivr.net',
            'https://unpkg.com',
            "'unsafe-inline'"
        ],
        'font-src': [
            'https://fonts.gstatic.com',
            'https://cdn.jsdelivr.net',
            'data:'
        ],
        'connect-src': [
            'https://www.google-analytics.com',
            'https://stats.g.doubleclick.net'
        ],
        'frame-src': [
            'https://www.google.com/'
        ]       
    }
)

###############################################
#                  Forms                      #
###############################################     

class ContactForm(FlaskForm):
    first_name = StringField('First Name',[DataRequired()])
    last_name = StringField('Last Name',[DataRequired()])
    email = StringField('Email',[Email(message=('Not a valid email address.')),DataRequired()])
    subject = StringField('Subject',[DataRequired()])
    subject = StringField('Subject',[DataRequired()])
    message = TextAreaField('Message',[DataRequired(),Length(min=20,message=('Your message is too short.'))])
    recaptcha = RecaptchaField()
    submit = SubmitField('Submit')

###############################################
#                 Routes                      #
###############################################

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
