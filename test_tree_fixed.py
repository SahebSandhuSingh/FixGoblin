class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

def preorder(root, res):
    if not root:
        return
    
    res.append(root.val)      # Visit root FIRST (preorder)
    preorder(root.left, res)  # Then left
    preorder(root.right, res) # Then right

root = Node(1)
root.left = Node(2)
root.right = Node(3)

res = []
preorder(root, res)
print(res)  # Should output: [1, 2, 3]
