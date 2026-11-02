"""Brace-aware authored-text macro parsing, without KB or diagnostic dependencies."""
from dataclasses import dataclass


@dataclass(frozen=True)
class MacroCall:
    """A parsed two-argument macro call."""

    name: str
    args: tuple[str, str]
    start: int
    end: int


def parse_two_arg_macro_calls(
    text: str,
    name: str,
) -> tuple[list[MacroCall], list[str]]:
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
            first_start = _skip_whitespace(text, after)
            arg1, first_end = _parse_braced_arg(text, first_start)
            second_start = _skip_whitespace(text, first_end)
            arg2, second_end = _parse_braced_arg(text, second_start)
        except ValueError as exc:
            issues.append(str(exc))
            pos = after
            continue
        calls.append(MacroCall(name=name, args=(arg1, arg2), start=start, end=second_end))
        pos = second_end
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

