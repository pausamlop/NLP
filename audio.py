import gtts # Para generar audio a partir de texto
import os


# Verificar si un idioma es compatible con GTTS
def language_supported(language):

    if language[:2] in gtts.lang.tts_langs(): 
        return True
    
    return False


# Reproducir texto como audio
def play_audio(text, language):

    print("reproducing audio")
    tts = gtts.gTTS(text=text, lang=language[:2])
    tts.save("audio.mp3")

    os.system("afplay audio.mp3")

    return


play_audio("hola", "es_XX")
