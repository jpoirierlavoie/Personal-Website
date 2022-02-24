from flask import Flask, render_template, url_for, redirect

app = Flask(__name__)

@app.route('/')
def home():
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
