import cv2
import numpy as np
from djitellopy import Tello
import time

STATES = {
    "DETECT_SQUARE": 0,
    "DETECT_CIRCLE": 1,
    "DETECT_HEXAGON": 2,
    "DETECT_TRAPEZOID": 3,
    "COMPLETED": 4
}
current_state = STATES["DETECT_SQUARE"]

tello = Tello()
tello.connect()
tello.streamon()
tello.takeoff()


def filter_color(state, image, min_contour_area):
    if state == STATES["DETECT_SQUARE"]:
        lower_color = np.array([0, 48, 37])
        upper_color = np.array([89, 255, 255])
    elif state == STATES["DETECT_CIRCLE"]:
        lower_color = np.array([0, 0, 0])
        upper_color = np.array([0, 255, 255])
    elif state == STATES["DETECT_HEXAGON"]:
        lower_color = np.array([0, 0, 0])
        upper_color = np.array([0, 255, 255])
    elif state == STATES["DETECT_TRAPEZOID"]:
        lower_color = np.array([0, 0, 0])
        upper_color = np.array([0, 255, 255])

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_image, lower_color, upper_color)

    result = find_contours_and_centroid(mask, min_contour_area)
    return result

def find_contours_and_centroid(image, min_contour_area):
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    square_contours = []

    if contours:
        for contour in contours:
            area = cv2.contourArea(contour)
            
            if area > min_contour_area:
                epsilon = 0.04 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)

                if len(approx) == 4:
                    square_contours.append(contour)

    return square_contours

try:
    while current_state != STATES["COMPLETED"]:
        estado = list(STATES.keys())[list(STATES.values()).index(current_state)]
        battery = tello.get_battery()
        img = 255 * np.ones((400, 400, 3), dtype=np.uint8)
        cv2.putText(img, "Estado", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(img, f"Bateria: {battery}%", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(img, f"Estado: {estado}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        image = tello.get_frame_read().frame
        image = cv2.resize(image, (800, 600))
        image = cv2.GaussianBlur(image, (5, 5), 0)

        result = filter_color(current_state, image, min_contour_area=1000)

        desire_x = 400
        desire_y = 300

        if result:
            approx, centroide, contours = result
            cv2.drawContours(image, [approx], -1, (0, 255, 0), 2)
            cv2.circle(image, centroide, 5, (0, 0, 255), -1)
            cv2.putText(img, f"Deseado: ({desire_x}, {desire_y})", (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            cv2.putText(img, f"Centroide: {centroide}", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

            if medir_tamano:
                current_state = movimiento(medir_tamano, current_state)

        cv2.imshow("Estado", img)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

except Exception as e:
    print(f"Error: {str(e)}")