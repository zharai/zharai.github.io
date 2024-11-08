from flask import Flask, render_template, redirect, url_for, request, session
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta


app = Flask(__name__, template_folder="templates")
db = SQLAlchemy(app)
app.secret_key = "hi3u4h"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///info.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(days=30)

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
        display = "Name of Company: " + request.form["company_name"] + ". Job Position: "+ request.form ["job_title"] + ". Details: " + request.form["description"]
        session["display"] = display
        init_db()
        inf = Info(display)
        db.session.add(inf)
        db.session.commit()

        return redirect(url_for("display")) 
    else:
        return render_template("postJobs.html")

@app.route("/display")
def display():
    if "display" in session:
        display = session["display"]

        return f"<b>{display}</b>"
    else:
        return redirect(url_for("postJobs"))

def init_db():
    with app.app_context():
        db.create_all()

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
            return render_template("admin_login.html", error="Invalid credentials. Try again.")   # error message does not show up
    return render_template('admin_login.html')


@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    # get all job postings?
    return render_template('admin_panel.html')

def init_db():
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    app.run(debug=True)