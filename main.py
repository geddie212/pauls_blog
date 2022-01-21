from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import post_db
from datetime import date

app = Flask(__name__)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# BOOTSTRAP SETUP
bootstrap = Bootstrap(app)

# SECRET KEY SETUP
app.config["SECRET_KEY"] = '571ebf8e13ca209536c29be68d435c00'

# CK EDITOR SETUP
ckeditor = CKEditor(app)

# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.String, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField('body')
    submit = SubmitField("Submit Post")


@app.route('/')
def home():
    # instance of post class
    blog_posts = post_db.Post()
    # list of all the dictionaries extracted from post class containing, id, title, subtitle, body
    blog_posts = blog_posts.all_posts()
    # sends html template and uses jinja in HTML to show the posts in the blog_posts list of dictionaries
    return render_template("index.html", posts=blog_posts)


@app.route('/blog/<num>')
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
    # html post using the jinja inputs from the dictionary
    return render_template("post.html", title=title, subtitle=subtitle, body=body, date=date, author=author,
                           img_url=img_url, post_id=num)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/new_post', methods=['GET', 'POST'])
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
        return render_template("index.html", posts=blog_posts)
    else:
        return render_template("make_post.html", form=form, heading=h1_text)


@app.route('/edit_post/<post_id>', methods=['GET', 'POST'])
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
        return render_template("index.html", posts=blog_posts)
    else:
        return render_template('make_post.html', heading=h1_text, form=form)

@app.route('/delete_post/<post_id>')
def delete_post(post_id):
    post_data = BlogPost.query.filter_by(id=post_id).delete()
    db.session.commit()
    # instance of post class
    blog_posts = post_db.Post()
    # list of all the dictionaries extracted from post class containing, id, title, subtitle, body
    blog_posts = blog_posts.all_posts()
    # sends html template and uses jinja in HTML to show the posts in the blog_posts list of dictionaries
    return render_template("index.html", posts=blog_posts)


if __name__ == "__main__":
    app.run(debug=True)
