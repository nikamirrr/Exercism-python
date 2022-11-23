from json import dumps


class Tree:
    def __init__(self, label, children=None):
        self.label = label
        self.children = children if children is not None else []

    def __dict__(self):
        return {self.label: [c.__dict__() for c in sorted(self.children)]}

    def __str__(self, indent=None):
        return dumps(self.__dict__(), indent=indent)

    def __lt__(self, other):
        return self.label < other.label

    def __eq__(self, other):
        return self.__dict__() == other.__dict__()

    def from_pov(self, from_node):
        cur_path = [[self, 0]]
        while cur_path:
            subtree, next_index = cur_path[-1]
            if subtree.label == from_node:
                break
            if next_index < len(subtree.children):
                next_node = subtree.children[next_index]
                cur_path[-1][1] += 1
                cur_path.append([next_node, 0])
            else:
                cur_path.pop()
        if not cur_path:
            raise ValueError("Tree could not be reoriented")

        it = iter(cur_path)
        p = next(it)
        for c in it:
            p[0].children.pop(p[1] - 1)
            c[0].children.append(p[0])
            p = c

        return cur_path[-1][0]


    def path_to(self, from_node, to_node):

        to_find = {from_node, to_node}
        found_paths = dict()
        cur_path = []

        def helper(subtree):
            nonlocal to_find, found_paths, cur_path
            cur_path.append(subtree.label)
            if subtree.label in to_find:
                found_paths[subtree.label] = cur_path.copy()
                to_find.remove(subtree.label)

            for c in subtree.children:
                if len(to_find) == 0:
                    break
                helper(c)
            cur_path.pop()

        helper(self)
        if from_node in to_find:
            raise ValueError("Tree could not be reoriented")
        if to_node in to_find:
            raise ValueError("No path found")

        from_path = found_paths[from_node]
        to_path = found_paths[to_node]
        from_part = []
        to_part = []
        while len(from_path) > len(to_path):
            from_part.append(from_path.pop())
        while len(to_path) > len(from_path):
            to_part.append(to_path.pop())
        while from_path[-1] != to_path[-1]:
            from_part.append(from_path.pop())
            to_part.append(to_path.pop())
        from_part.append(from_path[-1])

        to_part.reverse()
        from_part.extend(to_part)
        return from_part

