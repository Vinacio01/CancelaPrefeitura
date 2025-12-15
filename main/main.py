import os
import cv2
import requests

from detectores.detector_placas import PlateDetector
from ocr.leitor_ocr import PlateReader
from banco.banco import BancoDeDados
from core.controle_cancela import ControleCancela



BASE_DIR = os.path.dirname(os.path.dirname(__file__))  
CASCADE_PATH = os.path.join(BASE_DIR, "detectores", "haarcascade_russian_plate_number.xml")

# Caminho da imagem de teste
IMG_PATH = os.path.join(BASE_DIR, "imagens", "teste_carro1.jpg")

API_URL = "http://127.0.0.1:8000/camera"


def test_image_file():
    os.makedirs("crops", exist_ok=True)

    img = cv2.imread(IMG_PATH)
    if img is None:
        print(f"Erro ao carregar imagem: {IMG_PATH}")
        return

    detector = PlateDetector(CASCADE_PATH)
    ocr = PlateReader(lang_list=['en'], gpu=False)
    db = BancoDeDados()
    cancela = ControleCancela(db)

    detections = detector.detect(img)
    print(f"{len(detections)} detecções encontradas")

    user_desktop = os.path.join(os.path.expanduser("~"), "Desktop")

    for i, (bbox, cropped) in enumerate(detections):
        x, y, w, h = bbox

        output_path = os.path.join(user_desktop, f"crop_{i}.png")
        cv2.imwrite(output_path, cropped)
        print("Imagem da placa salva em:", output_path)

        placa_lida = ocr.read_plate(cropped)
        print(f"Detecção {i}: bbox={(x, y, w, h)} -> placa: {placa_lida}")

        # Envia para API
        if placa_lida:
            try:
                response = requests.post(API_URL, json={"plate": placa_lida})
                data = response.json()
                resultado_bool = data.get("autorizado", False)
                resultado_msg = data.get("mensagem", "")
            except Exception as e:
                resultado_bool = False
                resultado_msg = f"Erro API: {e}"
        else:
            resultado_bool = False
            resultado_msg = "Não Lido"

        print(f"Resultado: {resultado_bool} - {resultado_msg}")

        color = (0, 255, 0) if resultado_bool else (0, 0, 255)
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        cv2.putText(img, resultado_msg, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    boxed_output = os.path.join(user_desktop, "resultado_detectado.png")
    img_boxed = detector.draw_boxes(img, detections)
    cv2.imwrite(boxed_output, img_boxed)
    print("Imagem final com bounding boxes salva em:", boxed_output)


def main_camera():
    cap = cv2.VideoCapture(0)

    detector = PlateDetector(CASCADE_PATH)
    ocr = PlateReader(lang_list=['en'], gpu=False)
    db = BancoDeDados()
    cancela = ControleCancela(db)

    print("Sistema iniciando --- pressione Q para encerrar")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Erro ao acessar a câmera ❌")
            break

        detections = detector.detect(frame)

        for bbox, cropped in detections:
            x, y, w, h = bbox
            placa = ocr.read_plate(cropped)

            if placa:
                try:
                    response = requests.post(API_URL, json={"plate": placa})
                    data = response.json()
                    autorizado = data.get("autorizado", False)
                    msg = data.get("mensagem", "")
                except Exception as e:
                    autorizado = False
                    msg = f"Erro API: {e}"
            else:
                autorizado = False
                msg = "Não Lido"

            color = (0, 255, 0) if autorizado else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, msg, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        cv2.imshow("Cancela — OCR em Tempo Real", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    test_image_file()
    main_camera()
