import cv2
import os
import requests
from detectores.detector_placas import PlateDetector
from ocr.leitor_ocr import PlateReader

CASCADE_PATH = "detectores/haarcascade_russian_plate_number.xml"

API_URL = "http://127.0.0.1:8000/camera/simular"
VIDEO_TESTE = "videos/teste_carros.mp4"
IMAGENS_TESTE = "imagens/"


def simulate_video():
    cap = cv2.VideoCapture(VIDEO_TESTE)
    detector = PlateDetector(CASCADE_PATH)
    ocr = PlateReader(lang_list=["en"], gpu=False)

    print("Iniciando simulação com vídeo:", VIDEO_TESTE)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Fim do vídeo ou erro ao acessar vídeo.")
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
                msg = "Placa não lida"

            color = (0, 255, 0) if autorizado else (0, 0, 255)

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

            texto = f"{placa} - {msg}" if placa else msg
            cv2.putText(
                frame,
                texto,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2
            )

        cv2.imshow("Simulação Cancela — Vídeo Teste", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def simulate_images():
    detector = PlateDetector(CASCADE_PATH)
    ocr = PlateReader(lang_list=["en"], gpu=False)

    for filename in os.listdir(IMAGENS_TESTE):
        if not filename.lower().endswith((".jpg", ".png")):
            continue

        path = os.path.join(IMAGENS_TESTE, filename)
        img = cv2.imread(path)
        if img is None:
            continue

        detections = detector.detect(img)

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
                msg = "Placa não lida"

            color = (0, 255, 0) if autorizado else (0, 0, 255)

            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)

            texto = f"{placa} - {msg}" if placa else msg
            cv2.putText(
                img,
                texto,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2
            )

        cv2.imshow(f"Simulação Cancela — {filename}", img)
        cv2.waitKey(1000)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    simulate_video()
