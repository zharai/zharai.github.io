from flask import Flask, render_template, redirect, url_for, request, session
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta


app = Flask(__name__, template_folder="templates")
app.secret_key = "hi3u4h"
app.permanent_session_lifetime = timedelta(days=30)

@app.route("/home")
def home():
    return render_template("homepage.html")

@app.route("/applications")
def applications():
    print("Rendering applicationPage.html")
    return render_template("applicationPage.html")

@app.route("/postJobs", methods=["POST", "GET"])
def postJobs():
    if request.method == "POST": 
        session.permanent = True
        display = request.form["company_name"]

        session["display"] = display

        return redirect(url_for("display")) 
    else:
        return render_template("postJobs.html")

@app.route("/display")
def display():
    if "display" in session:
        display = session["display"]
        return f"<h1>{display}</h1>"
    else:
        return redirect(url_for("postJobs"))

if __name__ == "__main__":

    app.run(debug=True)