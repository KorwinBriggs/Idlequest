
from rich import print
from rich.console import Console
from rich.prompt import Prompt


console = Console()

def write(text):
    return console.print(f"\n{text}")

def write_event(text):
    return console.print(f"{text}")

def write_gain(text):
    return console.print(f"[cyan3]{text}")

def write_gain_failed(text):
    return console.print(f"[turquoise4]{text}")

def write_loss(text):
    return console.print(f"[orange_red1]{text}")

def write_loss_failed(text):
    return console.print(f"[deep_pink4]{text}")

def read(text, choice_array=None):
    if choice_array:
        return Prompt.ask(f"\n{text}", choices=choice_array)
    else:
        return Prompt.ask(f"\n{text}")
    
def write_error(text):
    return console.print(f"\n[red3]{text}")