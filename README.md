# SSH-Script-con-IA
Desarrollo de una aplicación en Python para validación de credenciales  SSH y Telnet usando Shodan API


# README - Auditoría SSH y Telnet con Shodan

## Descripción

Este script permite realizar auditorías de seguridad en servidores SSH y Telnet utilizando la API de Shodan para detectar dispositivos con estos servicios expuestos. La herramienta intenta validar credenciales utilizando una lista predefinida de combinaciones usuario/contraseña y notifica los accesos exitosos mediante Telegram.

## Requisitos

- Python 3.x
- API Key de Shodan
- Token de bot y ID de chat de Telegram
- Lista de contraseñas (ej. `rockyou.txt`)

## Instalación

1. Clonar el repositorio o descargar el script:

   ```sh
   git clone https://github.com/tu-repo/auditoria-ssh-telnet.git
   cd auditoria-ssh-telnet
   ```

2. Instalar las dependencias requeridas:

   ```sh
   pip install shodan paramiko requests
   ```

3. Configurar las credenciales en el script:

   - Reemplazar `API_KEY`, `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` con valores válidos.
   - Asegurar que el archivo `rockyou.txt` esté disponible en la ruta especificada.

## Uso

Ejecutar el script con:

```sh
python auditoria.py
```

El script mostrará una advertencia legal y solicitará confirmación antes de proceder.

## Ejemplo de Uso

1. Se consultan dispositivos en Shodan con puertos 22 y 23 abiertos en Colombia.
2. Se filtran IPs activas.
3. Se prueban combinaciones de credenciales.
4. Se notifican accesos exitosos en Telegram.

## Alcance y Limitaciones

- **Uso responsable:** Este script es solo para pruebas autorizadas y educativas.
- **Consumo de créditos:** La API de Shodan tiene límites de uso según el tipo de cuenta.
- **Múltiples API Keys:** Si se requiere analizar muchas IPs, se puede distribuir la carga entre varias claves.
- **Protecciones en servidores:** Algunos sistemas pueden bloquear intentos rápidos, por lo que se recomienda ajustar los tiempos de espera.

## Advertencia Legal

⚠️ **Este script debe ser utilizado únicamente con autorización expresa del propietario de los sistemas auditados.** El uso indebido podría ser ilegal y estar sujeto a sanciones.

