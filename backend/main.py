from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
import io
import zipfile
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path
import mimetypes

BASE_DIR = Path(os.environ.get("BASE_DIR", os.getcwd())).resolve()

app = FastAPI(title="SD Gallery Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

def resolve_rel(rel_path: str = "") -> Path:
    target = (BASE_DIR / rel_path).resolve()
    if not str(target).startswith(str(BASE_DIR)):
        raise HTTPException(status_code=400, detail="Invalid path")
    return target


@app.get("/api/folders")
def list_folder(path: str = Query("", description="relative path under BASE_DIR")):
    p = resolve_rel(path)
    if not p.exists() or not p.is_dir():
        raise HTTPException(status_code=404, detail="Not found")
    folders = []
    images = []
    for child in sorted(p.iterdir()):
        if child.is_dir():
            folders.append(child.name)
        elif child.is_file() and child.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp", ".gif"]:
            images.append(child.name)
    return {"path": str(Path(path)), "folders": folders, "images": images}


@app.get("/api/image")
def get_image(path: str = Query(..., description="relative file path under BASE_DIR"), download: bool = False):
    p = resolve_rel(path)
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    media_type = mimetypes.guess_type(str(p))[0] or "application/octet-stream"
    if download:
        return FileResponse(path=str(p), media_type=media_type, filename=p.name)
    return FileResponse(path=str(p), media_type=media_type)


@app.get("/api/zip")
def get_zip(path: str = Query("", description="relative directory under BASE_DIR"), files: List[str] = Query(None)):
    p = resolve_rel(path)
    if not p.exists() or not p.is_dir():
        raise HTTPException(status_code=404, detail="Not found")
    if not files:
        raise HTTPException(status_code=400, detail="no files specified")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in files:
            # sanitize and resolve
            try:
                fpath = resolve_rel(str(Path(path) / name))
            except HTTPException:
                continue
            if fpath.exists() and fpath.is_file():
                zf.write(str(fpath), arcname=name)
    buf.seek(0)
    zip_name = (Path(path).name or "images") + ".zip"
    return StreamingResponse(buf, media_type="application/zip", headers={"Content-Disposition": f"attachment; filename=\"{zip_name}\""})
