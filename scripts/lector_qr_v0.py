#!/usr/bin/env python3
import rospy
import cv2
from cv_bridge import CvBridge
from pyzbar.pyzbar import decode
from sensor_msgs.msg import Image, LaserScan
from geometry_msgs.msg import Twist

class NavegadorQR:
    def __init__(self):
        # Inicializar el nodo
        rospy.init_node('navegador_qr', anonymous=True)
        self.bridge = CvBridge()
        self.pub_vel = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

        # Suscriptores a los sensores
        self.sub_laser = rospy.Subscriber('/scan', LaserScan, self.cb_laser)
        self.sub_camara = rospy.Subscriber('/camera/rgb/image_raw', Image, self.cb_camara)

        # Variables de estado
        self.estado = 'AVANZANDO'
        self.distancia_frontal = 1.0 # Valor inicial seguro
        self.qr_detectado = False
        self.rate = rospy.Rate(10) # 10 Hz

    def cb_laser(self, msg):
        # El índice 0 del láser apunta exactamente al frente del robot
        distancia = msg.ranges[0]
        # Filtrar errores de lectura del simulador
        if 0.0 < distancia < float('inf'):
            self.distancia_frontal = distancia

    def cb_camara(self, data):
        # Solo procesamos la imagen si seguimos avanzando (ahorro de cómputo)
        if self.estado != 'AVANZANDO':
            return

        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except Exception as e:
            rospy.logerr(f"Error procesando imagen: {e}")
            return

        # Escanear el código QR
        codigos = decode(cv_image)
        for codigo in codigos:
            datos_qr = codigo.data.decode('utf-8')
            rospy.loginfo(f"¡QR Detectado a {self.distancia_frontal:.2f}m! Contenido: {datos_qr}")
            
            # Dibujar un recuadro verde para la visualización
            puntos = codigo.polygon
            if len(puntos) == 4:
                pts = [(p.x, p.y) for p in puntos]
                for i in range(4):
                    cv2.line(cv_image, pts[i], pts[(i+1)%4], (0, 255, 0), 3)
            
            # Cambiamos el estado para que el bucle principal inicie el giro
            self.qr_detectado = True
            self.estado = 'GIRANDO'
            break

        # Mostrar la ventana con lo que ve el robot
        cv2.imshow("Camara Robot", cv_image)
        cv2.waitKey(1)

    def ejecutar(self):
        vel_msg = Twist()
        
        while not rospy.is_shutdown():
            if self.estado == 'AVANZANDO':
                # Si estamos a más de 22 cm de la pared y no hemos visto el QR, avanzamos
                if self.distancia_frontal > 0.22 and not self.qr_detectado:
                    vel_msg.linear.x = 0.15  # Velocidad constante y eficiente
                    vel_msg.angular.z = 0.0
                else:
                    # Si llegamos a la distancia límite de seguridad, frenamos y esperamos a la cámara
                    vel_msg.linear.x = 0.0
                    vel_msg.angular.z = 0.0
                    
            elif self.estado == 'GIRANDO':
                rospy.loginfo("Iniciando giro evasivo...")
                vel_msg.linear.x = 0.0
                vel_msg.angular.z = 0.5 # Velocidad angular de 0.5 rad/s
                
                # Calcular el tiempo para un giro de aproximadamente 90 grados
                tiempo_giro = 3.14 
                t_fin = rospy.Time.now() + rospy.Duration(tiempo_giro)
                
                # Bucle de giro
                while rospy.Time.now() < t_fin and not rospy.is_shutdown():
                    self.pub_vel.publish(vel_msg)
                    self.rate.sleep()
                
                # Al terminar el giro, pasamos a estado detenido
                self.estado = 'DETENIDO'
                
            elif self.estado == 'DETENIDO':
                # Asegurar detención total
                vel_msg.linear.x = 0.0
                vel_msg.angular.z = 0.0
                rospy.loginfo_once("Maniobra completada. Robot a la espera.")
                
            # Publicar la velocidad en cada iteración del bucle
            self.pub_vel.publish(vel_msg)
            self.rate.sleep()

if __name__ == '__main__':
    try:
        nodo = NavegadorQR()
        nodo.ejecutar()
    except rospy.ROSInterruptException:
        cv2.destroyAllWindows()