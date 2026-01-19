from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
from PIL import Image
import torch
import os
import Prompts
# from transformers import Qwen3VLForConditionalGeneration, AutoProcessor

# ────────────────────────────────────────────────
# Carga (solo una vez)
# model_id = "Qwen/Qwen3-VL-8B-Instruct"
model_id = "Qwen/Qwen2.5-VL-3B-Instruct"

processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)

model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    model_id,
    torch_dtype="auto",
    device_map="auto",
    low_cpu_mem_usage=True,
    trust_remote_code=True,
)
#
# model = Qwen3VLForConditionalGeneration.from_pretrained(
#     model_id,
#     torch_dtype="auto",
#     device_map="auto",
#     low_cpu_mem_usage=True,
#     trust_remote_code=True,
# )

model.eval()

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Modelo cargado en: {device}")
# ────────────────────────────────────────────────

def evaluar_coherencia_multimodal(
    ruta_o_url: str,
    tipo: str = "IMAGE",
    max_new_tokens: int = 800,
    fps: float = 3 ,
    max_pixels: int = 512 * 512,
) -> str:

    if(tipo.upper() == "IMAGE"):
        prompt_texto = Prompts.prompt_M2_Imagen()
    elif(tipo.upper() == "VIDEO"):
        prompt_texto = Prompts.prompt_M2_Video()

    # Construcción correcta de messages (formato chat de Qwen-VL)
    messages = [

        # {
        #     "role": "system",
        #     "content": [
        #         {
        #             "type": "text",
        #             "text": prompt_texto
        #         }
        #     ]
        # },

        {
            "role": "user",
            "content": []
        }
    ]

    # Agregar visual
    if tipo.upper() == "IMAGE":
        image = Image.open(ruta_o_url).convert("RGB")
        messages[0]["content"].append({"type": "image", "image": image})
    elif tipo.upper() == "VIDEO":
        visual = {
            "video": ruta_o_url,
            "fps": fps,
            "max_pixels": max_pixels,
        }
        messages[0]["content"].append({"type": "video", **visual})
    else:
        raise ValueError(f"Tipo no soportado: {tipo}. Usa 'IMAGE' o 'VIDEO'")

    # # Agregar el prompt de análisis al final
    # messages[1]["content"].append(
    #     {"type": "text", "text": "Analiza este contenido según las instrucciones del system prompt."}
    # )
    messages[0]["content"].append({"type": "text", "text": prompt_texto})

    # Procesar con chat template
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    # Procesar visión (imágenes/videos)
    image_inputs, video_inputs = process_vision_info(messages)

    inputs = processor(
        text=[text],
        images=image_inputs,
        videos=video_inputs,
        padding=True,
        return_tensors="pt",
    ).to(model.device)

    # Generar
    with torch.no_grad():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.4,
            top_p=0.92,
            top_k=60,
            repetition_penalty=1.05,
        )

    # Trim: quitar tokens del prompt de entrada
    generated_ids = generated_ids[:, inputs.input_ids.shape[1]:]
    response = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()

    return response


def analizar_contenido(ruta, tipo="IMAGE"):
    try:
        result = evaluar_coherencia_multimodal(ruta, tipo)
        return result
    except Exception as e:
        return f"Error al analizar {ruta}: {str(e)}"
