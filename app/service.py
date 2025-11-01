from random import choice, randint, shuffle
from tkinter import Button,Entry,Toplevel,Label,Frame,Tk
from app.store_json import JsonStore

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

class AccountService:
    def __init__(self, store: JsonStore):
        self.store = store
        self.data= self.store.load()


    def list_all(self):
        for site, accounts in self.data.items():
            if site =="__MASTERPASSWORD":
                continue
            for acc in accounts:
                yield (site,acc["username"],acc["password"])

    def find(self,site:str,username:str):
        key = normalize_site(site)
        for acc in self.data.get(key,[]):
            if acc["username"]==username:
                return key, acc
        return None, None
    

    def check_acc(self,site:str,username:str):
        key = normalize_site(site)
        if not any (a["username"]==username for a in self.data[key]):
            raise ValueError[f""]
              # A TRABALHAR AQUI   
    

    def add(self, site:str, username:str, password: str):
        key = normalize_site(site)
        self.data.setdefault(key,[])
        if any (a["username"]==username for a in self.data[key]):
            raise ValueError("Account already exists for this site/username.")
        self.data[key].append({"username":username,"password":password})
        self.store.save(self.data)


    def edit (self,site:str,username:str,new_username:str,new_password:str):
        key, acc = self.find(site,username)
        if not acc:
            raise KeyError ("Account not found.")
        
        # prevenir duplicados se alterar o username
        if new_username != username and any (a["username"]==new_username for a in self.data[key]):
            raise ValueError ("Another account with this username already exists for this site.")
        
        acc["username"] = new_username
        acc["password"] = new_password
        self.store.save(self.data)


    def delete (self,site:str,username:str):
        key = normalize_site(site)
        arr = self.data.get(key,[])
        for i, a in enumerate(arr):
            if a ["username"]== username:
                arr.pop(i)
                if not arr: 
                    self.data.pop(key,None)
                self.store.save(self.data)
                return
        raise KeyError("Account not found to delete.")
        
        
        