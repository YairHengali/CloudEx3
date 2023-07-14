import requests

def query_resolver(fileName:String):
  with open("query.txt", "r") as file:
    for line in file:
      response = requests.get(url, headers=headers, params=querystring)
