# veno

![](logo.png)

Multi-purpose text/code editor meant for easy and vast expandability.

## Features

 - Fully modular
   - Realtime crash-preventing module unloading
   - Keybinding initialization error detection with automatic dynamic key unbinding
   - Help window reporting generated keybindings and respective module functions
 - Syntax highlighting
 - Multi-file support
 - Run window with command output
 - Diff window comparing disk/editor file contents
 - Regex Find/Replace mode
 - Text select-region toggle; cut, copy, paste
 - Line jump
 - In-editor configuration customizer
   - Bracket matching, quote matching
   - Auto-indent
   - Find/Replace regex/standard toggle
 - Language-specific configuration overrides
 - 100% Python code

## Install

Requires Python 3.

Dependencies:
 - Pygments
 - ncurses

Run `pip3 install -r requirements.txt` to install dependencies.
 - In case this does not successfully install Pygments, installing Pygments through a package manager may.
   - On Ubuntu, run `sudo apt install python3-pygments`
   - On NetBSD 9.2, run `pkgin install py39-curses py39-cursespanel py39-pygments && sed 's/python3/python3.9/g' veno`


Run `chmod +x veno` to mark `veno` as executable.

To use `veno` globally, add the repo to your $PATH. Alternatively, add an alias to `veno` in your `.bashrc` or `.bash_alias`.

## Usage

`veno [filename [filename ...]]` Filename(s) optional.

Runs in a terminal window. GUI not yet implemented.

## Keybindings

|Keybinding|Description|
|:-:|:--|
|Ctrl-C|Cancel/Quit|
|printable characters|Add character at cursor in file|
|Enter Key, Ctrl-J|Add newline at cursor in file|
|Tab Key, Ctrl-I|Add tab character or equivalent spaces at cursor in file / indent selected lines|
|Shift-Tab|Unindent current line / selected lines|
|Backspace Key, Ctrl-?, Ctrl-H|Remove previous character at cursor from file|
|Delete Key|Remove character at cursor from file|
|Ctrl-D|Remove line at cursor from file|
|Arrow Keys|Move cursor in file|
|PageUp, PageDown|Scroll cursor up/down|
|Ctrl/Alt-PageUp, Ctrl/Alt-PageDown|Scroll viewport up/down|
|Ctrl-Arrow Keys|Move viewport up/down/left/right.  (Ctrl-Arrow Keys not supported by all terminals)|
|Ctrl-W|Save file|
|Home Key|Go to start of line in file|
|End Key|Go to end of line in file|
|F1|Toggle Help Window|
|F2|Run command|
|F3|Go to start of file|
|F4|Go to end of file|
|F5|Go to previous open file|
|F6|Go to next open file|
|F9|Close file|
|Ctrl-L|Go to a line in file|
|Ctrl-F|Find regex string in file|
|Ctrl-G|Find next match in file|
|Ctrl-R|Find and replace string in file|
|Ctrl-B|Select text in file|
|Ctrl-A|Select all text in file|
|Ctrl-K|Copy and store selection in file|
|Ctrl-X|Cut and store selection from file|
|Ctrl-V|Paste selection into file|
|Ctrl-O|Open file|
|Ctrl-T|Diff file|
|Ctrl-_, Ctrl-/|Toggle config customizer|
|F12|Toggle debug window|

