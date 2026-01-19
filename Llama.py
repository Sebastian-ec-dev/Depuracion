import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import Prompts

# CONFIGURACIÓN
model_id = "meta-llama/Llama-3.2-3B-Instruct"
HF_TOKEN = "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"

print("Cargando Llama-3.2-3B-Instruct...")
tokenizer = AutoTokenizer.from_pretrained(model_id, token=HF_TOKEN)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    token=HF_TOKEN
)


def comparar_fidelidad(prompt_original, descripcion_imagen):
    prompt_sistema = Prompts.prompt_Llama()


    mensaje_usuario = f"PROMPT ORIGINAL: {prompt_original}\nDESCRIPCIÓN DE LA IMAGEN: {descripcion_imagen}"

    messages = [
        {"role": "system", "content": prompt_sistema},
        {"role": "user", "content": mensaje_usuario},
    ]

    # 1. Usamos el template pero lo pasamos por el tokenizer para obtener input_ids y attention_mask
    prompt_formateado = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=False
    )

    inputs = tokenizer(prompt_formateado, return_tensors="pt").to(model.device)

    terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]

    # 2. Desempaquetamos los inputs usando **
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=300,
            eos_token_id=terminators,
            do_sample=False,
            temperature=0.0
        )

    # 3. Decodificamos omitiendo el prompt
    respuesta = tokenizer.decode(outputs[0][inputs.input_ids.shape[-1]:], skip_special_tokens=True)
    return respuesta


