from random import choice, randint, shuffle
from tkinter import Button,Entry,Toplevel,Label,Frame,Tk

def normalize_site(name: str) -> str:
#Normalize website key to avoid case/whitespace issues.
    return name.strip().lower()


def generate_password() -> str:
#Generate a random password (similar rules to original code)."""
    letters = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    numbers = list("0123456789")
    symbols = list("!#$%&()*+")

    password_list = [choice(letters) for _ in range(randint(8, 10))]
    password_list += [choice(numbers) for _ in range(randint(2, 4))]
    password_list += [choice(symbols) for _ in range(randint(2, 4))]
    shuffle(password_list)
    return "".join(password_list)



def custom_message_info(parent:Tk, title, message):
    win= Toplevel(parent)
    win.withdraw()
    win.title(title)
    win.configure(padx=10,pady=10)

    win.resizable(False,False)
    win.attributes("-topmost",True)
    win.transient(parent)

    parent.update_idletasks()
    x = parent.winfo_rootx()+(parent.winfo_width()//2-150)
    y = parent.winfo_rooty()+(parent.winfo_height()//2-150)
    win.geometry(f"+{x}+{y}")

    lbl = Label(win, text=message,font=("Arial",12,"bold"),justify="center")
    lbl.pack(expand=True,pady=20)
    btn = Button(win, text="OK",command=win.destroy,width=10)
    btn.pack(pady=10)

    win.deiconify()
    win.grab_set()
    btn.focus_set()
    win.wait_window()


def custom_message_askokcancel(parent:Tk, title, message)-> bool:
    result_message=False

    win= Toplevel(parent)
    win.withdraw()
    win.title(title)
    win.configure(padx=10,pady=10)

    win.resizable(False,False)
    win.attributes("-topmost",True)
    win.transient(parent)

    parent.update_idletasks()
    x = parent.winfo_rootx()+(parent.winfo_width()//2-150)
    y = parent.winfo_rooty()+(parent.winfo_height()//2-150)
    win.geometry(f"+{x}+{y}")

    lbl = Label(win, text=message,font=("Arial",12,"bold"),justify="center")
    lbl.pack(expand=True,pady=10)

    btn_frame = Frame(win)
    btn_frame.pack(pady=10)

    def on_ok():
        nonlocal result_message
        result_message= True
        win.destroy()

    def on_cancel():
        nonlocal result_message
        result_message= False
        win.destroy()

    ok_btn = Button(btn_frame, text="OK",command=on_ok,width=10)
    ok_btn.pack(side="left",padx=20)

    cancel_btn = Button(btn_frame, text="Cancel",command=on_cancel,width=10)
    cancel_btn.pack(side="right",padx=20)

    win.deiconify()
    win.grab_set()
    ok_btn.focus_set()
    win.wait_window()

    return result_message


def toggle_password(btn:Button,ent:Entry,state:dict):
    # Toggle password visibility in Entry widget
    state["visible"] = not state["visible"]
    if state["visible"]:
        ent.config(show="")
        btn.config(text="Hide")
    else:
        ent.config(show="*")
        btn.config(text="Show")  

        