import pickle
from cffi import FFI
from ctypes import c_char_p, cdll, cast
import tempfile

ffi = FFI()
ffi.cdef("""
   typedef struct {const char* response;} ReqStruct;
   ReqStruct rust_get(const char*);
   void dict_pass(const char*, const char*);
""")

C = ffi.dlopen("target/release/librequest_export.dylib")

def to_string(text):
    return ffi.new("char[]", text.encode("utf-8"))

def read_string(bytes_string):
    strf = b''
    counter = 0
    while True:
        if bytes_string[counter] == b'\0':
            break
        strf += bytes_string[counter]
        counter += 1
    return strf.decode()

# a = C.rust_get(to_string("https://google.com"))
# output = read_string(a.response)

def function_call(function, data):
    inp_file = tempfile.NamedTemporaryFile()
    out_file = tempfile.NamedTemporaryFile()
    with open(inp_file.name, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    function(to_string(inp_file.name), to_string(out_file.name))
    with open(out_file.name, 'rb') as f:
        return pickle.load(f)

data = {'url': 'https://google.com'}
output = function_call(C.dict_pass, data)
print(output)
