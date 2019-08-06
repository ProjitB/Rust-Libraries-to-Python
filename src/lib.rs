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

#[repr(C)]
pub struct ReqStruct {
    response: *const c_char
}


#[no_mangle]
pub extern "C" fn rust_get(link: *const c_char) -> ReqStruct {
    assert!(!link.is_null());
    let c_str = unsafe { CStr::from_ptr(link) };
    let string = c_str.to_str().expect("Not a valid UTF-8 string");
    let url = Url::parse(&string).unwrap();
    let resp = reqwest::get(url).unwrap().text().unwrap();

    //println!("{:#?}", resp);
    let c_to_print = CString::new(resp).expect("CString::new failed");
    ReqStruct {
        response: c_to_print.into_raw()
    }
}

#[no_mangle]
pub extern "C" fn dict_pass(input_temp_file: *const c_char, output_temp_file: *const c_char) -> i64 {
    // File to read and write to
    assert!(!input_temp_file.is_null());
    assert!(!output_temp_file.is_null());
    let temp_file_c_str = unsafe { CStr::from_ptr(input_temp_file) };
    let filename = temp_file_c_str.to_str().expect("Not a valid UTF-8 string");

    let output_temp_file_c_str = unsafe { CStr::from_ptr(output_temp_file) };
    let output_filename = output_temp_file_c_str.to_str().expect("Not a valid UTF-8 string");

    //println!("{:#?}", output_filename);
    let reader: Box<Read> = Box::new(File::open(filename).unwrap());
    let decoded: json::Value = pickle::from_reader(reader).unwrap();
    //println!("{:#?}", decoded["url"]);
    let temp = decoded["url"].as_str().expect("Not a valid UTF-8 string");
    let url = Url::parse(&temp).unwrap();
    let resp = reqwest::get(url).unwrap().text().unwrap();
    let mut map = BTreeMap::new();
    map.insert("response".to_string(), resp);
    let serialized = serde_pickle::to_vec(&map, true).unwrap();
    fs::write(output_filename, serialized).expect("Unable to write file");
    0
}
    // Some potentiall useful code for later
    //let mut map = BTreeMap::new();
    //map.insert("x".to_string(), 1.0);
    //map.insert("y".to_string(), 2.0);

    //// Serialize the map into a pickle stream.
    //// The second argument selects pickle version 3.
    //let serialized = serde_pickle::to_vec(&map, true).unwrap();
    //println!("{:#?}", serialized);

    //// Deserialize the pickle stream back into a map.
    //// Because we compare it to the original `map` below, Rust infers
    //// the type of `deserialized` and lets serde work its magic.
    //let deserialized = serde_pickle::from_slice(&serialized).unwrap();
    //println!("{:#?}", deserialized);
    //assert_eq!(map, deserialized);
