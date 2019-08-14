# Guide to Using Rust Libraries from Python3
#### Author: Projit Bandyopadhyay

### Aim:
    - Show how to port some of the functionality from the Rust reqwest library to Python.
    - Show how to pass data between Rust and Python through cffi

### Motivation:
    - High import time for the Python Requests library (Run: time python3 -c "import requests")
    - Functionality / Performance in some libraries(or functions) of Rust may be higher than those of Python.

Here, I try to generalize the porting of some functions from Rust libraries, to be easily integrated with Python scripts.

#### Disclaimer: I don't know Rust very well at all  :(

#### File Structure:
```
main.py
Cargo.toml
src
└── lib.rs
```

#### To build:
```
cargo build --release
```
*Note* This was done on OSX, so your linked library may be different on another platform. Change the path in main.py accordingly

### Contents

Multiple versions of my implementations of an interface for rust, callable from python.
I created two functions:
    - (Python) old_function_call -> (Rust) dict_pass

    - (Python) function_call -> (Rust) general_pass

To these you must pass which function, from the cffi interface you want to use, and the data, as a dictionary.
On the other side of things, in Rust, the function definition should be the same as dict_pass(if using old_function_call), or general_pass(if using function_call)

### Code Explanations:

#### Python <main.py>

#### Imports
```
import pickle
from cffi import FFI
import tempfile
```
cffi is used as an interface between Python and C.
As rust is compatible with C in many areas, it will be used here as well.

#### ffi cdef
```
ffi = FFI()
ffi.cdef("""
   typedef struct {const char* response;} ReqStruct;
   typedef struct {int length; const char* response;} RetStruct;
   void dict_pass(const char*, const char*);
   RetStruct general_pass(const char*);
   RetStruct rust_post(const char*);
""")
```
To be able to use functions from Rust, we need to write out their function definitions. (Kind of like a C header file?).
One thing you will notice is that the definitions are written in C, and slightly differ from the definitions(in their types) from the ones we write in Rust.
The aim of these declarations, is in a way, to find the closest compatabile type to those in the rust definitions.

#### LIB
```
LIB = ffi.dlopen("target/release/librequest_export.dylib")
```
This line may change based on the operating system you are running. In OSX, dylib (dynamic library) is generated from the Cargo.toml, however other formats may also be generated. (.so, etc..)
Change the path accordingly

#### old_function_call
```
def old_function_call(function, data):
    inp_file = tempfile.NamedTemporaryFile()
    out_file = tempfile.NamedTemporaryFile()
    with open(inp_file.name, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    function(to_string(inp_file.name), to_string(out_file.name))
    with open(out_file.name, 'rb') as handle:
        obj = pickle.load(handle)
        return obj
```
This function call creates two separate temporary files.
The data that needs to be passed to the function on the other side

