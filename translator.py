from transformers import pipeline
from langdetect import detect



##################################################
# cargar pipeline de traducción del modelo
##################################################
def load_translation_pipeline():

    translator = pipeline(task="translation", model="facebook/mbart-large-50-many-to-many-mmt")
    return translator



##################################################
# traducir el prompt a español
##################################################
def translate_forward(translator, input):

    # detección del lenguaje de entrada
    input_lang = detect(input)

    # Si el idioma detectado es catalán (ca), lo tratamos como español (es)
    if input_lang == "ca":
        input_lang = "es_XX"

    lang_list = ["ar_AR", "cs_CZ", "de_DE", "en_XX", "es_XX", "et_EE", "fi_FI", "fr_XX", "gu_IN", "hi_IN", "it_IT", "ja_XX", "kk_KZ", 
                "ko_KR", "lt_LT", "lv_LV", "my_MM", "ne_NP", "nl_XX", "ro_RO", "ru_RU", "si_LK", "tr_TR", "vi_VN", "zh_CN", "af_ZA", 
                "az_AZ", "bn_IN", "fa_IR", "he_IL", "hr_HR", "id_ID", "ka_GE", "km_KH", "mk_MK", "ml_IN", "mn_MN", "mr_IN", "pl_PL", 
                "ps_AF", "pt_XX", "sv_SE", "sw_KE", "ta_IN", "te_IN", "th_TH", "tl_XX", "uk_UA", "ur_PK", "xh_ZA", "gl_ES", "sl_SI"] 

    for lang in lang_list:
        if lang.startswith(input_lang):
            input_lang = lang

    if input_lang == "en_XX":
        return input_lang, input
    
    # traducción   
    output = translator(input, src_lang=input_lang, tgt_lang="en_XX",max_length = 1000)[0]["translation_text"]

    return input_lang, output



##################################################
# traducir el prompt al idioma original
##################################################
def translate_backwards(translator, input, language):

    input = input.replace("\n\n", "\n")

    if language == "en_XX":
        return input
    
    # traducción   
    output = translator(input, src_lang="en_XX", tgt_lang=language,max_length = 1000)[0]["translation_text"]

    return output
