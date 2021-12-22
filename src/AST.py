# coding=utf-8
# 定义抽象语法树，定义内部节点和外部节点
# 节点都有属性key，但是只有叶子节点有属性value

class AST_Node():
    """
    key属性描述了这个节点的变量，如果它是叶子节点，则有value
    """
    def __init__(self, key):
        self.key = key

class AST_LeafNode(AST_Node):
    """
    叶子节点
    key     : String, 表示变量名称
    value   : String, 表示终结符
    """
    def __init__(self, key, value):
        self.key = str(key)
        self.value = str(value)
    
    def __str__(self):
        return self.value

class AST_InternalNode(AST_Node):
    """
    内部节点
    key     : String, 表示变量名称
    children : List<AST_Node> 描述了语法分析树的树形结构
    """
    def __init__(self, key, childen):
        self.key = str(key)
        self.childen = childen
        for i in range(len(self.childen)):
            if not isinstance(self.childen[i],AST_Node):
                self.childen[i] = AST_LeafNode(key=str(self.childen[i]),value=str(self.childen[i]))
    
    def __str__(self):
        result = self.key + "["
        for i in range(len(self.childen)-1):
            result += str(self.childen[i]) + ","
        result += str(self.childen[-1]) + "]"
        return result

# 用于测试
if __name__ == '__main__':
    """
    这个树不是一个严格的语法分析树，只是检查print
            expr
         /    |   \
        expr  |   expr
        a     +    b
    结果：expr[expr[a],+,expr[b]]
    """
    root = AST_InternalNode("expr", [])
    left = AST_InternalNode("expr",[])
    mid = AST_LeafNode("+","+")
    right = AST_InternalNode("expr",[])
    a = AST_LeafNode("a","a")
    b = AST_LeafNode("b","b")

    root.childen = [left, mid, right]
    left.childen = [a]
    right.childen = [b]
    print(root)
    