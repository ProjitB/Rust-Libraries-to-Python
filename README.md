# Guide to Using Rust Libaries from Python
## Author: Projit Bandyopadhyay

 This repository aims to show how to port some of the functionality from the Rust reqwest library to Python.
 The Motivation for this is the high import time for the Python Requests library (Run: time python3 -c "import requests")
 Functionality / Performance in some libraries of Rust may be higher than those of Python. Here, I try to generalize the porting of some function from these libraries, to be easily called from within Python.

#### Disclaimer: I don't know Rust

#### File Structure:

main.py 

Cargo.toml 

src

└── lib.rs

 
