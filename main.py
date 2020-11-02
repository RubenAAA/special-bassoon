import pandas as pd
import datetime
import os
from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user
from flask_login import logout_user, login_required
from forms import RegistrationForm, LoginForm, PostForm, PPForm

app = Flask(__name__)

app.config["SECRET_KEY"] = "enter-a-hard-to-guess-string"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(60), nullable=False)
    lname = db.Column(db.String(60), nullable=False)
    uname = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    profilepic = db.Column(db.String(100), default=None)
    posts = db.relationship("Posts", backref="op", lazy=True)

    def __repr__(self):
        return f"User(id: '{self.id}', fname: '{self.fname}', " +\
               f" lname: '{self.lname}', uname: '{self.uname}')" +\
               f" password: '{self.password}', email: '{self.email}')"


class Posts(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(140), nullable=False)
    length = db.Column(db.String(10), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False,
                             default=datetime.datetime.now)
    imgn = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"Product(id: '{self.id}', conrent: '{self.content}', " +\
               f" length: '{self.length}', " +\
               f" date_created: '{self.date_created}', " +\
               f" imgn: '{self.imgn}', op: '{self.user_id}')"


@app.route("/")
def index():
    if current_user.is_authenticated:
        posts = get_posts()
        return render_template("index.html", posts_df=posts, User=User)
    else:
        return redirect(url_for("login"))


@app.route("/profile/<username>")
def profilepage(username):
    if User.query.filter_by(uname=username).count() > 0:
        if current_user.is_authenticated:
            my_user = User.query.filter_by(uname=username).first()
            fullname = my_user.fname + " " + my_user.lname
            return render_template("profile.html", fullname=fullname,
                                   username=username, User=User)
        else:
            return redirect(url_for("login"))
    else:
        return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()

    if form.validate_on_submit():
        registration_worked = register_user(form)
        if registration_worked:
            return redirect(url_for("login"))

    return render_template("register.html", form=form, User=User)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()

    if form.validate_on_submit():
        if is_login_successful(form):
            return redirect(url_for("index"))
        else:
            if User.query.filter_by(email=form.email.data).count() > 0:
                flash("Login unsuccessful, please check your credentials and try again")
            else:
                return redirect(url_for("register"))
    return render_template("login.html", form=form, User=User)


@app.route("/change-profile", methods=["GET", "POST"])
def changeprof():
    if current_user.is_authenticated:

        form = PPForm()

        if form.validate_on_submit():
            if form.profilepic.data:
                assets_dir = "static"
                d = form.profilepic.data
                filename = d.filename
                imgpath = os.path.join(assets_dir, filename)
                d.save(imgpath)
            else:
                filename = User.query.filter_by(id=current_user.id).first().profilepic
            if form.profilename.data:
                newname = form.profilename.data
            else:
                newname = User.query.filter_by(id=current_user.id).first().uname
            change_prof(form, filename, newname)
            return redirect(url_for("index"))

        return render_template("changeprof.html", form=form, User=User)
    else:
        return redirect(url_for("login"))


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if current_user.is_authenticated:

        form = PostForm()

        if form.validate_on_submit():
            if form.user_file.data:
                assets_dir = "static"
                d = form.user_file.data
                filename = d.filename
                imgpath = os.path.join(assets_dir, filename)
                d.save(imgpath)
            else:
                filename = None
            add_post(form, filename)
            return redirect(url_for("index"))
        else:
            flash("Post length over the 140 characters limit.")

        return render_template("upload.html", form=form, User=User)
    else:
        return redirect(url_for("login"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


###############################################################################
# Helper functions
###############################################################################

def register_user(form_data):
    def email_already_taken(email):
        if User.query.filter_by(email=email).count() > 0:
            return True
        else:
            return False

    def uname_already_taken(uname):
        if User.query.filter_by(uname=uname).count() > 0:
            return True
        else:
            return False
    if email_already_taken(form_data.email.data):
        flash("That email is already taken!")
        return False
    if uname_already_taken(form_data.uname.data):
        flash("That username is already taken!")
        return False

    hashed_password = bcrypt.generate_password_hash(form_data.password.data)
    user = User(fname=form_data.fname.data,
                lname=form_data.lname.data,
                uname=form_data.uname.data,
                email=form_data.email.data,
                password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return True


def is_login_successful(form_data):

    email = form_data.email.data
    password = form_data.password.data

    user = User.query.filter_by(email=email).first()

    if user is not None:
        if bcrypt.check_password_hash(user.password, password):
            login_user(user)

            return True
    else:
        return False


def add_post(form_data, filename):
    length = len(form_data.content.data)
    post = Posts(content=form_data.content.data,
                 length=length,
                 imgn=filename,
                 user_id=current_user.id)
    db.session.add(post)
    db.session.commit()


def change_prof(form_data, filename, newname):
    user = User(id=User.query.filter_by(id=current_user.id).first().id,
                fname=User.query.filter_by(id=current_user.id).first().fname,
                lname=User.query.filter_by(id=current_user.id).first().lname,
                uname=newname,
                email=User.query.filter_by(id=current_user.id).first().email,
                password=User.query.filter_by(id=current_user.id).first().password,
                profilepic=filename)
    User.query.filter_by(id=current_user.id).delete()
    db.session.add(user)
    db.session.commit()


def get_posts():
    df = pd.read_sql(Posts.query.statement, db.session.bind)
    df = df.sort_index(ascending=False)
    return df


if __name__ == "__main__":
    app.run(debug=True)
