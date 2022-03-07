import os
from flask import Flask, render_template, redirect, url_for, request, flash, abort, g
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import post_db
import post_comment
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from sqlalchemy.ext.declarative import declarative_base
from flask_gravatar import Gravatar

app = Flask(__name__)

# CONNECT TO DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://ceaugjvnkjutvo:fa8a28740a2a8996ece52bcabfafd2b0a971f1874e72fb045f990d90c7df33f4@ec2-44-192-245-97.compute-1.amazonaws.com:5432/d3qpa3ur0epea5'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)

# BOOTSTRAP SETUP
bootstrap = Bootstrap(app)

# SECRET KEY SETUP
app.config["SECRET_KEY"] = '571ebf8e13ca209536c29be68d435c00'

# CK EDITOR SETUP
ckeditor = CKEditor(app)

Base = declarative_base()


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String())
    name = db.Column(db.String(100))

    # one to many relationship where the comment is assigned to the User
    comments = relationship("Comment", back_populates="author")

    # This will act like a List of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author")


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object, the "posts" refers to the posts property in the User class.
    author = relationship("User", back_populates="posts")

    # creates relationship to Comments table
    comments = relationship("Comment", back_populates="parent_post")

    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(), nullable=False)


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)

    # foreign key which maps the post to the User ID
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # back-populates the comments variable in User and User comments variable back to author
    author = relationship("User", back_populates="comments")

    # creates foreign key to map the comment to the post ID
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    # Creates reference to the BlogPost object, the comments property refers to comments property in BlogPost class
    parent_post = relationship("BlogPost", back_populates="comments")

    gravatar = Gravatar(app,
                        size=50,
                        rating='x',
                        default='retro',
                        force_default=False,
                        force_lower=False,
                        use_ssl=False,
                        base_url=None)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# WTForm Create Post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField('body')
    submit = SubmitField("Submit Post")


class MakeCommentForm(FlaskForm):
    body = CKEditorField('comment', validators=[DataRequired()])
    submit = SubmitField('Submit Comment')


# WTForm Register Form
class RegisterForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    name = StringField("Your Name", validators=[DataRequired()])
    Register = SubmitField("Register")


# WTForm Login Form
class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    Login = SubmitField("Login")


def get_user_id():
    return current_user.get_id()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.get_id() != '1':
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def home():
    # instance of post class
    blog_posts = post_db.Post()
    # list of all the dictionaries extracted from post class containing, id, title, subtitle, body
    blog_posts = blog_posts.all_posts()
    # sends html template and uses jinja in HTML to show the posts in the blog_posts list of dictionaries
    return render_template("index.html", posts=blog_posts, user_id=get_user_id())


@app.route('/blog/<num>', methods=['GET', 'POST'])
def get_blog(num):
    # creates instance of post class
    poster = post_db.Post()
    # this method extracts the dictionary from the num input in URL which contains the post data
    poster = poster.post_data(int(num) - 1)
    # variables to be used by Jinja from the post dictionary
    title = poster['title']
    subtitle = poster['subtitle']
    body = poster['body']
    date = poster['date']
    author = poster['author']
    img_url = poster['img_url']


    blog_comments = post_comment.BlogComment(num).get_comments()

    form = MakeCommentForm()
    if request.method == 'POST':
        user_id = get_user_id()
        post_id = num
        comment_text = form.body.data
        new_comment = Comment(text=comment_text, author_id=user_id, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
        blog_comments = post_comment.BlogComment(num).get_comments()
        return render_template("post.html", title=title, subtitle=subtitle, body=body, date=date, author=author,
                               img_url=img_url, post_id=num, user_id=get_user_id(), form=form,
                               blog_comments=blog_comments)

    return render_template("post.html", title=title, subtitle=subtitle, body=body, date=date, author=author,
                           img_url=img_url, post_id=num, user_id=get_user_id(), form=form, blog_comments=blog_comments)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/new_post', methods=['GET', 'POST'])
@admin_only
def new_post():
    form = CreatePostForm()
    h1_text = 'New Post'
    if request.method == 'POST':
        title = form.title.data
        subtitle = form.subtitle.data
        today_date = date.today().strftime("%d/%m/%Y")
        body = form.body.data
        author = User.query.filter_by(id=int(get_user_id())).all()[0]
        img_url = form.img_url.data
        new_post = BlogPost(title=title, subtitle=subtitle, date=today_date, body=body, author=author, img_url=img_url)
        db.session.add(new_post)
        db.session.commit()

        blog_posts = post_db.Post()
        blog_posts = blog_posts.all_posts()
        # sends html template and uses jinja in HTML to show the posts in the blog_posts list of dictionaries
        return render_template("index.html", posts=blog_posts, user_id=get_user_id())
    else:
        return render_template("make_post.html", form=form, heading=h1_text)


@app.route('/edit_post/<post_id>', methods=['GET', 'POST'])
@admin_only
def edit_post(post_id):
    h1_text = 'Edit Post'
    post_data = BlogPost.query.filter_by(id=post_id).first()
    print(post_data.title)
    form = CreatePostForm(
        title=post_data.title,
        subtitle=post_data.subtitle,
        img_url=post_data.img_url,
        author=post_data.author,
        body=post_data.body
    )
    today_date = date.today().strftime("%d/%m/%Y")
    if request.method == 'POST':
        post_data.title = form.title.data
        post_data.subtitle = form.subtitle.data
        post_data.img_url = form.img_url.data
        post_data.author = form.author.data
        post_data.body = form.body.data
        db.session.commit()
        # instance of post class
        blog_posts = post_db.Post()
        # list of all the dictionaries extracted from post class containing, id, title, subtitle, body
        blog_posts = blog_posts.all_posts()
        # sends html template and uses jinja in HTML to show the posts in the blog_posts list of dictionaries
        return render_template("index.html", posts=blog_posts, user_id=get_user_id())
    else:
        return render_template('make_post.html', heading=h1_text, form=form)


@app.route('/delete_post/<post_id>')
@admin_only
def delete_post(post_id):
    post_data = BlogPost.query.filter_by(id=post_id).delete()
    db.session.commit()
    # instance of post class
    blog_posts = post_db.Post()
    # list of all the dictionaries extracted from post class containing, id, title, subtitle, body
    blog_posts = blog_posts.all_posts()
    # sends html template and uses jinja in HTML to show the posts in the blog_posts list of dictionaries
    return render_template("index.html", posts=blog_posts, user_id=get_user_id())


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        email = form.email.data
        password = form.password.data
        name = form.name.data

        user = User.query.filter_by(email=email).first()
        if user == None:
            password_hash = generate_password_hash(password=password, method='sha512', salt_length=10)
            new_user = User(email=email, password=password_hash, name=name)
            db.session.add(new_user)
            db.session.commit()

            blog_posts = post_db.Post()
            blog_posts = blog_posts.all_posts()
            return render_template("index.html", posts=blog_posts, user_id=get_user_id())
        else:
            flash('This user already exists, please try logging in')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    blog_posts = post_db.Post()
    blog_posts = blog_posts.all_posts()
    return render_template("index.html", posts=blog_posts, user_id=get_user_id())


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user == None:
            flash('user does not exist')
        else:
            password_hash_sql = user.password
            hash_check = check_password_hash(pwhash=password_hash_sql, password=password)
            if hash_check == True:
                login_user(user)
                blog_posts = post_db.Post()
                blog_posts = blog_posts.all_posts()
                return render_template("index.html", posts=blog_posts, user_id=get_user_id())
            else:
                flash('wrong password')

    return render_template('login.html', form=form)

if __name__ == "__main__":
    app.run(debug=True)
