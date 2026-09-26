"""Tests for the InferenceService class."""

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from api.inference import InferenceService, ModelNotAvailableError


@pytest.fixture
def mock_ultralytics():
    """Inject a fake ultralytics module into sys.modules."""
    mock_yolo_class = MagicMock()
    fake_module = types.ModuleType("ultralytics")
    fake_module.YOLO = mock_yolo_class

    with patch.dict(sys.modules, {"ultralytics": fake_module}):
        yield mock_yolo_class


@pytest.fixture
def checkpoint_file(tmp_path):
    """Create a temporary checkpoint file so the path check passes."""
    model_file = tmp_path / "test-model.pt"
    model_file.write_bytes(b"fake-model-data")
    return model_file


class TestModelNotAvailableError:
    def test_error_message_includes_path(self):
        error = ModelNotAvailableError("models/missing.pt")
        assert "models/missing.pt" in str(error)

    def test_error_is_exception(self):
        assert issubclass(ModelNotAvailableError, RuntimeError)


class TestInferenceServiceInitialization:
    def test_default_model_path(self):
        service = InferenceService()
        assert service.model_path.name == "acdc-yolov8n-best.pt"

    def test_custom_model_path(self):
        service = InferenceService(model_path="custom/path/model.pt")
        assert service.model_path == Path("custom/path/model.pt")

    def test_model_not_loaded_initially(self):
        service = InferenceService()
        assert service.is_loaded is False


class TestLazyLoading:
    def test_model_loads_on_first_predict(self, mock_ultralytics, checkpoint_file):
        service = InferenceService(model_path=str(checkpoint_file))
        mock_model = MagicMock()
        mock_result = MagicMock()
        mock_result.boxes = None
        mock_ultralytics.return_value = mock_model
        mock_model.predict.return_value = [mock_result]

        service.predict(MagicMock(), confidence=0.25, image_size=512)

        assert service.is_loaded is True

    def test_model_loads_only_once(self, mock_ultralytics, checkpoint_file):
        service = InferenceService(model_path=str(checkpoint_file))
        mock_model = MagicMock()
        mock_result = MagicMock()
        mock_result.boxes = None
        mock_ultralytics.return_value = mock_model
        mock_model.predict.return_value = [mock_result]

        service.predict(MagicMock(), confidence=0.25, image_size=512)
        service.predict(MagicMock(), confidence=0.25, image_size=512)
        service.predict(MagicMock(), confidence=0.25, image_size=512)

        mock_ultralytics.assert_called_once()

    def test_missing_checkpoint_raises_error(self, tmp_path):
        missing_path = tmp_path / "nonexistent.pt"
        service = InferenceService(model_path=str(missing_path))

        with pytest.raises(ModelNotAvailableError):
            service.predict(MagicMock(), confidence=0.25, image_size=512)

    def test_is_loaded_false_after_failed_load(self, tmp_path):
        missing_path = tmp_path / "nonexistent.pt"
        service = InferenceService(model_path=str(missing_path))

        with pytest.raises(ModelNotAvailableError):
            service.predict(MagicMock(), confidence=0.25, image_size=512)

        assert service.is_loaded is False


class TestPredict:
    def test_predict_returns_empty_list_when_no_detections(
        self, mock_ultralytics, checkpoint_file
    ):
        service = InferenceService(model_path=str(checkpoint_file))
        mock_model = MagicMock()
        mock_result = MagicMock()
        mock_result.boxes = None
        mock_ultralytics.return_value = mock_model
        mock_model.predict.return_value = [mock_result]

        result = service.predict(MagicMock(), confidence=0.25, image_size=512)

        assert result == []

    def test_predict_returns_detection_dicts(self, mock_ultralytics, checkpoint_file):
        service = InferenceService(model_path=str(checkpoint_file))
        mock_model = MagicMock()

        mock_xyxy_row = MagicMock()
        mock_xyxy_row.tolist.return_value = [10, 20, 100, 200]
        mock_box = MagicMock()
        mock_box.cls = MagicMock()
        mock_box.cls.item.return_value = 2
        mock_box.conf = MagicMock()
        mock_box.conf.item.return_value = 0.87
        mock_box.xyxy = MagicMock()
        mock_box.xyxy.__getitem__ = MagicMock(return_value=mock_xyxy_row)

        mock_result = MagicMock()
        mock_result.boxes = [mock_box]
        mock_result.names = {0: "person", 1: "rider", 2: "car"}
        mock_ultralytics.return_value = mock_model
        mock_model.predict.return_value = [mock_result]

        result = service.predict(MagicMock(), confidence=0.25, image_size=512)

        assert len(result) == 1
        detection = result[0]
        assert detection["class_id"] == 2
        assert detection["class_name"] == "car"
        assert detection["confidence"] == pytest.approx(0.87)
        assert detection["bbox"] == {"x1": 10, "y1": 20, "x2": 100, "y2": 200}

    def test_predict_passes_confidence_and_image_size(
        self, mock_ultralytics, checkpoint_file
    ):
        service = InferenceService(model_path=str(checkpoint_file))
        mock_model = MagicMock()
        mock_result = MagicMock()
        mock_result.boxes = None
        mock_ultralytics.return_value = mock_model
        mock_model.predict.return_value = [mock_result]

        service.predict(MagicMock(), confidence=0.5, image_size=640)

        mock_model.predict.assert_called_once()
        call_kwargs = mock_model.predict.call_args
        assert call_kwargs.kwargs["conf"] == 0.5
        assert call_kwargs.kwargs["imgsz"] == 640
