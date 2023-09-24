from tabbed import TabbedText

import pathlib
# tabbed = TabbedText(pathlib.Path("tabbed.txt").read_text())
# def_str = tabbed["class TabbedText:"]["def __str__(self):"]
# def_str["oeha"] = ["oea", "12"]
# print(tabbed)
#
# tabbed = TabbedText()
# tabbed.append("[END1]").parent.append("[END2]")
# tabbed.prepend("</nav>").parent.prepend("<nav>").append("aboba1").parent.append("aboba2")
# print(tabbed)
#
#
# class TaggedText(TabbedText):
#     def prepend_tag(self, tag: str):
#         self.prepend(f"</{tag}>")
#         return self.prepend(f"<{tag}>")
#
#
# print("-"*80)
# tabbed = TaggedText()
# tabbed.append("[END1]").parent.append("[END2]")
# tabbed.prepend_tag("nav").append("aboba1").parent.append("aboba2")
# print(tabbed)
#
# print("-"*80)
# tabbed = TaggedText()
# tabbed.append("[END1]", []).append("[END2]", [])
# tabbed.prepend_tag("nav").append("aboba1").parent.append("aboba2")
# print(tabbed)
tabbed = TabbedText(pathlib.Path("html.html").read_text())
tabbed["<body>"].prepend("</nav>", []).prepend("<nav>", ["132"])
(tabbed["<body>"] / ("<nav>", [])).f()
tabbed["<body>"].add("<nav>", []).f()
tabbed["<body>"](lambda x: x.add("<nav>").extend([])).f()
tabbed("<body>", lambda b: b.add(...))
tabbed["<body>"].prepend("</nav>").append(tabbed["<nav>"]['<a class=home href="/">HVOX.ART</a>', tabbed["<div class=global>"]['<a href=".">ARTWORKS</a>', '<a href=".">GAMES</a>', '<a href=".">TOOLS</a>', '<a class=active href=".">OTHER</a>']])
tabbed["<body>"].prepend("</nav>").append(tabbed["<nav>"]('<a class=home href="/">HVOX.ART</a>', tabbed["<div class=global>"]('<a href=".">ARTWORKS</a>', '<a href=".">GAMES</a>', '<a href=".">TOOLS</a>', '<a class=active href=".">OTHER</a>')))
tabbed["<body>"].prepend("</nav>").append(tabbed("<nav>")('<a class=home href="/">HVOX.ART</a>', tabbed("<div class=global>")('<a href=".">ARTWORKS</a>', '<a href=".">GAMES</a>', '<a href=".">TOOLS</a>', '<a class=active href=".">OTHER</a>')))
tabbed["<body>"].prepend("</nav>").append("<nav>", ['<a class=home href="/">HVOX.ART</a>', "<div class=global>", ['<a href=".">ARTWORKS</a>', '<a href=".">GAMES</a>', '<a href=".">TOOLS</a>', '<a class=active href=".">OTHER</a>']])
tabbed["<body>"].prepend("</nav>").append( "<nav>", ['<a class=home href="/">HVOX.ART</a>', ("<div class=global>", ['<a href=".">ARTWORKS</a>', '<a href=".">GAMES</a>', '<a href=".">TOOLS</a>', '<a class=active href=".">OTHER</a>'])])
print(tabbed["<body>"])
