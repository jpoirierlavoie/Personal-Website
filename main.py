###############################################
#              Import Packages                #
###############################################

from flask import Flask, request, render_template, url_for, redirect, abort
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from flask_talisman import Talisman
from google.cloud import datastore
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
#             Access Datastore                #
###############################################

datastore = datastore.Client()

def upsert_post(post):
    entity = datastore.Entity(key=datastore.key('posts'))
    entity.update({'content': post})
    datastore_client.put(entity)

def fetch_post(post):
    query = datastore.query(kind='posts')
    query.add_filter = ['slug', '=', post]
    return query.fetch()
    
def fetch_posts(limit):
    query = datastore.query(kind='posts')
    query.order = ['date']
    posts = query.fetch(limit=limit)
    return posts

###############################################
#      Define and Configure Application       #
###############################################

app = Flask(__name__)
app.config['SECRET_KEY'] = access_secret('Flask')

###############################################
#             Secure Application              #
###############################################

talisman = Talisman(
    app,
    content_security_policy_nonce_in = ['script-src', 'style-src'],
    content_security_policy_report_uri = 'https://jpoirierlavoie.report-uri.com/r/d/csp/enforce',
    strict_transport_security_preload = True,
    session_cookie_samesite = 'Strict',
    content_security_policy = {
        'default-src': "'none'",
        'img-src': [
            "'self'"
        ],
        'script-src': [
            "'self'",
            "'strict-dynamic'",
            'https://code.jquery.com',
            'https://cdn.jsdelivr.net',
            'https://cdnjs.cloudflare.com',
            'https://unpkg.com'
        ],
        'style-src': [
            "'self'",
            'https://fonts.googleapis.com',
            'https://cdn.jsdelivr.net',
            'https://cdnjs.cloudflare.com',
            'https://unpkg.com'
        ],
        'font-src': [
            'https://fonts.gstatic.com',
            'https://cdn.jsdelivr.net',
            'data:'
        ],
        'manifest-src': "'self'",
        'connect-src': "'self'",
        'frame-ancestors': "'none'",
        'base-uri': "'none'",
        'form-action': "'self'"
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
    submit = SubmitField('Submit')    

###############################################
#                 Routes                      #
###############################################

@app.after_request
def add_reporting_endpoints(response):
    response.headers['Report-To']='{"group":"default","max_age":31536000,"endpoints":[{"url":"https://jpoirierlavoie.report-uri.com/a/d/g"}],"include_subdomains":true}'
    response.headers['NEL']='{"report_to":"default","max_age":31536000,"include_subdomains":true}'
    return response

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error.html'), 500

@app.route('/')
def home():
    posts = fetch_posts(5)
    return render_template('home.html', title='Home', posts=posts)

@app.route('/blog')
def blog():
    posts = fetch_posts(10)
    return render_template('blog.html', title= 'Blog', posts=posts)

@app.route('/blog/<post>')
def blog_post(post):
    single_post = fetch_post(post)
    try:
        return render_template('/blog/' + post + '.html', post=single_post)
    except:
        abort(404)
        
@app.route('/resume')
def resume():
    return render_template('resume.html', title='Resume')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
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
        return render_template('contact.html', title="Contact", form=form)

@app.route('/manifest.webmanifest')
def manifest():
    return app.send_static_file('manifest.webmanifest'), 200, {'Content-Type': 'application/manifest+json'}

@app.route('/sitemap.xml')
def sitemap():
    return app.send_static_file('sitemap.xml'), 200, {'Content-Type': 'application/xml'}

@app.route('/robots.txt')
def crawler():
    return app.send_static_file('robots.txt'), 200, {'Content-Type': 'text/plain'}

@app.route('/teapot')
def teapot():
    abort(418)

###############################################
#             Development Server              #
###############################################

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
