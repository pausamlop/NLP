import gtts # Para generar audio a partir de texto
import pyglet # Para reproducir archivos de audio

# Verificar si un idioma es compatible con GTTS
def language_supported(language):
    if language[:2] in gtts.lang.tts_langs(): 
        return True
    return False

# Reproducir texto como audio
def play_audio(text, language):
    # Convierte texto a audio en el idioma especificado y lo reproduce
    print("reproducing audio")
    # Generar archivo de audio con GTTS
    tts = gtts.gTTS(text=text, lang=language[:2])
    tts.save("audio.mp3")
    # Cargar y reproducir el archivo de audio
    audio = pyglet.media.load("audio.mp3")
    audio.play()

    return
