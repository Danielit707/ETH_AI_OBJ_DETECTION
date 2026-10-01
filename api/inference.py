import os
from pathlib import Path
from threading import Lock
from typing import Callable

from PIL import Image
import requests


DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "acdc-yolov8n-best.pt"
MAX_MODEL_BYTES = 512 * 1024 * 1024
ProgressCallback = Callable[[str], None]


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

    def _get_model(self, progress_callback: ProgressCallback | None = None):
        if self._model is not None:
            return self._model
        with self._model_lock:
            if self._model is not None:
                return self._model
            if not self.model_path.is_file():
                self._download_model(progress_callback)
            if progress_callback:
                progress_callback("loading_model")
            try:
                from ultralytics import YOLO

                self._model = YOLO(str(self.model_path))
            except (ImportError, OSError, RuntimeError) as error:
                raise ModelNotAvailableError(
                    f"Could not load model checkpoint at {self.model_path}: {error}"
                ) from error
        return self._model

    def _download_model(self, progress_callback: ProgressCallback | None = None):
        model_url = os.environ.get("MODEL_URL")
        if not model_url:
            raise ModelNotAvailableError(
                f"Model checkpoint not found at {self.model_path}. "
                "Mount the trained checkpoint or configure MODEL_URL."
            )
        if not model_url.startswith("https://"):
            raise ModelNotAvailableError("MODEL_URL must use HTTPS.")
        if progress_callback:
            progress_callback("downloading_model")

        headers = {}
        token = os.environ.get("MODEL_DOWNLOAD_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.model_path.with_name(f".{self.model_path.name}.download")
        try:
            with requests.get(
                model_url, headers=headers, stream=True, timeout=(10, 120)
            ) as response:
                response.raise_for_status()
                total_bytes = 0
                with temporary_path.open("wb") as checkpoint:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if not chunk:
                            continue
                        total_bytes += len(chunk)
                        if total_bytes > MAX_MODEL_BYTES:
                            raise ModelNotAvailableError(
                                f"Model download exceeds the {MAX_MODEL_BYTES // (1024 * 1024)} MiB limit."
                            )
                        checkpoint.write(chunk)
            if total_bytes == 0:
                raise ModelNotAvailableError("Model download returned an empty checkpoint.")
            temporary_path.replace(self.model_path)
        except ModelNotAvailableError:
            raise
        except (requests.RequestException, OSError) as error:
            raise ModelNotAvailableError(f"Could not download model checkpoint: {error}") from error
        finally:
            temporary_path.unlink(missing_ok=True)

    def predict(
        self,
        image: Image.Image,
        confidence: float,
        image_size: int,
        progress_callback: ProgressCallback | None = None,
    ):
        model = self._get_model(progress_callback)
        if progress_callback:
            progress_callback("predicting")
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
