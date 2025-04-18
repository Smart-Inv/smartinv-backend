from fastapi import FastAPI
from firestore_client import db

app = FastAPI()

@app.get('/hello')
def render_hello():
    return {"response":"Hello World"}

@app.post("/productos/")
def agregar_producto(nombre: str, stock: int, precio: float):
    doc_ref = db.collection("productos").document()
    doc_ref.set({
        "nombre": nombre,
        "stock": stock,
        "precio": precio
    })
    return {"id": doc_ref.id}

@app.get("/productos/")
def listar_productos():
    productos = db.collection("productos").stream()
    return [{**doc.to_dict(), "id": doc.id} for doc in productos]
