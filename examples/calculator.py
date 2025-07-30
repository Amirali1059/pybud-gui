import pybud as pb
from pybud.callbacks import OnKeyboardInputContext
import pybud.widgets as pbw

class Main(pb.Window):
    def __init__(self):
        super().__init__(
            size = (36, 13),
            position = (0, 0),
            title = "Calculator Example"
        )
        self.result = pbw.Label(
            text="0",
            centered=True,
            size=(self.size.width - 4, 1),
            position=(2, 1),
        )
        self.add_widget(self.result)

        buttons = [
            ("7", self.append_digit), ("8", self.append_digit), ("9", self.append_digit), ("/", self.append_operator),
            ("4", self.append_digit), ("5", self.append_digit), ("6", self.append_digit), ("*", self.append_operator),
            ("1", self.append_digit), ("2", self.append_digit), ("3", self.append_digit), ("-", self.append_operator),
            ("0", self.append_digit), (".", self.append_digit), ("=", self.calculate_result), ("+", self.append_operator),
        ]

        for i, (text, callback) in enumerate(buttons):
            x = (i % 4) * 8 + 2
            y = (i // 4) * 2 + 4
            btn = pbw.Button(
                text=text,
                size=(6, 1),
                position=(x, y),
            )
            btn.set_callback(lambda c, t=text: callback(t))
            self.add_widget(btn)
        
        self.add_callback("on_keyboard_input", self.append_char)

    def append_char(self, context: OnKeyboardInputContext):
        if context.key is None:
            return
        key = context.key
        if key.isdigit():
            self.append_digit(key)
        elif key in "+-*/":
            self.append_operator(key)
        elif key in "=":
            self.calculate_result(key)
    
    def append_digit(self, digit):
        if self.result.text.vec[0] == "0":
            self.result.text = ansi.AnsiString(digit)
        else:
            self.result.text = self.result.text + ansi.AnsiString(digit)

    def append_operator(self, operator: str):
        if self.result.text.vec[-1].char in "+-*/":
            self.result.text = self.result.text.split_at(len(self.result.text)-1)[0] + ansi.AnsiString(operator)
        else:
            self.result.text = self.result.text + ansi.AnsiString(operator)

    def calculate_result(self, _):
        try:
            self.result.text = str(eval(self.result.text))
        except Exception:
            self.result.text = "Error"

if __name__ == "__main__":
    import asyncio
    
    import pybud.drawer.ansi as ansi
    ansi.init()

    s = pb.Session((36, 13), background=(100, 100, 250))
    s.add_window(Main())
    asyncio.run(s.show())