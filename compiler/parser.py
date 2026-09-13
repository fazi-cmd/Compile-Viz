"""
CompileViz Parser Module
Recursive descent parser that builds an Abstract Syntax Tree (AST).
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any
from .lexer import Token


# ─── AST Node Classes ────────────────────────────────────────────────────────

@dataclass
class ASTNode:
    node_type: str
    children: List[Any] = field(default_factory=list)
    value: Optional[str] = None
    line: Optional[int] = None

    def to_dict(self):
        return {
            'node_type': self.node_type,
            'value': self.value,
            'line': self.line,
            'children': [c.to_dict() if isinstance(c, ASTNode) else str(c) for c in self.children]
        }


class ParseError(Exception):
    def __init__(self, message, line=None, column=None):
        super().__init__(message)
        self.line = line
        self.column = column


# ─── Parser ──────────────────────────────────────────────────────────────────

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.errors = []

    def current(self) -> Optional[Token]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def peek(self, offset=1) -> Optional[Token]:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return None

    def consume(self, expected_type=None, expected_value=None) -> Token:
        tok = self.current()
        if tok is None:
            raise ParseError("Unexpected end of input")
        if expected_type and tok.type != expected_type:
            raise ParseError(
                f"Expected {expected_type} but got '{tok.value}' ({tok.type})",
                tok.line, tok.column
            )
        if expected_value and tok.value != expected_value:
            raise ParseError(
                f"Expected '{expected_value}' but got '{tok.value}'",
                tok.line, tok.column
            )
        self.pos += 1
        return tok

    def match(self, *types) -> bool:
        tok = self.current()
        return tok is not None and tok.type in types

    def match_value(self, *values) -> bool:
        tok = self.current()
        return tok is not None and tok.value in values

    # ── Grammar Rules ─────────────────────────────────────────────────────────

    def parse(self) -> ASTNode:
        program = ASTNode('Program', line=1)
        while self.current() is not None:
            try:
                stmt = self.parse_statement()
                if stmt:
                    program.children.append(stmt)
            except ParseError as e:
                self.errors.append({
                    'message': str(e),
                    'line': getattr(e, 'line', None),
                    'column': getattr(e, 'column', None)
                })
                # Skip to next semicolon or brace for error recovery
                while self.current() and self.current().type not in ('SEMICOLON', 'RBRACE'):
                    self.pos += 1
                if self.current() and self.current().type == 'SEMICOLON':
                    self.pos += 1
        return program

    def parse_statement(self) -> Optional[ASTNode]:
        tok = self.current()
        if tok is None:
            return None

        # Variable declaration: int x = 5;
        if tok.type == 'KEYWORD' and tok.value in ('int', 'float', 'string', 'bool'):
            return self.parse_declaration()

        # If statement
        elif tok.type == 'KEYWORD' and tok.value == 'if':
            return self.parse_if()

        # While loop
        elif tok.type == 'KEYWORD' and tok.value == 'while':
            return self.parse_while()

        # For loop
        elif tok.type == 'KEYWORD' and tok.value == 'for':
            return self.parse_for()

        # Function definition
        elif tok.type == 'KEYWORD' and tok.value == 'func':
            return self.parse_function()

        # Return statement
        elif tok.type == 'KEYWORD' and tok.value == 'return':
            return self.parse_return()

        # Print statement
        elif tok.type == 'KEYWORD' and tok.value == 'print':
            return self.parse_print()

        # Assignment or function call: x = ... or foo(...)
        elif tok.type == 'IDENTIFIER':
            return self.parse_assign_or_call()

        # Block end
        elif tok.type == 'RBRACE':
            return None

        else:
            raise ParseError(f"Unexpected token '{tok.value}'", tok.line, tok.column)

    def parse_declaration(self) -> ASTNode:
        type_tok = self.consume()
        name_tok = self.consume('IDENTIFIER')
        node = ASTNode('Declaration', value=f"{type_tok.value} {name_tok.value}", line=type_tok.line)
        node.children.append(ASTNode('Type', value=type_tok.value, line=type_tok.line))
        node.children.append(ASTNode('Name', value=name_tok.value, line=name_tok.line))
        if self.match('ASSIGN'):
            self.consume('ASSIGN')
            expr = self.parse_expression()
            node.children.append(expr)
        self.consume('SEMICOLON')
        return node

    def parse_if(self) -> ASTNode:
        tok = self.consume('KEYWORD')  # 'if'
        node = ASTNode('IfStatement', line=tok.line)
        self.consume('LPAREN')
        condition = self.parse_expression()
        node.children.append(ASTNode('Condition', children=[condition], line=tok.line))
        self.consume('RPAREN')
        self.consume('LBRACE')
        then_block = ASTNode('ThenBlock', line=tok.line)
        while self.current() and self.current().type != 'RBRACE':
            stmt = self.parse_statement()
            if stmt:
                then_block.children.append(stmt)
        self.consume('RBRACE')
        node.children.append(then_block)
        # else
        if self.current() and self.current().value == 'else':
            self.consume()
            self.consume('LBRACE')
            else_block = ASTNode('ElseBlock', line=tok.line)
            while self.current() and self.current().type != 'RBRACE':
                stmt = self.parse_statement()
                if stmt:
                    else_block.children.append(stmt)
            self.consume('RBRACE')
            node.children.append(else_block)
        return node

    def parse_while(self) -> ASTNode:
        tok = self.consume('KEYWORD')
        node = ASTNode('WhileLoop', line=tok.line)
        self.consume('LPAREN')
        condition = self.parse_expression()
        node.children.append(ASTNode('Condition', children=[condition], line=tok.line))
        self.consume('RPAREN')
        self.consume('LBRACE')
        body = ASTNode('Body', line=tok.line)
        while self.current() and self.current().type != 'RBRACE':
            stmt = self.parse_statement()
            if stmt:
                body.children.append(stmt)
        self.consume('RBRACE')
        node.children.append(body)
        return node

    def parse_for(self) -> ASTNode:
        tok = self.consume('KEYWORD')
        node = ASTNode('ForLoop', line=tok.line)
        self.consume('LPAREN')
        # init
        init = self.parse_declaration() if self.current() and self.current().type == 'KEYWORD' else self.parse_assign_or_call()
        node.children.append(ASTNode('Init', children=[init], line=tok.line))
        cond = self.parse_expression()
        node.children.append(ASTNode('Condition', children=[cond], line=tok.line))
        self.consume('SEMICOLON')
        # update
        update = self.parse_assign_or_call(no_semi=True)
        node.children.append(ASTNode('Update', children=[update], line=tok.line))
        self.consume('RPAREN')
        self.consume('LBRACE')
        body = ASTNode('Body', line=tok.line)
        while self.current() and self.current().type != 'RBRACE':
            stmt = self.parse_statement()
            if stmt:
                body.children.append(stmt)
        self.consume('RBRACE')
        node.children.append(body)
        return node

    def parse_function(self) -> ASTNode:
        tok = self.consume('KEYWORD')  # func
        name_tok = self.consume('IDENTIFIER')
        node = ASTNode('FunctionDef', value=name_tok.value, line=tok.line)
        self.consume('LPAREN')
        params = ASTNode('Params', line=tok.line)
        while self.current() and self.current().type != 'RPAREN':
            ptype = self.consume('KEYWORD')
            pname = self.consume('IDENTIFIER')
            params.children.append(ASTNode('Param', value=f"{ptype.value} {pname.value}", line=ptype.line))
            if self.current() and self.current().type == 'COMMA':
                self.consume('COMMA')
        self.consume('RPAREN')
        node.children.append(params)
        self.consume('LBRACE')
        body = ASTNode('Body', line=tok.line)
        while self.current() and self.current().type != 'RBRACE':
            stmt = self.parse_statement()
            if stmt:
                body.children.append(stmt)
        self.consume('RBRACE')
        node.children.append(body)
        return node

    def parse_return(self) -> ASTNode:
        tok = self.consume('KEYWORD')
        node = ASTNode('Return', line=tok.line)
        if self.current() and self.current().type != 'SEMICOLON':
            node.children.append(self.parse_expression())
        self.consume('SEMICOLON')
        return node

    def parse_print(self) -> ASTNode:
        tok = self.consume('KEYWORD')
        node = ASTNode('Print', line=tok.line)
        self.consume('LPAREN')
        while self.current() and self.current().type != 'RPAREN':
            node.children.append(self.parse_expression())
            if self.current() and self.current().type == 'COMMA':
                self.consume('COMMA')
        self.consume('RPAREN')
        self.consume('SEMICOLON')
        return node

    def parse_assign_or_call(self, no_semi=False) -> ASTNode:
        name_tok = self.consume('IDENTIFIER')
        if self.current() and self.current().type == 'LPAREN':
            # Function call
            node = ASTNode('FunctionCall', value=name_tok.value, line=name_tok.line)
            self.consume('LPAREN')
            while self.current() and self.current().type != 'RPAREN':
                node.children.append(self.parse_expression())
                if self.current() and self.current().type == 'COMMA':
                    self.consume('COMMA')
            self.consume('RPAREN')
            if not no_semi:
                self.consume('SEMICOLON')
        else:
            # Assignment
            node = ASTNode('Assignment', value=name_tok.value, line=name_tok.line)
            node.children.append(ASTNode('Name', value=name_tok.value, line=name_tok.line))
            self.consume('ASSIGN')
            node.children.append(self.parse_expression())
            if not no_semi:
                self.consume('SEMICOLON')
        return node

    def parse_expression(self) -> ASTNode:
        return self.parse_logical()

    def parse_logical(self) -> ASTNode:
        left = self.parse_comparison()
        while self.current() and self.current().type in ('OP_AND', 'OP_OR'):
            op = self.consume()
            right = self.parse_comparison()
            node = ASTNode('BinaryOp', value=op.value, line=op.line)
            node.children = [left, right]
            left = node
        return left

    def parse_comparison(self) -> ASTNode:
        left = self.parse_additive()
        while self.current() and self.current().type in ('OP_EQ', 'OP_NEQ', 'OP_LT', 'OP_GT', 'OP_LTE', 'OP_GTE'):
            op = self.consume()
            right = self.parse_additive()
            node = ASTNode('BinaryOp', value=op.value, line=op.line)
            node.children = [left, right]
            left = node
        return left

    def parse_additive(self) -> ASTNode:
        left = self.parse_multiplicative()
        while self.current() and self.current().type in ('PLUS', 'MINUS'):
            op = self.consume()
            right = self.parse_multiplicative()
            node = ASTNode('BinaryOp', value=op.value, line=op.line)
            node.children = [left, right]
            left = node
        return left

    def parse_multiplicative(self) -> ASTNode:
        left = self.parse_unary()
        while self.current() and self.current().type in ('MULTIPLY', 'DIVIDE', 'MODULO'):
            op = self.consume()
            right = self.parse_unary()
            node = ASTNode('BinaryOp', value=op.value, line=op.line)
            node.children = [left, right]
            left = node
        return left

    def parse_unary(self) -> ASTNode:
        if self.current() and self.current().type == 'MINUS':
            op = self.consume()
            operand = self.parse_primary()
            node = ASTNode('UnaryOp', value='-', line=op.line)
            node.children = [operand]
            return node
        return self.parse_primary()

    def parse_primary(self) -> ASTNode:
        tok = self.current()
        if tok is None:
            raise ParseError("Unexpected end of expression")

        if tok.type == 'INTEGER':
            self.consume()
            return ASTNode('Integer', value=tok.value, line=tok.line)
        elif tok.type == 'FLOAT':
            self.consume()
            return ASTNode('Float', value=tok.value, line=tok.line)
        elif tok.type == 'STRING':
            self.consume()
            return ASTNode('String', value=tok.value, line=tok.line)
        elif tok.type == 'KEYWORD' and tok.value in ('true', 'false'):
            self.consume()
            return ASTNode('Boolean', value=tok.value, line=tok.line)
        elif tok.type == 'IDENTIFIER':
            self.consume()
            if self.current() and self.current().type == 'LPAREN':
                node = ASTNode('FunctionCall', value=tok.value, line=tok.line)
                self.consume('LPAREN')
                while self.current() and self.current().type != 'RPAREN':
                    node.children.append(self.parse_expression())
                    if self.current() and self.current().type == 'COMMA':
                        self.consume('COMMA')
                self.consume('RPAREN')
                return node
            return ASTNode('Identifier', value=tok.value, line=tok.line)
        elif tok.type == 'LPAREN':
            self.consume('LPAREN')
            expr = self.parse_expression()
            self.consume('RPAREN')
            return expr
        else:
            raise ParseError(f"Unexpected token in expression: '{tok.value}'", tok.line, tok.column)


def parse(tokens):
    parser = Parser(tokens)
    ast = parser.parse()
    return ast, parser.errors
