import asyncio
import json
import os
import time
from collections import defaultdict

from pydantic_ai import Agent

from src.agents.contextual_agent import contextual_agent
from src.core.settings import settings
from src.preprocessing.chunk_splitter import (
    num_tokens_from_string,
    save_as_json,
)

async def fetch(agent: Agent[str], chunk: str, key: str) -> str:
    response = await agent.run(chunk, deps=key)
    return response

async def async_fetch(values: list[str], key: str) -> list[str]:
    tasks = [fetch(contextual_agent, value, key) for value in values]
    responses = await asyncio.gather(*tasks)
    return responses


async def generate_context(data: dict[str, list[str]]) -> dict[str, list[str]]:
    json_to_save: dict[str, list[str]] = defaultdict(list)
    keys_to_fetch_sync: list[str] = []
    tokens_used: int = 0

    for key in data.keys():
        print('Async process started for', key)

        values = data.get(key)
        assert isinstance(values, list)

        total_tokens = sum([num_tokens_from_string(value) for value in values])

        if total_tokens > settings.MAX_TOKENS_PER_MINUITE:
            print(
                f'Async process skipped for {key} due to the number of tokens.'
            )
            keys_to_fetch_sync.append(key)
            continue

        if (total_tokens + tokens_used) > settings.MAX_TOKENS_PER_MINUITE:
            tokens_used = 0
            print('Waiting 60 seconds due to TPM limit...')
            time.sleep(60)

        responses = await async_fetch(values, key)
        chunk_context = [response for response in responses]
        json_to_save[key] = chunk_context

    for key in keys_to_fetch_sync:
        print('Sync process started for', key)
        values = data.get(key)
        assert isinstance(values, list)

        aggregated_contexts: list[str] = []

        for n, value in enumerate(values):
            total_tokens = num_tokens_from_string(value)

            if (total_tokens + tokens_used) > settings.MAX_TOKENS_PER_MINUITE:
                tokens_used = 0
                print('Waiting 60 seconds due to TPM limit...')
                time.sleep(60)

            response = await contextual_agent.run(value, deps=key)

            aggregated_contexts.append(response)

            print(f'{n}/{len(values)}')

        json_to_save[key] = aggregated_contexts

    return json_to_save
