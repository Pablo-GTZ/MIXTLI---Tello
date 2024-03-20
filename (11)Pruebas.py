import cv2
import numpy as np
from djitellopy import Tello

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

while current_state != STATES["COMPLETED"]:
    image = tello.get_frame_read().frame  # Obtener la imagen actual del dron Tello

    # Redimensionar la imagen para un procesamiento más rápido
    image = cv2.resize(image, (800, 600))

    # Aplicar un filtro gaussiano para suavizar la imagen y reducir el ruido
    image = cv2.GaussianBlur(image, (5, 5), 0)

    # Convertir la imagen a espacio de color HSV en lugar de LAB
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Definir los rangos de color para las figuras (cuadrado, círculo, hexágono, trapecio) en HSV
    lower_square = np.array([0, 0, 0])  # Ajusta estos valores
    upper_square = np.array([10, 255, 255])  # Ajusta estos valores

    lower_circle = np.array([0, 0, 0])  # Ajusta estos valores
    upper_circle = np.array([10, 255, 255])  # Ajusta estos valores

    lower_hexagon = np.array([0, 0, 0])  # Ajusta estos valores
    upper_hexagon = np.array([10, 255, 255])  # Ajusta estos valores

    lower_trapezoid = np.array([0, 0, 0])  # Ajusta estos valores
    upper_trapezoid = np.array([10, 255, 255])  # Ajusta estos valores

    # Crear máscaras para cada figura en el espacio de color HSV
    mask_square = cv2.inRange(hsv_image, lower_square, upper_square)
    mask_circle = cv2.inRange(hsv_image, lower_circle, upper_circle)
    mask_hexagon = cv2.inRange(hsv_image, lower_hexagon, upper_hexagon)
    mask_trapezoid = cv2.inRange(hsv_image, lower_trapezoid, upper_trapezoid)


    # Encontrar contornos en las máscaras
    contours_square, _ = cv2.findContours(mask_square, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_circle, _ = cv2.findContours(mask_circle, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_hexagon, _ = cv2.findContours(mask_hexagon, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_trapezoid, _ = cv2.findContours(mask_trapezoid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Definir un valor de área mínima
    min_contour_area = 10

    # Filtrar contornos por área mínima para cada figura
    valid_contours_square = [contour for contour in contours_square if cv2.contourArea(contour) >= min_contour_area]
    valid_contours_circle = [contour for contour in contours_circle if cv2.contourArea(contour) >= min_contour_area]
    valid_contours_hexagon = [contour for contour in contours_hexagon if cv2.contourArea(contour) >= min_contour_area]
    valid_contours_trapezoid = [contour for contour in contours_trapezoid if cv2.contourArea(contour) >= min_contour_area]

    #Umbral de movimiento
    center_threshold = 50

    # Realizar acciones basadas en el estado actual
    if current_state == STATES["DETECT_SQUARE"]:
        # Detección de cuadrado
        if len(valid_contours_square) > 0:
            cv2.imshow("Máscara Cuadrado", mask_square)
            for contour in valid_contours_square:
                # Calcular contornos 
                epsilon = 0.04 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                # Si el polígono tiene cuatro vértices, se considera un cuadrado
                if len(approx) == 4:
                    # Calcular el centro del cuadrado
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        center_x = int(M["m10"] / M["m00"])
                        center_y = int(M["m01"] / M["m00"])

                        # Coordenadas deseadas
                        desired_x = 100
                        desired_y = 500 

                        # Mover el dron hacia las coordenadas deseadas hasta que esté centrado
                        while abs(center_x - desired_x) > center_threshold and abs(center_y - desired_y) > center_threshold:
                            # Calcular la diferencia en coordenadas
                            dx = desired_x - center_x
                            dy = desired_y - center_y

                            # Definir velocidades de movimiento (ajusta según tus necesidades)
                            speed_x = 10  # Velocidad en el eje X
                            speed_y = 10  # Velocidad en el eje Y

                            # Mover el dron hacia el centro de la imagen
                            if dx > center_threshold:
                                # Mover a la derecha
                                tello.move_right(speed_x)
                            elif dx < -center_threshold:
                                # Mover a la izquierda
                                tello.move_left(speed_x)

                            if dy > center_threshold:
                                # Mover hacia abajo (la coordenada Y crece hacia abajo)
                                tello.move_back(speed_y)
                            elif dy < -center_threshold:
                                # Mover hacia arriba (la coordenada Y disminuye hacia arriba)
                                tello.move_forward(speed_y)

                        # El dron está centrado, detener el movimiento
                        tello.send_rc_control(20, 0, 0, 0)

                        # Avanzar al siguiente estado en el flujo de trabajo
                        current_state += 1
            

    if current_state == STATES["DETECT_CIRCLE"]:
        # Detección de círculo
        if len(valid_contours_circle) > 0:
            for contour in valid_contours_circle:
                # Encuentra los círculos en el contorno
                circles = cv2.HoughCircles(
                cv2.cvtColor(hsv_image, cv2.COLOR_BGR2GRAY),  # Convierte la imagen a escala de grises
                cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=0, maxRadius=0
                )
                if circles is not None:
                    circles = np.uint16(np.around(circles))
                    for circle in circles[0, :]:
                        center_x, center_y = circle[0], circle[1]
                        radius = circle[2]

                        # Coordenadas deseadas
                        desired_x = 100
                        desired_y = 300 

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
                                # Mover a la derecha
                                tello.move_right(speed_x)
                            elif dx < -center_threshold:
                                # Mover a la izquierda
                                tello.move_left(speed_x)

                            if dy > center_threshold:
                                # Mover hacia abajo (la coordenada Y crece hacia abajo)
                                tello.move_backward(speed_y)
                            elif dy < -center_threshold:
                                # Mover hacia arriba (la coordenada Y disminuye hacia arriba)
                                tello.move_forward(speed_y)
                        # El dron está centrado, detener el movimiento
                        tello.send_rc_control(0, 0, 0, 0)

                        # El dron está centrado, detener el movimiento
                        tello.send_rc_control(20, 0, 0, 0)

                        # Avanzar al siguiente estado en el flujo de trabajo
                        current_state += 1
                        

    if current_state == STATES["DETECT_HEXAGON"]:
        # Detección de hexágono
        if len(valid_contours_hexagon) > 0:
            for contour in valid_contours_hexagon:
                # Calcular contornos 
                epsilon = 0.04 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                # Si el polígono tiene seis vértices, se considera un hexágono
                if len(approx) == 6:
                    # Calcular el centro del hexágono y realizar acciones específicas
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        center_x = int(M["m10"] / M["m00"])
                        center_y = int(M["m01"] / M["m00"])

                        # Coordenadas deseadas
                        desired_x = 100
                        desired_y = 300 

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
                                # Mover a la derecha
                                tello.move_right(speed_x)
                            elif dx < -center_threshold:
                                # Mover a la izquierda
                                tello.move_left(speed_x)

                            if dy > center_threshold:
                                # Mover hacia abajo (la coordenada Y crece hacia abajo)
                                tello.move_backward(speed_y)
                            elif dy < -center_threshold:
                                # Mover hacia arriba (la coordenada Y disminuye hacia arriba)
                                tello.move_forward(speed_y)
                        # El dron está centrado, detener el movimiento
                        tello.send_rc_control(0, 0, 0, 0)

                        # El dron está centrado, detener el movimiento
                        tello.send_rc_control(20, 0, 0, 0)

                        # Avanzar al siguiente estado en el flujo de trabajo
                        current_state += 1


    if current_state == STATES["DETECT_TRAPEZOID"]:
        # Detección de trapecio
        if len(valid_contours_trapezoid) > 0:
            for contour in valid_contours_trapezoid:
                # Calcular contornos 
                epsilon = 0.04 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                # Si el poligono tiene cuatro lados es un trapecio
                if len(approx) == 4:
                    # Calcular el centro del trapecio y realizar acciones específicas
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        center_x = int(M["m10"] / M["m00"])
                        center_y = int(M["m01"] / M["m00"])

                        # Coordenadas deseadas
                        desired_x = 100
                        desired_y = 300 

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
                                # Mover a la derecha
                                tello.move_right(speed_x)
                            elif dx < -center_threshold:
                                # Mover a la izquierda
                                tello.move_left(speed_x)

                            if dy > center_threshold:
                                # Mover hacia abajo (la coordenada Y crece hacia abajo)
                                tello.move_backward(speed_y)
                            elif dy < -center_threshold:
                                # Mover hacia arriba (la coordenada Y disminuye hacia arriba)
                                tello.move_forward(speed_y)
                        # El dron está centrado, detener el movimiento
                        tello.send_rc_control(0, 0, 0, 0)

                        # El dron está centrado, detener el movimiento
                        tello.send_rc_control(20, 0, 0, 0)

                        # Avanzar al siguiente estado en el flujo de trabajo
                        current_state += 1

                        # Avanzar al siguiente estado en el flujo de trabajo
                        current_state += 1

    # Salir del bucle si se presiona la tecla 'ESC' o se completa el recorrido
    key = cv2.waitKey(1) & 0xFF
    if key == 27 or current_state == STATES["COMPLETED"]:
        break

# Detener la transmisión de video y cerrar la conexión con el dron Tello
tello.streamoff()
tello.land()
tello.disconnect()

