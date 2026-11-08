"""Brace-aware authored-text macro parsing, without KB or diagnostic dependencies."""
from dataclasses import dataclass


@dataclass(frozen=True)
class MacroCall:
    """A parsed macro call with its original source span."""

    name: str
    args: tuple[str, ...]
    start: int
    end: int


def parse_two_arg_macro_calls(
    text: str,
    name: str,
) -> tuple[list[MacroCall], list[str]]:
    return parse_macro_calls(text, name, 2)


def parse_macro_calls(
    text: str, name: str, argument_count: int,
) -> tuple[list[MacroCall], list[str]]:
    """Read a fixed-arity macro without interpreting mathematics in its arguments."""
    calls: list[MacroCall] = []
    issues: list[str] = []
    macro = "\\" + name
    pos = 0
    while True:
        start = text.find(macro, pos)
        if start == -1:
            break
        after = start + len(macro)
        if after < len(text) and (text[after].isalnum() or text[after] == "_"):
            pos = after
            continue
        try:
            end = after
            args = []
            for _ in range(argument_count):
                arg, end = _parse_braced_arg(text, _skip_whitespace(text, end))
                args.append(arg)
        except ValueError as exc:
            issues.append(str(exc))
            pos = after
            continue
        calls.append(MacroCall(name=name, args=tuple(args), start=start, end=end))
        pos = end
    return calls, issues


def _parse_braced_arg(text: str, index: int) -> tuple[str, int]:
    if index >= len(text) or text[index] != "{":
        raise ValueError("Expected braced macro argument")
    depth = 0
    arg_start = index + 1
    pos = index
    while pos < len(text):
        char = text[pos]
        if char == "\\" and pos + 1 < len(text) and text[pos + 1] in "{}\\":
            pos += 2
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[arg_start:pos], pos + 1
        pos += 1
    raise ValueError("Unclosed braced macro argument")


def _skip_whitespace(text: str, index: int) -> int:
    while index < len(text) and text[index].isspace():
        index += 1
    return index

