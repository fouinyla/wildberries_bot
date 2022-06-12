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
    data_for_log = f'{url=}, {method=}, {params=}, {headers=}, {data=}, {json=}'
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
        except TimeoutException as err:
            print(f'Retry # {n} failed: {err=}, {data_for_log}')
            if n > MAX_RETRIES:
                print(f'No response received for {n} retries: {err=}, {data_for_log}')
                return None
            n += 1
            # await asyncio.sleep(2 ** n + randint(0, 1000) / 1000)  # add jitter 0-1000 ms
            await asyncio.sleep(5 + (randint(0, 1000) / 1000))
        else:
            if response.status_code != 200:
                print(f'Status={response.status_code}, {data_for_log}')
            return response
