# htmlparse: A basic HTML parser in Python
## Installation
```sh
# Linux
python3 -m pip install parser-html
# Windows
python -m pip install parser-html
# Build from source
python -m pip install git+https://github.com/AaravMalani/htmlparse
```

## Usage
```py
import htmlparse

with open('index.html', 'r') as f:
    element = htmlparse.parse_html(f.read())
    if not element:
        raise ValueError("Parsing failed!")
print(element.children) # Sub-elements
print(element.innerHTML) # Data enclosed by tag
print(element.outerHTML) # Data enclosed by tag as well as the tag itself
element.innerHTML = 'e&gt;' # Rebuilds this element and sets the innerHTML of all the parent elements
print(element.children) # ['e>'] (The HTMLText element is represented as a string literal)
print(element.children[0].text) # e> (Use HTMLText.outerHTML for an HTML escaped string (e&gt;) however don't set it)
element.outerHTML = '<div class="black blue"><a href="https://github.com/" id="abc"></div>' # Read above statement
# assigning to element.children is in the works
print(tag.attrs) # {"href":"https://github.com/", "id":"abc"}
print(tag.tag_name) # a
element.children = []
element.attrs = {} # WARNING! You have to set it, you can't do element.attrs.update or element.attrs |=
print(tag.outerHTML) # <div></div>
```

## ToDo
- [ ] Support for CSS styles 
- [ ] Support for JS scripts
- [x] Support for assignment to `HTMLElement.children` list
- [x] Support for text between strings
- [ ] Support for CSS selectors
- [ ] Support for XPATH



