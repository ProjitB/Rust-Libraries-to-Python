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

a = C.rust_get(to_string("https://google.com"))
print(a)
print(dir(a))
# pt = ffi.new("char[]", a.resp)
# print(pt)
