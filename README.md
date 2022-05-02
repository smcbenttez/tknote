# TkNote
The goal of this project is to create a cross platform drop in replacement for the Notes application on macOS.

## Current Status
TkNote is still very much a work in progress and is in the alpha stages of development. In its current state it provides users all the basic functionality to create, delete, and store notes.

Remote note storage and syncing will be the next feature added. This will go hand in hand with work on the storage service which can be tracked [here].

### Project Features:
- Only uses the Python Standard Library (tkinter used for GUI)
- reST docstrings compatible with Sphinx for automatic documentation
- Complete type annotations to be used with static checkers like [mypy](https://github.com/python/mypy)
- Rudimentary animation support for tkinter widgets
- Custom list widget similar to what is found on macOS and iOS

### Application Features
- Application state and window position is saved and loaded on application launch
- Automatically saves notes and edits
- Ability to undo note deletion
- Ability to customize font and font size
- Ability to customize how the notes are sorted in the UI

### Planned Application Features (in order of planned completion):
- Remote note storage and syncing via HTTP(S)
- Markdown support for notes
- Note encryption
- Text search
- Standalone application distributables

### Current Platform Support
- macOS

*TkNote may work on other platforms since tkinter is a cross platform GUI framework, but it has note been tested and ymmv.*

### Planned Platform Support
- macOS
- Linux
- Windows

### Installation
Tknote requires Python>=3.10.2. If you do not have a compatible version of python installed on your system, please install that first.

Clone the repo and cd into the new directory.
```
git clone https://github.com/smcbenttez/tknote.git && cd tknote
```
Create a virtual environment and activate it.
```
python3 -m venv venv
source ./venv/bin/activate
```
Use pip to install the package. If you want to modify the source use the '-e' flag.
```
pip install -e ./
```
Run Tknote. A sqlite database that stores the application data will be created in the same directory if one is not found. Currently the applicaiton expects the database to live in the directory from where the application is executed. If you want to move the database file, create a symlink to the new location.
```
python -m tknote
```
