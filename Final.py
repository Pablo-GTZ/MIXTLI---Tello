import cv2
import numpy as np
from djitellopy import Tello
import time

# Definir los posibles estados del flujo de trabajo
STATES = {
    "DETECT_SQUARE": 0,
    "DETECT_CIRCLE": 1,
    "DETECT_HEXAGON": 2,
    "DETECT_TRAPEZOID": 3,
    "COMPLETED": 4
}

# Inicializar el estado en el primer paso del flujo
current_state = STATES["DETECT_SQUARE"]

# Iniciar la conexión con el dron Tello
tello = Tello()
tello.connect()
tello.streamon()
tello.takeoff()

def filter_color(image, shape_type):
    if shape_type == "square":
        lower_color = np.array([0, 97, 89])  # Ajusta estos valores
        upper_color = np.array([24, 255, 231])  # Ajusta estos valores
    elif shape_type == "circle":
        lower_color = np.array([0, 0, 0])  # Ajusta estos valores
        upper_color = np.array([0, 255, 255])  # Ajusta estos valores
    elif shape_type == "hexagon":
        lower_color = np.array([0, 0, 0])  # Ajusta estos valores
        upper_color = np.array([0, 255, 255])  # Ajusta estos valores
    elif shape_type == "trapezoid":
        lower_color = np.array([0, 0, 0])  # Ajusta estos valores
        upper_color = np.array([0, 255, 255])  # Ajusta estos valores

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_image, lower_color, upper_color)
    return mask

def detect_and_center_shape(image, shape_type, desired_x, desired_y):
    mask = filter_color(image, shape_type)

    # Encontrar contornos
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Definir un valor de área mínima
    min_contour_area = 1

    # Filtrar contornos por área mínima
    valid_contours = [contour for contour in contours if cv2.contourArea(contour) >= min_contour_area]

    center_threshold = 50

    if len(valid_contours) > 0:
        for contour in valid_contours:
            # Calcular contornos 
            epsilon = 0.04 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            # Calcular el centro de la forma
            M = cv2.moments(contour)
            if M["m00"] != 0:
                center_x = int(M["m10"] / M["m00"])
                center_y = int(M["m01"] / M["m00"])

                # Mover el dron hacia las coordenadas deseadas hasta que esté centrado
                while abs(center_x - desired_x) > center_threshold or abs(center_y - desired_y) > center_threshold:
                    # Calcular la diferencia en coordenadas
                    dx = desired_x - center_x
                    dy = desired_y - center_y

                    # Definir velocidades de movimiento (ajusta según tus necesidades)
                    speed_x = 10  # Velocidad en el eje X
                    speed_y = 10  # Velocidad en el eje Y

                    # Mover el dron hacia el centro de la imagen
                    if dx > center_threshold:
                        #tello.move_right(speed_x)
                        print("Moviendo derecha")
                    elif dx < -center_threshold:
                        #tello.move_left(speed_x)
                        print("Moviendo izq")

                    if dy > center_threshold:
                        #tello.move_down(speed_y)
                        print("Moviendo arriba")
                    elif dy < -center_threshold:
                        #tello.move_up(speed_y)
                        print("Moviendo abajo")

                # El dron está centrado, detener el movimiento
                tello.send_rc_control(0, 0, 0, 0)
                return True

    return False

def perform_circle_rotation():
    tello.rotate_clockwise(360)  # Hacer una rotación de 360 grados
    time.sleep(5)  # Esperar 5 segundos para la rotación
    tello.send_rc_control(0, 0, 0, 0)  # Detener la rotación

while current_state != STATES["COMPLETED"]:
    image = tello.get_frame_read().frame  # Obtener la imagen actual del dron Tello
    image = cv2.resize(image, (800, 600))
    image = cv2.GaussianBlur(image, (5, 5), 0)

    # Aplicar umbral a la imagen en escala de grises
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, threshold = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if current_state == STATES["DETECT_SQUARE"]:
        print("Rectangulo")
        if detect_and_center_shape(image, "square", 400, 500):
            print("Detectada")
            perform_circle_rotation()  # Realizar rotación después de detectar el cuadrado
            current_state += 1

    elif current_state == STATES["DETECT_CIRCLE"]:
        print("Circulo")
        if detect_and_center_shape(image, "circle", 100, 300):
            print("Rectangulo")
            perform_circle_rotation()  # Realizar rotación después de detectar el círculo
            current_state += 1

    elif current_state == STATES["DETECT_HEXAGON"]:
        if detect_and_center_shape(image, "hexagon", 100, 300):
            perform_circle_rotation()  # Realizar rotación después de detectar el hexágono
            current_state += 1

    elif current_state == STATES["DETECT_TRAPEZOID"]:
        if detect_and_center_shape(image, "trapezoid", 100, 300):
            perform_circle_rotation()  # Realizar rotación después de detectar el trapecio
            current_state += 1

    key = cv2.waitKey(1) & 0xFF
    if key == 27 or current_state == STATES["COMPLETED"]:
        break

# Detener la transmisión de video, realizar un aterrizaje y cerrar la conexión con el dron Tello
tello.streamoff()
tello.land()
tello.disconnect()
