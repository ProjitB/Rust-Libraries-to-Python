import pickle
from cffi import FFI
from ctypes import c_char_p, cdll, cast
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

C = ffi.dlopen("target/release/librequest_export.dylib")

def to_string(text):
    return ffi.new("char[]", text.encode("utf-8"))

def read_pickle_bytes(pointer, length):
    arr = b''
    for i in range(length):
        arr += pointer[i]
    return arr

def function_call(function, data):
    inp_file = tempfile.NamedTemporaryFile()
    with open(inp_file.name, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    val = function(to_string(inp_file.name))
    obj  = pickle.loads(read_pickle_bytes(val.response, val.length))
    return obj['response']

data = {'url': 'https://postman-echo.com/post', 'data':{"hello": "world"}}
output = eval(function_call(C.rust_post, data))
print(type(output))
print(output)
print(output["args"])
