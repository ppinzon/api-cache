from fastapi import FastAPI, HTTPException
import httpx
from typing import List, Dict
import asyncio
from cachetools import TTLCache
from asyncache import cached

app = FastAPI(
    title="API Cache Service",
    description="A simple API that queries JSONPlaceholder API",
    version="1.0.0"
)

EXTERNAL_API_BASE_URL = "https://pokeapi.co/api/v2"
cache = TTLCache(maxsize=100, ttl=300)

@app.get("/pokemon", response_model=Dict)
async def get_posts():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EXTERNAL_API_BASE_URL}/pokemon")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"External API error: {str(e)}")

@app.get("/pokemon/{post_id}")
@cached(cache)
async def get_post(post_id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EXTERNAL_API_BASE_URL}/pokemon/{post_id}")
            response.raise_for_status()
            
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"External API error: {str(e)}")