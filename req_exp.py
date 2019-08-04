from cffi import FFI
from ctypes import c_char_p, cdll, cast

ffi = FFI()
ffi.cdef("""
   typedef struct {const char* response;} ReqStruct;
   ReqStruct rust_get(const char*);
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

a = C.rust_get(to_string("https://google.com"))
output = read_string(a.response)

print("\n-----PYTHON START ----\n")
print(output)


