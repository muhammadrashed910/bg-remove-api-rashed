from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.responses import Response
import requests
import os
import tempfile

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

    # temp file save
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(input_image)
        temp_path = tmp.name

    # Pixelcut upload endpoint
    files = {
        "image": open(temp_path, "rb")
    }

    headers = {
        "X-API-KEY": PIXELCUT_API_KEY
    }

    response = requests.post(
        "https://api.developer.pixelcut.ai/v1/remove-background",
        headers=headers,
        files=files
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return Response(
        content=response.content,
        media_type="image/png"
    )
