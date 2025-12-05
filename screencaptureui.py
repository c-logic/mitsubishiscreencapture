#!/usr/bin/python3
import pathlib
import tkinter as tk
import pygubu

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "screen.ui"
RESOURCE_PATHS = [PROJECT_PATH]


class screenUI:
    def __init__(
        self,
        master=None,
        translator=None,
        on_first_object_cb=None,
        data_pool=None
    ):
        self.builder = pygubu.Builder(
            translator=translator,
            on_first_object=on_first_object_cb,
            data_pool=data_pool
        )
        self.builder.add_resource_paths(RESOURCE_PATHS)
        self.builder.add_from_file(PROJECT_UI)
        # Main widget
        self.mainwindow: tk.Toplevel = self.builder.get_object(
            "toplevel1", master)

        self.savepic: tk.BooleanVar = None
        self.captime: tk.IntVar = None
        self.line1: tk.StringVar = None
        self.line2: tk.StringVar = None
        self.line3: tk.StringVar = None
        self.line4: tk.StringVar = None
        self.line5: tk.StringVar = None
        self.line6: tk.StringVar = None
        self.builder.import_variables(self)

        self.builder.connect_callbacks(self)

    def run(self):
        self.mainwindow.mainloop()

    def callback(self, event=None):
        pass


if __name__ == "__main__":
    app = screenUI()
    app.run()
