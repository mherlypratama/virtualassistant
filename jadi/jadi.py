import speech_recognition as sr
import pyttsx3
import openai
from gtts import gTTS
from io import BytesIO
import pygame
import requests
from bs4 import BeautifulSoup
import pywhatkit


# openai.api_key = "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"
openai.api_key = "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"
pygame.init()


# fungsi untuk mendapatkan hari dan tanggal
def get_date():
    res = requests.get("https://www.timeanddate.com/worldclock/indonesia/tanjungkarang")
    soup = BeautifulSoup(res.text, "html.parser")
    date = soup.select_one("#ctdat").text
    return date


# fungsi untuk mendapatkan berita terkini dari BBC News
def get_news():
    url = "https://www.detik.com/"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    news = [i.text.strip() for i in soup.select("h2", class_="title")]
    return news


# Untuk Berbicara
def speak(response_str):
    tts = gTTS(text=response_str, lang="id", slow=False)
    # Membuat file audio dalam memori
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    # Memainkan file audio dari memori dengan pygame
    audio = pygame.mixer.Sound(fp)
    audio.play()

    # Menunggu sampai file audio selesai diputar
    while pygame.mixer.get_busy():
        continue


if __name__ == "__main__":
    r = sr.Recognizer()
    mic = sr.Microphone(device_index=1)

    conversation = ""
    user_name = "Her"
    bot_name = "Ana"

    while True:
        with mic as source:
            print("\n Listening...")
            r.adjust_for_ambient_noise(source, duration=0.2)
            audio = r.listen(source)
        print("no longer listening")

        try:
            user_input = r.recognize_google(audio, language="id-ID")
        except:
            continue

        prompt = user_name + ":" + user_input + "\n" + bot_name + ":"
        conversation += prompt

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=conversation,
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        print(user_input)
        if "Halo Ana" in user_input or "halo Ana" in user_input:
            user_input = (
                user_input.replace("Ana", "").replace("Halo", "").replace("halo", "")
            )

            if user_input == "selesai":
                response_str = "Terima kasih telah menggunakan layanan saya"
                speak(response_str)
                break

            # TANGGAL
            elif "tanggal" in user_input or "hari" in user_input:
                response_str = "Hari ini adalah " + get_date()
                speak(response_str)

            # LAGU
            elif "lagu" in user_input:
                print(user_input)
                song = user_input.replace("lagu", "")
                response_str = "Memutar Lagu " + song

                speak(response_str)
                pywhatkit.playonyt(song)

            # BERITA
            elif "berita" in user_input:
                news = get_news()
                response_str = "Berikut adalah beberapa berita terkini dari Detik.com: "
                speak(response_str)
                # speak("Berikut adalah beberapa berita terkini dari Detik.com: ")
                for i, n in enumerate(news[:5]):
                    response_str = str(i + 1) + ". " + n
                    speak(response_str)
            else:
                response_str = response["choices"][0]["text"].replace("\n", "")
                response_str = response_str.split(user_name + ":", 1)[0].split(
                    bot_name + ":", 1
                )[0]

                conversation += response_str + "\n"
                print(response_str)
                speak(response_str)
        else:
            user_input = ""
            continue
