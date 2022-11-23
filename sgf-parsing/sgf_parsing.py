from enum import Enum


class SgfTree:
    def __init__(self, properties=None, children=None):
        self.properties = properties or {}
        self.children = children or []

    def __eq__(self, other):
        if not isinstance(other, SgfTree):
            return False
        for key, value in self.properties.items():
            if key not in other.properties:
                return False
            if other.properties[key] != value:
                return False
        for key in other.properties.keys():
            if key not in self.properties:
                return False
        if len(self.children) != len(other.children):
            return False
        for child, other_child in zip(self.children, other.children):
            if child != other_child:
                return False
        return True

    def __ne__(self, other):
        return not self == other


class ParseStates(Enum):
    LABEL_START = 1
    IN_LABEL = 2
    IN_VALUE = 3
    IN_VALUE_ESCAPED = 4
    VALUE_COMPLETE = 5


char_translates = {"\t": " ",
                   "\v": " "}


def parse_sgf_text(input_string, pos, values):
    n = len(input_string)
    state = ParseStates.IN_VALUE
    value_chars = []
    while pos < n:
        input_char = input_string[pos]
        if state == ParseStates.IN_VALUE_ESCAPED:
            value_chars.append(char_translates.get(input_char, input_char))
            state = ParseStates.IN_VALUE
        elif input_char == "\\":
            state = ParseStates.IN_VALUE_ESCAPED
        elif input_char == ":":
            raise ValueError("Unescaped : in the value")
        elif input_char == "]":
            values.append("".join(value_chars))
            return pos
        else:
            value_chars.append(char_translates.get(input_char, input_char))
        pos += 1
    raise ValueError("Incomplete property value")


def parse_node(input_string, pos, properties):
    state = ParseStates.LABEL_START
    n = len(input_string)
    prop_start = pos
    while pos < n:
        input_char = input_string[pos]
        if state != ParseStates.IN_VALUE_ESCAPED and input_char in "();":
            if state not in (ParseStates.LABEL_START, ParseStates.VALUE_COMPLETE):
                raise ValueError("properties without delimiter")
            break
        if state == ParseStates.LABEL_START:
            if not input_char.isupper():
                raise ValueError("property must be in uppercase")
            prop_start = pos
            state = ParseStates.IN_LABEL
        elif state == ParseStates.IN_LABEL:
            if input_char == "[":
                prop_name = input_string[prop_start:pos]
                if prop_name in properties:
                    raise ValueError("Duplicate property name")
                properties[prop_name] = values = []
                pos = parse_sgf_text(input_string, pos + 1, values)
                state = ParseStates.VALUE_COMPLETE
            elif not input_char.isupper():
                raise ValueError("property must be in uppercase")
        elif state == ParseStates.VALUE_COMPLETE:
            if input_char == "[":
                pos = parse_sgf_text(input_string, pos + 1, values)
            else:
                state = ParseStates.LABEL_START
                continue

        pos += 1
    return pos


def parse(input_string):
    n = len(input_string)
    if n == 0 or input_string[0] != '(' or input_string[-1] != ')':
        raise ValueError('tree missing')
    if n == 2:
        raise ValueError('tree with no nodes')
    pos = 0
    result_stack = [SgfTree()]

    while pos < n:
        input_char = input_string[pos]
        if input_char in "(":
            new_node = SgfTree()
            result_stack[-1].children.append(new_node)
            result_stack.append(new_node)
            pos += 1
            if pos == n or input_string[pos] != ";":
                raise ValueError('Node start is missing')
            pos += 1
        elif input_char in ";":
            new_node = SgfTree()
            result_stack.pop().children.append(new_node)
            result_stack.append(new_node)
            pos += 1
        elif input_char == ")":
            result_stack.pop()
            pos += 1
        else:
            raise ValueError('Node start is missing')
        # parse the node data
        pos = parse_node(input_string, pos, result_stack[-1].properties)

    if len(result_stack) != 1:
        raise ValueError('Wrong tree structure')
    return result_stack[0].children[0]
