from fastapi import FastAPI, HTTPException
import httpx
from typing import Dict
from cachetools import TTLCache
from asyncache import cached
import redis
import json

app = FastAPI(
    title="API Cache Service",
    description="A simple API that queries JSONPlaceholder API",
    version="1.0.0"
)

EXTERNAL_API_BASE_URL = "https://pokeapi.co/api/v2"
# cache = TTLCache(maxsize=100, ttl=300)
redis_client = redis.Redis(host='redis', port=6379, db=0)

@app.get("/pokemon", response_model=Dict)
# @cached(cache)
async def get_posts():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EXTERNAL_API_BASE_URL}/pokemon")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"External API error: {str(e)}")

@app.get("/pokemon/{post_id}")
# @cached(cache)
async def get_post(post_id: int):

    try:
        cached_pokemon = redis_client.get(f"pokemon_{post_id}")
        if cached_pokemon:
            # Decode the cached data
            cached_pokemon = json.loads(cached_pokemon.decode('utf-8'))
            return cached_pokemon
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EXTERNAL_API_BASE_URL}/pokemon/{post_id}")
            response.raise_for_status()
            
            encoded = json.dumps(response.json(), indent=2).encode('utf-8')
            redis_client.set(f"pokemon_{post_id}", encoded)

            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"External API error: {str(e)}")