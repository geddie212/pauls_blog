import main

class BlogComment:

    def __init__(self, post_id):
        self.post_id = post_id
        self.comment_list = []
        post_comments = main.Comment.query.filter_by(post_id=self.post_id).all()
        # print(post_comments[0].author.name)
        for comment in post_comments:
            self.comment_list.append(
                {
                    'comment': comment.text,
                    'author': comment.author.name
                }
            )


    def get_comments(self):
        return self.comment_list

# def __init__(self):
#     self.posts = []
#     SQL_post_list = main.BlogPost.query.all()
#     for post in SQL_post_list:
#         self.posts.append(
#             {
#                 'id': post.id,
#                 'title': post.title,
#                 'subtitle': post.subtitle,
#                 'author': post.author,
#                 'date': post.date,
#                 'body': post.body,
#                 'author_id': post.author_id,
#                 'img_url': post.img_url
#             }
#         )
#
#
# def all_posts(self):
#     return self.posts
#
#
# def post_data(self, post_id):
#     return self.posts[post_id]
#
