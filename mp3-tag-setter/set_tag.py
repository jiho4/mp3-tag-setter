import os
from typing import Final

import mutagen
import yaml
from mutagen import File
from mutagen.id3 import ID3, ID3NoHeaderError, TALB

from model.process_mode import ProcessMode

with open('resources/config.yml') as f:
    __conf = yaml.safe_load(f)

PROCESS_MODE: Final[str] = __conf['process_mode']


def set_tags_in_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.mp3'):
                if PROCESS_MODE == ProcessMode.SET_ALBUM_TAG_BY_PATH:
                    _set_album_tag_by_folder_name(root, file)
                else:
                    raise print('unexpected process_mode')  # TODO: add an exception


def _set_album_tag_by_folder_name(root, file):
    file_path = os.path.join(root, file)
    folder_name = os.path.basename(root)  # get the name of the parent subdir

    # remove current tag information, and then set only album tag to the folder name
    _remove_tags(file_path)
    _set_album_tag(file_path, folder_name)


def _remove_tags(file_path):
    file = File(file_path)

    if file.tags is None:
        # set blank tags to the file
        tags = mutagen.File(file_path)
        tags.add_tags()
    else:
        file.tags.clear()

    file.save()


def _set_album_tag(file_path, album_name):
    # open the file
    try:
        tags = ID3(file_path)
    except (ID3NoHeaderError, AttributeError) as e:
        print('Error when opening: ' + file_path + ' # Err: {}'.format(e))
        tags = mutagen.File(file_path)
        tags.add_tags()

    if 'album' in tags:
        raise print('album tag is already exist in ' + file_path)  # TODO: add an exception
    else:
        # set album tag
        try:
            tags.add(TALB(encoding=3, text=album_name))
        except BaseException as e:  # TODO: change BaseException to a proper one
            print('An exception occurred: {}'.format(e))
            print(file_path)

    tags.save()
