from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

app = Flask(__name__, template_folder="templates")

@app.route("/home")
def home():
    return render_template("homepage.html")

@app.route("/applications")
def test():
    return render_template("applicationPage.html")

@app.route("/postJobs", methods=["POST", "GET"])
def jobPostingPage():
    if request.method == "POST": 
        company_name = request.form ["company_name"]
        return redirect(url_for('display', display=company_name)) 
    else:
        return render_template("postJobs.html")

@app.route("/<display>")
def display(display):
    return render_template("displayPage.html", display=display)

if __name__ == "__main__":
    app.run(debug=True)