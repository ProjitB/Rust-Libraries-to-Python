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

#### Dict Pass
```
pub extern "C" fn dict_pass(input_temp_file: *const c_char, output_temp_file: *const c_char) {
    // File to read and write to
    let input_filename = unsafe { CStr::from_ptr(input_temp_file).to_str().expect("Not a valid UTF-8 string") };
    let output_filename = unsafe { CStr::from_ptr(output_temp_file).to_str().expect("Not a valid UTF-8 string") };

    //Processing
    let reader: Box<Read> = Box::new(File::open(input_filename).unwrap());
    let decoded: json::Value = pickle::from_reader(reader).unwrap();
    let mut map = BTreeMap::new();

    //Needs to be implemented
    let url = Url::parse(&decoded["url"].as_str().expect("Not a valid UTF-8 string")).unwrap();
    let resp = reqwest::get(url).unwrap().text().unwrap();
    map.insert("response".to_string(), resp);


    //Processing
    let serialized = serde_pickle::to_vec(&map, true).unwrap();
    fs::write(output_filename, serialized).expect("Unable to write file");
}
```
This function is compatible with the old_function_call python function.
To create another function like this, all that needs to be done is to copy the above except for the "Needs to be implemented" part of the code. The function name should also be changed to whatever you want.
The File read write acquires the file names of the input and output files. The input file will read the pickled data passed from python, while the output will send pickled data back.
In the processing section, we decode the pickled data. All variables passed in the dictionary from python are now accessable via &decoded[variable]. Based on the type required for the rust function that you wish to invoke, you may need to do some type manipulations.
Insert into map all the responses you wish to collect from the rust function and it will be sent back to the python script. (Look at the needs to be implemented part for an example of how to do this)



#### General Pass
```
#[no_mangle]
pub extern "C" fn general_pass(input_temp_file: *const c_char) -> RetStruct {
    // File to read and write to
    let input_filename = unsafe { CStr::from_ptr(input_temp_file).to_str().expect("Not a valid UTF-8 string") };

    //Processing
    let reader: Box<Read> = Box::new(File::open(input_filename).unwrap());
    let decoded: json::Value = pickle::from_reader(reader).unwrap();
    let mut map = BTreeMap::new();

    //Needs to be implemented
    // Implementing reqwest get in this case
    let url = Url::parse(&decoded["url"].as_str().expect("Not a valid UTF-8 string")).unwrap();
    let resp = reqwest::get(url).unwrap().text().unwrap();
    map.insert("response".to_string(), resp);


    //Processing
    let mut serialized = serde_pickle::to_vec(&map, true).unwrap();
    let x = serialized.len();
    let p = serialized.as_mut_ptr();
    mem::forget(serialized);
    RetStruct{
    length: x as i64,
    response: p
    }

}
```
This function is compatible with function_call on the python end
General pass is very similar to the dict pass except for the way values are returned. The serialized data is sent back in the form of a struct, but you don't need to worry about this.
Just the "Needs to be implemented" part needs to be filled out, with map being populated with the results that you want to send back to python.

#### Example: rust_post
```
#[no_mangle]
pub extern "C" fn rust_post(input_temp_file: *const c_char) -> RetStruct{
    // File to read and write to
    let input_filename = unsafe { CStr::from_ptr(input_temp_file).to_str().expect("Not a valid UTF-8 string") };

    //Processing
    let reader: Box<Read> = Box::new(File::open(input_filename).unwrap());
    let decoded: json::Value = pickle::from_reader(reader).unwrap();
    let mut map = BTreeMap::new();

    //To Implement
    let data = &decoded["data"];
    let url = Url::parse(&decoded["url"].as_str().expect("Not a valid UTF-8 string")).unwrap();
    let client = reqwest::Client::new();
    let mut resp = client.post(url)
        .json(&data)
        .send().unwrap();
    map.insert("response".to_string(), resp.text().unwrap());

    //Processing
    let mut serialized = serde_pickle::to_vec(&map, true).unwrap();
    let x = serialized.len();
    let p = serialized.as_mut_ptr();
    mem::forget(serialized);
    RetStruct{
    length: x as i64,
    response: p
    }
}
```
Using the framework of general_pass, we now port reqwest::post to python. Note that we receive a data parameter as well as a url parameter which must be passed from the python end. We then insert the response that we get back into the map, and it is sent back to python :). To see how it is invoked on the python end, look at the function test_function_call() in main.py

#### Some Performance Stats
```
benchmarking python3 test_rust_reqwest.py
time                 4.015 s    (1.627 s .. 6.019 s)
                     0.960 R²   (0.858 R² .. 1.000 R²)
mean                 4.271 s    (3.997 s .. 4.544 s)
std dev              346.8 ms   (161.4 ms .. 445.1 ms)
variance introduced by outliers: 21% (moderately inflated)

--------------------------
benchmarking python3 test_python_requests.py
time                 4.322 s    (3.639 s .. 5.580 s)
                     0.990 R²   (0.978 R² .. 1.000 R²)
mean                 4.009 s    (3.898 s .. 4.203 s)
std dev              189.0 ms   (45.55 ms .. 249.4 ms)
variance introduced by outliers: 19% (moderately inflated)
```

There are some speed improvements on benchmarking some of the performance(used get request to http://google.com for the benchmark)
These may be more noticeable when only a few requests are made, as the import of the python requests library takes a few hundered milliseconds on average
However, this is a simple case, but this framework should generalize to allowing any rust library to be used, provided you create an interface as shown above. There can be benefits of both performance and access to another set of cool libaries from python as a result of this.

#### Disclaimer: I've left out some of the error handling that can be done on the rust side. Feel free to use this (terrible) code or modify it further
