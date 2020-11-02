from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField
from flask_wtf import Form


class RegistrationForm(FlaskForm):
    fname = StringField("First Name", validators=[DataRequired()])
    lname = StringField("Last Name", validators=[DataRequired()])
    uname = StringField("User Name", validators=[DataRequired()])
    email = StringField("email", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    submit_button = SubmitField("Submit")


class LoginForm(FlaskForm):
    email = StringField("email", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    submit_button = SubmitField("Submit")


class PostForm(Form):
    user_file = FileField("Image for your post")
    content = StringField("Type your post", validators=[DataRequired(),
                                                        Length(max=140,
                                                               message="""Post
                                                          is over 140
                                                          characters""")])
    submit_button = SubmitField("Submit")


class PPForm(Form):
    profilepic = FileField("Upload your profile picture")
    profilename = StringField("Type your new username")
    submit_button = SubmitField("Submit")
