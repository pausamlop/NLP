from transformers import pipeline
from langdetect import detect


# Cargar pipeline de traducción del modelo
def load_translation_pipeline():
    translator = pipeline(
        task="translation", 
        model="facebook/mbart-large-50-many-to-many-mmt", 
        use_fast=False
    )
    return translator


# Traducir el texto al inglés
def translate_forward(translator, input):

    # Detectar el idioma del texto de entrada
    input_lang = detect(input)

    # Si el idioma detectado es catalán (ca), lo tratamos como español (es)
    if input_lang == "ca":
        input_lang = "es_XX"

    # Lista de idiomas admitidos por el modelo
    lang_list = ["ar_AR", "cs_CZ", "de_DE", "en_XX", "es_XX", "et_EE", "fi_FI", "fr_XX", "gu_IN", "hi_IN", "it_IT", "ja_XX", "kk_KZ", 
                "ko_KR", "lt_LT", "lv_LV", "my_MM", "ne_NP", "nl_XX", "ro_RO", "ru_RU", "si_LK", "tr_TR", "vi_VN", "zh_CN", "af_ZA", 
                "az_AZ", "bn_IN", "fa_IR", "he_IL", "hr_HR", "id_ID", "ka_GE", "km_KH", "mk_MK", "ml_IN", "mn_MN", "mr_IN", "pl_PL", 
                "ps_AF", "pt_XX", "sv_SE", "sw_KE", "ta_IN", "te_IN", "th_TH", "tl_XX", "uk_UA", "ur_PK", "xh_ZA", "gl_ES", "sl_SI"] 

    # Mapear el idioma detectado al formato esperado
    for lang in lang_list:
        if lang.startswith(input_lang):
            input_lang = lang

    # Si ya está en inglés, devolver directamente
    if input_lang == "en_XX":
        return input_lang, input
    
    # Traducción al inglés  
    output = translator(
        input, 
        src_lang=input_lang, 
        tgt_lang="en_XX",
        max_length = 1000
    )[0]["translation_text"]

    return input_lang, output


# Traducir el texto al idioma original
def translate_backwards(translator, input, language):
    # Normalizar texto
    input = input.replace("\n\n", "\n")

    # Si el idioma original es inglés, devolver directamente
    if language == "en_XX":
        return input
    
    print("Translating back to:", language)
    
    # Traducción al idioma original   
    output = translator(
        input, 
        src_lang="en_XX", 
        tgt_lang=language,
        max_length = 1000
    )[0]["translation_text"]
    
    return output
