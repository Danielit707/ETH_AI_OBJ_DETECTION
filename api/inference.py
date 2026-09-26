import os
from pathlib import Path
from threading import Lock

from PIL import Image


DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "acdc-yolov8n-best.pt"


class ModelNotAvailableError(RuntimeError):
    """Raised when the configured model checkpoint cannot be loaded."""


class InferenceService:
    def __init__(self, model_path=None):
        self.model_path = Path(model_path or os.environ.get("MODEL_PATH", DEFAULT_MODEL_PATH))
        self._model = None
        self._model_lock = Lock()
        self._prediction_lock = Lock()

    @property
    def is_loaded(self):
        return self._model is not None

    def _get_model(self):
        if self._model is not None:
            return self._model
        with self._model_lock:
            if self._model is not None:
                return self._model
            if not self.model_path.is_file():
                raise ModelNotAvailableError(
                    f"Model checkpoint not found at {self.model_path}. "
                    "Mount the trained checkpoint and set MODEL_PATH."
                )
            try:
                from ultralytics import YOLO

                self._model = YOLO(str(self.model_path))
            except (ImportError, OSError, RuntimeError) as error:
                raise ModelNotAvailableError(
                    f"Could not load model checkpoint at {self.model_path}: {error}"
                ) from error
        return self._model

    def predict(self, image: Image.Image, confidence: float, image_size: int):
        model = self._get_model()
        with self._prediction_lock:
            results = model.predict(image, conf=confidence, imgsz=image_size, verbose=False)
        detections = []
        for result in results:
            names = result.names
            boxes = result.boxes
            if boxes is None:
                continue
            for box in boxes:
                class_id = int(box.cls.item())
                class_name = names[class_id] if isinstance(names, dict) else names[class_id]
                x1, y1, x2, y2 = (float(coordinate) for coordinate in box.xyxy[0].tolist())
                detections.append(
                    {
                        "class_id": class_id,
                        "class_name": str(class_name),
                        "confidence": float(box.conf.item()),
                        "bbox": {
                            "x1": x1,
                            "y1": y1,
                            "x2": x2,
                            "y2": y2,
                        },
                    }
                )
        return detections

    def predict_with_tta(
        self, image: Image.Image, confidence: float, image_size: int
    ):
        """Predict with test-time augmentation (multi-scale + flip)."""
        from api.tta import tta_predict

        model = self._get_model()
        detections = tta_predict(model, image, confidence, image_size)
        names = model.names if isinstance(model.names, dict) else {
            i: n for i, n in enumerate(model.names)
        }
        for det in detections:
            det["class_name"] = names.get(det["class_id"], str(det["class_id"]))
        return detections
