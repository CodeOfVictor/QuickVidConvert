from textual.app import App, ComposeResult
from textual.containers import Center
from textual.widgets import Label, Button

def ask_upload_confirmation() -> bool:
    app = ConfirmUploadApp()
    return app.run_and_get_result()

def ask_delete_confirmation() -> bool:
    app = ConfirmDeleteApp()
    return app.run_and_get_result()

class ConfirmUploadApp(App):

    def __init__(self):
        super().__init__()
        self.result = None

    def compose(self) -> ComposeResult:
        with Center():
            yield Label("Do you want to upload the content to the server?", id="question")
            yield Button("Yes", id="yes", variant="success")
            yield Button("No", id="no", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.result = True
        elif event.button.id == "no":
            self.result = False
        self.exit()

    def run_and_get_result(self) -> bool:
        self.run()
        return self.result

class ConfirmDeleteApp(App):

    def __init__(self):
        super().__init__()
        self.result = None

    def compose(self) -> ComposeResult:
        with Center():
            yield Label("Do you want to delete the file after conversion?", id="question")
            yield Button("Yes", id="yes", variant="success")
            yield Button("No", id="no", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.result = True
        elif event.button.id == "no":
            self.result = False
        self.exit()

    def run_and_get_result(self) -> bool:
        self.run()
        return self.result