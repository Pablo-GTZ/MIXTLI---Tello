import cv2
from djitellopy import Tello
import numpy as np
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
#tello.takeoff()
tello.BITRATE_2MBPS

cv2.namedWindow("Estado", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Estado", 400, 400)



def filter_color(STATES, image, min_contour_area):
    if STATES == "DETECT_SQUARE":
        lower_color = np.array([82, 0, 198])
        upper_color = np.array([255, 195, 255])
    elif STATES == "DETECT_CIRCLE":
        lower_color = np.array([0, 0, 0])
        upper_color = np.array([0, 255, 255])
    elif STATES == "DETECT_HEXAGON":
        lower_color = np.array([0, 0, 0])
        upper_color = np.array([0, 255, 255])
    elif STATES == "DETECT_TRAPEZOID":
        lower_color = np.array([0, 0, 0])
        upper_color = np.array([0, 255, 255])

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_image, lower_color, upper_color)

    result = find_contours_and_centroid(mask, min_contour_area)
    if result:
        approx, centroide, contours = result
        return approx, centroide, contours
    else:
        print("no hay contornos")

def find_contours_and_centroid(image, min_contour_area):
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if contours:
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > min_contour_area:
                epsilon = 0.04 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)

                momentos = cv2.moments(contour)

                if momentos["m00"] != 0:
                    cx = int(momentos["m10"] / momentos["m00"])
                    cy = int(momentos["m01"] / momentos["m00"])

                    centroide = (cx, cy)

                    return approx, centroide, contours

def Oratrice_Mecanique_dAnalyse_Cardinale(desire_x, desire_y, img, centroide):    
    cx, cy = centroide
    diff_x = desire_x - cx
    diff_y = desire_y - cy
    cv2.putText(img, f"Diff_x: {diff_x}", (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(img, f"Diff_y: {diff_y}", (10, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    
    if diff_x > 15:
        cv2.putText(img, f"Mover_x: izquierda", (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        #tello.move_left(20)
    elif diff_x < -15:
        cv2.putText(img, f"Mover_x: derecha", (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        #tello.move_right(20)
    else:
        cv2.putText(img, f"Centrado en X", (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    if diff_y > 15:
        cv2.putText(img, f"Mover_y: arriba", (10, 340), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        #tello.move_up(20)
    elif diff_y < -15:
        cv2.putText(img, f"Mover_y: abajo", (10, 340), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        #tello.move_down(20)
    else:
        cv2.putText(img, f"Centrado en Y", (10, 340), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    if -10 <= diff_x <= 10 and -10 <= diff_y <= 10:
        cv2.putText(img, f"Centrado en X y Y", (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        return True

def medir_tamano_figura(contorno, img, desire_x,desire_y):
    global tiempo_ultima_verificacion
    cv2.putText(img, f"Area: {cv2.contourArea(contorno)}", (10, 370), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) 
    intervalo_verificacion = 2
    tiempo_actual = time.time()
    
    if tiempo_actual - tiempo_ultima_verificacion >= intervalo_verificacion:
        tiempo_ultima_verificacion = tiempo_actual
        #tello.move_forward(20)
        centrado = Oratrice_Mecanique_dAnalyse_Cardinale(desire_x, desire_y)
        if not centrado:
            Oratrice_Mecanique_dAnalyse_Cardinale(desire_x, desire_y)
        return np.sqrt(cv2.contourArea(contorno) > 300000)

def movimiento(medir_tamano, current_state):
    if medir_tamano:
        if current_state == STATES["DETECT_SQUARE"]:
            tello.send_command("left 2")
            time.sleep(2)
            tello.send_command("back 2")
            
            return STATES["DETECT_CIRCLE"]
        elif current_state == STATES["DETECT_CIRCLE"]:
            tello.send_command("right 2")
            time.sleep(2)
            tello.send_command("forward 2")
            
            return STATES["DETECT_HEXAGON"]
        elif current_state == STATES["DETECT_HEXAGON"]:
            tello.send_command("up 2")
            time.sleep(2)
            tello.send_command("down 2")
            
            return STATES["DETECT_TRAPEZOID"]
        elif current_state == STATES["DETECT_TRAPEZOID"]:
            tello.send_command("left 2")
            time.sleep(2)
            tello.send_command("right 2")
            
            return STATES["COMPLETED"]

def process_image_and_display():
    estado = list(STATES.keys())[list(STATES.values()).index(current_state)]
    battery = tello.get_battery()
    img = 255 * np.ones((400, 400, 3), dtype=np.uint8)
    cv2.putText(img, "Estado", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img, f"Bateria: {battery}%", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(img, f"Estado: {estado}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    image = tello.get_frame_read().frame
    image = cv2.resize(image, (800, 600))
    image = cv2.GaussianBlur(image, (5, 5), 0)

    result = filter_color("DETECT_SQUARE", image, min_contour_area=1000)

    desire_x = 400
    desire_y = 300

    if result:
        approx, centroide, contours = result
        cv2.drawContours(image, [approx], -1, (0, 255, 0), 2)
        cv2.circle(image, centroide, 5, (0, 0, 255), -1)
        cv2.putText(img, f"Deseado: ({desire_x}, {desire_y})", (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(img, f"Centroide: {centroide}", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.imshow("Imagen con Contornos", image)
        Oratrice_Mecanique_dAnalyse_Cardinale(desire_x, desire_y, img, centroide)


try:
    while current_state != STATES["COMPLETED"]:
        process_image_and_display()

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

except Exception as e:
    print(f"Error: {str(e)}")

finally:
    cv2.destroyAllWindows()
    tello.land()






