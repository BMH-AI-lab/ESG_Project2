# source .venv/Scripts/activate
# python app.py
# http://127.0.0.1:5000


from flask import Flask, render_template, request, send_file, Response, jsonify
from ultralytics import YOLO
from PIL import Image
import numpy as np
import cv2
import io
import time
import threading
import re
import json  # ✅ 추가

from google import genai   # ✅ Gemini 추가

try:
    import serial
except Exception:
    serial = None

app = Flask(__name__)

# ===============================
# YOLO MODEL
# ===============================
MODEL_PATH = r"C:/ESG_Project2/yolov26n_train_result/weights/best.pt"
model = YOLO(MODEL_PATH)

CLASS_ORDER = [
    "Anomaly Solar Panel",
    "Normal Solar Panel",
    "Snow",
    "Structural Damage",
    "Surface Contaminant" # n모델 사용시 s추가
]
NORMAL_CLASS = "Normal Solar Panel"

# ===============================
# 결과 저장 (구조 일치화)
# ===============================
latest_image_defect_stats = {cls: {"percent": 0.0, "count": 0} for cls in CLASS_ORDER}
latest_defect_stats = {cls: {"percent": 0.0, "count": 0} for cls in CLASS_ORDER}

# ===============================
# Gemini 설정
# ===============================
GEMINI_API_KEY = "사용자의 제미나이 API"
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

GEMINI_CACHE = {}

# ===============================
# Arduino 설정
# ===============================
ARDUINO_PORT = "COM8"
ARDUINO_BAUD = 9600

arduino_enabled = True
is_live_page = False

_last_cmd = None
_serial_lock = threading.Lock()

_ser = None
if serial:
    try:
        _ser = serial.Serial(ARDUINO_PORT, ARDUINO_BAUD, timeout=1)
        time.sleep(2)
        if _ser.in_waiting:
            print(_ser.readline().decode(errors="ignore").strip())
        print(f"✅ Successfully connected to Arduino on {ARDUINO_PORT}")
    except Exception as e:
        print(f"❌ Arduino connection failed: {e}")

def send_arduino(cmd: str, force=False):
    global _last_cmd

    if cmd not in ("N", "A", "O"):
        cmd = "O"

    if not arduino_enabled and cmd != "O":
        cmd = "O"

    with _serial_lock:
        if (not force) and (cmd == _last_cmd):
            return

        _last_cmd = cmd

        if _ser and _ser.is_open:
            try:
                _ser.write(f"{cmd}\n".encode())
                _ser.flush()
            except Exception as e:
                print(f"Serial Write Error: {e}")

def reset_arduino():
    send_arduino("O", force=True)

def beep_for_seconds(sec=3):
    send_arduino("A", force=True)

    def stop():
        send_arduino("O", force=True)

    t = threading.Timer(sec, stop)
    t.daemon = True
    t.start()

# ===============================
# UTIL
# ===============================
def compute_confidence_stats(result):
    stats = {cls: {"percent": 0.0, "count": 0} for cls in CLASS_ORDER}
    conf_sum = {cls: 0.0 for cls in CLASS_ORDER}

    for box in result.boxes:
        cls_idx = int(box.cls[0])
        cls = result.names[cls_idx]
        conf = float(box.conf[0])

        if cls in stats:
            stats[cls]["count"] += 1
            conf_sum[cls] += conf

    for cls in CLASS_ORDER:
        if stats[cls]["count"] > 0:
            stats[cls]["percent"] = (conf_sum[cls] / stats[cls]["count"]) * 100

    return stats

def get_arduino_mode_from_boxes(result):
    for box in result.boxes:
        cls = result.names[int(box.cls[0])]
        if cls != NORMAL_CLASS:
            return "A"
    for box in result.boxes:
        cls = result.names[int(box.cls[0])]
        if cls == NORMAL_CLASS:
            return "N"
    return "O"

def get_arduino_mode_from_stats(stats):
    for cls, data in stats.items():
        if cls != NORMAL_CLASS and data["count"] > 0:
            return "A"
    any_detected = any(data["count"] > 0 for data in stats.values())
    return "N" if any_detected else "O"

# ===============================
# Gemini 분석 유틸
# ===============================
def generate_gemini_report(abnormal_info):
    lines = [
        f"{cls}: {info['count']}개 탐지, 평균 신뢰도 {info['avg_confidence']}"
        for cls, info in abnormal_info.items()
    ]

    prompt = f"""
다음은 태양광 패널 이미지에 대한 AI 탐지 결과이다.

탐지 결과:
{chr(10).join(lines)}

아래 규칙을 반드시 지켜서 분석 결과를 작성하라.

 [작성 규칙]
    - 번호(1,2,3) 사용 금지
    - 마크다운 형식 사용 금지
    - 일반 텍스트만 사용
    - 항목 제목은 대괄호 [ ] 로 작성
    - 각 항목 제목 아래에는 여러 줄의 내용을 작성
    - 각 줄은 하이픈(-)으로 시작할 수 있으나, 마크다운 문법으로 해석되지 않도록 일반 텍스트 문장으로 작성
    - 각 항목당 내용은 최소 5줄, 최대 10줄로 제한
    - 항목 제목 앞에 각 항목에 걸맞는 이모지 추가

    [출력 예시]
    [탐지 세부 결과 설명]
    - 첫 번째 설명 문장이다.
    - 두 번째 설명 문장이다.
    - 세 번째 설명 문장이다.
    - 네 번째 설명 문장이다.
    - 다섯 번째 설명 문장이다.

    [항목]
    - 탐지 세부 결과 설명
    - 현 상황에서의 문제점
    - 현 상황에 대한 대응방안
    - 중·장기 관리 및 예방 전략
"""

    response = gemini_client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )

    return response.text.strip()

def fallback_report(abnormal_info, reason):
    return f"""
[탐지 세부 결과 설명]
AI 분석 중 오류가 발생했습니다.

[현 상황에서의 문제점]
자동 분석 시스템 오류로 상세 해석이 제한되었습니다.

[현 상황에 대한 대응방안]
현장 점검을 우선 수행하는 것이 권장됩니다.

[중·장기 관리 및 예방 전략]
시스템 안정성 개선이 필요합니다.

[오류 사유]
{reason}
""".strip()

# ✅ 추가
def normalize_report_for_web(text: str) -> str:
    text = re.sub(r"\n(\[)", r"\n\n\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

# ✅ 수정된 핵심
def safe_generate_gemini_report(abnormal_info, max_retry=2, wait_sec=0.5):
    cache_key = json.dumps(abnormal_info, sort_keys=True, ensure_ascii=False)

    if cache_key in GEMINI_CACHE:
        return GEMINI_CACHE[cache_key]

    REQUIRED_SECTIONS = [
        "[탐지 세부 결과 설명]",
        "[현 상황에서의 문제점]",
        "[현 상황에 대한 대응방안]",
        "[중·장기 관리 및 예방 전략]"
    ]

    last_error = None

    for _ in range(max_retry):
        try:
            text = generate_gemini_report(abnormal_info)
            if all(sec in text for sec in REQUIRED_SECTIONS):
                GEMINI_CACHE[cache_key] = text
                return text
            last_error = "섹션 형식 일부 누락"
        except Exception as e:
            last_error = str(e)

        time.sleep(wait_sec)

    return fallback_report(abnormal_info, last_error)

# ===============================
# PAGE ROUTES
# ===============================
@app.route("/")
def index():
    global is_live_page
    is_live_page = False
    reset_arduino()
    return render_template("index.html")

@app.route("/intro")
def intro():
    global is_live_page
    is_live_page = False
    reset_arduino()
    return render_template("intro.html")

@app.route("/image")
def image():
    global is_live_page
    is_live_page = False
    reset_arduino()
    return render_template("image.html")

@app.route("/live")
def live():
    global is_live_page
    is_live_page = True
    reset_arduino()
    return render_template("live.html")

@app.route("/arduino_reset", methods=["POST"])
def arduino_reset():
    global is_live_page
    is_live_page = False
    reset_arduino()
    return jsonify(ok=True)

@app.route("/arduino_enable", methods=["POST"])
def arduino_enable():
    global arduino_enabled
    data = request.get_json(silent=True) or {}
    enabled = bool(data.get("enabled", True))
    arduino_enabled = enabled

    if not arduino_enabled:
        reset_arduino()

    return jsonify(enabled=arduino_enabled)

@app.route("/arduino_status")
def arduino_status():
    return jsonify(enabled=arduino_enabled, is_live_page=is_live_page)

# ===============================
# IMAGE DETECTION
# ===============================
@app.route("/detect-image", methods=["POST"])
def detect_image():
    file = request.files.get("image")
    if not file:
        return "NO IMAGE", 400

    img = Image.open(file).convert("RGB")
    result = model.predict(np.array(img), conf=0.25, verbose=False)[0]

    stats = compute_confidence_stats(result)
    latest_image_defect_stats.update(stats)

    mode = get_arduino_mode_from_stats(stats)

    if mode == "A":
        beep_for_seconds(3)
    elif mode == "N":
        send_arduino("N", force=True)
    else:
        send_arduino("O", force=True)

    annotated = Image.fromarray(result.plot())
    buf = io.BytesIO()
    annotated.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

@app.route("/image_defect_stats")
def image_defect_stats():
    return jsonify(latest_image_defect_stats)

# ===============================
# Gemini 분석 API
# ===============================
@app.route("/analyze-gemini", methods=["POST"])
def analyze_gemini():
    data = request.get_json()
    stats = data.get("stats", {})

    abnormal_info = {
        cls: {
            "count": info["count"],
            "avg_confidence": round(info["percent"] / 100, 3)
        }
        for cls, info in stats.items()
        if cls != NORMAL_CLASS and info["count"] > 0
    }

    if not abnormal_info:
        return jsonify(report="탐지된 이상 항목이 없어 추가 분석이 필요하지 않습니다.")

    report = safe_generate_gemini_report(abnormal_info)
    report = normalize_report_for_web(report)
    return jsonify(report=report)

# ===============================
# WEBCAM STREAM
# ===============================
_camera_lock = threading.Lock()

def gen_frames():
    global is_live_page

    with _camera_lock:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return

        try:
            while True:
                if not is_live_page:
                    send_arduino("O", force=True)
                    break

                success, frame = cap.read()
                if not success:
                    send_arduino("O", force=True)
                    break

                frame = cv2.resize(frame, (512, 512))
                result = model.predict(frame, conf=0.30, verbose=False)[0]

                stats = compute_confidence_stats(result)
                latest_defect_stats.update(stats)

                mode = get_arduino_mode_from_boxes(result)
                send_arduino(mode, force=False)

                out = result.plot()
                ok, buf = cv2.imencode(".jpg", out)
                if not ok:
                    continue

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"
                )
        finally:
            cap.release()
            send_arduino("O", force=True)

@app.route("/video_feed")
def video_feed():
    return Response(
        gen_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/defect_stats")
def defect_stats():
    return jsonify(latest_defect_stats)

# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
