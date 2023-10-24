import subprocess
import getopt
import sys
import socket
import uuid
import requests
import re

# Función para obtener los datos de fabricación de una tarjeta de red por IP
def obtener_datos_por_ip(ip):
    host = socket.gethostname()
    mi_ip = socket.gethostbyname(host)

    if (ip == mi_ip):
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        mac = ":".join([mac[e:e+2] for e in range(0, 11, 2)])

        obtener_datos_por_mac(mac)

    else:
        print("Error: ip is outside the host network")

# Función para obtener los datos de fabricación de una tarjeta de red por MAC
def obtener_datos_por_mac(mac):
    
    try:
        print("MAC address:\t" + mac)
        print("Fabricante:\t" + obtener_fabricante(mac))

    except Exception as e:
        print("Error al obtener fabricante")

# Función para obtener la tabla ARP
def obtener_tabla_arp():
    try:
        tabla = subprocess.check_output(["arp", "-a"], shell=True).decode("latin-1")
        lineas = tabla.split("\n")[3:]

        listaIpMac = []
        for linea in lineas:
            datos = re.split(r"\s+", linea.strip())
            if len(datos[0]) > 0 and datos[0][0].isnumeric():
                ip, mac = datos[0], datos[1]
                listaIpMac.append((ip, mac))
        
        print("IP/MAC/Vendor")
        for dato in listaIpMac:
            fabricante = obtener_fabricante(dato[1])
            if fabricante != "Not found":
                print(f"{dato[0]}\t /   {dato[1]}   /   {fabricante}")

    except subprocess.CalledProcessError as e:
        print(str(e))

def obtener_fabricante(mac):
    url = f"https://api.macvendors.com/{mac}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return "Not found"

    except Exception as e:
        return e

def main(argv):
    try:
        opts = getopt.getopt(argv, "i:m:a", ["ip=", "mac=", "arp"])[0]

    except getopt.GetoptError:
        print("""Use: python OUILookup.py --ip <IP> | --mac <IP> | --arp | [--help]
    --ip : IP del host a consultar.
    --mac: MAC a consultar. P.e. aa:bb:cc:00:00:00.
    --arp: muestra los fabricantes de los host disponibles en la tabla arp.
    --help: muestra este mensaje y termina.""")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-i", "--ip"):
            obtener_datos_por_ip(arg)
        elif opt in ("-m", "--mac"):
            obtener_datos_por_mac(arg)
        else:
            obtener_tabla_arp()

if __name__ == "__main__":
    main(sys.argv[1:])
