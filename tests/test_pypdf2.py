"""
Unit test for the pypdf2.py script
"""
from tools import pypdf2
import pathlib

def test_create_output_dir():

    # Fixtures 
    base_path= './tests'
    dir_name= 'temp'
    full_path = pathlib.Path.joinpath(base_path, dir_name)

    # test if directory was created in the input path
    pypdf2.create_output_dir(base_path, dir_name)

    assert full_path.exists() == True

