import serial
import mysql.connector
import time

# Conexión al Arduino
# Cambia 'COM3' por el puerto correcto en Windows o '/dev/ttyUSB0' en Linux
arduino = serial.erial('COM3', 9600, timeout=1)
time.sleep(2)  # esperar a que arranque el Arduino

# Conexión a MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",  # tu contraseña
    database="proyecto_planta"
)
cursor = conn.cursor()

print("Escuchando datos del Arduino...")

try:
    while True:
        if arduino.in_waiting > 0:
            humedad = arduino.readline().decode().strip()
            if humedad in ["baja", "media", "alta"]:
                cursor.execute("INSERT INTO plantas (nombre, humedad) VALUES (%s, %s)", ("Sensor", humedad))
                conn.commit()
                print(f"✔ Registro insertado: Sensor - {humedad}")
except KeyboardInterrupt:
    print("Programa detenido por el usuario")
finally:
    arduino.close()
    cursor.close()
    conn.close()