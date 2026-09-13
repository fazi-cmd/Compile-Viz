"""
CompileViz Semantic Analyzer
Type checking, scope analysis, and symbol table construction.
"""

from .parser import ASTNode
from typing import List, Dict, Optional


class SemanticError(Exception):
    def __init__(self, message, line=None):
        super().__init__(message)
        self.line = line


class SymbolTable:
    def __init__(self):
        self.scopes: List[Dict] = [{}]  # Stack of scopes
        self.all_symbols = []  # Flat list for visualization

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def declare(self, name: str, var_type: str, line: int):
        current_scope = self.scopes[-1]
        if name in current_scope:
            raise SemanticError(f"Variable '{name}' already declared in this scope", line)
        current_scope[name] = {'type': var_type, 'line': line, 'scope': len(self.scopes) - 1}
        self.all_symbols.append({
            'name': name,
            'type': var_type,
            'line': line,
            'scope': len(self.scopes) - 1,
            'scope_name': 'global' if len(self.scopes) == 1 else f'scope_{len(self.scopes)-1}'
        })

    def lookup(self, name: str) -> Optional[Dict]:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def get_all(self):
        return self.all_symbols


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.warnings = []
        self.functions = {}

    def analyze(self, ast: ASTNode):
        self.visit(ast)
        return self.symbol_table, self.errors, self.warnings

    def visit(self, node: ASTNode):
        method = f'visit_{node.node_type}'
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode):
        for child in node.children:
            if isinstance(child, ASTNode):
                self.visit(child)

    def visit_Program(self, node: ASTNode):
        for child in node.children:
            if isinstance(child, ASTNode):
                self.visit(child)

    def visit_Declaration(self, node: ASTNode):
        type_node = node.children[0] if node.children else None
        name_node = node.children[1] if len(node.children) > 1 else None
        expr_node = node.children[2] if len(node.children) > 2 else None

        if type_node and name_node:
            var_type = type_node.value
            var_name = name_node.value
            try:
                self.symbol_table.declare(var_name, var_type, node.line)
            except SemanticError as e:
                self.errors.append({'message': str(e), 'line': e.line})

            if expr_node:
                expr_type = self.visit(expr_node)
                if expr_type and var_type != expr_type:
                    # Type coercion warning
                    self.warnings.append({
                        'message': f"Type mismatch: assigning {expr_type} to {var_type} '{var_name}'",
                        'line': node.line
                    })

    def visit_Assignment(self, node: ASTNode):
        var_name = node.value
        sym = self.symbol_table.lookup(var_name)
        if sym is None:
            self.errors.append({
                'message': f"Undeclared variable '{var_name}'",
                'line': node.line
            })
        for child in node.children[1:]:
            if isinstance(child, ASTNode):
                self.visit(child)

    def visit_Identifier(self, node: ASTNode):
        sym = self.symbol_table.lookup(node.value)
        if sym is None:
            self.errors.append({
                'message': f"Use of undeclared variable '{node.value}'",
                'line': node.line
            })
            return 'unknown'
        return sym['type']

    def visit_Integer(self, node: ASTNode):
        return 'int'

    def visit_Float(self, node: ASTNode):
        return 'float'

    def visit_String(self, node: ASTNode):
        return 'string'

    def visit_Boolean(self, node: ASTNode):
        return 'bool'

    def visit_BinaryOp(self, node: ASTNode):
        left_type = self.visit(node.children[0]) if node.children else None
        right_type = self.visit(node.children[1]) if len(node.children) > 1 else None
        if node.value in ('==', '!=', '<', '>', '<=', '>=', '&&', '||'):
            return 'bool'
        return left_type or right_type or 'int'

    def visit_UnaryOp(self, node: ASTNode):
        return self.visit(node.children[0]) if node.children else 'int'

    def visit_IfStatement(self, node: ASTNode):
        self.symbol_table.enter_scope()
        for child in node.children:
            if isinstance(child, ASTNode):
                self.visit(child)
        self.symbol_table.exit_scope()

    def visit_WhileLoop(self, node: ASTNode):
        self.symbol_table.enter_scope()
        for child in node.children:
            if isinstance(child, ASTNode):
                self.visit(child)
        self.symbol_table.exit_scope()

    def visit_ForLoop(self, node: ASTNode):
        self.symbol_table.enter_scope()
        for child in node.children:
            if isinstance(child, ASTNode):
                self.visit(child)
        self.symbol_table.exit_scope()

    def visit_FunctionDef(self, node: ASTNode):
        func_name = node.value
        self.functions[func_name] = node
        self.symbol_table.declare(func_name, 'func', node.line)
        self.symbol_table.enter_scope()
        for child in node.children:
            if isinstance(child, ASTNode):
                self.visit(child)
        self.symbol_table.exit_scope()

    def visit_FunctionCall(self, node: ASTNode):
        for child in node.children:
            if isinstance(child, ASTNode):
                self.visit(child)
        return 'unknown'

    def visit_Print(self, node: ASTNode):
        for child in node.children:
            if isinstance(child, ASTNode):
                self.visit(child)

    def visit_Return(self, node: ASTNode):
        for child in node.children:
            if isinstance(child, ASTNode):
                self.visit(child)

    def visit_Condition(self, node: ASTNode):
        for child in node.children:
            if isinstance(child, ASTNode):
                self.visit(child)

    def visit_ThenBlock(self, node: ASTNode):
        for child in node.children:
            if isinstance(child, ASTNode):
                self.visit(child)

    def visit_ElseBlock(self, node: ASTNode):
        for child in node.children:
            if isinstance(child, ASTNode):
                self.visit(child)

    def visit_Body(self, node: ASTNode):
        for child in node.children:
            if isinstance(child, ASTNode):
                self.visit(child)

    def visit_Params(self, node: ASTNode):
        for child in node.children:
            if isinstance(child, ASTNode):
                parts = child.value.split()
                if len(parts) == 2:
                    try:
                        self.symbol_table.declare(parts[1], parts[0], child.line)
                    except SemanticError as e:
                        self.errors.append({'message': str(e), 'line': e.line})


def analyze(ast: ASTNode):
    analyzer = SemanticAnalyzer()
    symbol_table, errors, warnings = analyzer.analyze(ast)
    return symbol_table.get_all(), errors, warnings
