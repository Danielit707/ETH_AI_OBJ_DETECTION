"""Test-Time Augmentation (TTA) for improved inference accuracy.

Runs inference at multiple scales and flip orientations, then merges
results using Weighted Boxes Fusion (WBF).
"""

from __future__ import annotations

from typing import Any

import numpy as np
from PIL import Image


def tta_predict(
    model: Any,
    image: Image.Image,
    confidence: float = 0.25,
    image_size: int = 512,
    scales: list[float] | None = None,
    use_flip: bool = True,
) -> list[dict[str, Any]]:
    """Run TTA inference and return merged detections.

    Args:
        model: Loaded Ultralytics YOLO model.
        image: Input PIL image.
        confidence: Confidence threshold.
        image_size: Base image size for inference.
        scales: List of scale factors (default: [0.8, 1.0, 1.2]).
        use_flip: Whether to include horizontal flip TTA.

    Returns:
        List of merged detection dicts with class_id, class_name,
        confidence, and bbox.
    """
    if scales is None:
        scales = [0.8, 1.0, 1.2]

    all_boxes: list[np.ndarray] = []
    all_scores: list[np.ndarray] = []
    all_labels: list[np.ndarray] = []

    img_array = np.array(image)
    h, w = img_array.shape[:2]

    variants: list[tuple[np.ndarray, float, bool]] = []

    for scale in scales:
        scaled_w = int(w * scale)
        scaled_h = int(h * scale)
        scaled = np.array(image.resize((scaled_w, scaled_h), Image.BILINEAR))
        variants.append((scaled, scale, False))
        if use_flip:
            variants.append((np.fliplr(scaled).copy(), scale, True))

    for variant_img, scale, is_flipped in variants:
        pil_variant = Image.fromarray(variant_img)
        results = model.predict(
            pil_variant, conf=confidence, imgsz=image_size, verbose=False
        )
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            for box in boxes:
                cls_id = int(box.cls.item())
                conf = float(box.conf.item())
                x1, y1, x2, y2 = (float(c) for c in box.xyxy[0].tolist())

                if is_flipped:
                    x1, x2 = w - x2, w - x1

                x1 /= scale
                x1 = max(0, min(x1, w))
                x2 /= scale
                x2 = max(0, min(x2, w))
                y1 /= scale
                y1 = max(0, min(y1, h))
                y2 /= scale
                y2 = max(0, min(y2, h))

                all_boxes.append([x1, y1, x2, y2])
                all_scores.append(conf)
                all_labels.append(cls_id)

    if not all_boxes:
        return []

    boxes_arr = np.array(all_boxes)
    scores_arr = np.array(all_scores)
    labels_arr = np.array(all_labels)

    merged_boxes, merged_scores, merged_labels = _weighted_boxes_fusion(
        [boxes_arr], [scores_arr], [labels_arr], iou_thr=0.7
    )

    detections: list[dict[str, Any]] = []
    for box, score, label in zip(
        merged_boxes, merged_scores, merged_labels, strict=True
    ):
        x1, y1, x2, y2 = (float(v) for v in box)
        class_id = int(label)
        detections.append(
            {
                "class_id": class_id,
                "class_name": str(class_id),
                "confidence": float(score),
                "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
            }
        )

    detections.sort(key=lambda d: d["confidence"], reverse=True)
    return detections


def _weighted_boxes_fusion(
    boxes_list: list[np.ndarray],
    scores_list: list[np.ndarray],
    labels_list: list[np.ndarray],
    iou_thr: float = 0.55,
    skip_box_thr: float = 0.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Simplified Weighted Boxes Fusion.

    Fuses duplicate detections across TTA variants by clustering boxes
    with IoU > iou_thr and averaging their coordinates weighted by score.
    """
    all_boxes = np.concatenate(boxes_list, axis=0)
    all_scores = np.concatenate(scores_list, axis=0)
    all_labels = np.concatenate(labels_list, axis=0)

    if len(all_boxes) == 0:
        return (
            np.empty((0, 4)),
            np.empty((0,)),
            np.empty((0,), dtype=int),
        )

    order = np.argsort(-all_scores)
    all_boxes = all_boxes[order]
    all_scores = all_scores[order]
    all_labels = all_labels[order]

    used = np.zeros(len(all_boxes), dtype=bool)
    fused_boxes: list[list[float]] = []
    fused_scores: list[float] = []
    fused_labels: list[int] = []

    for i in range(len(all_boxes)):
        if used[i]:
            continue
        used[i] = True

        cluster_indices = [i]
        for j in range(i + 1, len(all_boxes)):
            if used[j]:
                continue
            if all_labels[j] != all_labels[i]:
                continue
            if _box_iou(all_boxes[i], all_boxes[j]) >= iou_thr:
                cluster_indices.append(j)
                used[j] = True

        cluster_boxes = all_boxes[cluster_indices]
        cluster_scores = all_scores[cluster_indices]

        weights = cluster_scores / cluster_scores.sum()
        fused_box = (cluster_boxes * weights[:, None]).sum(axis=0)

        fused_boxes.append(fused_box.tolist())
        fused_scores.append(float(cluster_scores.max()))
        fused_labels.append(int(all_labels[i]))

    return (
        np.array(fused_boxes),
        np.array(fused_scores),
        np.array(fused_labels, dtype=int),
    )


def _box_iou(box: np.ndarray, boxes: np.ndarray) -> np.ndarray:
    """Compute IoU between one box and an array of boxes."""
    if len(boxes) == 0:
        return np.array([])

    x1 = np.maximum(box[0], boxes[:, 0])
    y1 = np.maximum(box[1], boxes[:, 1])
    x2 = np.minimum(box[2], boxes[:, 2])
    y2 = np.minimum(box[3], boxes[:, 3])

    inter = np.maximum(0, x2 - x1) * np.maximum(0, y2 - y1)
    area1 = (box[2] - box[0]) * (box[3] - box[1])
    area2 = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    union = area1 + area2 - inter

    return np.where(union > 0, inter / union, 0)
