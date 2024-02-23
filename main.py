import numpy as np
import cv2
import time
import os
from datetime import datetime
import pandas as pd

def center(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)
    cx = x + x1
    cy = y + y1
    return cx, cy

def save_results_to_csv(results, csv_file_path):
    df = pd.DataFrame(results, columns=["Data e Hora", "Total", "Subindo", "Descendo"])
    if os.path.exists(csv_file_path):
        df.to_csv(csv_file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(csv_file_path, index=False)

result_folder = "Resultados"

if not os.path.exists(result_folder):
    os.makedirs(result_folder)

cap = cv2.VideoCapture('teste.mp4')

new_width = 640
new_height = 480

fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()

detects = []

object_ids = {}

next_object_id = 1

posL = 260
offset = 30

xy1 = (0, posL)
xy2 = (640, posL)

total = 0
up = 0
down = 0

max_execution_time = 60 * 60
start_time = time.time()

result_csv_path = os.path.join(result_folder, "Relatório.csv")

all_results = []

start_reset_time = time.time()

while 1:
    ret, frame = cap.read()

    frame = cv2.resize(frame, (new_width, new_height))

    fgmask = fgbg.apply(frame)

    retval, th = cv2.threshold(fgmask, 150, 255, cv2.THRESH_BINARY)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_orange = np.array([0, 100, 100])
    upper_orange = np.array([30, 255, 255])

    mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))

    opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel, iterations=2)

    dilation = cv2.dilate(opening, kernel, iterations=7)

    closing = cv2.morphologyEx(dilation, cv2.MORPH_CLOSE, kernel, iterations=7)
    cv2.imshow('closing', closing)

    cv2.line(frame, xy1, xy2, (255, 0, 0), 3)

    cv2.line(frame, (xy1[0], posL - offset), (xy2[0], posL - offset), (255, 255, 0), 2)

    cv2.line(frame, (xy1[0], posL + offset), (xy2[0], posL + offset), (255, 255, 0), 2)

    _, contours, hierarchy = cv2.findContours(dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    i = 0
    for cnt in contours:
        (x, y, w, h) = cv2.boundingRect(cnt)

        area = cv2.contourArea(cnt)

        if int(area) > 2000:
            centro = center(x, y, w, h)

            if (
                    centro[1] > posL - offset
                    and centro[1] < posL + offset
                    and mask_orange[centro[1], centro[0]] == 0
            ):
                if i not in object_ids:
                    object_ids[i] = next_object_id
                    next_object_id += 1

                centro_with_id = (centro[0], centro[1], object_ids[i])

                while len(detects) <= i:
                    detects.append([])

                add_object = True
                for (c, l) in enumerate(detects[i]):
                    distance = np.sqrt((centro[0] - l[0]) ** 2 + (centro[1] - l[1]) ** 2)
                    if distance < 20:
                        add_object = False
                        break

                if add_object:
                    detects[i].append(centro_with_id)

                cv2.putText(frame, str(i), (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                cv2.circle(frame, centro, 4, (0, 0, 255), -1)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                if len(detects) <= i:
                    detects.append([])

                if centro[1] > posL - offset and centro[1] < posL + offset:
                    if i not in object_ids:
                        object_ids[i] = next_object_id
                        next_object_id += 1

                    centro_with_id = (centro[0], centro[1], object_ids[i])

                    detects[i].append(centro_with_id)
                else:
                    detects[i].clear()
                i += 1

    if i == 0:
        detects.clear()

    i = 0

    if len(contours) == 0:
        detects.clear()
    else:
        for detect in detects:
            for (c, l) in enumerate(detect):
                if detect[c - 1][1] < posL and l[1] > posL:
                    detect.clear()
                    up += 1
                    total += 1
                    cv2.line(frame, xy1, xy2, (0, 255, 0), 5)
                    continue

                if detect[c - 1][1] > posL and l[1] < posL:
                    detect.clear()
                    down += 1
                    total += 1
                    cv2.line(frame, xy1, xy2, (0, 0, 255), 5)
                    continue

                if c > 0:
                    cv2.line(frame, (int(detect[c - 1][0]), int(detect[c - 1][1])), (int(l[0]), int(l[1])), (0, 0, 255), 1)

    cv2.putText(frame, "TOTAL: " + str(total), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
    cv2.putText(frame, "SUBINDO: " + str(up), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.putText(frame, "DESCENDO: " + str(down), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    cv2.imshow("frame", frame)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

    current_time = time.time()
    elapsed_time = current_time - start_time

    if elapsed_time > max_execution_time:
        print("Tempo total de execução:", elapsed_time)
        print("Total de pessoas subindo:", up)
        print("Total de pessoas descendo:", down)

        current_timestamp = datetime.now()
        partial_result = [current_timestamp, total, up, down]

        save_results_to_csv([partial_result], result_csv_path)

        start_time = time.time()
        start_reset_time = time.time()

        total = 0
        up = 0
        down = 0

        detects.clear()

    current_reset_time = time.time()
    elapsed_reset_time = current_reset_time - start_reset_time

    if elapsed_reset_time > 3600:
        total = 0
        up = 0
        down = 0
        detects.clear()

        current_timestamp = datetime.now()
        partial_result = [current_timestamp, total, up, down]

        save_results_to_csv([partial_result], result_csv_path)

        start_reset_time = time.time()

cap.release()
cv2.destroyAllWindows()