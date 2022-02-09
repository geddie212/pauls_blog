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
