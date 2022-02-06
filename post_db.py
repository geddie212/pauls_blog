import main

class Post():

    def __init__(self):
        self.posts = []
        SQL_post_list = main.BlogPost.query.all()
        for post in SQL_post_list:
            self.posts.append(
                {
                    'id': post.id,
                    'title': post.title,
                    'subtitle': post.subtitle,
                    'author': post.author,
                    'date': post.date,
                    'body': post.body,
                    'parent_id': post.parent_id,
                    'img_url': post.img_url
                }
            )

    def all_posts(self):
        return self.posts

    def post_data(self, post_id):
        return self.posts[post_id]


#title
#subtitle
#author
#date
#body
#parent_id