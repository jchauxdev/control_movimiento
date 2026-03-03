# Control de Movimiento y Navegación QR - TurtleBot3

Este paquete de ROS (Noetic) implementa un sistema de navegación autónoma para un TurtleBot3 en entornos logísticos simulados en Gazebo. El robot avanza de forma eficiente, utiliza su sensor LiDAR para detenerse a una distancia segura de los obstáculos y procesa códigos QR a través de su cámara RGB para tomar decisiones de enrutamiento dinámico (Izquierda, Derecha o Parar).

Proyecto desarrollo por Julian Rene Chaux en el marco del proyecto de investigación
para el doctorado en Ingeniería de la UAM - Universidad Autónoma de Manizales 

## Requisitos Previos

* Ubuntu 20.04
* ROS Noetic

## Instalación y Compilación

1. **Instalar el entorno de TurtleBot3:**
   Antes de clonar el paquete, es necesario contar con las librerías oficiales de TurtleBot3 y sus simulaciones:
   
   ```bash
   sudo apt-get update
   sudo apt-get install ros-noetic-turtlebot3 ros-noetic-turtlebot3-msgs ros-noetic-turtlebot3-simulations

2. Ve a la carpeta fuente de tu espacio de trabajo:
   ```bash
   cd ~/catkin_ws/src

3. Clona este repositorio:
    ```bash
    git clone [https://github.com/TU_USUARIO/control_movimiento.git](https://github.com/TU_USUARIO/control_movimiento.git)

3. Instala las dependencias del sistema y de Python necesarias (como cv_bridge y pyzbar). Utiliza rosdep en la raíz de tu espacio de trabajo para resolver dependencias de ROS, y pip3 para la librería de visión:

    ```bash
    cd ~/catkin_ws
    rosdep update
    rosdep install --from-paths src --ignore-src -r -y
    sudo apt-get install libzbar0
    pip3 install pyzbar

4. Compila el paquete y recarga el entorno:
    ```bash
    catkin_make
    source devel/setup.bash

5. Asegúrate de que los scripts de Python tengan permisos de ejecución:
    ```bash
    chmod +x ~/catkin_ws/src/control_movimiento/scripts/*.py

## Ejecución de la Simulación

El paquete incluye un archivo launch general que levanta el entorno de Gazebo, inyecta la pared logística con el código QR y ejecuta el nodo de visión y control simultáneamente.

Asegúrate de exportar el modelo del robot antes de lanzar:

    export TURTLEBOT3_MODEL=waffle
    roslaunch control_movimiento main_proyecto.launch distancia_pared:=2.5

Nota: Puedes modificar el parámetro distancia_pared al vuelo para cambiar la posición inicial de la pared logística frente al robot. Por ejemplo: distancia_pared:=3.5.

##  Personalización de Comandos (Códigos QR)
El robot responde a texturas de códigos QR específicas. Por defecto, el sistema reconoce tres comandos en texto plano:

IZQUIERDA (Gira 90 grados a la izquierda y avanza)

DERECHA (Gira 90 grados a la derecha y avanza)

PARAR (Se detiene frente al objetivo de forma segura)

Para cambiar el comando activo en la simulación:

Genera un código QR de tipo texto con la palabra exacta que deseas (ej. DERECHA) usando cualquier generador gratuito en línea.

Descarga la imagen generada en formato .png.

Renombra tu imagen a qr.png y reemplaza el archivo de textura actual ubicado en tu paquete:
~/catkin_ws/src/control_movimiento/models/caja_qr/materials/textures/qr.png

Vuelve a lanzar la simulación. Gazebo cargará automáticamente la nueva textura incrustada en la pared logística.
