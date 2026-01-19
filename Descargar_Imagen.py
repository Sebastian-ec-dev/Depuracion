import requests
import os

def descargar_archivo(url, id_busqueda, tipo="auto"):
    carpeta_destino = "descargas"
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)

    # Definir extensión según tipo
    if tipo == "VIDEO":
        extension = ".mp4"
    elif tipo == "IMAGEN":
        extension = ".png"
    else:
        # intentar detectar por la URL primero
        if any(url.lower().endswith(ext) for ext in [".mp4", ".mov", ".avi"]):
            extension = ".mp4"
        elif any(url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png"]):
            extension = os.path.splitext(url)[1]
        else:
            # revisar tipo MIME
            response_head = requests.head(url)
            content_type = response_head.headers.get("content-type", "")
            if "video" in content_type:
                extension = ".mp4"
            elif "image" in content_type:
                extension = ".png"
            else:
                extension = ".bin"

    # Ruta final
    ruta_archivo = os.path.join(carpeta_destino, id_busqueda + extension)

    # Descargar archivo
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(ruta_archivo, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Archivo descargado: {ruta_archivo}")
        return ruta_archivo
    else:
        print(f"Error al descargar el archivo. Status: {response.status_code}")
        return None

