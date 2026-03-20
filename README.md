# mp3-tag-setter

*created: 2023/08/08*

A command-line utility that batch-processes MP3 files by clearing existing ID3 tags and setting the album tag based on the parent folder name.

## Features

- Recursively scans a directory for `.mp3` files
- Removes all existing ID3 tags from each file
- Sets the `TALB` (Album) tag to the name of the file's immediate parent folder
- Configurable processing mode via `config.yml`

## Requirements

- Python 3.9+
- Dependencies listed in `requirements.txt`:
  - `mutagen~=1.46.0` — MP3 tag manipulation
  - `PyYAML~=6.0` — configuration parsing
  - `setuptools~=65.5.1`

## Installation

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

Run as a Python module from the project root:

```bash
python -m mp3-tag-setter
```

You will be prompted to enter the full path of the root folder to process:

```
Enter the full path of root folder: /path/to/music
```

All `.mp3` files found recursively under that folder will have their tags cleared and their album tag set to the parent folder's name.

### Example

Given the following folder structure:

```
/music/
  Album A/
    track1.mp3
    track2.mp3
  Album B/
    track1.mp3
```

After running, each file will have:

- All previous tags removed
- Album tag set to `Album A` or `Album B` respectively

## Configuration

`mp3-tag-setter/resources/config.yml`:

```yaml
process_mode: 'SET_ALBUM_TAG_BY_PATH'
```

| Key | Value | Description |
|---|---|---|
| `process_mode` | `SET_ALBUM_TAG_BY_PATH` | Sets album tag from parent folder name |

## Project Structure

```
mp3-tag-setter/
├── mp3-tag-setter/
│   ├── __main__.py          # Entry point
│   ├── set_tag.py           # Core tag manipulation logic
│   ├── model/
│   │   └── process_mode.py  # ProcessMode enum
│   └── resources/
│       └── config.yml       # Application configuration
├── tests/
├── requirements.txt
├── test_requirements.txt
└── setup.py
```
