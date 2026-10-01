# Adverse Weather Object Detection — Web UI

Next.js 14 + TypeScript + Tailwind CSS interface for the YOLO11 ACDC object
detection API.

## Quick start

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

The UI expects the FastAPI backend at `http://localhost:8000` by default.
Set `DETECTION_API_URL` to change it:

```bash
DETECTION_API_URL=http://192.168.1.100:8000 npm run dev
```

## Features

| Feature | Description |
|---|---|
| Drag-and-drop upload | PNG, JPEG, WebP (max 10 MB) |
| Demo scene | Built-in synthetic image for quick testing |
| Visual overlay | Bounding boxes with class colors and confidence |
| Confidence slider | Filter detections 0-100% in real time |
| Class toggles | Show/hide specific object classes |
| Stats bar | Object count, average confidence, per-class breakdown |
| Inference timing | Displays API response time |
| Prediction progress | Shows queue, model download/load, and inference stages |
| Export | Download annotated image (PNG) or detections (JSON) |
| API status | Live indicator showing backend connection state |

## Production build

```bash
npm run build
npm start
```
