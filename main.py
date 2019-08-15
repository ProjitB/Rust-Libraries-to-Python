import pickle
from cffi import FFI
import tempfile

# Rust Function Interface Definitions
ffi = FFI()
ffi.cdef("""
   typedef struct {const char* response;} ReqStruct;
   typedef struct {int length; const char* response;} RetStruct;
   void dict_pass(const char*, const char*);
   RetStruct general_pass(const char*);
   RetStruct rust_post(const char*);
""") 
LIB = ffi.dlopen("target/release/librequest_export.dylib")


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
    function(to_string(inp_file.name), to_string(out_file.name))
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


def test_old():
    data = {'url': 'https://google.com'}
    output = old_function_call(LIB.dict_pass, data)
    print(output)


def test_function_call():
    data = {'url': 'https://postman-echo.com/post', 'data': {"hello": "world"}}
    output = eval(function_call(LIB.rust_post, data))
    print(type(output))
    print(output)
    print(output["args"])


if __name__ == '__main__':
    test_old()
    test_function_call()
