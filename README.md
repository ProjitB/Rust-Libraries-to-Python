# Guide to Using Rust Libraries from Python3
#### Author: Projit Bandyopadhyay

###Aim:
    - Show how to port some of the functionality from the Rust reqwest library to Python.
    - Show how to pass data between Rust and Python through cffi

###Motivation:
    - High import time for the Python Requests library (Run: time python3 -c "import requests")
    - Functionality / Performance in some libraries(or functions) of Rust may be higher than those of Python.

Here, I try to generalize the porting of some functions from Rust libraries, to be easily integrated with Python scripts.

#### Disclaimer: I don't know Rust

#### File Structure:
```
main.py
Cargo.toml
src
└── lib.rs
```




