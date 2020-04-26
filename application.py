from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


engine = create_engine("postgresql://egehurturk:egehurturk@localhost:5432/sessiontest")
db = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if checkLogin(False) == False:
        return redirect(url_for('hello'))
    if request.form.get("command") == "login" :
        password = request.form.get("password")
        
        user = db.execute("SELECT * FROM users WHERE userpassword=:password", {"password":password}).fetchall()
        if len(user) == 0:
            message = "incorrect password. Try again:"
        else:
            session["isLoggedIn"] = True
            session["loggedInUser"] = user[0]
            return redirect(url_for('hello'))

    return render_template("login.html", message=message)

@app.route("/dashboard")
def hello():
    if checkLogin(True) == False:
        return redirect(url_for('hello'))
    loggedInUser = session.get("loggedInUser")
    return render_template("dashboard.html", loggedInUser=loggedInUser)


@app.route("/logout")
def logout():
    if checkLogin(True) == False:
        return redirect(url_for('hello'))
    session["isLoggedIn"] = None
    session["loggedInUser"] = None
    return redirect(url_for('login'))


@app.route("/signup", methods=["POST", "GET"])
def signup():
    message = ""
    if request.form.get("command") == "signup":
        userpassword = request.form.get("password")
        name = request.form.get("name")
        email = request.form.get("email")
        
        usercount = db.execute("SELECT * FROM users WHERE userpassword=:userpassword", {"userpassword":userpassword}).rowcount
        if usercount > 0:
            message = "You already have an account." 
        else:
            newuser = db.execute("INSERT INTO users (userpassword, name, email) VALUES (:userpassword, :name, :email)", {"userpassword": userpassword, "name": name, "email":email})
            db.commit()
            message = "You have been registered"
            return redirect(url_for('login'))
    return render_template("signup.html", message=message)


@app.route("/resetpassword", methods=["POST", "GET"])
def reset():
    message = ""
    if request.form.get("command") == "reset":
        email = request.form.get("email")
        checkEmail = db.execute("SELECT * FROM users WHERE email=:email", {"email": email}).rowcount
        if checkEmail == 0:
            message="Please enter a valid email."
        else:
            showPassword = db.execute("SELECT * FROM users WHERE email=:email", {"email":email}).fetchall()
            message=f"Your password is {showPassword[0][1]}"

    return render_template("reset.html", message=message)


def checkLogin(isProtected):
    if isProtected == True:
        isLoggedIn = session.get("isLoggedIn")
        if isLoggedIn is None:
            return False
    else:
        isLoggedIn = session.get("isLoggedIn")
        if isLoggedIn is not None:
            return False
    

