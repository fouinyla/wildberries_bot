from httpx import Response, TimeoutException, AsyncClient
import asyncio
from random import randint
from typing import Optional, Dict

TIMEOUT = 40
MAX_RETRIES = 7


async def request_with_retry(
        client: AsyncClient,
        method: str,
        url: str,
        params: Dict = None,
        headers: Dict = None,
        data: Dict = None,
        json: Dict = None,
        ) -> Optional[Response]:
    """
    Coroutine for sending async requests with retries
    """
    data_for_log = f'{url=}, {method=}, {params=}, {headers=}, {data=}, {json=}'
    for n in range(MAX_RETRIES):
        try:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                data=data,
                json=json,
                timeout=TIMEOUT,
                follow_redirects=True)
        except TimeoutException as err:
            print(f'Retry # {n} failed: {err=}, {data_for_log}')
            # await asyncio.sleep(2 ** n + randint(0, 1000) / 1000)  # add jitter 0-1000 ms
            await asyncio.sleep(5 + (randint(0, 1000) / 1000))
        except Exception as err:
            print(f'Retry # {n} failed: {err=}, {data_for_log}')
            # notify admins
            return None
        else:
            if response.status_code == 500:
                print(f'Retry # {n} failed: status=500, {data_for_log}')
                await asyncio.sleep(5 + (randint(0, 1000) / 1000))
            else:
                return response
