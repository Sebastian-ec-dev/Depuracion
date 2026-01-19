import json

def leer_json(ruta_archivo):
    """Lee un archivo JSON y devuelve los datos."""
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        return json.load(f)

def buscar_por_id(datos, id_buscar):
    """Busca un objeto en la lista por su campo 'id'."""
    for item in datos:
        if item.get("id") == id_buscar:
            return item
    return None

def extaer_datos(ruta, id_buscar):
    ruta = ruta
    id_a_buscar = id_buscar

    datos = leer_json(ruta)
    resultado = buscar_por_id(datos, id_a_buscar)

    return resultado;
