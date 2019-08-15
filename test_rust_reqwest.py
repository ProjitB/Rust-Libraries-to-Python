import time
start = time.time()
from main import function_call, LIB

data_post = {'url': 'https://postman-echo.com/post', 'data': {"hello": "world"}}

data_get = {'url': 'https://google.com'}

def rust_post():
    output = eval(function_call(LIB.rust_post, data_post))
    # print(output)

def rust_get():
    function_call(LIB.general_pass, data_get)

'''
Output for Post is:
{'args': {}, 'data': {'hello': 'world'}, 'files': {}, 'form': {}, 'headers': {'x-forwarded-proto': 'https', 'host': 'postman-echo.com', 'content-length': '17', 'accept': '*/*', 'accept-encoding': 'gzip', 'content-type': 'application/json', 'user-agent': 'reqwest/0.9.19', 'x-forwarded-port': '443'}, 'json': {'hello': 'world'}, 'url': 'https://postman-echo.com/post'}
'''

request_start = time.time()
for i in range(10):
    # rust_post()
    rust_get()

end = time.time()
# print("(Rust) Time taken for import + 10 requests: {}".format(end-start))
# print("(Rust) Time taken for just the 10 requests: {}".format(end-request_start))
