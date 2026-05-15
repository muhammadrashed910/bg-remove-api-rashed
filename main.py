from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.responses import Response
import requests
import os
import base64

app = FastAPI()

PIXELCUT_API_KEY = os.getenv("PIXELCUT_API_KEY")
APP_API_KEY = os.getenv("APP_API_KEY")


@app.get("/")
async def home():
    return {"status": "Rashed Pixelcut BG Remove API Running"}


@app.post("/remove-bg")
async def remove_bg(
    image: UploadFile = File(...),
    x_rashed_api_key: str = Header(None)
):

    if x_rashed_api_key != APP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    input_image = await image.read()

    image_base64 = base64.b64encode(input_image).decode("utf-8")

    headers = {
        "X-API-KEY": PIXELCUT_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    json_data = {
        "image_base64": image_base64,
        "format": "png"
    }

    response = requests.post(
        "https://api.developer.pixelcut.ai/v1/remove-background",
        headers=headers,
        json=json_data
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    result = response.json()

    output_url = result.get("result_url")

    if not output_url:
        raise HTTPException(status_code=500, detail="No output image")

    final_image = requests.get(output_url)

    return Response(
        content=final_image.content,
        media_type="image/png"
    )
