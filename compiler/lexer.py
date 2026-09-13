"""
CompileViz Lexer Module
Tokenizes source code into a stream of tokens.
"""

import re
from dataclasses import dataclass
from typing import List, Optional

# Token types
TOKEN_TYPES = [
    ('FLOAT',      r'\d+\.\d+'),
    ('INTEGER',    r'\d+'),
    ('STRING',     r'"[^"]*"'),
    ('KEYWORD',    r'\b(if|else|while|for|int|float|string|bool|return|print|true|false|and|or|not|func|end)\b'),
    ('BOOLEAN',    r'\b(true|false)\b'),
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('OP_EQ',      r'=='),
    ('OP_NEQ',     r'!='),
    ('OP_LTE',     r'<='),
    ('OP_GTE',     r'>='),
    ('OP_AND',     r'&&'),
    ('OP_OR',      r'\|\|'),
    ('ASSIGN',     r'='),
    ('OP_LT',      r'<'),
    ('OP_GT',      r'>'),
    ('PLUS',       r'\+'),
    ('MINUS',      r'-'),
    ('MULTIPLY',   r'\*'),
    ('DIVIDE',     r'/'),
    ('MODULO',     r'%'),
    ('LPAREN',     r'\('),
    ('RPAREN',     r'\)'),
    ('LBRACE',     r'\{'),
    ('RBRACE',     r'\}'),
    ('SEMICOLON',  r';'),
    ('COMMA',      r','),
    ('COLON',      r':'),
    ('COMMENT',    r'//[^\n]*'),
    ('NEWLINE',    r'\n'),
    ('WHITESPACE', r'[ \t]+'),
    ('UNKNOWN',    r'.'),
]

MASTER_PATTERN = re.compile(
    '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_TYPES)
)


@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int

    def to_dict(self):
        return {
            'type': self.type,
            'value': self.value,
            'line': self.line,
            'column': self.column
        }


class LexerError(Exception):
    def __init__(self, message, line, column):
        super().__init__(message)
        self.line = line
        self.column = column


def tokenize(source_code: str) -> List[Token]:
    """Tokenize source code and return list of tokens."""
    tokens = []
    errors = []
    line = 1
    line_start = 0

    for match in MASTER_PATTERN.finditer(source_code):
        kind = match.lastgroup
        value = match.group()
        column = match.start() - line_start + 1

        if kind == 'NEWLINE':
            line += 1
            line_start = match.end()
            continue
        elif kind in ('WHITESPACE', 'COMMENT'):
            continue
        elif kind == 'UNKNOWN':
            errors.append({
                'message': f"Unknown character '{value}'",
                'line': line,
                'column': column
            })
            continue

        tokens.append(Token(type=kind, value=value, line=line, column=column))

    return tokens, errors
