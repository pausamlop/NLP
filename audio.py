
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


# añadir audio
    if language_supported(input_lang):
        st.session_state["show_play_button"] = True

# Reproducir la respuesta
if st.session_state.get("show_play_button"): 
    input_lang = st.session_state["input_lang"]
    play_question = translate_backwards(translator, "Would you like to play the answer?", input_lang)
    if st.button(play_question):
        response = st.session_state["response"]
        play_audio(response, input_lang)