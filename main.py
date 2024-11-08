from flask import Flask, render_template, redirect, url_for, request, session
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = 'tO$&!|0wkamvVia0?n$NqIRVWOG'

#database stuff??


@app.route("/home")
def home():
    return render_template("homepage.html")

@app.route("/applications")
def applications():
    print("Rendering applicationPage.html")
    return render_template("applicationPage.html")

@app.route("/postJobs", methods=["POST", "GET"])
def jobPostingPage():
    if request.method == "POST": 
        company_name = request.form ["company_name"]
        job_title = request.form ["job_title"]
        description = request.form["description"]
        return redirect(url_for('display', display=company_name + " is looking for a " + job_title + ". Details:(" + description + ")")) 
    else:
        return render_template("postJobs.html")

@app.route("/display/<display>")
def display(display):
    return render_template("displayPage.html", display=display)

@app.route('/admin', methods=["POST", "GET"])
def admin_login():
    session['admin_logged_in'] = False
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "admin" and password == "adminpass":  #erm..
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

if __name__ == "__main__":
    app.run(debug=True)