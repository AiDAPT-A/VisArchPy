"""
Test for metadata pakcage
"""

import pytest
import os
import visarchpy.metadata as metadata
import warnings

@pytest.fixture(scope="module")
def root_path():
    return './data'

@pytest.fixture(scope="module")
def file_path():
    return 'multi-image-caption.pdf'


def test_extract_mods_metadata():
    """Test extract_mods_metadata function"""

    results = metadata.extract_mods_metadata("tests/data/sample-mods.xml")
    with pytest.warns(UserWarning):
        warnings.warn("No identifiers found in MODS file", UserWarning)

    assert isinstance(results, dict)



class TestFilePathClass:
    """ tests for the FilePath class"""

    def test_init(self, root_path, file_path):
        """
        test the init method
        """
        path = metadata.FilePath(root_path, file_path)
        assert path.root_path == root_path
        assert path.file_path == file_path

    def test_post_init(self):
        """
        test the post_init method, which check the data types 
        of root and file pathes
        """
        with pytest.raises(TypeError):
            metadata.FilePath(1000, 'file_path')
     
        with pytest.raises(TypeError):
            metadata.FilePath('root_path', 1000)

    def test_update_root_path(self, root_path, file_path):
        """
        test the update_root_path method
        """
        _path = metadata.FilePath(root_path, file_path)
        _path.update_root_path('new_root_path')
        assert _path.root_path == 'new_root_path'

    def test_full_path(self, root_path, file_path):
        """
        test the full_path method
        """
        _path = metadata.FilePath(root_path, file_path)
        assert _path.full_path() == str(os.path.join(root_path, file_path))


class TestDocumentClass:
    """test for the Document class"""

    def test_location_full_path(self, root_path, file_path):
        """
        test full path can be generated from the location
        """
        _path = metadata.FilePath(root_path, file_path)
        doc = metadata.Document(_path)
        assert doc.location.full_path() == str(os.path.join(root_path, file_path))
   

