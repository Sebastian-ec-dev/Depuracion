import Leer_JSON
import Descargar_Imagen
import Analisis_M2
import Llama
import Prompt_Original
import time

def leer_json(id_buscar):
    datos = Leer_JSON.extaer_datos("publications.json", id_buscar)

    if datos is None:
        print("No se encontró ningún objeto con ese ID.")
        return

    return datos

def descargar_link(url, id_buscar, tipo_descarga):
    return Descargar_Imagen.descargar_archivo(url, id_buscar, tipo_descarga)


if __name__ == "__main__":
    inicio = time.perf_counter()
    datos = leer_json("Qt6i_xxLAa4EYIfk9mhXh")
    if(datos is not None):
        descarga = descargar_link(datos["url"], datos["id"], datos["contentType"])
        if(descarga is not None):

            prompt_original = Prompt_Original.construir_prompt_original(datos)

            print(" ============== Prompt Original =============")
            print(prompt_original)


            resultado_analisis = Analisis_M2.analizar_contenido("./"+descarga , datos["contentType"])
            print(" ============== Descripcion de la Imagen =============")
            print(resultado_analisis)

            similitud = Llama.comparar_fidelidad(prompt_original, resultado_analisis)
            print(" ============== Veredicto =============")
            print(similitud)

            fin = time.perf_counter()
            segundos_totales = fin - inicio
            minutos = int(segundos_totales // 60)
            segundos = int(segundos_totales % 60)

            print(f"⏱️ Tiempo total de análisis: {minutos:02d}:{segundos:02d}")

