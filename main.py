import cv2
from imageProcessing import readPlate

cap = cv2.VideoCapture(0)  # 0 for webcam, 1 for external camera
# cap = cv2.VideoCapture("video.ts")  # For video file

while True:
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    interval = int(frame_rate * 0.6)
    ret, frame = cap.read()
    img = readPlate(frame)
    cv2.imshow('Screen', frame)
    if cv2.waitKey(interval) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

