from fastapi import FastAPI
from pydantic import BaseModel
from banco.banco import BancoDeDados
from core.controle_cancela import ControleCancela

app = FastAPI(title="API da Cancela da Prefeitura")

db = BancoDeDados()
controle = ControleCancela(db)



class PlacaModel(BaseModel):
    placa: str
    descricao: str = ""


class VerificarModel(BaseModel):
    placa: str



@app.post("/placas")
def adicionar_placa(dados: PlacaModel):
    sucesso = db.adicionar_placa(dados.placa, dados.descricao)
    if sucesso:
        return {"status": "ok", "mensagem": "Placa adicionada com sucesso"}
    return {"status": "erro", "mensagem": "Placa já existe"}


@app.get("/placas")
def listar_placas():
    dados = db.listar_placas()
    return {"placas": dados}


@app.delete("/placas/{placa}")
def remover_placa(placa: str):
    sucesso = db.remover_placa(placa)
    if sucesso:
        return {"status": "ok", "mensagem": "Placa removida"}
    return {"status": "erro", "mensagem": "Placa não encontrada"}



@app.post("/verificar")
def verificar(dados: VerificarModel):
    resultado, mensagem = controle.verificar_placa(dados.placa)
    return {
        "resultado": resultado,
        "mensagem": mensagem
    }


@app.get("/movimentacao")
def listar_movimentacao():
    mov = db.listar_movimentacao()
    return {"movimentacao": mov}


class IntelbrasLPR(BaseModel):
    plate: str                   
    confidence: int | None = 0   
    timestamp: str | None = ""   
    image_url: str | None = ""   


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
