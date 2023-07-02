
from rich import print
from rich.console import Console
from rich.prompt import Prompt
import traceback


console = Console()

def write(text):
    console.print(f"\n{text}")

def write_event(text):
    console.print(f"{text}")

def write_gain(text):
    console.print(f"[cyan3]{text}")

def write_gain_failed(text):
    console.print(f"[turquoise4]{text}")

def write_loss(text):
    console.print(f"[orange_red1]{text}")

def write_loss_failed(text):
    console.print(f"[deep_pink4]{text}")

def read(text, choice_array=None):
    if choice_array:
        return Prompt.ask(f"\n{text}", choices=choice_array)
    else:
        return Prompt.ask(f"\n{text}")
    
def write_error(text):
    console.print(f"\n[red3]{text}")
    traceback.print_exc()


if __name__ == '__main__':

    test = read("test prompt")
    write(test)