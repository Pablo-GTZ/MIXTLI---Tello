
import cv2
import numpy as np

# Función de retorno vacío para las barras de seguimiento
def empty(a):
    pass

# Crear una ventana para las barras de seguimiento
cv2.namedWindow("COLOR1")
cv2.resizeWindow("COLOR1", 400, 200)
# Crear barras de seguimiento para ajustar los valores de L, A y B en el espacio de color LAB
cv2.createTrackbar("L Min", "COLOR1", 0, 255, empty)
cv2.createTrackbar("L Max", "COLOR1", 255, 255, empty)
cv2.createTrackbar("A Min", "COLOR1", 0, 255, empty)
cv2.createTrackbar("A Max", "COLOR1", 255, 255, empty)
cv2.createTrackbar("B Min", "COLOR1", 0, 255, empty)
cv2.createTrackbar("B Max", "COLOR1", 255, 255, empty)

# Crear una ventana para las barras de seguimiento
cv2.namedWindow("COLOR2")
cv2.resizeWindow("COLOR2", 400, 200)
# Crear barras de seguimiento para ajustar los valores de L, A y B en el espacio de color LAB
cv2.createTrackbar("L Min", "COLOR2", 0, 255, empty)
cv2.createTrackbar("L Max", "COLOR2", 255, 255, empty)
cv2.createTrackbar("A Min", "COLOR2", 0, 255, empty)
cv2.createTrackbar("A Max", "COLOR2", 255, 255, empty)
cv2.createTrackbar("B Min", "COLOR2", 0, 255, empty)
cv2.createTrackbar("B Max", "COLOR2", 255, 255, empty)

# Crear una ventana para las barras de seguimiento
cv2.namedWindow("COLOR3")
cv2.resizeWindow("COLOR3", 400, 200)
# Crear barras de seguimiento para ajustar los valores de L, A y B en el espacio de color LAB
cv2.createTrackbar("L Min", "COLOR3", 0, 255, empty)
cv2.createTrackbar("L Max", "COLOR3", 255, 255, empty)
cv2.createTrackbar("A Min", "COLOR3", 0, 255, empty)
cv2.createTrackbar("A Max", "COLOR3", 255, 255, empty)
cv2.createTrackbar("B Min", "COLOR3", 0, 255, empty)
cv2.createTrackbar("B Max", "COLOR3", 255, 255, empty)

# Crear una ventana para las barras de seguimiento
cv2.namedWindow("COLOR4")
cv2.resizeWindow("COLOR4", 400, 200)
# Crear barras de seguimiento para ajustar los valores de L, A y B en el espacio de color LAB
cv2.createTrackbar("L Min", "COLOR4", 0, 255, empty)
cv2.createTrackbar("L Max", "COLOR4", 255, 255, empty)
cv2.createTrackbar("A Min", "COLOR4", 0, 255, empty)
cv2.createTrackbar("A Max", "COLOR4", 255, 255, empty)
cv2.createTrackbar("B Min", "COLOR4", 0, 255, empty)
cv2.createTrackbar("B Max", "COLOR4", 255, 255, empty)

# Leer la imagen de entrada
image = cv2.imread('plata.jpg')

while True:
    # Obtener los valores actuales de las barras de seguimiento
    min_L = cv2.getTrackbarPos("L Min", "COLOR1")
    max_L = cv2.getTrackbarPos("L Max", "COLOR1")
    min_A = cv2.getTrackbarPos("A Min", "COLOR1")
    max_A = cv2.getTrackbarPos("A Max", "COLOR1")
    min_B = cv2.getTrackbarPos("B Min", "COLOR1")
    max_B = cv2.getTrackbarPos("B Max", "COLOR1")

    min_L2 = cv2.getTrackbarPos("L Min", "COLOR2")
    max_L2 = cv2.getTrackbarPos("L Max", "COLOR2")
    min_A2 = cv2.getTrackbarPos("A Min", "COLOR2")
    max_A2 = cv2.getTrackbarPos("A Max", "COLOR2")
    min_B2 = cv2.getTrackbarPos("B Min", "COLOR2")
    max_B2 = cv2.getTrackbarPos("B Max", "COLOR2")

    min_L3 = cv2.getTrackbarPos("L Min", "COLOR3")
    max_L3 = cv2.getTrackbarPos("L Max", "COLOR3")
    min_A3 = cv2.getTrackbarPos("A Min", "COLOR3")
    max_A3 = cv2.getTrackbarPos("A Max", "COLOR3")
    min_B3 = cv2.getTrackbarPos("B Min", "COLOR3")
    max_B3 = cv2.getTrackbarPos("B Max", "COLOR3")

    min_L4 = cv2.getTrackbarPos("L Min", "COLOR4")
    max_L4 = cv2.getTrackbarPos("L Max", "COLOR4")
    min_A4 = cv2.getTrackbarPos("A Min", "COLOR4")
    max_A4 = cv2.getTrackbarPos("A Max", "COLOR4")
    min_B4 = cv2.getTrackbarPos("B Min", "COLOR4")
    max_B4 = cv2.getTrackbarPos("B Max", "COLOR4")

    # Convertir la imagen a espacio de color LAB
    lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    lab_image2 = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    lab_image3 = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    lab_image4 = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    # Crear una máscara para el rango de colores en el espacio de color LAB
    lower_lab = np.array([min_L, min_A, min_B])
    upper_lab = np.array([max_L, max_A, max_B])
    mask = cv2.inRange(lab_image, lower_lab, upper_lab)

    lower_lab2 = np.array([min_L2, min_A2, min_B2])
    upper_lab2 = np.array([max_L2, max_A2, max_B2])
    mask2 = cv2.inRange(lab_image2, lower_lab2, upper_lab2)

    lower_lab3 = np.array([min_L3, min_A3, min_B3])
    upper_lab3 = np.array([max_L3, max_A3, max_B3])
    mask3 = cv2.inRange(lab_image3, lower_lab3, upper_lab3)

    lower_lab4 = np.array([min_L4, min_A4, min_B4])
    upper_lab4 = np.array([max_L4, max_A4, max_B4])
    mask4 = cv2.inRange(lab_image4, lower_lab4, upper_lab4)

    # Aplicar la máscara a la imagen original
    result = cv2.bitwise_and(image, image, mask=mask)
    result2 = cv2.bitwise_and(image, image, mask=mask2)
    result3 = cv2.bitwise_and(image, image, mask=mask3)
    result4 = cv2.bitwise_and(image, image, mask=mask4)


    # Mostrar la imagen resultante
    cv2.imshow("COLOR1", result)
    cv2.imshow("COLOR2", result2)
    cv2.imshow("COLOR3", result3)
    cv2.imshow("COLOR4", result4)


    if cv2.waitKey(1) & 0xFF == 27:
        break

cv2.destroyAllWindows()