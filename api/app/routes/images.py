from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.image_store import image_store
from pydantic import BaseModel
import httpx
import uuid
from app.deps import get_app
from app.providers.base import ProviderError

router = APIRouter()

class AvatarUpdate(BaseModel):
    filename: str

class ImageGenerateRequest(BaseModel):
    prompt: str
    model: str

class ImageEditRequest(BaseModel):
    imageUrl: str
    prompt: str
    model: str = "dall-e-2"

@router.get("/")
async def get_images():
    return image_store.get_all()

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        content = await file.read()
        filename = file.filename
        image_store.save_image(filename, content)
        return {"url": f"/static/uploads/{filename}", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
async def generate_image(request: ImageGenerateRequest, app=Depends(get_app)):
    try:
        registry = app.state.registry

        # Try to find the provider that owns the requested model first.
        provider = None
        for p in registry.providers:
            # We check if the provider is configured and if it might support this model.
            # Note: ProviderRegistry.candidates could be used here if we adapted it for images.
            if p.configured:
                # If the provider's default model matches, or if it's an OpenAI-compat provider
                # and the model ID matches a known pattern, it's a good candidate.
                if p.default_model == request.model:
                    provider = p
                    break

        # Fallback: Find any configured provider that doesn't explicitly fail
        # (since we don't have a 'supports_image' flag on the base class).
        if not provider:
            for p in registry.providers:
                if p.configured:
                    provider = p
                    break

        if not provider:
            raise HTTPException(status_code=503, detail="No image generation provider available")

        image_url = await provider.generate_image(request.model, request.prompt)

        async with httpx.AsyncClient() as client:
            resp = await client.get(image_url)
            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail="Failed to download generated image")
            content = resp.content

        filename = f"gen_{uuid.uuid4().hex[:12]}.png"
        image_store.save_image(filename, content)

        return {"url": f"/static/uploads/{filename}", "filename": filename}
    except ProviderError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/edit")
async def edit_image(request: ImageEditRequest, app=Depends(get_app)):
    try:
        registry = app.state.registry

        # Try to find the provider that owns the requested model.
        provider = None
        for p in registry.providers:
            if p.configured and p.default_model == request.model:
                provider = p
                break

        if not provider:
            for p in registry.providers:
                if p.configured:
                    provider = p
                    break

        if not provider:
            raise HTTPException(status_code=503, detail="No image editing provider available")

        image_url = await provider.edit_image(request.model, request.imageUrl, request.prompt)

        async with httpx.AsyncClient() as client:
            resp = await client.get(image_url)
            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail="Failed to download edited image")
            content = resp.content

        filename = f"edit_{uuid.uuid4().hex[:12]}.png"
        image_store.save_image(filename, content)

        return {"url": f"/static/uploads/{filename}", "filename": filename}
    except ProviderError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/avatar")
async def set_avatar(data: AvatarUpdate):
    try:
        image_store.set_avatar(data.filename)
        return {"success": True}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{filename}")
async def delete_image(filename: str):
    try:
        image_store.delete_image(filename)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
