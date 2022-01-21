# requests imported to get JSON data
import requests
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker


# This class returns blog data from SQL database
class Post:

    def __init__(self):
        engine = db.create_engine('sqlite:///posts.db')
        connection = engine.connect()
        metadata = db.MetaData()
        posts = db.Table('blog_post', metadata, autoload=True, autoload_with=engine)

        Session = sessionmaker(bind=engine)
        session = Session()

        self.post_list = []

        for post in session.query(posts).all():
            self.post_list.append({'id': post[0],
                                   'body': post[4],
                                   'title': post[1],
                                   'subtitle': post[2],
                                   'date': post[3],
                                   'author': post[5],
                                   'img_url': post[6]
                                   })

    # This function returns the JSON dictionary element containing id, body, title and subtitle keys from a list of
    # dictionaries
    def post_data(self, post_id):
        return self.post_list[post_id]

    # Returns the whole post list of dictionaries
    def all_posts(self):
        return self.post_list
