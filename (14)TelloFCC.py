import cv2
import numpy as np
from djitellopy import Tello

# Función de retorno vacío para las barras de seguimiento
def empty(a):
    pass

# Nombres de las ventanas y valores iniciales para las barras de seguimiento
windows = ["COLOR1", "COLOR2", "COLOR3", "COLOR4"]
trackbars = ["L Min", "L Max", "A Min", "A Max", "B Min", "B Max"]
initial_values = [
    [0, 255, 0, 255, 0, 0],  # Valores iniciales para COLOR1
    [0, 255, 0, 255, 0, 0],  # Valores iniciales para COLOR2
    [0, 255, 0, 255, 0, 0],  # Valores iniciales para COLOR3
    [0, 255, 0, 255, 0, 0]   # Valores iniciales para COLOR4
]

# Iniciar la conexión con el dron Tello
tello = Tello()
tello.connect()
tello.streamon()
tello.takeoff()

# Definir el marguen para el centro de la imagen
target_x = 400

# Leer la imagen de entrada y reducir la resolución
image = tello.get_frame_read().frame
image = cv2.resize(image, (800, 600))

# Crear las ventanas y las barras de seguimiento
for i, window in enumerate(windows):
    cv2.namedWindow(window)
    cv2.resizeWindow(window, 400, 200)
    for j, trackbar in enumerate(trackbars):
        cv2.createTrackbar(trackbar, window, initial_values[i][j], 255, empty)

contours_enabled = False  # Variable para habilitar o deshabilitar el dibujo de contornos
coordinates = []  # Lista para almacenar las coordenadas de los centros

areamin=100 # Calcular el área de la pantalla

while True:
    #print(tello.get_battery())
    # Obtener la imagen actual del dron Tello
    image = tello.get_frame_read().frame

    for i, window in enumerate(windows):
        # Obtener los valores actuales de las barras de seguimiento
        min_L, max_L, min_A, max_A, min_B, max_B = [cv2.getTrackbarPos(trackbar, window) for trackbar in trackbars]

        # Convertir la imagen a espacio de color LAB
        lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

        # Crear una máscara para el rango de colores en el espacio de color LAB
        lower_lab = np.array([min_L, min_A, min_B])
        upper_lab = np.array([max_L, max_A, max_B])
        mask = cv2.inRange(lab_image, lower_lab, upper_lab)

        # Aplicar la máscara a la imagen original
        result = cv2.bitwise_and(image, image, mask=mask)

        key = cv2.waitKey(1) & 0xFF
        

        
        # Aplicar Canny
        canny = cv2.Canny(result, 100, 200)

        # Encontrar contornos
        contours, _ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Clasificar figuras geométricas en los contornos
        for contour in contours:
            # Calcular el área del contorno
            area = cv2.contourArea(contour)

            # Verificar si el área del contorno es mayor al 1/6 del área de la pantalla
            if area > areamin:
                # Calcular el número de lados de la figura
                epsilon = 0.04 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                num_sides = len(approx)

                # Calcular el área y el perímetro del contorno
                area = cv2.contourArea(contour)
                perimeter = cv2.arcLength(contour, True)
                # Calcular la relación entre el área y el perímetro
                circularity = 4 * np.pi * area / (perimeter ** 2)

                # Clasificar la figura
                if circularity > 0.7:  # Ajusta este valor según tus necesidades
                    # Se considera un círculo
                    cv2.drawContours(result, [contour], -1, (0, 0, 255), 2)  # Dibujar círculos en rojo

                # Calasificar la figura
                if num_sides == 3:
                    cv2.drawContours(result, [contour], -1, (255, 0, 0), 2)  # Dibujar triángulos
                elif num_sides == 4:
                    cv2.drawContours(result, [contour], -1, (255, 0, 0), 2)  # Dibujar cuadrados
                elif num_sides >= 6:
                    cv2.drawContours(result, [contour], -1, (255, 0, 0), 2)  # Dibujar hexágonos en azul

                # Lista de coordenadas objetivo para cada figura
                targets = [(100, 300), (400, 200), (200, 400), (500, 300)]

                for target_x, target_y in targets:
                    # Calcular el centroide de la figura
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        current_x = int(M["m10"] / M["m00"])
                    else:
                        current_x = 0

                    # Calcular la diferencia entre el centro actual y el centro objetivo
                    diff_x = target_x - current_x

                    # Controlar el movimiento del dron para ajustarlo a la derecha del centro
                    if abs(diff_x) > 10:  # Ajusta este umbral según tus necesidades
                        if diff_x > 0:
                            tello.move_right(10)  # Ajusta la distancia del movimiento a la derecha
                        else:
                            tello.move_left(10)  # Ajusta la distancia del movimiento a la izquierda

                    # Avanzar 
                    tello.move_forward(20)  # Ajusta la distancia del avance

        # Mostrar el resultado en la ventana correspondiente
        cv2.imshow(window, result)

    
    

    # Salir del bucle si se presiona la tecla 'ESC'
    if key == 27:
        break

    
    
    if key == ('s'):
        tello.land()

cv2.destroyAllWindows()

# Detener la transmisión de video y cerrar la conexión con el dron Tello
tello.land()
tello.streamoff()
tello.disconnect()

# Imprimir las coordenadas de los centros
for i, coord in enumerate(coordinates):
    print(f"Centro {i + 1}: ({coord[0]}, {coord[1]})")
