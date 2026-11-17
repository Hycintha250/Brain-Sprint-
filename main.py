"""IQ-style brain puzzle game for Android (Kivy) and desktop Python.

Run with: python iq_brain_game.py
For Android, use Pydroid 3 with its Kivy support/plugin, or package with Buildozer.
This is a recreational puzzle score, not a standardized IQ assessment.
"""
from random import shuffle

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget


# Question bank is intentionally transparent and can be expanded or edited.
QUESTIONS = [
    {"kind": "Pattern", "prompt": "What comes next?\n2, 4, 8, 16, ___", "choices": ["24", "30", "32", "34"], "answer": "32", "explanation": "Each number doubles: 16 × 2 = 32."},
    {"kind": "Logic", "prompt": "All glips are norks. Some norks are blue.\nMust some glips be blue?", "choices": ["Yes", "No", "Only at night", "Cannot tell"], "answer": "Cannot tell", "explanation": "The blue norks may or may not be glips; the facts do not establish a link."},
    {"kind": "Number sequence", "prompt": "What comes next?\n3, 6, 11, 18, 27, ___", "choices": ["36", "38", "40", "42"], "answer": "38", "explanation": "The differences are +3, +5, +7, +9, then +11. 27 + 11 = 38."},
    {"kind": "Pattern", "prompt": "Which item is the odd one out?", "choices": ["Triangle", "Square", "Circle", "Cube"], "answer": "Cube", "explanation": "A cube is three-dimensional; the others are 2D shapes."},
    {"kind": "Logic", "prompt": "Mia is taller than Jo. Jo is taller than Lee.\nWho is shortest?", "choices": ["Mia", "Jo", "Lee", "Cannot tell"], "answer": "Lee", "explanation": "Mia > Jo > Lee in height, so Lee is shortest."},
    {"kind": "Number sequence", "prompt": "What comes next?\n1, 1, 2, 3, 5, 8, ___", "choices": ["11", "12", "13", "14"], "answer": "13", "explanation": "Each term is the sum of the two before it: 5 + 8 = 13."},
    {"kind": "Pattern", "prompt": "If ▲ = 3 and ■ = 4, what is ▲ + ■ + ▲?", "choices": ["7", "9", "10", "12"], "answer": "10", "explanation": "3 + 4 + 3 = 10."},
    {"kind": "Logic", "prompt": "A farmer has 17 sheep. All but 9 wander off.\nHow many remain?", "choices": ["8", "9", "17", "26"], "answer": "9", "explanation": "“All but 9” means 9 remain."},
    {"kind": "Number sequence", "prompt": "What comes next?\n81, 27, 9, 3, ___", "choices": ["0", "1", "2", "6"], "answer": "1", "explanation": "Each number is divided by 3."},
    {"kind": "Pattern", "prompt": "Rearrange the letters in LISTEN to make a word meaning quiet.", "choices": ["SILENT", "ENLIST", "TINSEL", "INLETS"], "answer": "SILENT", "explanation": "LISTEN and SILENT use the same letters; silent means quiet."},
    {"kind": "Logic", "prompt": "A clock shows 3:00. What is the smaller angle between its hands?", "choices": ["45°", "60°", "90°", "180°"], "answer": "90°", "explanation": "At 3:00, the minute hand is at 12 and the hour hand at 3: one quarter-turn, or 90 degrees."},
    {"kind": "Number sequence", "prompt": "What comes next?\n2, 5, 10, 17, 26, ___", "choices": ["35", "36", "37", "38"], "answer": "37", "explanation": "These are n² + 1: 1²+1, 2²+1, …, 6²+1 = 37."},
]

BG = (0.035, 0.055, 0.10, 1)
PANEL = (0.075, 0.105, 0.17, 1)
ACCENT = (0.26, 0.91, 0.70, 1)
TEXT = (0.91, 0.95, 1, 1)
MUTED = (0.58, 0.68, 0.79, 1)


def label(text="", size=18, color=TEXT, **kwargs):
    return Label(text=text, font_size=dp(size), color=color, halign="center", valign="middle", **kwargs)


class BrainGame(App):
    def build(self):
        self.title = "Brain Sprint"
        Window.clearcolor = BG
        self.manager = ScreenManager(transition=SlideTransition(duration=.18))
        self.manager.add_widget(HomeScreen(name="home", app=self))
        self.manager.add_widget(QuizScreen(name="quiz", app=self))
        self.manager.add_widget(ResultScreen(name="result", app=self))
        return self.manager

    def start_game(self, *_):
        self.manager.get_screen("quiz").begin()
        self.manager.current = "quiz"

    def show_results(self):
        self.manager.get_screen("result").present(self.manager.get_screen("quiz"))
        self.manager.current = "result"

    def go_home(self, *_):
        self.manager.current = "home"


class HomeScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        root = BoxLayout(orientation="vertical", padding=[dp(26), dp(36)], spacing=dp(16))
        root.add_widget(Widget(size_hint_y=.45))
        root.add_widget(label("◆  BRAIN SPRINT", 15, ACCENT, size_hint_y=None, height=dp(32)))
        root.add_widget(label("Give your mind\na quick workout.", 34, TEXT, bold=True, size_hint_y=None, height=dp(120)))
        root.add_widget(label("12 puzzles · 6 minutes · no pressure", 16, MUTED, size_hint_y=None, height=dp(44)))
        root.add_widget(Widget(size_hint_y=.15))
        start = Button(text="START CHALLENGE", size_hint_y=None, height=dp(58), background_normal="", background_color=ACCENT, color=BG, bold=True, font_size=dp(17))
        start.bind(on_release=app.start_game)
        root.add_widget(start)
        root.add_widget(label("A recreational puzzle score—not a clinical IQ test.", 12, MUTED, size_hint_y=None, height=dp(52)))
        root.add_widget(Widget(size_hint_y=.35))
        self.add_widget(root)


class QuizScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.seconds = 360
        self.index = 0
        self.score = 0
        self.responses = []
        self._tick = None
        root = BoxLayout(orientation="vertical", padding=[dp(20), dp(20)], spacing=dp(13))
        top = BoxLayout(size_hint_y=None, height=dp(34))
        self.counter = label("", 14, MUTED)
        self.timer = label("06:00", 17, ACCENT, bold=True)
        top.add_widget(self.counter)
        top.add_widget(self.timer)
        root.add_widget(top)
        self.progress = ProgressBar(max=len(QUESTIONS), value=0, size_hint_y=None, height=dp(6))
        root.add_widget(self.progress)
        self.kind = label("", 14, ACCENT, size_hint_y=None, height=dp(28))
        root.add_widget(self.kind)
        self.prompt = label("", 25, TEXT, bold=True)
        root.add_widget(self.prompt)
        self.buttons = []
        for _ in range(4):
            b = Button(text="", size_hint_y=None, height=dp(58), background_normal="", background_color=PANEL, color=TEXT, font_size=dp(17))
            b.bind(on_release=self.choose)
            self.buttons.append(b)
            root.add_widget(b)
        root.add_widget(Widget())
        self.add_widget(root)

    def begin(self):
        if self._tick:
            self._tick.cancel()
        self.index, self.score, self.seconds, self.responses = 0, 0, 360, []
        self.show_question()
        self._tick = Clock.schedule_interval(self.count_down, 1)

    def count_down(self, _dt):
        self.seconds -= 1
        self.timer.text = f"{self.seconds // 60:02d}:{self.seconds % 60:02d}"
        if self.seconds <= 0:
            self.finish()
            return False
        return True

    def show_question(self):
        q = QUESTIONS[self.index]
        self.counter.text = f"PUZZLE {self.index + 1} / {len(QUESTIONS)}"
        self.progress.value = self.index
        self.kind.text = q["kind"].upper()
        self.prompt.text = q["prompt"]
        self.prompt.font_size = dp(24 if len(q["prompt"]) < 80 else 21)
        opts = q["choices"][:]
        shuffle(opts)
        for btn, option in zip(self.buttons, opts):
            btn.text = option
            btn.disabled = False
            btn.background_color = PANEL

    def choose(self, button):
        q = QUESTIONS[self.index]
        selected = button.text
        correct = selected == q["answer"]
        self.responses.append({"question": q["prompt"], "selected": selected, "answer": q["answer"], "correct": correct, "explanation": q["explanation"]})
        if correct:
            self.score += 1
        for b in self.buttons:
            b.disabled = True
            if b.text == q["answer"]:
                b.background_color = (0.12, 0.42, 0.34, 1)
            elif b is button:
                b.background_color = (0.48, 0.18, 0.23, 1)
        Clock.schedule_once(self.next_question, .55)

    def next_question(self, _dt):
        self.index += 1
        if self.index >= len(QUESTIONS):
            self.finish()
        else:
            self.show_question()

    def finish(self):
        if self._tick:
            self._tick.cancel()
            self._tick = None
        self.app.show_results()


class ResultScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.root = BoxLayout(orientation="vertical", padding=[dp(22), dp(20)], spacing=dp(12))
        self.add_widget(self.root)

    def present(self, quiz):
        self.root.clear_widgets()
        total = len(QUESTIONS)
        pct = round(quiz.score / total * 100)
        if pct >= 80:
            headline, note = "Sharp thinking.", "You spotted most of the patterns. Keep challenging yourself."
        elif pct >= 50:
            headline, note = "Good mental reps.", "A few tricky ones—review the explanations and try again."
        else:
            headline, note = "Every puzzle is practice.", "Take a look at the solutions, then have another go."
        self.root.add_widget(label("CHALLENGE COMPLETE", 14, ACCENT, size_hint_y=None, height=dp(30)))
        self.root.add_widget(label(f"{quiz.score} / {total}", 48, TEXT, bold=True, size_hint_y=None, height=dp(82)))
        self.root.add_widget(label(headline, 23, TEXT, bold=True, size_hint_y=None, height=dp(40)))
        self.root.add_widget(label(note, 15, MUTED, size_hint_y=None, height=dp(48)))
        scroll = ScrollView()
        body = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=[dp(2), dp(4)])
        body.bind(minimum_height=body.setter("height"))
        for i, item in enumerate(quiz.responses, 1):
            status = "✓" if item["correct"] else "•"
            txt = f"{status} {i}. {item['question'].replace(chr(10), ' ')}\nYour answer: {item['selected']}  ·  Answer: {item['answer']}\n{item['explanation']}"
            body.add_widget(label(txt, 13, TEXT if item["correct"] else MUTED, size_hint_y=None, height=dp(104)))
        scroll.add_widget(body)
        self.root.add_widget(scroll)
        again = Button(text="PLAY AGAIN", size_hint_y=None, height=dp(54), background_normal="", background_color=ACCENT, color=BG, bold=True)
        again.bind(on_release=self.app.start_game)
        self.root.add_widget(again)
        home = Button(text="HOME", size_hint_y=None, height=dp(44), background_normal="", background_color=PANEL, color=TEXT)
        home.bind(on_release=self.app.go_home)
        self.root.add_widget(home)


if __name__ == "__main__":
    BrainGame().run()
