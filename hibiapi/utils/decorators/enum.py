import ast
import inspect
from enum import Enum
from typing import Dict, Type, TypeVar

_ET = TypeVar("_ET", bound=Type[Enum])


def enum_auto_doc(enum: _ET) -> _ET:
    enum_class_ast, *_ = ast.parse(inspect.getsource(enum)).body
    assert isinstance(enum_class_ast, ast.ClassDef)

    enum_value_comments: Dict[str, str] = {}
    for index, body in enumerate(body_list := enum_class_ast.body):
        if (
            isinstance(body, ast.Assign)
            and (next_index := index + 1) < len(body_list)
            and isinstance(next_body := body_list[next_index], ast.Expr)
        ):
            target, *_ = body.targets
            assert isinstance(target, ast.Name)
            assert isinstance(next_body.value, ast.Constant)
            assert isinstance(member_doc := next_body.value.value, str)
            enum[target.id].__doc__ = member_doc
            enum_value_comments[target.id] = inspect.cleandoc(member_doc)

    if not enum_value_comments and all(member.name == member.value for member in enum):
        return enum

    members_doc = ""
    for member in enum:
        value_document = "-"
        if member.name != member.value:
            value_document += f" `{member.name}` ="
        value_document += f" *`{member.value}`*"
        if doc := enum_value_comments.get(member.name):
            value_document += f" : {doc}"
        members_doc += value_document + "\n"

    enum.__doc__ = f"{enum.__doc__}\n{members_doc}"
    return enum
