#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist

def ejecutar_secuencia():
    # Inicializar el nodo
    rospy.init_node('navegador_basico', anonymous=True)
    
    # Publicador al tópico de velocidad del TurtleBot3
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    
    # Frecuencia de control (10 Hz)
    rate = rospy.Rate(10)
    vel_msg = Twist()

    # --- Fase 1: Movimiento lineal hacia adelante ---
    rospy.loginfo("Avanzando...")
    vel_msg.linear.x = 0.2  # Velocidad de 0.2 m/s
    vel_msg.angular.z = 0.0
    
    t0 = rospy.Time.now().to_sec()
    distancia_objetivo = 1.0 # Avanzar 1 metro
    distancia_recorrida = 0.0
    
    while distancia_recorrida < distancia_objetivo and not rospy.is_shutdown():
        pub.publish(vel_msg)
        t1 = rospy.Time.now().to_sec()
        distancia_recorrida = vel_msg.linear.x * (t1 - t0)
        rate.sleep()

    # Frenar el robot suavemente antes del giro
    vel_msg.linear.x = 0.0
    pub.publish(vel_msg)
    rospy.sleep(1.0)

    # --- Fase 2: Giro sobre su propio eje ---
    rospy.loginfo("Girando...")
    vel_msg.linear.x = 0.0
    vel_msg.angular.z = 0.5 # Velocidad angular de 0.5 rad/s
    
    t0 = rospy.Time.now().to_sec()
    angulo_objetivo = 1.57 # Girar aproximadamente 90 grados (Pi/2 radianes)
    angulo_recorrido = 0.0
    
    while angulo_recorrido < angulo_objetivo and not rospy.is_shutdown():
        pub.publish(vel_msg)
        t1 = rospy.Time.now().to_sec()
        angulo_recorrido = vel_msg.angular.z * (t1 - t0)
        rate.sleep()

    # Detener el robot por completo
    vel_msg.angular.z = 0.0
    pub.publish(vel_msg)
    rospy.loginfo("Secuencia completada con éxito.")

if __name__ == '__main__':
    try:
        ejecutar_secuencia()
    except rospy.ROSInterruptException:
        pass