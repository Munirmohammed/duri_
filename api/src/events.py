import json
import asyncio
import aio_pika
from .core import crud, tables, schema, db

async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        parsed_message = message.body.decode('utf-8')
        mess_json = json.loads(parsed_message)
        print('------------>', mess_json)
        database = db.SessionLocal()
        crud_notification = crud.Notification(tables.Notification,database)
        notification_obj_create = schema.Notification(
            data=mess_json,
            workspace_id='aeb8b025-73db-4fd7-bb3e-d2bda0fddad6',
        )
        notification_obj=crud_notification.create(notification_obj_create)
        database.commit()
        database.close()

async def consume(queue):
    while queue:
        try:
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    print(message)
                    await process_message(message)
        except Exception as e: #aio_pika.exceptions.ChannelNotFound:
            print("Channel closed by broker, reconnecting...")
            await asyncio.sleep(5)  # Wait before reconnecting
            continue