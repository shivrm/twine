# Changelog
All notable changes to this project will be documented in this file.

## [1.0.0] - 2022-02-19
### Added
 - twine documentation (`docs/`)
   - Introduction to twine
   - twine Types Reference
   - Python Implementation Reference

 - twine implementation in Python (`src/python/`)
   - Depends only on standard library modules (`struct`, `math` and `typing`)
   - twine encoders using `generators` (`encoder.py`)
   - twine decoders (`decoder.py`)
   - Ability to add handlers for custom data types using `set_handler` (`__init__.py`)