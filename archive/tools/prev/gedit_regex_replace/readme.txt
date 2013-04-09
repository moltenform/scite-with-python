http://halfhourhacks.blogspot.com/2008/03/gedit-regular-expression-plugin.html
=================

A friend told me that gedit was missing a regular expressions plugin that could replace. I use gedit occasionally, and so I worked on this plugin. It uses Python's good regular expression module, and supports backreferences, making it possible to do significant text processing. 

This plugin is based on extensão para o gEdit by Daniel Carvalho. I fixed bugs, cleaned up the interface, moved the menuitem to the Search menu, added backreferences support, added replace all, and added an option for case-sensitivity. Also, the search mode is multiline, so ^ matches the start of a line. Download 
To install, place the files in ~/.gnome2/gedit/plugins/. Then open gedit, choose Preferences from the Edit menu. On the plugins tab, you should see Regular Expression Replace in the list. Check to enable. Now, you should have a "Regular Expression" item in the Search menu. Tell me if you have any feedback. 

Backreferences are very useful. In the screenshot above, I've written a regular expression for turning "one.tim" into "tim.one", and so on.

