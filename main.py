from flask import Flask, render_template, redirect, url_for, request, session
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

import os
from werkzeug.utils import secure_filename


app = Flask(__name__, template_folder="templates")
app.secret_key = "hi3u4h"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///info.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(days=30)

db = SQLAlchemy(app)

class Info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display = db.Column("jobPosting", db.String(1000), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)  # New column to track if the job is approved

    def __init__(self, display):
        self.display = display
        self.is_approved = False  # Initially, set all new job posts as unapproved
        super().__init__()


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    resume_path = db.Column(db.String(200), nullable=False)  # Path to uploaded resume file
    job_id = db.Column(db.Integer, db.ForeignKey('info.id'), nullable=False)  # Foreign key linking to job post

    def __init__(self, student_name, email, resume_path, job_id):
        self.student_name = student_name
        self.email = email
        self.resume_path = resume_path
        self.job_id = job_id



# Configure the upload folder
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/apply/<int:job_id>", methods=["GET", "POST"])
def apply(job_id):
    job_post = Info.query.get_or_404(job_id)  # Get job post by ID
    if request.method == "POST":
        student_name = request.form['student_name']
        email = request.form['email']
        resume_file = request.files['resume']

        
    if resume_file and resume_file.filename != '':
        filename = secure_filename(resume_file.filename)
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        resume_file.save(resume_path)

        # Create and save the application
        application = Application(student_name=student_name, email=email, resume_path=resume_path, job_id=job_id)
        db.session.add(application)
        db.session.commit()
        return redirect(url_for('display'))  # Redirect back to the job display page

        
    else:
        pass
    # Handle case where no file is selected
    return render_template("apply.html", job_post=job_post, error="Please upload a resume.")


       

@app.route("/home")
def home():
    return render_template("homepage.html")

@app.route("/applications")
def applications():
    job_post = Info.query.first()  # Replace with logic to get the specific job post
    return render_template("applicationPage.html", job_post=job_post)


@app.route("/postJobs", methods=["POST", "GET"])
def postJobs():
    if request.method == "POST": 
        session.permanent = True
        display = (
            "Name of Company: " + request.form["company_name"] 
            + ". Job Position: "+ request.form ["job_title"] 
            + ". Details: " + request.form["description"]
        )
        # session["display"] = display
        # init_db()
        # found_job = Info.query.filter_by(id=display).first()
        # if found_job: 
        #     session["display"] = found_job.display
        # else:
        #     job_posting = Info(display)
        #     db.session.add(job_posting)
        #     db.session.commit()
        
     # Create a new job posting and add it to the database
        job_posting = Info(display)
        db.session.add(job_posting)
        db.session.commit()
        
        return redirect(url_for("display")) 
    else:
        return render_template("postJobs.html")

@app.route("/display")
def display():
    approved_posts = Info.query.filter_by(is_approved=True).all()
    return render_template("displayPage.html", selected_posts=approved_posts)


@app.route('/admin/login', methods=["POST", "GET"])
def admin_login():
    session['employer_logged_in'] = False
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
        selected_job_ids = [int(id) for id in request.form.getlist("selected_jobs")]
        for job_id in selected_job_ids:
            job = Info.query.get(job_id)
            if job:
                job.is_approved = True
        db.session.commit()

    job_posts = Info.query.all()
    return render_template('admin_panel.html', job_posts = job_posts)


@app.route('/employer/login', methods=["POST", "GET"])
def employer_login():
    session['admin_logged_in'] = False  # Clear admin login state
    session['employer_logged_in'] = False
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "employer" and password == "employerpass":
            session['employer_logged_in'] = True
            return redirect(url_for('view_applications'))
        else:
            session['employer_logged_in'] = False
            return render_template("employer_login.html", error="Invalid credentials. Try again.")
    return render_template('employer_login.html')

@app.route('/employer')
def view_applications():
    if not session.get('employer_logged_in'):
        return redirect(url_for('employer_login'))
    
    applications = Application.query.all()  # Retrieve all applications
    return render_template("employer.html", applications=applications)


def init_db():
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    app.run(debug=True)