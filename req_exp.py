import pickle
from cffi import FFI
from ctypes import c_char_p, cdll, cast

ffi = FFI()
ffi.cdef("""
   typedef struct {const char* response;} ReqStruct;
   ReqStruct rust_get(const char*);
   int dict_pass();
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

with open('filename.pickle', 'wb') as handle:
    pickle.dump(to_pass, handle, protocol=pickle.HIGHEST_PROTOCOL)

C.dict_pass()
