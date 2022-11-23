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


def parse(input_string):
    n = len(input_string)
    if n == 0 or input_string[0] != '(' or input_string[-1] != ')':
        raise ValueError('tree missing')
    if n == 2:
        raise ValueError('tree with no nodes')

    result_stack = []
    s_len = len(input_string)
    # parse the root
    start = 0
    while start < s_len:
        if input_string[start] == "(":
             
            result_stack.append(SgfTree())
        
            
         
    return result_stack.pop()
