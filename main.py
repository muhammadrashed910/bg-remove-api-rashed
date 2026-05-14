from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.responses import Response
from rembg import remove, new_session

app = FastAPI()

API_KEY = "rashed_unlimited_key_2026"

# ছোট model, Railway free/trial এ কম crash করবে
session = new_session("u2net")

@app.get("/")
async def home():
    return {"status": "Rashed BG Remove API Running"}

@app.post("/remove-bg")
async def remove_bg(
    image: UploadFile = File(...),
    x_rashed_api_key: str = Header(None)
):
    if x_rashed_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    input_image = await image.read()
    output_image = remove(input_image, session=session)

    return Response(content=output_image, media_type="image/png")
