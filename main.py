from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Header
import cloudinary.uploader
from fastapi.middleware.cors import CORSMiddleware
import os

# Configurar Cloudinary con variables de entorno
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUDNAME"),
    api_key=os.environ.get("CLOUDINARY_APIKEY"),
    api_secret=os.environ.get("CLOUDINARY_APISECRET")
)

# Lista temporal de URLs
photos = []

# Token simple para login
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "123456")  # Cambia a algo seguro

app = FastAPI(title="Showroom API")

# CORS para tu panel web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O pon tu dominio en producción
    allow_methods=["*"],
    allow_headers=["*"]
)

# Dependencia para verificar token en headers
def verify_token(authorization: str = Header(...)):
    if authorization != f"Bearer {ADMIN_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

# Endpoints

@app.get("/api/photos")
def get_photos():
    """Devuelve todas las URLs de fotos"""
    return photos

@app.post("/api/photos")
async def upload_photo(file: UploadFile = File(...), token: str = Depends(verify_token)):
    """Sube una foto a Cloudinary"""
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    result = cloudinary.uploader.upload(file.file, folder="showroom")
    url = result["secure_url"]
    photos.append(url)
    return {"url": url}

@app.delete("/api/photos")
def delete_photo(url: str, token: str = Depends(verify_token)):
    """Elimina una foto de la lista"""
    if url in photos:
        photos.remove(url)
        return {"detail": "Deleted"}
    raise HTTPException(status_code=404, detail="Photo not found")

@app.put("/api/photos")
async def replace_photo(old_url: str, file: UploadFile = File(...), token: str = Depends(verify_token)):
    """Reemplaza una foto existente por una nueva"""
    if old_url not in photos:
        raise HTTPException(status_code=404, detail="Old photo not found")
    
    # Subir nueva foto
    result = cloudinary.uploader.upload(file.file, folder="showroom")
    new_url = result["secure_url"]
    
    # Reemplazar en la lista
    index = photos.index(old_url)
    photos[index] = new_url
    return {"old_url": old_url, "new_url": new_url}

