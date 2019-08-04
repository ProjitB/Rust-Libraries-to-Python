use reqwest;
use url::Url;
use std::os::raw::c_char;
use std::ffi::CStr;
use std::ffi::CString;

#[repr(C)]
pub struct ReqStruct {
    // response: [u8; 10]
    // response: *mut c_char
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

