import easyocr
import cv2
import numpy as np
import re

class PlateReader:
    #vai usar imagens para visualizar as letras e numeros
    def __init__(self,lang_list=['en'], gpu=False):
        self.reader = easyocr.Reader(lang_list, gpu=False)

    def preprocess(self, plate_img):#vai processar a placa para melhor captura
        gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY) # --> deixamos a imagem cinza para melhor operação
        blur = cv2.GaussianBlur(gray, (3,3), 0)#--> desfoca Gaussiano e reduz o ruido
        thresh = cv2.adaptiveThreshold(
            blur, 255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY_INV,
            35, 15
        )
        return thresh
    
    def extract_text(self, img):
        results = self.reader.readtext(img, detail=0)
        if results:
            return results[0]# --> retorna a primeira string detectada
        return ""
    
    def clean_plate_text(self, text): #--> vamos validar o texto em formato Brasil
        text = text.upper()
        text = re.sub('[^A-Z0-9]', '', text)# --> remove tudo que não for letra (A–Z) ou número (0–9).
        padrao = r'^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$'# --> padrao mercosul brasil

        if re.match(padrao, text):
            return text
        
        return None
    
    def read_plate(self, plate_img):
        processed = self.preprocess(plate_img)
        raw_text = self.extract_text(processed)#--> pega o texto bruto 
        cleaned = self.clean_plate_text(raw_text)

        return cleaned
    