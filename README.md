# veno
```
                 ▓               
                 ▓▓              
 ▓▓▓  ▓▓ ▓▓▓▓▓▓▓ ▓▓▓  ▓▓  ▓▓▓▓▓ 
 ▓▓▓  ▓▓ ▓▓      ▓▓▓▓ ▓▓ ▓▓   ▓▓
  ▓▓  ▓▓ ▓▓▓▓▓▓▓ ▓▓▓▓▓▓▓ ▓▓   ▓▓
  ▓▓ ▓▓  ▓▓      ▓▓▓ ▓▓▓ ▓▓   ▓▓
   ▓▓▓   ▓▓▓▓▓▓▓ ▓▓▓  ▓▓  ▓▓▓▓▓ 
                       ▓         
```
Multi-purpose text/code editor meant for easy and vast expandability.

## Install

Requires Python 3.

Dependencies:
 - Pygments
 - ncurses

Run `pip3 install -r requirements.txt` to install dependencies.
 - In case this does not successfully install Pygments, installing Pygments through a package manager may.
   - On Ubuntu, try `sudo apt install python3-pygments`

Run `chmod +x veno` to mark `veno` as executable.

To use `veno` globally, add the repo to your $PATH. Alternatively, add an alias to `veno` in your `.bashrc` or `.bash_alias`.

## Usage

`veno [filename [filename ...]]` Filename(s) optional.

Runs in a terminal window. GUI not yet implemented.

## Keybindings

 - **Ctrl-C** -- cancel/quit
 - **Printable characters** -- add character at cursor in file
 - **Enter Key, Ctrl-J** -- add newline at cursor in file
 - **Tab Key, Ctrl-I** -- add tab character or equivalent spaces at cursor in file / indent selected lines
 - **Shift-Tab** -- unindent current line / selected lines
 - **Backspace Key, Ctrl-?, Ctrl-H** -- remove previous character at cursor from file
 - **Delete Key** -- remove character at cursor from file
 - **Ctrl-D** -- remove line at cursor from file
 - **Arrow Keys** -- move cursor in file
 - **PageUp, PageDown** -- scroll screen up/down
 - **Ctrl-Arrow Keys** -- move viewport in file. Ctrl-Arrow Keys not supported by all terminals.
 - **Ctrl-W** -- save file
 - **Home Key** -- go to start of line in file
 - **End Key** -- go to end of line in file
 - **F3** -- go to start of file
 - **F4** -- go to end of file
 - **F5** -- go to previous open file
 - **F6** -- go to next open file
 - **Ctrl-L** - go to a line in file
 - **Ctrl-F** -- find regex string in file
 - **Ctrl-G** -- find next match in file
 - **Ctrl-R** -- find and replace string in file
 - **Ctrl-B** -- select text in file
 - **Ctrl-K** -- copy and store selection in file
 - **Ctrl-X** -- cut and store selection from file
 - **Ctrl-V** -- paste selection into file
 - **Ctrl-_, Ctrl-/** -- toggle config customizer.

