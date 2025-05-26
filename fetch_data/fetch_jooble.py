import http.client
from dotenv import load_dotenv
import os

load_dotenv()

host = 'jooble.org'
key = os.getenv("JOOBLE_API_KEY")

connection = http.client.HTTPSConnection(host)
#request headers
headers = {"Content-type": "application/json"}
#json query
body = '{ "keywords": "Data", "location": "Paris"}'
connection.request('POST','/api/' + key, body, headers)
response = connection.getresponse()
print(response.status, response.reason)
print(response.read())