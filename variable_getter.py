import requests

response = requests.get('https://api.heroku.com/apps/pauls-awesome-blog/config-vars')
print(response.status_code)