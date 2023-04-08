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
element.innerHTML = 'e' # Rebuilds this element and sets the innerHTML of all the parent elements
element.outerHTML = '<div class="black blue"><a href="https://github.com/" id="abc"></div>' # Read above statement
# assigning to element.children is in the works
tag = element.getElementById('abc')
print(tag.attrs) # {"href":"https://github.com/", "id":"abc"}
print(tag.tag_name) # a
```

## ToDo
- [ ] Support for CSS styles 
- [ ] Support for JS scripts
- [ ] Support for assignment to `HTMLElement.children` list



