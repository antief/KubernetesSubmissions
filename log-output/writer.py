import os
from datetime import datetime, timezone
from pathlib import Path
from time import sleep
from uuid import uuid4


OUTPUT_FILE = Path(
    os.getenv("OUTPUT_FILE", "/usr/src/app/files/output.txt")
)

RANDOM_STRING = str(uuid4())


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(
        timespec="milliseconds"
    ).replace("+00:00", "Z")


def main() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    while True:
        line = f"{timestamp()}: {RANDOM_STRING}\n"

        with OUTPUT_FILE.open("a", encoding="utf-8") as output:
            output.write(line)

        print(line, end="", flush=True)
        sleep(5)


if __name__ == "__main__":
    main()
