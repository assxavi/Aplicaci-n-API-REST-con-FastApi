from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from db import Base, engine, get_db
from models import Incidencia
from schema import IncidenciaOut, IncidenciaCreate
from auth import authenticate_user, create_access_token, get_current_username

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Incidentes - FastAPI + MySQL + JWT")

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    ok = authenticate_user(form_data.username, form_data.password)
    if not ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
    token = create_access_token(subject=form_data.username)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/incidencias", response_model=list[IncidenciaOut])
def listar_incidencias(db: Session = Depends(get_db)):
    return db.query(Incidencia).all()

@app.get("/me")
def quien_soy(username: str = Depends(get_current_username)):
    return {"username": username}

@app.post("/incidencias", response_model=IncidenciaOut)
def crear_incidencia(
    data: IncidenciaCreate,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username),
):
    incidencia = Incidencia(**data.model_dump())
    db.add(incidencia)
    db.commit()
    db.refresh(incidencia)
    return incidencia
