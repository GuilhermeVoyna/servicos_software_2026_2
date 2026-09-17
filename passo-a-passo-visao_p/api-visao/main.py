import io, os
import requests
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image
from transformers import pipeline

MODELO = os.getenv("MODELO_VISAO", "google/vit-base-patch16-224")
ARMAZENAMENTO_URL = os.getenv("ARMAZENAMENTO_URL", "http://armazenamento-service:8082")

app = FastAPI(title="Serviço de Visão")

print(f"Carregando modelo de visao: ({MODELO})...", flush=True)
classificador = pipeline("image-classification", model = MODELO)
print("Modelo carregado!", flush=True)

@app.get("/")
def status():
    # endpoint leve: alvo do healthcheck agora e da readnessProbe na aula 7
    return {"status": "ok"}

@app.post("/analisar")
async def analisar_imagem(file: UploadFile = File(...)):
    conteudo = await file.read()
    try:
        imagem = Image.open(io.BytesIO(conteudo)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=415, detail="Imagem inválida")

    resultados = classificador(imagem)
    melhor = resultados[0]
    rotulo = melhor["label"]
    confianca = round(float(melhor["score"]), 4)

    files = {"file": (file.filename, conteudo, file.content_type)}
    data = {"rotulo": rotulo}
    try:
        r = requests.post(f"{ARMAZENAMENTO_URL}/salvar",
        files = files, data = data, timeout = 60)
        status_db = ("Salvo com sucesso" if r.status_code ==200 else f"Erro ao salvar ({r.status_code})")
    except requests.RequestException as e:
        status_db = "Falha na comunicacao: {e}"

    return {"rotulo": rotulo, "confianca": confianca, "status_db": status_db}