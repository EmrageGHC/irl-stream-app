"""
IRL Stream App - Self-Made
Kamera + Mikrofon → OBS
Made by EmrageGHC
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import requests
import io
from threading import Thread
import time

# Android imports (nur auf Android aktiv)
try:
    from android.permissions import request_permissions, Permission
    from android.runnable import run_on_ui_thread
    ANDROID = True
except ImportError:
    ANDROID = False

class IRLStreamApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server_url = "http://100.64.0.5:8888"
        self.streaming = False
        self.frames_sent = 0

    def build(self):
        # Request permissions on Android
        if ANDROID:
            request_permissions([
                Permission.CAMERA,
                Permission.RECORD_AUDIO,
                Permission.INTERNET
            ])

        # Main Layout
        layout = BoxLayout(orientation='vertical', padding=5, spacing=5)

        # Camera Preview
        self.camera = Camera(
            resolution=(1280, 720),
            play=True,
            index=0
        )
        layout.add_widget(self.camera)

        # Server URL Input
        url_box = BoxLayout(size_hint=(1, None), height=50, spacing=5)
        url_box.add_widget(Label(text='Server:', size_hint=(0.2, 1)))
        self.url_input = TextInput(
            text=self.server_url,
            multiline=False,
            size_hint=(0.8, 1)
        )
        url_box.add_widget(self.url_input)
        layout.add_widget(url_box)

        # Status
        self.status = Label(
            text='[b]Ready[/b]\nEnter server URL',
            size_hint=(1, None),
            height=60,
            markup=True
        )
        layout.add_widget(self.status)

        # Buttons
        btn_box = BoxLayout(size_hint=(1, None), height=60, spacing=5)

        self.btn_stream = Button(
            text='START',
            background_color=(0, 0.8, 0, 1)
        )
        self.btn_stream.bind(on_press=self.toggle_stream)
        btn_box.add_widget(self.btn_stream)

        self.btn_cam = Button(
            text='FLIP',
            size_hint=(0.3, 1),
            background_color=(0.3, 0.3, 0.8, 1)
        )
        self.btn_cam.bind(on_press=self.flip_camera)
        btn_box.add_widget(self.btn_cam)

        layout.add_widget(btn_box)

        return layout

    def flip_camera(self, instance):
        """Switch camera"""
        self.camera.index = 1 if self.camera.index == 0 else 0
        self.camera.play = True

    def toggle_stream(self, instance):
        if not self.streaming:
            self.start_stream()
        else:
            self.stop_stream()

    def start_stream(self):
        self.server_url = self.url_input.text.strip()

        if not self.server_url:
            self.status.text = '[color=ff0000][b]ERROR[/b][/color]\nEnter URL!'
            return

        # Test connection
        try:
            r = requests.get(f"{self.server_url}/stream/status", timeout=3)
            if r.status_code != 200:
                self.status.text = f'[color=ff0000][b]ERROR[/b][/color]\nServer: {r.status_code}'
                return
        except Exception as e:
            self.status.text = f'[color=ff0000][b]OFFLINE[/b][/color]\n{str(e)[:30]}'
            return

        # Start streaming
        self.streaming = True
        self.frames_sent = 0

        self.btn_stream.text = 'STOP'
        self.btn_stream.background_color = (0.8, 0, 0, 1)
        self.status.text = '[color=00ff00][b]LIVE[/b][/color]\n0 frames'

        # 20 FPS
        Clock.schedule_interval(self.send_frame, 1.0 / 20)

    def stop_stream(self):
        self.streaming = False

        self.btn_stream.text = 'START'
        self.btn_stream.background_color = (0, 0.8, 0, 1)
        self.status.text = f'[b]STOPPED[/b]\n{self.frames_sent} frames sent'

        Clock.unschedule(self.send_frame)

    def send_frame(self, dt):
        if not self.streaming:
            return

        try:
            texture = self.camera.texture
            if not texture:
                return

            # Get pixels
            pixels = texture.pixels
            size = texture.size

            # Convert to JPEG
            try:
                from PIL import Image
                img = Image.frombytes('RGBA', size, pixels)
                img = img.convert('RGB')

                buf = io.BytesIO()
                img.save(buf, format='JPEG', quality=85)
                jpeg = buf.getvalue()
            except:
                return

            # Upload
            r = requests.post(
                f"{self.server_url}/stream/video",
                data=jpeg,
                headers={'Content-Type': 'image/jpeg'},
                timeout=2
            )

            if r.status_code == 200:
                self.frames_sent += 1
                if self.frames_sent % 30 == 0:
                    self.status.text = f'[color=00ff00][b]LIVE[/b][/color]\n{self.frames_sent} frames'
            else:
                self.status.text = f'[color=ff9900][b]WARNING[/b][/color]\n{r.status_code}'

        except Exception as e:
            pass

if __name__ == '__main__':
    IRLStreamApp().run()