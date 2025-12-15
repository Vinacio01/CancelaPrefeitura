from fastapi import FastAPI
from pydantic import BaseModel
from banco.banco import BancoDeDados
from core.controle_cancela import ControleCancela

app = FastAPI(
    title="API da Cancela da Prefeitura",
    version="1.0.0"
)

db = BancoDeDados()
controle = ControleCancela(db)


# =========================
# EVENTO DE STARTUP
# =========================
@app.on_event("startup")
def carregar_placas_padrao():
    # Evita duplicação ao reiniciar a API
    db.adicionar_placa("TLZ2D52", "Veículo autorizado padrão")


# =========================
# MODELOS
# =========================
class PlacaModel(BaseModel):
    placa: str
    descricao: str = ""


class VerificarModel(BaseModel):
    placa: str


class IntelbrasLPR(BaseModel):
    plate: str
    confidence: int | None = 0
    timestamp: str | None = ""
    image_url: str | None = ""


# =========================
# ROTAS
# =========================
@app.get("/")
def healthcheck():
    return {"status": "API da Cancela ativa"}


@app.post("/placas")
def adicionar_placa(dados: PlacaModel):
    sucesso = db.adicionar_placa(dados.placa.upper(), dados.descricao)
    if sucesso:
        return {"status": "ok", "mensagem": "Placa adicionada com sucesso"}
    return {"status": "erro", "mensagem": "Placa já existe"}


@app.get("/placas")
def listar_placas():
    return {"placas": db.listar_placas()}


@app.delete("/placas/{placa}")
def remover_placa(placa: str):
    sucesso = db.remover_placa(placa.upper())
    if sucesso:
        return {"status": "ok", "mensagem": "Placa removida"}
    return {"status": "erro", "mensagem": "Placa não encontrada"}


@app.post("/verificar")
def verificar(dados: VerificarModel):
    autorizado, mensagem = controle.verificar_placa(dados.placa.upper())
    return {
        "autorizado": autorizado,
        "mensagem": mensagem
    }


@app.get("/movimentacao")
def listar_movimentacao():
    return {"movimentacao": db.listar_movimentacao()}


@app.post("/camera/intelbras")
def receber_placa_intelbras(dados: IntelbrasLPR):
    placa = dados.plate.upper().strip()
    autorizado, mensagem = controle.verificar_placa(placa)

    return {
        "autorizado": autorizado,
        "mensagem": mensagem
    }


@app.post("/camera/simular")
def simular_camera(payload: dict):
    placa = payload.get("plate", "").upper().strip()
    autorizado, mensagem = controle.verificar_placa(placa)

    return {
        "autorizado": autorizado,
        "mensagem": mensagem,
        "simulacao": True
    }
