# pyslock

High-performance distributed sync service and atomic DB. Provides good multi-core support through lock queues, high-performance asynchronous binary network protocols. Can be used for spikes, synchronization, event notification, concurrency control. https://github.com/snower/slock

# Install

```bash
pip install pyslock
```

# Event 

```python
import redis
import pyslock

slock_client = pyslock.Client("localhost")

event = slock_client.Event("test", 5, 120, False)
event.set()
```

```python
import asyncio
import pyslock

async def run():
    slock_client = pyslock.AsyncClient("localhost")

    event = slock_client.Event("test", 5, 120, False)
    await event.set()

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
```

# License

slock uses the MIT license, see LICENSE file for the details.