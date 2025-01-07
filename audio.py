
import gtts
import pyglet


##################################################
# comprobar si el lenguaje se puede reproducir
##################################################
def language_supported(language):

    if language[:2] in gtts.lang.tts_langs(): 
        return True
    
    return False



##################################################
# reproducir audio
##################################################
def play_audio(text, language):

    print("reproducing audio")
    tts = gtts.gTTS(text=text, lang=language[:2])
    tts.save("audio.mp3")

    audio = pyglet.media.load("audio.mp3")
    audio.play()

    return
    
