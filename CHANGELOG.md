# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0-SNAPSHOT] - 2026-03-20

### Fixed

- Fixed Enum vs. String comparison in `set_tag.py` - config value is now properly parsed into `ProcessMode` enum
- Replaced `raise print(...)` with proper `ValueError` exceptions
- Fixed wrong ID3 tag key - changed from `'album'` to `'TALB'` for proper mutagen compatibility
- Fixed fragile config file path - now uses `Path(__file__).parent` for reliability
- Simplified `_remove_tags` logic - removed unnecessary file re-opening
- Narrowed overly broad exception catch from `BaseException` to `MutagenError`
- Fixed bare imports to use relative imports for proper package structure

### Changed

- Improved overall code quality and reliability

## [1.0.0] - 2023-08-08

Initial version of mp3-tag-setter.
