Explicação linha a linha — detector_placa.py

import cv2: importa OpenCV (tratamento de imagens).

from typing ...: só para anotação de tipos (ajuda leitura).

class PlateDetector: encapsula a lógica de detecção (bom para reutilização).

def __init__(self, cascade_path): construtor — recebe o caminho do XML e carrega o CascadeClassifier.

self.detector = cv2.CascadeClassifier(cascade_path): carrega o modelo Haar.

def detect(self, frame): método que detecta placas em um frame (imagem BGR).

gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY): converte para cinza, necessário para Haar.

plates = self.detector.detectMultiScale(...): encontra regiões que parecem placa — parâmetros controlam sensibilidade.

for (x,y,w,h) in plates: para cada detecção, recorta a ROI do frame colorido (melhor para OCR).

results.append(((x,y,w,h), roi)): devolve bbox + imagem recortada.

return results: retorna lista de detecções.