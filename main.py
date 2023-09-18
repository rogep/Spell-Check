import argparse
import ast
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class NameIdentifier:
    token: str
    line_number: int
    file: str
    identifier: str
    full_token: str

    def __str__(self) -> str:
        return f"{self.token},{self.line_number},{self.file},{self.identifier},{self.full_token}"


# class FileTypeAction(argparse.Action):
#     def __call__(
#         self,
#         parser: argparse.ArgumentParser,
#         namespace: str,
#         values: str,
#         option_string: str | None = None,
#     ) -> None:
#         file_name = values
#         if len(file_name.split(".")) != 2 or file_name.split(".")[-1] != "py":
#             raise argparse.ArgumentTypeError("File needs to be a Python file (.py)")
#         setattr(namespace, self.dest, file_name)


def split_pascal_case(text: str) -> list[str]:
    tokens = re.findall(r"[A-Z][a-z]*|[a-z]+", text)
    return tokens


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parses all user-defined identifiers",
    )
    parser.add_argument(
        "--path",
        "-p",
        type=str,
        # action=FileTypeAction,
        required=True,
        help="Directory to recursively traverse for python files.",
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
    parser.add_argument(
        "--lang",
        "-l",
        type=str,
        choices=["b", "british", "aus", "uk", "a", "american", "us", "usa"],
        default="british",
    )
    args = parser.parse_args()

    files = Path(args.path).rglob("*.py")
    if args.lang in ["b", "british", "aus", "uk"]:
        dictionary = "british-english"
    else:
        dictionary = "american-english"
    with open(dictionary, "r") as f:
        words = f.read().splitlines()

    for file in files:
        with open(file, "r") as f:
            python_code = f.read()

        root = ast.parse(python_code)
        file = str(file)
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
            if id.token not in words:
                print(str(id))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
