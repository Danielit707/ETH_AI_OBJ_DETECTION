from io import BytesIO
import unittest

from fastapi.testclient import TestClient
from PIL import Image

from api.inference import ModelNotAvailableError
from api.main import create_app


class FakeInferenceService:
    model_path = "/models/test.pt"
    is_loaded = True

    def __init__(self, detections=None, error=None):
        self.detections = detections or []
        self.error = error
        self.calls = []

    def predict(self, image, confidence, image_size):
        self.calls.append((image.size, confidence, image_size))
        if self.error:
            raise self.error
        return self.detections


def png_bytes():
    image = Image.new("RGB", (32, 24), color=(20, 30, 40))
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


class InferenceApiTests(unittest.TestCase):
    def setUp(self):
        self.service = FakeInferenceService(
            detections=[
                {
                    "class_id": 2,
                    "class_name": "car",
                    "confidence": 0.93,
                    "bbox": {"x1": 1.0, "y1": 2.0, "x2": 20.0, "y2": 22.0},
                }
            ]
        )
        self.client = TestClient(create_app(self.service))

    def test_health_reports_service_and_model_state(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "ok", "model_loaded": True, "model_path": "/models/test.pt"},
        )

    def test_prediction_returns_classes_confidence_and_pixel_boxes(self):
        response = self.client.post(
            "/predict",
            files={"image": ("scene.png", png_bytes(), "image/png")},
            params={"confidence": 0.4, "image_size": 416},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "width": 32,
                "height": 24,
                "detections": [
                    {
                        "class_id": 2,
                        "class_name": "car",
                        "confidence": 0.93,
                        "bbox": {"x1": 1.0, "y1": 2.0, "x2": 20.0, "y2": 22.0},
                    }
                ],
            },
        )
        self.assertEqual(self.service.calls, [((32, 24), 0.4, 416)])

    def test_empty_detection_list_is_successful_prediction(self):
        self.service.detections = []
        response = self.client.post(
            "/predict",
            files={"image": ("scene.png", png_bytes(), "image/png")},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["detections"], [])

    def test_rejects_unsupported_content_type(self):
        response = self.client.post(
            "/predict",
            files={"image": ("scene.gif", b"GIF89a", "image/gif")},
        )

        self.assertEqual(response.status_code, 415)

    def test_rejects_invalid_image_content(self):
        response = self.client.post(
            "/predict",
            files={"image": ("scene.png", b"not an image", "image/png")},
        )

        self.assertEqual(response.status_code, 400)

    def test_rejects_empty_upload(self):
        response = self.client.post(
            "/predict",
            files={"image": ("scene.png", b"", "image/png")},
        )

        self.assertEqual(response.status_code, 400)

    def test_rejects_upload_over_size_limit(self):
        response = self.client.post(
            "/predict",
            files={"image": ("scene.png", b"x" * (10 * 1024 * 1024 + 1), "image/png")},
        )

        self.assertEqual(response.status_code, 413)

    def test_rejects_image_with_excessive_dimensions(self):
        image = Image.new("RGB", (5001, 5000))
        output = BytesIO()
        image.save(output, format="PNG")
        response = self.client.post(
            "/predict",
            files={"image": ("scene.png", output.getvalue(), "image/png")},
        )

        self.assertEqual(response.status_code, 413)

    def test_rejects_invalid_confidence(self):
        response = self.client.post(
            "/predict",
            files={"image": ("scene.png", png_bytes(), "image/png")},
            params={"confidence": 1.5},
        )

        self.assertEqual(response.status_code, 422)

    def test_missing_checkpoint_is_reported_as_service_unavailable(self):
        service = FakeInferenceService(error=ModelNotAvailableError("checkpoint missing"))
        client = TestClient(create_app(service))

        response = client.post(
            "/predict",
            files={"image": ("scene.png", png_bytes(), "image/png")},
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "checkpoint missing")


if __name__ == "__main__":
    unittest.main()
