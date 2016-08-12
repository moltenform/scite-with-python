
import pyperclip
txt = pyperclip.paste()
txt = unicode(txt).encode('utf-8')
print(txt)
