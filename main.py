from flask import Flask, render_template, redirect, url_for, request, session
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

import os
from werkzeug.utils import secure_filename

#Initialize the Flask Application
app = Flask(__name__, template_folder="templates")
app.secret_key = "hi3u4h" #Secret key for session management
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///info.sqlite3' #database configuration
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(days=30) #Session duration

#Initialize SQLAlchemy for database interaction
db = SQLAlchemy(app)

# Define the Employer model, representing a table in the database
class Employer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password


# Define the Info model to store job postings
class Info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display = db.Column("jobPosting", db.String(1000), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)  # New column to track if the job is approved
    employer_id = db.Column(db.Integer, db.ForeignKey('employer.id'), nullable=False)  # Foreign key to Employer

    employer = db.relationship('Employer', backref='jobs')  # Add relationship


    def __init__(self, display, employer_id):
        self.display = display
        self.employer_id = employer_id
        self.is_approved = False  # Initially, set all new job posts as unapproved
        super().__init__()


# Define the Application model to store job applications
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    resume_path = db.Column(db.String(200), nullable=False)  # Path to uploaded resume file
    job_id = db.Column(db.Integer, db.ForeignKey('info.id'), nullable=False)  # Foreign key linking to job post (Info)

    def __init__(self, student_name, email, resume_path, job_id):
        self.student_name = student_name
        self.email = email
        self.resume_path = resume_path
        self.job_id = job_id


# Configure the upload folder for storing resumes
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True) # Ensure the folder exists

       
# Route for the homepage
@app.route("/home")
def home():
    return render_template("homepage.html")

@app.route("/about")
def about():
    return render_template("about.html")

# Redirect root URL to the homepage
@app.route("/")
def root():
    return redirect(url_for("home"))

# Route to apply for a job
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
            application = Application(student_name=student_name, email=email, resume_path=filename, job_id=job_id)
            db.session.add(application)
            db.session.commit()
            return redirect(url_for('display'))  # Redirect back to the job display page
        
        else:
            return render_template("applicationPage.html", job_post=job_post, error="Please upload a resume.")

    return render_template("applicationPage.html", job_post=job_post)

#route for "student or employer?" form
@app.route("/form")
def form():
    return render_template("form.html")

# Route for posting new jobs
@app.route("/postJobs", methods=["POST", "GET"])
def postJobs():
    if not session.get('employer_logged_in'):
        return redirect(url_for('employer_login'))
    
    if request.method == "POST": 
        session.permanent = True # Extend session duration
        display = (
            "Name of Company: " + request.form["company_name"] + "." + "<br>" 
            + "Job Position: "+ request.form ["job_title"] + "." + "<br>"
            + "Details: " + request.form["description"]
        )
        
        # Get the employer's ID from the session
        employer_id = session.get('employer_id')

        # Create a new job posting and associate it with the employer's ID
        job_posting = Info(display=display, employer_id=employer_id)
        db.session.add(job_posting)
        db.session.commit()

        return redirect(url_for("display")) 
    else:
        return render_template("postJobs.html")


# Route to display approved job postings
@app.route("/display")
def display():
    approved_posts = Info.query.filter_by(is_approved=True).all()
    return render_template("displayPage.html", selected_posts=approved_posts)


# Route for admin login
@app.route('/admin/login', methods=["POST", "GET"])
def admin_login():
    session['employer_logged_in'] = False
    session['admin_logged_in'] = False
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "admin" and password == "adminpass": # admin credentials check
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            session['admin_logged_in'] = False
            return render_template("admin_login.html", error="Invalid credentials. Try again.")
    return render_template('admin_login.html')


# Admin panel to approve or view all job postings
@app.route('/admin/panel', methods=["POST", "GET"])
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == "POST":
        selected_job_ids = [int(id) for id in request.form.getlist("selected_jobs")]
        for job_id in selected_job_ids:
            job = Info.query.get(job_id)
            if job:
                job.is_approved = True # Approve selected jobs
        db.session.commit()

    job_posts = Info.query.all()
    return render_template('admin_panel.html', job_posts = job_posts)


# Route for employer login
@app.route('/employer/login', methods=["POST", "GET"])
def employer_login():
    session['admin_logged_in'] = False  # Clear admin login state
    session['employer_logged_in'] = False
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        employer = Employer.query.filter_by(username=username).first()

        if employer and employer.password == password:
            session['employer_logged_in'] = True
            session['employer_id'] = employer.id  # Store employer ID in the session
            print("Session:", session)  # Debugging: Check session variables
            return redirect(url_for('view_applications'))
        else:
            return render_template("employer_login.html", error="Invalid credentials. Try again.")
    return render_template('employer_login.html')

# Route for employers to view applications for their job posts
@app.route('/employer')
def view_applications():
    print("Session at /employer:", session)  # Debugging: Check session variables
    if not session.get('employer_logged_in'):
        return redirect(url_for('employer_login'))
    
    employer_id = session.get('employer_id') 
    employer_jobs = Info.query.filter_by(employer_id=employer_id).all()
    
    # Fetch applications for jobs posted by the employer
    job_ids = [job.id for job in employer_jobs]
    applications = Application.query.filter(Application.job_id.in_(job_ids)).all()
    
    return render_template("employer.html", applications=applications)


# Route for employer signup
@app.route('/employer/signup', methods=["POST", "GET"])
def employer_signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        # Check if username already exists
        existing_employer = Employer.query.filter_by(username=username).first()
        if existing_employer:
            return render_template("employer_signup.html", error="Username already taken. Please choose another.")

        # Create a new employer and add to database
        new_employer = Employer(username=username, password=password)
        db.session.add(new_employer)
        db.session.commit()
        
        return redirect(url_for('employer_login'))
    
    return render_template("employer_signup.html")


# Initialize the database
def init_db():
    with app.app_context():
        db.create_all()

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)