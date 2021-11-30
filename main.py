from flask import Flask, render_template
import post

app = Flask(__name__)


# index page route
@app.route('/')
def home():
    # instance of post class
    blog_posts = post.Post()
    # list of all the dictionaries extracted from post class containing, id, title, subtitle, body
    blog_posts = blog_posts.all_posts()
    # sends html template and uses jinja in HTML to show the posts in the blog_posts list of dictionaries
    return render_template("index.html", posts=blog_posts)


@app.route('/blog/<num>')
def get_blog(num):
    # creates instance of post class
    poster = post.Post()
    # this method extracts the dictionary from the num input in URL which contains the post data
    poster = poster.post_data(int(num) - 1)
    # variables to be used by Jinja from the post dictionary
    title = poster['title']
    subtitle = poster['subtitle']
    body = poster['body']
    # html post using the jinja inputs from the dictionary
    return render_template("post.html", title=title, subtitle=subtitle, body=body)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact')
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)
