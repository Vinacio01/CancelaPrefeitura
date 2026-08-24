# CancelaPrefeitura

Sistema de **detecção e reconhecimento de placas veiculares** para controle de acesso ao estacionamento da Prefeitura de Caxias do Sul. O projeto identifica placas em imagens/vídeo (via visão computacional + OCR), verifica se estão autorizadas em um banco de dados local e libera ou nega a entrada/saída, registrando toda a movimentação.

## Como funciona

1. **Detecção** — `detectores/detector_placas.py` usa um classificador Haar Cascade (OpenCV) para localizar a região da placa em um frame.
2. **Leitura (OCR)** — `ocr/leitor_ocr.py` recorta a região detectada, faz pré-processamento (escala de cinza, blur, threshold adaptativo) e usa o **EasyOCR** para extrair o texto, validando o resultado contra o padrão de placas Mercosul (`AAA0A00`).
3. **Verificação** — a placa lida é enviada para uma **API FastAPI** (`main/api.py`), que consulta o banco (`banco/banco.py`, SQLite) e decide, via `core/controle_cancela.py`, se é `ENTRADA`, `SAÍDA` ou `ACESSO NEGADO`.
4. **Registro** — cada verificação é persistida na tabela `movimentacao`, permitindo consultar o histórico de entradas/saídas.
5. **Gestão** — `interface/gerenciar_placas.py` oferece um menu em terminal para cadastrar, remover e listar placas autorizadas e consultar a movimentação.

## Estrutura do projeto

CancelaPrefeitura/
├── banco/ # Camada de dados (SQLite): placas autorizadas e movimentação
├── core/ # Regras de negócio (liberar entrada/saída, negar acesso)
├── detectores/ # Detecção de placas com OpenCV (Haar Cascade)
├── ocr/ # Leitura e validação do texto da placa (EasyOCR)
├── interface/ # Menu de gerenciamento via terminal
├── main/ # API (FastAPI) e scripts de execução (câmera/imagem de teste)
├── imagens/ # Imagens de teste
├── videos/ # Vídeos de teste
├── data/ # Banco de dados SQLite (cancela.db)
├── simulate_camera.py # Simula a cancela usando vídeo/imagens de teste, sem câmera real
└── requirements.txt

## Requisitos

- Python 3.10+
- Dependências em `requirements.txt`:
  - `opencv-python`
  - `numpy`
  - `easyocr`
- Também é necessário `fastapi`, `uvicorn` e `requests` para rodar a API e os scripts de captura (ainda não listados no `requirements.txt`).

## Instalação

```bash
git clone https://github.com/Vinacio01/CancelaPrefeitura.git
cd CancelaPrefeitura
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install fastapi uvicorn requests
```

## Como executar

### 1. Subir a API (obrigatório para as verificações funcionarem)

```bash
uvicorn main.api:app --reload
```
A API sobe em `http://127.0.0.1:8000` e já cadastra a placa `TLZ2D52` como autorizada por padrão ao iniciar.

### 2. Testar com imagem/câmera real

```bash
python main/main.py
```
Roda primeiro a detecção sobre `imagens/teste_carro1.jpg` e, em seguida, abre a webcam para leitura em tempo real (pressione `Q` para encerrar).

### 3. Simular sem câmera (vídeo/imagens de teste)

```bash
python simulate_camera.py
```
Usa `videos/teste_carros.mp4` para simular o funcionamento da cancela, enviando cada placa lida para o endpoint `/camera/simular`.

### 4. Gerenciar placas autorizadas

```bash
python interface/gerenciar_placas.py
```
Menu em terminal para adicionar, remover e listar placas, além de consultar a movimentação.

## Endpoints da API

| Método | Rota                  | Descrição                                             |
|--------|------------------------|--------------------------------------------------------|
| GET    | `/`                    | Healthcheck da API                                     |
| POST   | `/placas`              | Cadastra uma nova placa autorizada                      |
| GET    | `/placas`              | Lista todas as placas autorizadas                       |
| DELETE | `/placas/{placa}`      | Remove uma placa autorizada                              |
| POST   | `/verificar`           | Verifica se uma placa está autorizada (entrada/saída)    |
| GET    | `/movimentacao`        | Lista o histórico de movimentações                       |
| POST   | `/camera/intelbras`    | Recebe leituras de câmeras LPR Intelbras                 |
| POST   | `/camera/simular`      | Endpoint usado por `simulate_camera.py`
