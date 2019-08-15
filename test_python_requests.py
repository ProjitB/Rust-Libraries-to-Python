import time
start = time.time()
import requests

data = {'url': 'https://postman-echo.com/post', 'data': {"hello": "world"}}

def python_post():
    response = requests.post(data['url'], json=data['data'])
    # print(response.text)

def python_get():
    response = requests.get("https://google.com")

'''
Output for post is:
{"args":{},"data":{"hello":"world"},"files":{},"form":{},"headers":{"x-forwarded-proto":"https","host":"postman-echo.com","content-length":"18","accept":"*/*","accept-encoding":"gzip, deflate","content-type":"application/json","user-agent":"python-requests/2.19.1","x-forwarded-port":"443"},"json":{"hello":"world"},"url":"https://postman-echo.com/post"}
'''

request_start = time.time()
for i in range(10):
    # python_post()
    python_get()

end = time.time()
# print("(Python) Time taken for import + 10 requests: {}".format(end-start))
# print("(Python) Time taken for just the 10 requests: {}".format(end-request_start))
