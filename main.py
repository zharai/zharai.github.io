from flask import Flask, render_template, redirect, url_for, request, session
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta


app = Flask(__name__, template_folder="templates")
app.secret_key = "hi3u4h"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///info.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(days=30)

db = SQLAlchemy(app)

class Info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display = db.Column("jobPosting", db.String(1000), nullable=False)
    def __init__(self, display):
        self.display = display
        super().__init__()

@app.route("/home")
def home():
    return render_template("homepage.html")

@app.route("/applications")
def applications():
    return render_template("applicationPage.html")

@app.route("/postJobs", methods=["POST", "GET"])
def postJobs():
    if request.method == "POST": 
        session.permanent = True
        display = (
            "Name of Company: " + request.form["company_name"] 
            + ". Job Position: "+ request.form ["job_title"] 
            + ". Details: " + request.form["description"]
        )
        session["display"] = display
        init_db()
        found_job = Info.query.filter_by(id=display).first()
        if found_job: 
            session["display"] = found_job.display
        else:
            job_posting = Info(display)
            db.session.add(job_posting)
            db.session.commit()
        return redirect(url_for("display")) 
    else:
        return render_template("postJobs.html")

@app.route("/display")
def display():
    selected_ids = session.get("selected_job_posts", [])
    if selected_ids:
        selected_posts = Info.query.filter(Info.id.in_(selected_ids)).all()
    else:
        selected_posts = []
    return render_template("displayPage.html", selected_posts = selected_posts)

@app.route('/admin', methods=["POST", "GET"])
def admin_login():
    session['admin_logged_in'] = False
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "admin" and password == "adminpass":
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            session['admin_logged_in'] = False
            return render_template("admin_login.html", error="Invalid credentials. Try again.")
    return render_template('admin_login.html')


@app.route('/admin/panel', methods=["POST", "GET"])
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == "POST":
        selected_job_ids = request.form.getlist("selected_jobs")
        session["selected_job_posts"] = [int(id) for id in selected_job_ids]


    job_posts = Info.query.all()
    return render_template('admin_panel.html', job_posts = job_posts)

def init_db():
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    app.run(debug=True)