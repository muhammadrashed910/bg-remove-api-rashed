from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.responses import Response
import requests
import os

app = FastAPI()

PIXELCUT_API_KEY = os.getenv("PIXELCUT_API_KEY")
APP_API_KEY = os.getenv("APP_API_KEY")


@app.get("/")
async def home():
    return {"status": "Pixelcut API Running"}


@app.post("/remove-bg")
async def remove_bg(
    image: UploadFile = File(...),
    x_rashed_api_key: str = Header(None)
):

    if x_rashed_api_key != APP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    image_data = await image.read()

    headers = {
        "X-API-KEY": PIXELCUT_API_KEY
    }

    files = {
        "image": ("image.png", image_data, "image/png")
    }

    data = {
        "format": "png"
    }

    response = requests.post(
        "https://api.developer.pixelcut.ai/v1/remove-background",
        headers=headers,
        files=files,
        data=data
    )

    print(response.text)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return Response(
        content=response.content,
        media_type="image/png"
    )
