import cv2
from typing import List, Tuple

class PlateDetector:
    def __init__(self, cascade_path: str, scale_factor: float = 1.1, min_neighbors: int = 5, min_size: Tuple[int,int]=(30,30)):
        self.detector = cv2.CascadeClassifier(cascade_path)
        
        if self.detector.empty():
            raise IOError(f"Haar cascade não carregada. Verifique o caminho: {cascade_path}") 

        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors
        self.min_size = min_size

    def detect(self, frame) -> List[Tuple[Tuple[int,int,int,int], any]]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        gray_eq = cv2.equalizeHist(gray)
        
        rects = self.detector.detectMultiScale(
            gray_eq,
            scaleFactor=self.scale_factor,
            minNeighbors=self.min_neighbors,
            minSize=self.min_size
        )

        results = []

        for (x, y, w, h) in rects:

            pad_x = int(w * 0.03)
            pad_y = int(h * 0.06)

            x1 = max(0, x - pad_x)
            y1 = max(0, y - pad_y)
            x2 = min(frame.shape[1], x + w + pad_x)
            y2 = min(frame.shape[0], y + h + pad_y)

            cropped = frame[y1:y2, x1:x2]

            results.append(((x1, y1, x2 - x1, y2 - y1), cropped))
        
        return results

    @staticmethod
    def draw_boxes(frame, detections):
        out = frame.copy()
        for (x, y, w, h), _ in detections:
            cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return out
