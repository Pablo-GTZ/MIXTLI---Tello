import cv2
import numpy as np
from djitellopy import Tello

# Función de retorno vacío para la barra de seguimiento
def empty(a):
    pass

window_name = "Color Selection"
trackbar_names = ["H Min", "H Max", "S Min", "S Max", "V Min", "V Max"]
initial_values = [0, 255, 0, 255, 0, 255]  # Valores iniciales para la barra de seguimiento

tello = Tello()
tello.connect()
tello.streamon()

cv2.namedWindow(window_name)
cv2.resizeWindow(window_name, 400, 200)

for trackbar_name in trackbar_names:
    cv2.createTrackbar(trackbar_name, window_name, 0, 255, empty)

contours_enabled = True  # Variable para habilitar o deshabilitar el dibujo de contornos

while True:
    print(tello.get_battery())
    # Leer la imagen de entrada y reducir la resolución
    image = tello.get_frame_read().frame
    image = cv2.resize(image, (800, 600))

    # Obtener los valores actuales de la barra de seguimiento
    min_H, max_H, min_S, max_S, min_V, max_V = [cv2.getTrackbarPos(trackbar_name, window_name) for trackbar_name in trackbar_names]

    # Convertir la imagen a espacio de color HSV
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Crear una máscara para el rango de colores en el espacio de color HSV
    lower_hsv = np.array([min_H, min_S, min_V])
    upper_hsv = np.array([max_H, max_S, max_V])
    mask = cv2.inRange(hsv_image, lower_hsv, upper_hsv)

    # Aplicar la máscara a la imagen original
    result = cv2.bitwise_and(image, image, mask=mask)

    # Mostrar el resultado en la ventana
    cv2.imshow(window_name, result)

    key = cv2.waitKey(1) & 0xFF

    # Salir del bucle si se presiona la tecla 'ESC'
    if key == 27:
        break

cv2.destroyAllWindows()

