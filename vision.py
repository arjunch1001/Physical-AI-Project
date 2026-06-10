import cv2
from ultralytics import YOLO

model = YOLO('yolov8n.pt')

def get_scene_data(frame):
    results = model(frame, verbose=False)
    objects = []

    for result in results:
        for box in result.boxes:
            confidence = float(box.conf[0])
            label = result.names[int(box.cls[0])]

            if confidence < 0.6:
                continue

            # bounding box coordinates
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            # center point of the object
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            # object size as % of total frame area
            frame_area = frame.shape[0] * frame.shape[1]
            box_area = (x2 - x1) * (y2 - y1)
            size_pct = round((box_area / frame_area) * 100, 1)

            objects.append({
                'label': label,
                'confidence': round(confidence, 2),
                'cx': cx,
                'cy': cy,
                'size_pct': size_pct
            })

    return {'objects': objects}


if __name__ == '__main__':
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        scene = get_scene_data(frame)

        if scene['objects']:
            print(scene)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()