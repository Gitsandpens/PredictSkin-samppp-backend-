import os
from contextlib import asynccontextmanager
from typing import List, Literal, Optional
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from model.similarity import CLASSES, ReferenceStore
from utils.auth import check_login, create_user, current_user, init_db, make_token
from utils.image_utils import decode_upload
from utils.nutrition import bmi_info, build_plan

store = ReferenceStore()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    store.load()  # scan dataset, build and cache reference embeddings (restart to refresh)
    yield


app = FastAPI(title="PredictSkin API", lifespan=lifespan)
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])


class Profile(BaseModel):
    age: int = Field(ge=1, le=120)
    gender: Optional[str] = None
    height_cm: float = Field(ge=50, le=250)
    weight_kg: float = Field(ge=10, le=400)
    activity: Literal["Sedentary", "Lightly active", "Moderately active", "Very active"] = "Lightly active"
    goal: Literal["LOSE", "MAINTAIN", "GAIN"] = "MAINTAIN"
    diet: Literal["veg", "egg", "nonveg"] = "veg"
    allergies: List[str] = []


@app.get("/health")
def health():
    return {"status": "ok", "dataset_ready": store.ready}


@app.get("/dataset-status")
def dataset_status():
    return store.status()


@app.get("/reference-image/{key}")
def reference_image(key: str):
    path = store.paths.get(key)
    if key not in CLASSES or not path:
        raise HTTPException(404, "Reference image not found.")
    return FileResponse(path)


@app.post("/predict-skin")
async def predict_skin(image: UploadFile = File(...), user: dict = Depends(current_user)):
    if not store.ready:
        detail = store.error or "Reference dataset incomplete. Add one valid reference image for each supported category."
        if store.missing:
            detail += " Missing: " + ", ".join(CLASSES[k] for k in store.missing) + "."
            if store.sync_note:
                detail += " " + store.sync_note
        raise HTTPException(409, detail)
    img = decode_upload(await image.read())  # processed in memory only, never saved
    return store.predict(img)


@app.post("/health-profile")
def health_profile(p: Profile):
    return bmi_info(p.weight_kg, p.height_cm, p.age)  # nothing is stored


@app.post("/nutrition-plan")
def nutrition_plan(p: Profile, user: dict = Depends(current_user)):
    plan = build_plan(p.model_dump())
    plan["bmi"] = bmi_info(p.weight_kg, p.height_cm, p.age)
    return plan


class SignupBody(BaseModel):
    name: str
    email: str
    password: str


class LoginBody(BaseModel):
    email: str
    password: str


@app.post("/auth/signup")
def signup(b: SignupBody):
    user = create_user(b.name, b.email, b.password)
    return {"token": make_token(user), "user": user}


@app.post("/auth/login")
def login(b: LoginBody):
    user = check_login(b.email, b.password)
    return {"token": make_token(user), "user": user}


@app.get("/auth/me")
def me(user: dict = Depends(current_user)):
    return user
