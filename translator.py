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
    
    lang_list = ["ar_AR", "cs_CZ", "de_DE", "en_US", "es_ES", "et_EE", "fi_FI", "fr_FR", "gu_IN", "hi_IN", "it_IT", "ja_JP", "kk_KZ", 
                "ko_KR", "lt_LT", "lv_LV", "my_MM", "ne_NP", "nl_NL", "ro_RO", "ru_RU", "si_LK", "tr_TR", "vi_VN", "zh_CN", "af_ZA", 
                "az_AZ", "bn_IN", "fa_IR", "he_IL", "hr_HR", "id_ID", "ka_GE", "km_KH", "mk_MK", "ml_IN", "mn_MN", "mr_IN", "pl_PL", 
                "ps_AF", "pt_PT", "sv_SE", "sw_KE", "ta_IN", "te_IN", "th_TH", "tl_TL", "uk_UA", "ur_PK", "xh_ZA", "gl_ES", "sl_SI"] 

    for lang in lang_list:
        if lang.startswith(input_lang):
            input_lang = lang

    if input_lang == "es_ES":
        return input_lang, input
    
    # traducción   
    output = translator(input, src_lang=input_lang, tgt_lang="es-ES")[0]["translation_text"]

    return input_lang, output



##################################################
# traducir el prompt al idioma original
##################################################
def translate_backwards(translator, input, language):

    if language == "es-ES":
        return input
    
    # traducción   
    output = translator(input, src_lang="es-ES", tgt_lang=language)[0]["translation_text"]

    return output