use reqwest;
use url::Url;
use std::os::raw::c_char;
use std::ffi::CStr;
use std::ffi::CString;
use serde_json as json;
use serde_pickle as pickle;
use std::collections::BTreeMap;
use std::fs;
use std::fs::File;
use std::io::{Read};
use std::mem;

#[repr(C)]
pub struct ReqStruct {
    response: *const c_char
}

#[repr(C)]
pub struct RetStruct {
    length: i64,
    response: *mut u8
}


#[no_mangle]
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
