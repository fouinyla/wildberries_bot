from httpx import Response, TimeoutException, AsyncClient
import asyncio
from random import randint
from typing import Optional, Dict

TIMEOUT = 40
MAX_RETRIES = float('inf')


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
    request_function: get, post, delete...
    """
    n = 1
    while True:
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
            response.raise_for_status()
        except TimeoutException as err:
            print(f'Retry # {n} failed: {err=}, {url=}, {method=}, {params=}, {headers=}')
            if n > MAX_RETRIES:
                print(f'No response received for {n} retries: {err=}, {url=}, {method=}, {params=}, {headers=}')
                return None
            n += 1
            # await asyncio.sleep(2 ** n + randint(0, 1000) / 1000)  # add jitter 0-1000 ms
            await asyncio.sleep(5 + (randint(0, 1000) / 1000))
        else:
            return response
