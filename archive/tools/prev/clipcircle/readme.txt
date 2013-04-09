Clipcircle32
Ben Fisher, 2011. Released under the GPLv3 license.
http://halfhourhacks.blogspot.com

Clipcircle lets you store multiple values in the clipboard at the same time and cycle between them.

Example
------------------
Open clipcircle32.exe (appears as an icon in the system tray when active).
Copy a word of text from any program.
Copy a different word of text.
Open notepad
Press Windows-V. (The windows key has a flag icon and is typically between Ctrl and Alt)
The word you copied appears and is selected!
Press Windows-V again.
Now, the first word copied appears.

Because Clipcircle selects as well as pastes, you can quickly cycle through the contents of the circle. 
By default, Clipcircle stores 8 items. It intentionally only stores this many items, so that you can repeatedly press
Windows-V to cycle through everything that is stored.

To close Clipcircle, press Windows-Escape.


Additional notes
------------------
Requires Windows XP or later.
Supports unicode characters.
One feature of Clipcircle is that it will select text after pasting, in order to quickly cycle
through the ring of contents. If the contents of the clipboard contain Unicode composed characters, 
bi-directional text, or non-printing characters, this auto-selection feature may select the wrong amount of text,
but this won't affect your data at all. Auto-select also won't occur for large quantities of text.

To customize how many items are stored, edit clipcircle.h, set g_nItems to another value, and re-build.


Clipcircle is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
 
Clipcircle is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with Clipcircle. If not, see <http://www.gnu.org/licenses/>.

Icon
---------------
The ToolBar Icons can be used for commercial and non-commercial purposes. 
Feel free to remix and use them any way you like. You do not need to credit 
BRKR Designs / Billy Barker / www.billybarker.net (unless you want to).
Enjoy this great collection of icons for iPhone, iPad, iPod, or whatever you choose.
Visit http://www.billybarker.net for more information.
Black ToolBar Icons for iPhone 4 Retina Display.
