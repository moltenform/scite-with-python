# SciTE Python Extension
# Ben Fisher, 2016
# Released under the GNU General Public License version 3

import pyperclip
txt = pyperclip.paste()
txt = unicode(txt).encode('utf-8')
print(txt)
