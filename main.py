import pickle
from cffi import FFI
from ctypes import c_char_p, cdll, cast
import tempfile

ffi = FFI()
ffi.cdef("""
   typedef struct {const char* response;} ReqStruct;
   ReqStruct rust_get(const char*);
   typedef struct {int length; const char* response;} RetStruct;
   void dict_pass(const char*, const char*);
   RetStruct alt_dict_pass(const char*);
   void rust_post(const char*, const char*);
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

def read_pickle_bytes(pointer, length):
    arr = b''
    for i in range(length):
        arr += pointer[i]
    return arr


# a = C.rust_get(to_string("https://google.com"))
# output = read_string(a.response)

def function_call(function, data):
    inp_file = tempfile.NamedTemporaryFile()
    with open(inp_file.name, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    val = function(to_string(inp_file.name))
    obj  = pickle.loads(read_pickle_bytes(val.response, val.length))
    print(obj['response'])

def function_call_2(function, data):
    serialized = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
    text = ffi.new("char[]", serialized)
    val = function(text)
    obj  = pickle.loads(read_pickle_bytes(val.response, val.length))
    print(obj['response'])

data = {'url': 'https://google.com'}
output = function_call(C.alt_dict_pass, data)
