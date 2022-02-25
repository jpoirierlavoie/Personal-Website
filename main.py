###############################################
#              Import Packages                #
###############################################
from flask import Flask, request, render_template, url_for, redirect

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
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/contact', methods=['POST'])
def contact():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']
    error = None
    
    if not first_name or not first_name.strip():
        error = 'First name is missing'
    if not last_name or not last_name.strip():
        error = 'Lirst name is missing'
    if not email or not email.strip() or '@' not in email:
        error = 'Email is missing'
    if not sunject or not subject.strip():
        error = 'Message is missing'
    if not message or not message.strip():
        error = 'Message is missing' 
    if error:
        return  render_template('index.html#contact', error = error, first_name = first_name, last_name = last_name, email = email, subject = subject, message = message)
    return render_template('index.html')
 
@app.route('/manifest.webmanifest')
def manifest():
    return app.send_static_file('manifest.webmanifest'), 200, {'Content-Type': 'application/manifest+json'}

@app.route('/robots.txt')
def crawler():
    return app.send_static_file('robots.txt'), 200, {}

@app.route('/sitemap.xml')
def sitemap():
    return app.send_static_file('sitemap.xml'), 200, {'Content-Type': 'text/xml; charset=utf-8'}

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
