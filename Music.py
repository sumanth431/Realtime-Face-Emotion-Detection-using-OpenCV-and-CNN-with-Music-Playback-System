import pygame  
import random  

pygame.mixer.init()  

music_paths = {  
    'happy': ['static/music/happy1.mp3'],  
    'sad': ['static/music/sad1.mp3'],  
    'angry': ['static/music/angry1.mp3'],  
    'neutral': ['static/music/neutral1.mp3'],  
    'fear': ['static/music/fear1.mp3'],  
    'surprise': ['static/music/surprise1.mp3'],  
    'disgust': ['static/music/disgust1.mp3'],  
}  

current_music = None  

def play_music(emotion):  
    global current_music  
    pygame.mixer.music.stop()  

    if emotion in music_paths:  
        music_list = music_paths[emotion]  
        if music_list:  
            music_path = random.choice(music_list)  
            try:  
                pygame.mixer.music.load(music_path)  
                pygame.mixer.music.play()  
                current_music = music_path  
                print(f"Playing music: {music_path}")  
            except pygame.error as e:  
                print(f"Error playing music: {e}")  
                return None  
            return music_path  
    else:  
        print(f"No music available for emotion: {emotion}")  
        return None  

def stop_music():  
    global current_music  
    if current_music:  
        pygame.mixer.music.stop()  
        current_music = None  

if _name_ == '_main_':  
    # Test the music player with different emotions  
    play_music('happy')  
    pygame.time.delay(5000)  # Play for 5 seconds  
    stop_music()  
    play_music('sad')  
    pygame.time.delay(5000)  # Play for 5 seconds  
    stop_music()
