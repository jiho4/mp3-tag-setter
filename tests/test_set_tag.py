import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
import importlib
import sys

import pytest
from mutagen import MutagenError
from mutagen.id3 import ID3NoHeaderError, TALB

# Import module with hyphens using importlib
set_tag = importlib.import_module('mp3-tag-setter.set_tag')
process_mode_module = importlib.import_module('mp3-tag-setter.model.process_mode')
ProcessMode = process_mode_module.ProcessMode


class TestSetTagsInFolder:
    """Tests for set_tags_in_folder function"""

    @patch.object(set_tag, '_set_album_tag_by_folder_name')
    @patch('os.walk')
    def test_processes_mp3_files_recursively(self, mock_walk, mock_set_album):
        """Test that it walks through directories and processes all mp3 files"""
        mock_walk.return_value = [
            ('/root', ['subdir'], ['song1.mp3', 'song2.mp3', 'other.txt']),
            ('/root/subdir', [], ['song3.mp3', 'doc.pdf']),
        ]

        set_tag.set_tags_in_folder('/root')

        assert mock_set_album.call_count == 3
        mock_set_album.assert_any_call('/root', 'song1.mp3')
        mock_set_album.assert_any_call('/root', 'song2.mp3')
        mock_set_album.assert_any_call('/root/subdir', 'song3.mp3')

    @patch.object(set_tag, '_set_album_tag_by_folder_name')
    @patch('os.walk')
    def test_ignores_non_mp3_files(self, mock_walk, mock_set_album):
        """Test that non-mp3 files are ignored"""
        mock_walk.return_value = [
            ('/root', [], ['song.mp4', 'song.wav', 'song.txt']),
        ]

        set_tag.set_tags_in_folder('/root')

        mock_set_album.assert_not_called()

    @patch.object(set_tag, 'PROCESS_MODE', ProcessMode.SET_ALBUM_TAG_BY_PATH)
    @patch.object(set_tag, '_set_album_tag_by_folder_name')
    @patch('os.walk')
    def test_uses_correct_process_mode(self, mock_walk, mock_set_album):
        """Test that correct processing mode is applied"""
        mock_walk.return_value = [
            ('/root', [], ['song.mp3']),
        ]

        set_tag.set_tags_in_folder('/root')

        mock_set_album.assert_called_once_with('/root', 'song.mp3')

    @patch.object(set_tag, 'PROCESS_MODE', 999)
    @patch('os.walk')
    def test_raises_error_for_invalid_process_mode(self, mock_walk):
        """Test that invalid process mode raises ValueError"""
        mock_walk.return_value = [
            ('/root', [], ['song.mp3']),
        ]

        with pytest.raises(ValueError, match='unexpected process_mode'):
            set_tag.set_tags_in_folder('/root')


class TestSetAlbumTagByFolderName:
    """Tests for _set_album_tag_by_folder_name function"""

    @patch.object(set_tag, '_set_album_tag')
    @patch.object(set_tag, '_remove_tags')
    def test_removes_tags_and_sets_album_tag(self, mock_remove, mock_set_album):
        """Test that tags are removed and album tag is set"""
        root = '/path/to/Album Name'
        file = 'song.mp3'

        set_tag._set_album_tag_by_folder_name(root, file)

        mock_remove.assert_called_once_with('/path/to/Album Name/song.mp3')
        mock_set_album.assert_called_once_with('/path/to/Album Name/song.mp3', 'Album Name')

    @patch.object(set_tag, '_set_album_tag')
    @patch.object(set_tag, '_remove_tags')
    def test_uses_folder_name_as_album_tag(self, mock_remove, mock_set_album):
        """Test that folder name is extracted correctly for album tag"""
        root = '/music/My Favorite Album'
        file = 'track01.mp3'

        set_tag._set_album_tag_by_folder_name(root, file)

        mock_set_album.assert_called_once_with(
            '/music/My Favorite Album/track01.mp3',
            'My Favorite Album'
        )


class TestRemoveTags:
    """Tests for _remove_tags function"""

    @patch.object(set_tag, 'File')
    def test_clears_existing_tags(self, mock_file_class):
        """Test that existing tags are cleared"""
        mock_file = MagicMock()
        mock_file.tags = MagicMock()
        mock_file_class.return_value = mock_file

        set_tag._remove_tags('/path/to/file.mp3')

        mock_file_class.assert_called_once_with('/path/to/file.mp3')
        mock_file.tags.clear.assert_called_once()
        mock_file.save.assert_called_once()

    @patch.object(set_tag, 'File')
    def test_adds_tags_if_none_exist(self, mock_file_class):
        """Test that tags are added if file has no tags"""
        mock_file = MagicMock()
        mock_file.tags = None
        mock_file_class.return_value = mock_file

        set_tag._remove_tags('/path/to/file.mp3')

        mock_file.add_tags.assert_called_once()
        mock_file.save.assert_called_once()


class TestSetAlbumTag:
    """Tests for _set_album_tag function"""

    @patch('mutagen.File')
    @patch.object(set_tag, 'ID3')
    def test_adds_album_tag_successfully(self, mock_id3_class, mock_mutagen_file):
        """Test that album tag is added successfully"""
        mock_tags = MagicMock()
        mock_tags.__contains__ = lambda self, key: False  # No existing TALB tag
        mock_id3_class.return_value = mock_tags

        set_tag._set_album_tag('/path/to/file.mp3', 'Test Album')

        mock_id3_class.assert_called_once_with('/path/to/file.mp3')
        # Verify TALB was added with correct encoding and text
        assert mock_tags.add.called
        added_tag = mock_tags.add.call_args[0][0]
        assert isinstance(added_tag, TALB)
        assert added_tag.encoding == 3
        assert added_tag.text == ['Test Album']  # TALB.text is a list
        mock_tags.save.assert_called_once()

    @patch('mutagen.File')
    @patch.object(set_tag, 'ID3')
    def test_raises_error_if_album_tag_exists(self, mock_id3_class, mock_mutagen_file):
        """Test that error is raised if album tag already exists"""
        mock_tags = MagicMock()
        mock_tags.__contains__ = lambda self, key: key == 'TALB'
        mock_id3_class.return_value = mock_tags

        with pytest.raises(ValueError, match='album tag already exists'):
            set_tag._set_album_tag('/path/to/file.mp3', 'Test Album')

    @patch('mutagen.File')
    @patch.object(set_tag, 'ID3')
    def test_handles_id3_no_header_error(self, mock_id3_class, mock_mutagen_file, capsys):
        """Test that ID3NoHeaderError is handled gracefully"""
        mock_id3_class.side_effect = ID3NoHeaderError('No ID3 header')

        mock_file = MagicMock()
        mock_tags = MagicMock()
        mock_tags.__contains__ = lambda self, key: False
        mock_file.tags = mock_tags
        mock_mutagen_file.return_value = mock_file

        set_tag._set_album_tag('/path/to/file.mp3', 'Test Album')

        captured = capsys.readouterr()
        assert 'Error when opening' in captured.out
        mock_file.add_tags.assert_called_once()
        mock_file.save.assert_called_once()

    @patch('mutagen.File')
    @patch.object(set_tag, 'ID3')
    def test_handles_attribute_error(self, mock_id3_class, mock_mutagen_file, capsys):
        """Test that AttributeError is handled gracefully"""
        mock_id3_class.side_effect = AttributeError('Attribute error')

        mock_file = MagicMock()
        mock_tags = MagicMock()
        mock_tags.__contains__ = lambda self, key: False
        mock_file.tags = mock_tags
        mock_mutagen_file.return_value = mock_file

        set_tag._set_album_tag('/path/to/file.mp3', 'Test Album')

        captured = capsys.readouterr()
        assert 'Error when opening' in captured.out
        mock_file.add_tags.assert_called_once()

    @patch('mutagen.File')
    @patch.object(set_tag, 'ID3')
    def test_handles_mutagen_error_on_add(self, mock_id3_class, mock_mutagen_file, capsys):
        """Test that MutagenError during tag add is handled gracefully"""
        mock_tags = MagicMock()
        mock_tags.__contains__ = lambda self, key: False
        mock_tags.add.side_effect = MutagenError('Error adding tag')
        mock_id3_class.return_value = mock_tags

        set_tag._set_album_tag('/path/to/file.mp3', 'Test Album')

        captured = capsys.readouterr()
        assert 'An exception occurred' in captured.out
        assert '/path/to/file.mp3' in captured.out
        mock_tags.save.assert_called_once()


class TestProcessMode:
    """Tests for ProcessMode enum"""

    def test_process_mode_enum_values(self):
        """Test that ProcessMode enum has expected values"""
        assert ProcessMode.SET_ALBUM_TAG_BY_PATH is not None
        assert isinstance(ProcessMode.SET_ALBUM_TAG_BY_PATH, ProcessMode)


class TestConfigLoading:
    """Tests for configuration loading"""

    def test_config_loads_process_mode(self):
        """Test that config file is loaded and process mode is set"""
        # This test validates that the module loads config correctly at import time
        # The actual loading happens at module level, so we mainly document the behavior
        assert hasattr(set_tag, 'PROCESS_MODE')
        assert isinstance(set_tag.PROCESS_MODE, ProcessMode)
