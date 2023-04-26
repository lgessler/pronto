from typing import Dict, List, Tuple

import nltk


def token_yield_of_tree_node(
    tree: nltk.tree.Tree, target: str, blockers: Dict[str, int] = {"S": 1}
) -> List[Tuple[int, List[str]]]:
    """
    Given a tree, return a list of 0-indexed tokens which are children of nodes of a particular type,
    indicated by the argument "target".

    "blockers" adjusts this behavior by ignoring any tokens that might have been included that occur
    in a part of the tree where the target's ancestors include more than the number specified in
    "blockers" of any one of the node types in "blockers". Note further that a key in "blockers"
    matches iff for a node type `n`, `n.startswith(k)` is True.

    For example, if a node's ancestors are [S, NP-X, V, NP], then the node would qualify as a target
    if blockers is {"V": 1}, but not qualify if blockers is {"NP": 1}.

    Args:
        tree:
            a parsed NLTK tree
        target:
            a specific node type whose tokens we want to find
        blockers:
            keys are node types, values are the number of times the node type needs to appear in a
            target's ancestry before the target is ignored

    Returns:
        A list of tuples with two elements: the first is a 0-indexed token index, and the second is an ancestor
        list for that token.
    """
    token_num = 0
    in_target = False
    token_yield = []
    blocker_tracker = {b: 0 for b in blockers.keys()}

    def dfs(node, ancestors=()):
        nonlocal token_num, in_target
        if type(node) is str:
            if in_target:
                token_yield.append((token_num, ancestors))
            token_num += 1
        elif type(node) == nltk.tree.Tree:
            node_type = node.label()
            node_supertype = node_type.split("-")[0]

            blocker_match = None
            for b in blockers.keys():
                if node_supertype.startswith(b):
                    blocker_match = b

            # pre
            if is_blocker := blocker_match is not None:
                blocker_tracker[blocker_match] += 1
            if is_target := target in node_type:
                if all(blocker_tracker[b] <= blockers[b] for b in blockers.keys()):
                    in_target = True

            for x in node:
                dfs(x, ancestors + (node_type,))

            # post
            if is_blocker:
                blocker_tracker[blocker_match] -= 1
            if is_target:
                in_target = False

    dfs(tree)

    return token_yield
