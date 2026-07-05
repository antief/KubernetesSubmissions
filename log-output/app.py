from datetime import datetime, timezone
from time import sleep
from uuid import uuid4


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def main() -> None:
    random_string = str(uuid4())

    while True:
        print(f"{timestamp()}: {random_string}", flush=True)
        sleep(5)


if __name__ == "__main__":
    main()