#!/usr/bin/env python3

#Proyecto desarrollo por Julian Rene Chaux en el marco del proyecto de investigación
#para el doctorado en Ingeniería de la UAM - Universidad Autónoma de Manizales 

import rospy
import cv2
from cv_bridge import CvBridge
from pyzbar.pyzbar import decode
from sensor_msgs.msg import Image, LaserScan
from geometry_msgs.msg import Twist

class NavegadorQR:
    def __init__(self):
        rospy.init_node('navegador_qr', anonymous=True)
        self.bridge = CvBridge()
        self.pub_vel = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

        self.sub_laser = rospy.Subscriber('/scan', LaserScan, self.cb_laser)
        self.sub_camara = rospy.Subscriber('/camera/rgb/image_raw', Image, self.cb_camara)

        rospy.loginfo("INICIANDO LA EJECUCION")
        self.estado = 'AVANZANDO'
        self.distancia_frontal = 1.0 
        self.qr_detectado = False
        self.rate = rospy.Rate(10)

    def cb_laser(self, msg):
        distancia = msg.ranges[0]
        if 0.0 < distancia < float('inf'):
            self.distancia_frontal = distancia

    def cb_camara(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except Exception as e:
            rospy.logerr(f"Error procesando imagen: {e}")
            return

        if self.estado == 'AVANZANDO':
            codigos = decode(cv_image)
            for codigo in codigos:
                datos_qr = codigo.data.decode('utf-8').strip().upper()
                rospy.loginfo(f"¡QR Detectado! Comando recibido: [{datos_qr}]")
                
                puntos = codigo.polygon
                if len(puntos) == 4:
                    pts = [(p.x, p.y) for p in puntos]
                    for i in range(4):
                        cv2.line(cv_image, pts[i], pts[(i+1)%4], (0, 255, 0), 3)
                
                self.qr_detectado = True
                
                if datos_qr == 'IZQUIERDA':
                    self.estado = 'GIRANDO_IZQUIERDA'
                elif datos_qr == 'DERECHA':
                    self.estado = 'GIRANDO_DERECHA'
                elif datos_qr == 'PARAR':
                    self.estado = 'DETENIDO'
                else:
                    rospy.logwarn(f"Comando desconocido [{datos_qr}]. Deteniendo.")
                    self.estado = 'DETENIDO'
                
                break

        cv2.imshow("Camara Robot", cv_image)
        cv2.waitKey(1)

    def ejecutar(self):
        vel_msg = Twist()
        tiempo_giro = 3.14 # Aproximadamente 90 grados a 0.5 rad/s
        tiempo_avance_nuevo = 4.0 # 4 segundos a 0.15 m/s = 0.6 metros
        
        while not rospy.is_shutdown():
            if self.estado == 'AVANZANDO':
                if self.distancia_frontal > 0.22 and not self.qr_detectado:
                    vel_msg.linear.x = 0.15  
                    vel_msg.angular.z = 0.0
                else:
                    vel_msg.linear.x = 0.0
                    vel_msg.angular.z = 0.0
                    
            elif self.estado == 'GIRANDO_IZQUIERDA':
                rospy.loginfo("Ejecutando maniobra: GIRO A LA IZQUIERDA")
                vel_msg.linear.x = 0.0
                vel_msg.angular.z = 0.5 
                
                t_fin = rospy.Time.now() + rospy.Duration(tiempo_giro)
                while rospy.Time.now() < t_fin and not rospy.is_shutdown():
                    self.pub_vel.publish(vel_msg)
                    self.rate.sleep()
                
                # Al terminar de girar, pasamos al nuevo estado de avance
                self.estado = 'AVANZANDO_POST_GIRO'
                
            elif self.estado == 'GIRANDO_DERECHA':
                rospy.loginfo("Ejecutando maniobra: GIRO A LA DERECHA")
                vel_msg.linear.x = 0.0
                vel_msg.angular.z = -0.5 
                
                t_fin = rospy.Time.now() + rospy.Duration(tiempo_giro)
                while rospy.Time.now() < t_fin and not rospy.is_shutdown():
                    self.pub_vel.publish(vel_msg)
                    self.rate.sleep()
                
                # Al terminar de girar, pasamos al nuevo estado de avance
                self.estado = 'AVANZANDO_POST_GIRO'

            elif self.estado == 'AVANZANDO_POST_GIRO':
                rospy.loginfo("Ejecutando maniobra: AVANCE TRAS GIRO")
                vel_msg.linear.x = 0.15 
                vel_msg.angular.z = 0.0 
                
                t_fin = rospy.Time.now() + rospy.Duration(tiempo_avance_nuevo)
                while rospy.Time.now() < t_fin and not rospy.is_shutdown():
                    self.pub_vel.publish(vel_msg)
                    self.rate.sleep()
                
                # Después de avanzar la distancia deseada, nos detenemos
                self.estado = 'DETENIDO'
                
            elif self.estado == 'DETENIDO':
                vel_msg.linear.x = 0.0
                vel_msg.angular.z = 0.0
                rospy.loginfo_once("Robot detenido. Maniobra evasiva completada con éxito.")
                
            self.pub_vel.publish(vel_msg)
            self.rate.sleep()

if __name__ == '__main__':
    try:
        nodo = NavegadorQR()
        nodo.ejecutar()
    except rospy.ROSInterruptException:
        cv2.destroyAllWindows()