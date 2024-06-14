# BenPythonCommon,
# 2015 Ben Fisher, released under the LGPLv3 license.

import pyperclip
txt = pyperclip.paste()
txt = unicode(txt).encode('utf-8')
print(txt)
