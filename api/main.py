import logging
import time
import uuid
from io import BytesIO
from threading import Lock
from typing import TypedDict

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, Query, UploadFile
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from api.inference import InferenceService, ModelNotAvailableError

MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 25_000_000
MAX_IMAGE_SIZE = 1280
SUPPORTED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_ACTIVE_JOBS = 1
JOB_RETENTION_SECONDS = 30 * 60
logger = logging.getLogger(__name__)


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


class PredictionJobResponse(BaseModel):
    job_id: str
    status: str
    stage: str
    message: str
    result: PredictionResponse | None = None


class PredictionJob(TypedDict):
    status: str
    stage: str
    message: str
    result: PredictionResponse | None
    updated_at: float


JOB_MESSAGES = {
    "queued": "Image received. Waiting for the inference worker.",
    "downloading_model": "Downloading the model checkpoint. This is usually needed only once.",
    "loading_model": "Loading the model into memory. The first run may take a little longer.",
    "predicting": "Analyzing the image and detecting objects.",
    "completed": "Detection complete.",
    "failed": "Detection failed.",
}


async def read_image(image: UploadFile) -> Image.Image:
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
            return uploaded_image.convert("RGB")
    except UnidentifiedImageError as error:
        raise HTTPException(
            status_code=400, detail="Uploaded file is not a valid image."
        ) from error
    except Image.DecompressionBombError as error:
        raise HTTPException(status_code=413, detail="Image dimensions are too large.") from error
    except OSError as error:
        raise HTTPException(
            status_code=400, detail="Could not decode the uploaded image."
        ) from error


def create_app(inference_service: InferenceService | None = None) -> FastAPI:
    service = inference_service if inference_service is not None else InferenceService()
    jobs: dict[str, PredictionJob] = {}
    jobs_lock = Lock()
    app = FastAPI(
        title="Adverse Weather Object Detection API",
        version="1.0.0",
        description="Detect road users in adverse-weather images with the trained ACDC YOLO model.",
    )
    app.state.inference_service = service
    app.state.prediction_jobs = jobs

    @app.get("/health")
    def health() -> dict[str, str | bool]:
        return {
            "status": "ok",
            "model_loaded": service.is_loaded,
            "model_path": str(service.model_path),
        }

    @app.post("/predict", response_model=PredictionResponse)
    async def predict(
        image: UploadFile = File(...),  # noqa: B008
        confidence: float = Query(default=0.05, ge=0.0, le=1.0),
        image_size: int = Query(default=512, ge=32, le=1280),
        use_tta: bool = Query(default=False, description="Enable test-time augmentation"),
        nms_iou: float = Query(default=0.7, ge=0.0, le=1.0, description="NMS IoU threshold"),
    ) -> PredictionResponse:
        input_image = await read_image(image)

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
            detections=[Detection(**detection) for detection in detections],
        )

    @app.post("/predict/jobs", response_model=PredictionJobResponse, status_code=202)
    async def create_prediction_job(
        background_tasks: BackgroundTasks,
        image: UploadFile = File(...),  # noqa: B008
        confidence: float = Query(default=0.05, ge=0.0, le=1.0),
        image_size: int = Query(default=512, ge=32, le=MAX_IMAGE_SIZE),
        use_tta: bool = Query(default=False),
    ) -> PredictionJobResponse:
        input_image = await read_image(image)
        now = time.monotonic()
        with jobs_lock:
            expired_ids = [
                job_id
                for job_id, job in jobs.items()
                if job["status"] in {"completed", "failed"}
                and now - job["updated_at"] > JOB_RETENTION_SECONDS
            ]
            for job_id in expired_ids:
                del jobs[job_id]

            active_jobs = sum(
                job["status"] in {"queued", "processing"} for job in jobs.values()
            )
            if active_jobs >= MAX_ACTIVE_JOBS:
                raise HTTPException(
                    status_code=429,
                    detail="The inference worker is busy. Please try again shortly.",
                    headers={"Retry-After": "5"},
                )

            job_id = str(uuid.uuid4())
            jobs[job_id] = {
                "status": "queued",
                "stage": "queued",
                "message": JOB_MESSAGES["queued"],
                "result": None,
                "updated_at": now,
            }

        def update_stage(stage: str) -> None:
            with jobs_lock:
                job = jobs.get(job_id)
                if job is not None:
                    job["status"] = "processing"
                    job["stage"] = stage
                    job["message"] = JOB_MESSAGES[stage]
                    job["updated_at"] = time.monotonic()

        def run_prediction() -> None:
            try:
                if use_tta:
                    from api.tta import tta_predict

                    model = service._get_model(update_stage)
                    update_stage("predicting")
                    detections = tta_predict(model, input_image, confidence, image_size)
                    names = model.names if isinstance(model.names, dict) else {
                        i: name for i, name in enumerate(model.names)
                    }
                    for detection in detections:
                        detection["class_name"] = names.get(
                            detection["class_id"], str(detection["class_id"])
                        )
                else:
                    detections = service.predict(
                        input_image,
                        confidence,
                        image_size,
                        progress_callback=update_stage,
                    )
                result = PredictionResponse(
                    width=input_image.width,
                    height=input_image.height,
                    detections=[Detection(**detection) for detection in detections],
                )
                with jobs_lock:
                    job = jobs[job_id]
                    job["status"] = "completed"
                    job["stage"] = "completed"
                    job["message"] = JOB_MESSAGES["completed"]
                    job["result"] = result
                    job["updated_at"] = time.monotonic()
            except Exception as error:
                logger.exception("Prediction job %s failed", job_id)
                message = (
                    str(error)
                    if isinstance(error, ModelNotAvailableError)
                    else "Inference failed unexpectedly. Please try again."
                )
                with jobs_lock:
                    job = jobs[job_id]
                    job["status"] = "failed"
                    job["stage"] = "failed"
                    job["message"] = message or JOB_MESSAGES["failed"]
                    job["updated_at"] = time.monotonic()

        background_tasks.add_task(run_prediction)
        return PredictionJobResponse(
            job_id=job_id,
            status="queued",
            stage="queued",
            message=JOB_MESSAGES["queued"],
        )

    @app.get("/predict/jobs/{job_id}", response_model=PredictionJobResponse)
    def get_prediction_job(job_id: str) -> PredictionJobResponse:
        with jobs_lock:
            job = jobs.get(job_id)
            if job is None:
                raise HTTPException(status_code=404, detail="Prediction job not found or expired.")
            return PredictionJobResponse(
                job_id=job_id,
                status=job["status"],
                stage=job["stage"],
                message=job["message"],
                result=job["result"],
            )

    return app


app = create_app()
