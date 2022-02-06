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
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from sqlalchemy.ext.declarative import declarative_base


app = Flask(__name__)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
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

# CONFIGURE TABLE
class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    children = relationship('BlogPost')

class BlogPost(db.Model):
    __tablename__ = 'BlogPost'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.String, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    parent_id = db.Column(db.Integer, ForeignKey(User.id))




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


@app.route('/blog/<num>')
def get_blog(num):
    # creates instance of post class
    poster = post_db.Post()
    # this method extracts the dictionary from the num input in URL which contains the post data
    poster = poster.post_data(int(num)-1)
    # variables to be used by Jinja from the post dictionary
    title = poster['title']
    subtitle = poster['subtitle']
    body = poster['body']
    date = poster['date']
    author = poster['author']
    img_url = poster['img_url']
    # html post using the jinja inputs from the dictionary
    return render_template("post.html", title=title, subtitle=subtitle, body=body, date=date, author=author,
                           img_url=img_url, post_id=num, user_id=get_user_id())


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
        author = form.author.data
        img_url = form.img_url.data
        new_post = BlogPost(title=title, subtitle=subtitle, date=today_date, body=body, author=author, img_url=img_url)
        db.session.add(new_post)
        db.session.commit()
        blog_posts = post_db.Post()
        # list of all the dictionaries extracted from post class containing, id, title, subtitle, body
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
