from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.responses import Response
from rembg import remove, new_session
import requests
import os

app = FastAPI()

# Pixelcut API Key
PIXELCUT_API_KEY = "yDYS9v5GN3w1fZ8co5UY7oDB"

# App API Key
APP_API_KEY = os.getenv("APP_API_KEY")

# fallback unlimited local model
session = new_session("u2net")


@app.get("/")
async def home():
    return {"status": "Hybrid BG Remove API Running: Pixelcut + Rembg Fallback"}


@app.post("/remove-bg")
async def remove_bg(
    image: UploadFile = File(...),
    x_rashed_api_key: str = Header(None)
):
    if x_rashed_api_key != APP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    image_data = await image.read()

    # 1st try: Pixelcut
    try:
        if PIXELCUT_API_KEY:
            headers = {
                "X-API-KEY": PIXELCUT_API_KEY
            }

            files = {
                "image": ("image.png", image_data, "image/png")
            }

            data = {
                "format": "png"
            }

            pixelcut_response = requests.post(
                "https://api.developer.pixelcut.ai/v1/remove-background",
                headers=headers,
                files=files,
                data=data,
                timeout=60
            )

            print("Pixelcut status:", pixelcut_response.status_code)
            print("Pixelcut response:", pixelcut_response.text[:300])

            if pixelcut_response.status_code == 200:
                return Response(
                    content=pixelcut_response.content,
                    media_type="image/png"
                )

            if pixelcut_response.status_code in [400, 401, 402, 403, 429, 500, 502, 503, 504]:
                print("Pixelcut failed. Falling back to rembg...")

    except Exception as e:
        print("Pixelcut exception:", str(e))
        print("Falling back to rembg...")

    # 2nd fallback: unlimited rembg
    try:
        output_image = remove(image_data, session=session)

        return Response(
            content=output_image,
            media_type="image/png"
        )

    except Exception as e:
        print("Rembg fallback failed:", str(e))
        raise HTTPException(status_code=500, detail="Both Pixelcut and fallback failed")
