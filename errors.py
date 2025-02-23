import requests

ARANGODB_ERRORS_FILE = "https://raw.githubusercontent.com/arangodb/arangodb/refs/heads/devel/lib/Basics/errors.dat"  # noqa: E501


def generate_section(line, output):
    text = line[3:].strip()
    print("#" * (len(text) + 4), file=output)
    print(f"# {text} #", file=output)
    print("#" * (len(text) + 4) + "\n", file=output)


def generate_error(line, output):
    text = line.split(",")
    err = text[0].strip()[6:]
    if err.startswith("ARANGO_"):
        err = err[7:]
    code = text[1].strip()
    cmt = text[2].strip('"')
    print(f"# {cmt}\n{err} = {code}\n", file=output)


def main():
    response = requests.get(ARANGODB_ERRORS_FILE)
    response.raise_for_status()

    lines = response.text.splitlines()
    with open("errno.py", "w") as output:
        for idx, line in enumerate(lines):
            if line.startswith("## ") and not lines[idx - 1].startswith("## "):
                generate_section(line, output)
            elif line.startswith("ERROR_"):
                generate_error(line, output)


if __name__ == "__main__":
    main()
