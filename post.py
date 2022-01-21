# requests imported to get JSON data
import requests
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

engine = db.create_engine('sqlite:///posts.db')
connection = engine.connect()
metadata = db.MetaData()
posts = db.Table('blog_post', metadata, autoload=True, autoload_with=engine)

Session = sessionmaker(bind=engine)
session = Session()

post_list = []

for post in session.query(posts).all():
    print(post)
    post_list.append({'id':post[0],
                      'body': post[4],
                      'title': post[1],
                      'subtitle': post[2]
    })

print(post_list)



# This class returns blog data from an API endpoint
class Post:

    def __init__(self):
        # NPOINT.IO allows you to store JSON data which you can access with their API
        # gets a response from the API endpoint
        self.response = requests.get('https://api.npoint.io/e0158e9d8d4f31971bbb')
        # JSON data is stored in post variable
        self.post = self.response.json()

    # This function returns the JSON dictionary element containing id, body, title and subtitle keys from a list of
    # dictionaries
    def post_data(self, post_id):
        print(type(post_id))
        return self.post[post_id]

    # Returns the whole post list of dictionaries
    def all_posts(self):
        return self.post
