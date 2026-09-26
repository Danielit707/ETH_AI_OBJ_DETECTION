import os
from io import BytesIO

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from api.inference import InferenceService, ModelNotAvailableError


MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 25_000_000
MAX_IMAGE_SIZE = 1280
SUPPORTED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class Detection(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: BoundingBox


class PredictionResponse(BaseModel):
    width: int
    height: int
    detections: list[Detection]


def create_app(inference_service=None):
    service = inference_service or InferenceService()
    app = FastAPI(
        title="Adverse Weather Object Detection API",
        version="1.0.0",
        description="Detect road users in adverse-weather images with the trained ACDC YOLO model.",
    )
    app.state.inference_service = service

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "model_loaded": service.is_loaded,
            "model_path": str(service.model_path),
        }

    @app.post("/predict", response_model=PredictionResponse)
    async def predict(
        image: UploadFile = File(...),
        confidence: float = Query(default=0.05, ge=0.0, le=1.0),
        image_size: int = Query(default=512, ge=32, le=1280),
        use_tta: bool = Query(default=False, description="Enable test-time augmentation"),
        nms_iou: float = Query(default=0.7, ge=0.0, le=1.0, description="NMS IoU threshold"),
    ):
        if image.content_type not in {"image/jpeg", "image/png", "image/webp"}:
            raise HTTPException(
                status_code=415,
                detail="Unsupported image type. Upload a JPEG, PNG, or WebP image.",
            )

        image_bytes = bytearray()
        while chunk := await image.read(min(1024 * 1024, MAX_IMAGE_BYTES + 1 - len(image_bytes))):
            image_bytes.extend(chunk)
            if len(image_bytes) > MAX_IMAGE_BYTES:
                raise HTTPException(
                    status_code=413,
                    detail=f"Image exceeds the {MAX_IMAGE_BYTES // (1024 * 1024)} MiB upload limit.",
                )
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Uploaded image is empty.")

        try:
            with Image.open(BytesIO(image_bytes)) as uploaded_image:
                if uploaded_image.format not in SUPPORTED_IMAGE_FORMATS:
                    raise HTTPException(
                        status_code=415,
                        detail="Unsupported image type. Upload a JPEG, PNG, or WebP image.",
                    )
                if uploaded_image.width * uploaded_image.height > MAX_IMAGE_PIXELS:
                    raise HTTPException(status_code=413, detail="Image dimensions are too large.")
                uploaded_image.load()
                input_image = uploaded_image.convert("RGB")
        except UnidentifiedImageError as error:
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid image.") from error
        except Image.DecompressionBombError as error:
            raise HTTPException(status_code=413, detail="Image dimensions are too large.") from error
        except OSError as error:
            raise HTTPException(status_code=400, detail="Could not decode the uploaded image.") from error

        try:
            if use_tta:
                from api.tta import tta_predict

                detections = await run_in_threadpool(
                    tta_predict, service._get_model(), input_image, confidence, image_size
                )
                for det in detections:
                    det["class_name"] = service._get_model().names.get(
                        det["class_id"], str(det["class_id"])
                    )
            else:
                detections = await run_in_threadpool(
                    service.predict, input_image, confidence, image_size
                )
        except ModelNotAvailableError as error:
            raise HTTPException(status_code=503, detail=str(error)) from error

        return PredictionResponse(
            width=input_image.width,
            height=input_image.height,
            detections=detections,
        )

    return app


app = create_app()
