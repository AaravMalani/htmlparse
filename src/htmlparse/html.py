"""
A basic HTML parser in Python
"""
from __future__ import annotations
import codecs
import re
import dataclasses
import typing
import uuid


@dataclasses.dataclass
class HTMLElement:
    """The main class for a single HTML element"""

    children: list[HTMLElement]  # The list of children element
    attrs: dict[str, str]  # The attributes (key="value")
    tag_name: str  # The tag name
    parent: typing.Optional[HTMLElement]  # The parent element
    innerHTML: dataclasses.InitVar[str]  # The innerHTML
    # The private uuid of the element in the parser
    id: typing.Optional[str] = None

    def __post_init__(self, innerHTML: str):
        self.__innerHTML: str = innerHTML
        self.id = uuid.uuid4()
        lst = ['']
        for i in self.attrs + ['']:
            try:
                if len(lst[-1].split("=", 1)) == 1 and lst[-1]:
                    lst[-1] = (lst[-1], '')
                    lst += [i]
                a = re.sub('\\\\.', '', lst[-1].split('=', 1)[1])
            except Exception:
                lst[-1] += i
                continue

            if a[0] not in ["'", '"']:
                raise ValueError("property not starting with ' or \": "+a[0])
            if a[0] != a[-1]:
                lst[-1] += i
                continue
            if a.index(a[0], 1) != len(a)-1:
                raise ValueError("property not ending with "+a[0])

            lst[-1] = lst[-1].split('=', 1)
            lst[-1][1] = codecs.escape_decode(lst[-1]
                                              [1][1:-1])[0].decode('utf-8')
            lst += [i]

        lst = lst[:-1]
        self.attrs = {k: v for k, v in lst}

    def decode(self) -> tuple[str]:
        """Returns the outer HTML tag(s) of the element

        Returns:
            tuple[str]: A singleton tuple for singleton tags or an opening and closing tag for normal elements
        """
        attrs_str = [i+'='+'\''+codecs.escape_encode(self.attrs[i].encode('utf-8'))[
            0].decode('utf-8')+'\'' for i in self.attrs]
        return f"<{self.tag_name} {' '.join(attrs_str)}>", (f"</{self.tag_name}>" if self.tag_name.lower() not in ['area', 'base', 'br', 'col', 'command', 'embed', 'hr', 'img', 'input', 'keygen', 'link', 'meta', 'param', 'source', 'track', 'wbr'] else "")

    @ property
    def innerHTML(self) -> str:
        """Returns the inner HTML

        Returns:
            str: The inner HTML 
        """
        return self.__innerHTML

    @ property
    def outerHTML(self) -> str:
        """Returns the outer HTML (innerHTML + surrounding tags)

        Returns:
            str: The outer HTML 
        """
        return self.decode()[0] + self.__innerHTML + self.decode()[1]

    @outerHTML.setter
    def outerHTML(self, value: str):
        """Set the outer HTML of the element

        Args:
            value (str): The HTML data

        Raises:
            ValueError: If the HTML is invalid
        """
        child = parse_html(value, parent=self.parent)
        if not child:
            raise ValueError("Error setting outerHTML")
        self.__dict__ = child.__dict__
        if self.parent:
            val = self.parent.decode()
            self.parent.outerHTML = val[0]+"".join(
                [i.outerHTML for i in self.parent.children]) + val[1]

    @ innerHTML.setter
    def innerHTML(self, value: str):
        """Set the inner HTML of the element

        Args:
            value (str): The HTML data

        Raises:
            ValueError: If the HTML is invalid
        """
        val = self.decode()
        if not val[1]:
            raise ValueError("Cannot set innerHTML of "+self.tag_name)
        child = parse_html(val[0]+value+val[1], parent=self.parent)

        if not child:
            raise ValueError("Error setting innerHTML")
        self.__innerHTML = value
        self.children = child.children
        if self.parent:
            val = self.parent.decode()
            self.parent.outerHTML = val[0]+"".join(
                [i.outerHTML for i in self.parent.children]) + val[1]

    def getElementById(self, id: str) -> typing.Optional[HTMLElement]:
        """Get an element inside this element (or this element) which has a given ID

        Args:
            id (str): The id to look for

        Returns:
            typing.Optional[HTMLElement]: The HTML element or None if not found
        """
        if self.attrs.get('id') == id:
            return self
        for i in self.children:
            val = i.getElementById(id)
            if val == id:
                return val

    def getElementsByClassName(self, class_name: str) -> list[HTMLElement]:
        """Get a list of elements inside this element (or this element) which has a given class

        Args:
            class_name (str): The class to look for

        Returns:
            list[HTMLElement]: The list of HTML elements with given class
        """
        lst = []
        if self.attrs.get('class') and set(class_name.split(' ')).issubset(set(self.attrs.get('class').split(' '))):
            lst += [self]
        for i in self.children:
            lst += i.getElementsByClassName(class_name)
        return lst

    def getElementsByTagName(self, tag_name: str) -> list[HTMLElement]:
        """Get a list of elements inside this element (or this element) which has a given tag name

        Args:
            tag_name (str): The tag name to look for

        Returns:
            list[HTMLElement]: The list of HTML elements with given tag name
        """
        lst = []
        if self.tag_name == tag_name:
            lst += [self]
        for i in self.children:
            lst += i.getElementsByTagName(tag_name)
        return lst

    def __repr__(self):
        nodef_f_vals = (
            (f.name, getattr(self, f.name))
            for f in dataclasses.fields(self)
            if f.name not in ['children', 'parent']
        )

        nodef_f_repr = ", ".join(
            f"{name}={repr(value)}" for name, value in nodef_f_vals)
        return f"{self.__class__.__name__}({nodef_f_repr})"

    def getElementsByAttrs(self, attrs: dict[str, str]) -> list[HTMLElement]:
        """Get a list of elements inside this element (or this element) which matches the attribute dict passed

        Args:
            attrs (dict[str, str]): The attributes to look for

        Returns:
            list[HTMLElement]: The list of HTML elements with given attributes
        """
        lst = []
        if attrs.items() <= self.attrs.items():
            lst += [attrs]
        for i in self.children:
            lst += i.getElementsByAttrs(attrs)
        return lst

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: HTMLElement):
        return self.id == other.id


def parse_html(data: str, parent: typing.Optional[HTMLElement] = None, tag_list: typing.Optional[list[re.Match]] = None) -> typing.Optional[HTMLElement]:
    """Convert data to into a tree of HTML elements

    Args:
        data (str): The HTML data to be parsed
        parent (typing.Optional[HTMLElement], optional): The parent HTML element (used for recursion). Defaults to None.
        tag_list (typing.Optional[list[re.Match]], optional): The list of HTML tags (it automatically sets it if its None). Defaults to None.

    Returns:
        typing.Optional[HTMLElement]: The root element or None if building failed
    """
    tag_list = tag_list or list(re.finditer(r'<(.*?)\/*>', data))
    if tag_list and tag_list[0].groups()[0].split(' ')[0].lower() == '!doctype':
        tag_list = tag_list[1:]
    if not tag_list:
        return
    
    j = 1
    lst = HTMLElement(children=[], attrs=tag_list[0].groups()[0].split(
        ' ')[1:], tag_name=tag_list[0].groups()[0].split(' ')[0], innerHTML=data[tag_list[0].end():tag_list[-1].start()], parent=parent)

    if '/'+tag_list[0].groups()[0].split(' ')[0] != tag_list[-1].groups()[0].split(' ')[0]:
        if tag_list[0].groups()[0].split(' ')[0].lower() in ['area', 'base', 'br', 'col', 'command', 'embed', 'hr', 'img', 'input', 'keygen', 'link', 'meta', 'param', 'source', 'track', 'wbr']:      
            return lst
        return None
    while j < len(tag_list)-1:
        tag = tag_list[j].groups()[0].split(' ')[0]

        j += 1

        if tag.lower() in ['area', 'base', 'br', 'col', 'command', 'embed', 'hr', 'img', 'input', 'keygen', 'link', 'meta', 'param', 'source', 'track', 'wbr']:
            child = parse_html(data, lst, [tag_list[j-1]])
            if not child:
                return
            lst.children += [child]
            continue
        i = j-1
        depth = 1

        while depth:
            if j == len(tag_list)-1:

                return
            if tag_list[j].groups()[0].split(' ')[0].startswith('/'):
                depth -= 1
            elif tag_list[j].groups()[0].split(" ")[0].lower() not in ['area', 'base', 'br', 'col', 'command', 'embed', 'hr', 'img', 'input', 'keygen', 'link', 'meta', 'param', 'source', 'track', 'wbr']:
                depth += 1
            j += 1
        if tag.lower() not in ['script', 'style']:
            child = parse_html(data, lst, tag_list[i: j])
            if not child:
                return
            lst.children += [child]
    return lst
