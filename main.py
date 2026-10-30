import json, os
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup

APP_TITLE = "Online Mock Test"
TEST_SECONDS = 90 * 60
NEGATIVE_MARKING = True
NEGATIVE_VALUE = 0.33

COLORS = {
    "bg": (0.95, 0.96, 0.98, 1),
    "nav": (0.13, 0.27, 0.34, 1),
    "blue": (0.0, 0.36, 0.92, 1),
    "green": (0.10, 0.55, 0.24, 1),
    "purple": (0.43, 0.18, 0.62, 1),
    "orange": (0.95, 0.52, 0.08, 1),
    "black": (0.08, 0.08, 0.08, 1),
    "white": (1, 1, 1, 1),
    "gray": (0.91, 0.92, 0.94, 1),
    "red": (0.82, 0.12, 0.12, 1),
}

def make_label(text, size=16, color=(0.12,0.12,0.12,1), height=None, bold=False):
    w = Label(text=str(text), size_hint_y=None if height else 1,
              height=dp(height) if height else None, color=color,
              font_size=dp(size), bold=bold, halign="left", valign="middle")
    w.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], None)))
    return w

class MockTestApp(App):
    def build(self):
        self.title = APP_TITLE
        Window.clearcolor = COLORS["bg"]
        self.questions = self.load_questions()
        self.answers = [None] * len(self.questions)
        self.review = [False] * len(self.questions)
        self.visited = [False] * len(self.questions)
        self.index = 0
        self.seconds = TEST_SECONDS
        self.finished = False
        self.root_box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        self.show_start()
        Window.bind(on_key_down=self.keyboard_handler)
        return self.root_box

    def load_questions(self):
        path = os.path.join(os.path.dirname(__file__), "questions", "questions.json")
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return [q for q in data if len(q.get("options", [])) >= 2]
        except Exception:
            return [{"q":"questions/questions.json ফাইলটি পাওয়া যায়নি।",
                     "options":["ফাইল যোগ করুন","অ্যাপ বন্ধ করুন"],"answer":0}]

    def clear(self):
        self.root_box.clear_widgets()

    def btn(self, text, callback, color=None, height=46):
        b = Button(text=text, size_hint_y=None, height=dp(height),
                   background_normal="", background_color=color or COLORS["blue"],
                   color=(1,1,1,1), font_size=dp(15))
        b.bind(on_release=lambda *_: callback())
        return b

    def show_start(self):
        self.clear()
        box = BoxLayout(orientation="vertical", spacing=dp(14), padding=dp(18))
        box.add_widget(make_label("ONLINE MOCK TEST", 25, COLORS["nav"], 58, True))
        box.add_widget(make_label(f"মোট প্রশ্ন: {len(self.questions)}", 18, height=42))
        box.add_widget(make_label("সময়: ৯০ মিনিট", 18, height=42))
        box.add_widget(make_label("Negative Marking: ON (প্রতি ভুলে 0.33)", 16, height=42))
        box.add_widget(make_label("Start Test চাপলে পরীক্ষা শুরু হবে।", 15, height=55))
        box.add_widget(self.btn("START TEST", self.start_test, height=54))
        box.add_widget(make_label("Keyboard: A/B/C/D = Option | ←/→ = Previous/Next | Enter = Save & Next", 12, height=65))
        self.root_box.add_widget(box)

    def start_test(self):
        self.seconds = TEST_SECONDS
        self.index = 0
        self.finished = False
        self.show_exam()
        self.tick_event = Clock.schedule_interval(self.tick, 1)

    def tick(self, _dt):
        if self.finished:
            return False
        self.seconds -= 1
        if hasattr(self, "timer_label"):
            self.timer_label.text = "সময় বাকি: " + self.format_time()
        if self.seconds <= 0:
            self.submit_test()
            return False

    def format_time(self):
        return f"{max(0,self.seconds)//60:02d}:{max(0,self.seconds)%60:02d}"

    def show_exam(self):
        self.clear()
        header = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.timer_label = make_label("সময় বাকি: " + self.format_time(), 16, (1,0.8,0.1,1), bold=True)
        self.timer_label.color = COLORS["nav"]
        header.add_widget(self.timer_label)
        header.add_widget(make_label(f"প্রশ্ন: {self.index+1}/{len(self.questions)}", 15, COLORS["nav"]))
        self.root_box.add_widget(header)

        body = BoxLayout(orientation="vertical", spacing=dp(8))
        q = self.questions[self.index]
        self.visited[self.index] = True
        qlabel = make_label(f"{self.index+1}. {q['q']}", 18, height=120, bold=True)
        body.add_widget(qlabel)

        self.option_group = []
        for oi, option in enumerate(q["options"]):
            selected = self.answers[self.index] == oi
            tb = ToggleButton(text=f"{chr(65+oi)}. {option}", group="answers",
                              state="down" if selected else "normal",
                              size_hint_y=None, height=dp(58),
                              background_normal="", background_down="",
                              background_color=COLORS["green"] if selected else COLORS["gray"],
                              color=(1,1,1,1) if selected else (0.12,0.12,0.12,1),
                              halign="left", font_size=dp(15))
            tb.bind(on_release=lambda inst, n=oi: self.select_answer(n))
            self.option_group.append(tb)
            body.add_widget(tb)

        scroll = ScrollView()
        scroll.add_widget(body)
        self.root_box.add_widget(scroll)

        nav = GridLayout(cols=2, spacing=dp(6), size_hint_y=None, height=dp(100))
        nav.add_widget(self.btn("Previous", self.previous, COLORS["nav"]))
        nav.add_widget(self.btn("Next", self.next_question))
        nav.add_widget(self.btn("Clear Response", self.clear_answer, COLORS["orange"]))
        nav.add_widget(self.btn("Mark Review", self.mark_review, COLORS["purple"]))
        self.root_box.add_widget(nav)

        actions = GridLayout(cols=2, spacing=dp(6), size_hint_y=None, height=dp(48))
        actions.add_widget(self.btn("Save & Next", self.next_question))
        actions.add_widget(self.btn("Question Palette", self.show_palette, COLORS["nav"]))
        self.root_box.add_widget(actions)
        self.root_box.add_widget(self.btn("SUBMIT TEST", self.confirm_submit, COLORS["red"], 48))

    def select_answer(self, n):
        self.answers[self.index] = n
        for i, b in enumerate(self.option_group):
            b.background_color = COLORS["green"] if i == n else COLORS["gray"]
            b.color = (1,1,1,1) if i == n else (0.12,0.12,0.12,1)

    def clear_answer(self):
        self.answers[self.index] = None
        self.show_exam()

    def mark_review(self):
        self.review[self.index] = not self.review[self.index]
        self.show_exam()

    def previous(self):
        if self.index > 0:
            self.index -= 1
            self.show_exam()

    def next_question(self):
        if self.index < len(self.questions)-1:
            self.index += 1
            self.show_exam()
        else:
            self.show_palette()

    def status_color(self, i):
        if self.review[i] and self.answers[i] is not None: return COLORS["orange"]
        if self.review[i]: return COLORS["purple"]
        if self.answers[i] is not None: return COLORS["green"]
        if self.visited[i]: return COLORS["white"]
        return COLORS["black"]

    def show_palette(self):
        content = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
        grid = GridLayout(cols=5, spacing=dp(5), size_hint_y=None)
        rows = (len(self.questions)+4)//5
        grid.height = dp(rows*44)
        for i in range(len(self.questions)):
            b = Button(text=str(i+1), size_hint_y=None, height=dp(38),
                       background_normal="", background_color=self.status_color(i),
                       color=(0,0,0,1) if self.status_color(i)==COLORS["white"] else (1,1,1,1))
            b.bind(on_release=lambda inst, n=i: self.jump(n))
            grid.add_widget(b)
        sc = ScrollView()
        sc.add_widget(grid)
        content.add_widget(sc)
        content.add_widget(make_label("কালো: Not Visited | সাদা: Not Answered | সবুজ: Answered | বেগুনি: Review | কমলা: Answered & Review", 12, height=55))
        content.add_widget(self.btn("Close", lambda: popup.dismiss()))
        popup = Popup(title="Question Palette", content=content, size_hint=(0.94,0.85))
        popup.open()

    def jump(self, n):
        self.index = n
        self.show_exam()
        # Close any open palette popup.
        for widget in Window.children:
            pass

    def confirm_submit(self):
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        content.add_widget(make_label("আপনি কি পরীক্ষা জমা দিতে চান?", 17, height=60))
        row = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(48))
        popup = Popup(title="Submit Test", content=content, size_hint=(0.85,0.35))
        row.add_widget(self.btn("না", popup.dismiss, COLORS["nav"]))
        row.add_widget(self.btn("হ্যাঁ, Submit", lambda: (popup.dismiss(), self.submit_test()), COLORS["red"]))
        content.add_widget(row)
        popup.open()

    def submit_test(self):
        if self.finished: return
        self.finished = True
        if hasattr(self, "tick_event"):
            self.tick_event.cancel()
        correct = wrong = unanswered = 0
        for i, q in enumerate(self.questions):
            a = self.answers[i]
            if a is None: unanswered += 1
            elif a == q.get("answer", -1): correct += 1
            else: wrong += 1
        score = correct - (wrong * NEGATIVE_VALUE if NEGATIVE_MARKING else 0)
        percent = (score / len(self.questions) * 100) if self.questions else 0
        self.show_result(correct, wrong, unanswered, score, percent)

    def show_result(self, correct, wrong, unanswered, score, percent):
        self.clear()
        box = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(12))
        box.add_widget(make_label("TEST RESULT", 25, COLORS["nav"], 58, True))
        for line in [f"সঠিক উত্তর: {correct}", f"ভুল উত্তর: {wrong}",
                     f"উত্তর দেননি: {unanswered}",
                     f"স্কোর: {score:.2f} / {len(self.questions)}",
                     f"শতকরা: {percent:.2f}%"]:
            box.add_widget(make_label(line, 18, height=42))
        box.add_widget(self.btn("Review Answers", self.show_review, COLORS["purple"]))
        box.add_widget(self.btn("New Test", self.restart, COLORS["blue"]))
        self.root_box.add_widget(box)

    def show_review(self):
        self.clear()
        layout = BoxLayout(orientation="vertical", spacing=dp(8))
        layout.add_widget(make_label("ANSWER REVIEW", 22, COLORS["nav"], 48, True))
        grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))
        for i, q in enumerate(self.questions):
            a = self.answers[i]
            your = "উত্তর দেননি" if a is None else q["options"][a]
            correct = q["options"][q["answer"]] if 0 <= q["answer"] < len(q["options"]) else "তথ্য নেই"
            block = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(150),
                              padding=dp(8), spacing=dp(4))
            block.add_widget(make_label(f"{i+1}. {q['q']}", 14, height=55, bold=True))
            block.add_widget(make_label(f"আপনার উত্তর: {your}", 13, height=35))
            block.add_widget(make_label(f"সঠিক উত্তর: {correct}", 13, COLORS["green"], 35, True))
            grid.add_widget(block)
        sc = ScrollView()
        sc.add_widget(grid)
        layout.add_widget(sc)
        layout.add_widget(self.btn("New Test", self.restart))
        self.root_box.add_widget(layout)

    def restart(self):
        self.answers = [None] * len(self.questions)
        self.review = [False] * len(self.questions)
        self.visited = [False] * len(self.questions)
        self.seconds = TEST_SECONDS
        self.finished = False
        self.show_start()

    def keyboard_handler(self, _window, key, _scancode, codepoint, _modifiers):
        if self.finished or not self.root_box.children: return
        # Kivy keycodes: left=276, right=275, enter=13.
        if key in (276,): self.previous()
        elif key in (275,): self.next_question()
        elif key in (13, 271): self.next_question()
        elif codepoint and codepoint.lower() in "abcd":
            n = ord(codepoint.lower()) - ord("a")
            if n < len(self.questions[self.index]["options"]):
                self.answers[self.index] = n
                self.show_exam()

if __name__ == "__main__":
    MockTestApp().run()
