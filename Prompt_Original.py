def construir_prompt_original(datos: dict) -> str:
    """
    Construye el prompt combinado según si es IMAGE o VIDEO.
    Omite campos de producto que sean None, vacíos o 'None'.
    """
    content_type = datos.get("contentType", "UNKNOWN")
    prompts = datos.get("prompts", [])

    if not prompts:
        return "Error: No se encontraron prompts en los datos"

    base = ""
    producto = None

    # Buscar el dict del producto y la base de video
    for item in prompts:
        if isinstance(item, dict) and "name" in item and "description" in item:
            producto = item
        elif isinstance(item, dict) and "scenes" in item:
            base = item  # para VIDEO

    # Para IMAGE: el prompt base suele ser el primer string
    if content_type == "IMAGE" and prompts and isinstance(prompts[0], str):
        base = prompts[0]

    if not producto:
        return f"Error: No se encontró diccionario de producto\n{content_type=}"

    # Construir solo las líneas con valores válidos
    campos = [
        ("name", producto.get("name")),
        ("description", producto.get("description")),
        ("imageInference", producto.get("imageInference")),
        ("businessCategory", producto.get("businessCategory")),
        ("usageContext", producto.get("usageContext")),
        ("guidelines", producto.get("guidelines")),
    ]

    lineas_validas = []
    for nombre, valor in campos:
        # Filtramos: None, cadena vacía, solo espacios, o literal "None"
        if valor is not None and valor != "None":
            valor_str = str(valor).strip()
            if valor_str:
                lineas_validas.append(f"{nombre}: {valor_str}")

    if lineas_validas:
        detalles_producto = "\n".join(lineas_validas)
    else:
        detalles_producto = "(No hay detalles de producto disponibles)"

    # VIDEO
    if content_type == "VIDEO" and isinstance(base, dict) and "scenes" in base:
        escenas_str = []
        for i, scene_dict in enumerate(base.get("scenes", []), 1):
            desc = scene_dict.get("scene", "").strip()
            act = scene_dict.get("action", "").strip()
            if desc or act:  # solo si hay algo útil
                escena_block = f"Escena {i}:"
                if desc:
                    escena_block += f"\n  - Descripción: {desc}"
                if act:
                    escena_block += f"\n  - Acción: {act}"
                escenas_str.append(escena_block)

        video_info = "VIDEO STRUCTURE:\n" + "\n\n".join(escenas_str) if escenas_str else "VIDEO STRUCTURE: (sin escenas definidas)"

        # # Agregamos voice y sound si existen
        # voice = base.get("voice", "").strip()
        # sound = base.get("sound", "").strip()
        # extras = []
        # if voice:
        #     extras.append(f"Voice-over: {voice}")
        # if sound:
        #     extras.append(f"Sound: {sound}")
        # if extras:
        #     video_info += "\n\n" + "\n".join(extras)

        prompt_final = f"""{video_info}

PRODUCT DETAILS:
{detalles_producto}"""

    # IMAGE
    else:
        prompt_final = f"""{base.strip()}

PRODUCT DETAILS:
{detalles_producto}"""

    return prompt_final.strip()