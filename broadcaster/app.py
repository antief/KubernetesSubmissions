import asyncio
import json
import logging
import os
from urllib.request import Request, urlopen

import nats


NATS_URL = os.environ["NATS_URL"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

NATS_SUBJECT = "todos.events"
NATS_QUEUE_GROUP = "todo-broadcasters"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("broadcaster")


def send_webhook(message: str) -> None:
    payload = json.dumps(
        {
            "user": "bot",
            "message": message,
        }
    ).encode()

    request = Request(
        WEBHOOK_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urlopen(request, timeout=10) as response:
        response.read()


async def main() -> None:
    client = await nats.connect(NATS_URL)

    async def handle_message(message) -> None:
        event = json.loads(message.data.decode())
        text = event["message"]

        await asyncio.to_thread(
            send_webhook,
            text,
        )

        logger.info("forwarded message=%r", text)

    await client.subscribe(
        NATS_SUBJECT,
        queue=NATS_QUEUE_GROUP,
        cb=handle_message,
    )

    logger.info(
        "subscribed subject=%s queue=%s",
        NATS_SUBJECT,
        NATS_QUEUE_GROUP,
    )

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
