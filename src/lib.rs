use reqwest;
use url::Url;
use std::os::raw::c_char;
use std::ffi::CStr;
use std::ffi::CString;
use serde_json as json;
use serde_pickle as pickle;
use std::collections::BTreeMap;
use std::env;
use std::fs;
use std::fs::File;
use std::io::{stdin, stdout, Read};
use std::process::exit;

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
pub extern "C" fn dict_pass() -> i64 {
    let reader: Box<Read> = Box::new(File::open("filename.pickle").unwrap());
    let decoded: json::Value = pickle::from_reader(reader).unwrap();
    //println!("{:#?}", decoded["url"]);
    let temp = decoded["url"].as_str().expect("Not a valid UTF-8 string");
    let url = Url::parse(&temp).unwrap();
    let resp = reqwest::get(url).unwrap().text().unwrap();
    let mut map = BTreeMap::new();
    map.insert("response".to_string(), resp);
    let serialized = serde_pickle::to_vec(&map, true).unwrap();
    fs::write("a.pickle", serialized).expect("Unable to write file");
    
    //println!("{:#?}", resp);
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
