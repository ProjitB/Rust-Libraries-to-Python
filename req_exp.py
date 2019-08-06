import pickle
from cffi import FFI
from ctypes import c_char_p, cdll, cast
import tempfile

ffi = FFI()
ffi.cdef("""
   typedef struct {const char* response;} ReqStruct;
   ReqStruct rust_get(const char*);
   int dict_pass(const char*, const char*);
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

to_pass = {'url': 'https://google.com'}
inp_file = tempfile.NamedTemporaryFile()
out_file = tempfile.NamedTemporaryFile()
with open(inp_file.name, 'wb') as handle:
    pickle.dump(to_pass, handle, protocol=pickle.HIGHEST_PROTOCOL)
C.dict_pass(to_string(inp_file.name), to_string(out_file.name))
with open(out_file.name, 'rb') as f:
    a = pickle.load(f)
    print(a['response'])
