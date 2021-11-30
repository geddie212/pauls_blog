#requests imported to get JSON data
import requests

#This class returns blog data from an API endpoint
class Post:

    def __init__(self):
        # NPOINT.IO allows you to store JSON data which you can access with their API
        # gets a response from the API endpoint
        self.response = requests.get('https://api.npoint.io/e0158e9d8d4f31971bbb')
        # JSON data is stored in post variable
        self.post = self.response.json()

    #This function returns the JSON dictionary element containing id, body, title and subtitle keys from a list of dictionaries
    def post_data(self, post_id):
        print(type(post_id))
        return self.post[post_id]

    #Returns the whole post list of dictionaries
    def all_posts(self):
        return self.post