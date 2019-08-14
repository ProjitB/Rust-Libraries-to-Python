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
The data that needs to be passed to the function on the other side in the form of a dictionary.
The function then calls the Rust function, giving the two input and output file names as parameters, and then returns the result.
More information in function_call.


#### function_call
```
def function_call(function, data):
    inp_file = tempfile.NamedTemporaryFile()
    with open(inp_file.name, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    val = function(to_string(inp_file.name))
    obj = pickle.loads(read_pickle_bytes(val.response, val.length))
    return obj['response']
```
This is a bit cleaner implementation of old_function_call, removing the need of the output file as we pass the string back from the rust side
to_string function declares the String version of the file name in a C compatible format.
*Note* It is important to note that the struct returned has both a response and length parameter. This will be mentioned on the rust side of the implementation.
The response will be the response of your rust function, and whatever else you sent back along with that information from your rust interface

#### Example runs
```
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
```
*Note* you could return the values and use them instead of printing them.


#### Rust src/lib.rs

#### Structs
```
#[repr(C)]
pub struct RetStruct {
    length: i64,
    response: *mut u8
}
```
RetStruct is the mechanism by which we will send back information to Python. It contains a response object, which will be a pickle, and the length in bytes of that(so that it can be decoded on the python end).
*Note* Pickle is used as there is an implementation of it in both python (pickle) and rust (serde_pickle)


