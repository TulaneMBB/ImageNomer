import ast
import numpy as np

# My modules

import session

def add(a,b):
    return a+b

def sub(a,b):
    return a-b

def mult(a,b):
    return a*b

def div(a,b):
    return a/b

''' Standard deviation '''
def std(*args):
    return np.std(args)

operators = {ast.Add: add, ast.Sub: sub, ast.Mult: mult, ast.Div: div}

def evalnode(node):
    if isinstance(node, ast.Expr):
        return node.value
    elif isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.Name):
        return session.load(node.id)
    elif isinstance(node, ast.BinOp):
        return operators[type(node.op)](evalnode(node.left), evalnode(node.right))
    elif isinstance(node, ast.Call):
        raise TypeError(node)
    else:
        raise TypeError(node)

def eval(expr):
    return evalnode(ast.parse(expr, mode='eval').body)