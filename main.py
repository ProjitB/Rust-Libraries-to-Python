import pickle
from cffi import FFI
import tempfile

# Rust Function Interface Definitions
ffi = FFI()
ffi.cdef("""
   typedef struct {const char* response;} ReqStruct;
   typedef struct {int length; const char* response;} RetStruct;
   ReqStruct rust_get(const char*);
   RetStruct rust_post(const char*);
   void dict_pass(const char*, const char*);
   RetStruct general_pass(const char*);
""")

lib = ffi.dlopen("target/release/librequest_export.dylib")

def to_string(text):
    return ffi.new("char[]", text.encode("utf-8"))

def read_pickle_bytes(pointer, length):
    arr = b''
    for i in range(length):
        arr += pointer[i]
    return arr

def old_function_call(function, data):
    inp_file = tempfile.NamedTemporaryFile()
    out_file = tempfile.NamedTemporaryFile()
    with open(inp_file.name, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    val = function(to_string(inp_file.name), to_string(out_file.name))
    with open(out_file.name, 'rb') as handle:
        obj = pickle.load(handle)
        return obj


def function_call(function, data):
    inp_file = tempfile.NamedTemporaryFile()
    with open(inp_file.name, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    val = function(to_string(inp_file.name))
    obj = pickle.loads(read_pickle_bytes(val.response, val.length))
    return obj['response']

# data = {'url': 'https://postman-echo.com/post', 'data':{"hello": "world"}}
# output = eval(function_call(lib.rust_post, data))
# print(type(output))
# print(output)
# print(output["args"])
data = {'url': 'https://google.com'}
output = old_function_call(lib.dict_pass, data)
print(output)
