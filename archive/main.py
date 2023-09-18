import argparse
import ast
import re
from dataclasses import dataclass


@dataclass
class NameIdentifier:
    identifier: str
    line_number: int
    file: str
    identifier_type: str
    full_identifier: str

    def __str__(self) -> str:
        return f"{self.identifier},{self.line_number},{self.file},{self.identifier_type},{self.full_identifier}"


class FileTypeAction(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: str,
        values: str,
        option_string: str | None = None,
    ) -> None:
        file_name = values
        if len(file_name.split(".")) != 2 or file_name.split(".")[-1] != "py":
            raise argparse.ArgumentTypeError("File needs to be a Python file (.py)")
        setattr(namespace, self.dest, file_name)


def split_pascal_case(text: str) -> list[str]:
    tokens = re.findall(r"[A-Z][a-z]*|[a-z]+", text)
    return tokens


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parses all user-defined identifiers",
    )
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        action=FileTypeAction,
        required=True,
        help="File name (.py) to parse",
    )
    parser.add_argument(
        "--out",
        "-o",
        type=str,
        default="out",
        help="Output file containing identifiers. Defaults to 'out'",
    )
    parser.add_argument(
        "--delimiter",
        "-d",
        type=str,
        default=",",
        help="Delimiter for output. Defaults to ','",
    )
    args = parser.parse_args()

    with open(args.file, "r") as f:
        python_code = f.read()

    root = ast.parse(python_code)
    file = args.file
    identifiers = []
    for node in ast.walk(root):
        if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load):
            for token in node.id.split("_"):
                if len(token) == 0:
                    continue

                identifiers.append(
                    NameIdentifier(token, node.lineno, file, "Variable", node.id),
                )

        if isinstance(node, ast.FunctionDef):
            if node.name.startswith("__") and node.name.endswith("__"):
                continue
            for token in node.name.split("_"):
                if len(token) == 0:
                    continue
                identifiers.append(
                    NameIdentifier(token, node.lineno, file, "Function", node.name),
                )

        if isinstance(node, ast.ClassDef):
            for token in split_pascal_case(node.name):
                identifiers.append(
                    NameIdentifier(
                        token.casefold(), node.lineno, file, "Class", node.name
                    ),
                )

    # TODO: think about having a flag for -a, -w, -s (sysout)
    for id in identifiers:
        print(str(id))
    return 73


if __name__ == "__main__":
    exit(main())
