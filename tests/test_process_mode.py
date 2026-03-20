import pytest
import importlib

# Import module with hyphens using importlib
process_mode_module = importlib.import_module('mp3-tag-setter.model.process_mode')
ProcessMode = process_mode_module.ProcessMode


class TestProcessMode:
    """Tests for ProcessMode enum"""

    def test_set_album_tag_by_path_exists(self):
        """Test that SET_ALBUM_TAG_BY_PATH mode exists"""
        assert hasattr(ProcessMode, 'SET_ALBUM_TAG_BY_PATH')

    def test_enum_value_is_unique(self):
        """Test that enum value is unique"""
        mode = ProcessMode.SET_ALBUM_TAG_BY_PATH
        assert mode.value == 1

    def test_enum_name(self):
        """Test that enum name is correct"""
        mode = ProcessMode.SET_ALBUM_TAG_BY_PATH
        assert mode.name == 'SET_ALBUM_TAG_BY_PATH'

    def test_enum_can_be_compared(self):
        """Test that enum values can be compared"""
        mode1 = ProcessMode.SET_ALBUM_TAG_BY_PATH
        mode2 = ProcessMode.SET_ALBUM_TAG_BY_PATH
        assert mode1 == mode2

    def test_enum_is_instance_of_process_mode(self):
        """Test that enum value is instance of ProcessMode"""
        mode = ProcessMode.SET_ALBUM_TAG_BY_PATH
        assert isinstance(mode, ProcessMode)

    def test_enum_string_representation(self):
        """Test that enum has proper string representation"""
        mode = ProcessMode.SET_ALBUM_TAG_BY_PATH
        assert 'SET_ALBUM_TAG_BY_PATH' in str(mode)
