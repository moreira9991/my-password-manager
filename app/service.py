from random import choice, randint, shuffle
from tkinter import Button,Entry,Toplevel,Label,Frame,Tk
from app.store_json import EncryptedStore, VaultDecryptionError
from typing import Any
from zxcvbn import zxcvbn

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
    
    win.bind("<Return>", lambda e:btn.invoke())

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

    win.bind("<Return>", lambda e:ok_btn.invoke())
    win.bind("<KP_Enter>", lambda e:ok_btn.invoke())

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

def password_strength_score(score: int) -> str:
    return ["very weak","weak","okay","strong","very strong"][score]

def add_password_msg(parent:Tk,site:str,pwd:str):
    result = zxcvbn(pwd)["score"]
    msg=password_strength_score(result)
    return custom_message_askokcancel(parent=parent, title=site.capitalize(),message=(
                    f"This password is {msg}!\n\n"
                    f"Saving account...\n\n"
                    "Press 'OK' to continue or 'Cancel'.")
            )


def edit_password_msg(parent:Tk,site:str,pwd:str):
    result = zxcvbn(pwd)["score"]
    msg=password_strength_score(result)
    return custom_message_askokcancel(parent=parent, title=f"Editing data for {site.capitalize()}",message=(
                    f"This password is {msg}!\n\n"
                    f"Saving account...\n\n" 
                    "Press 'OK' to continue or 'Cancel'.")
            )


def master_password_msg(parent:Tk,pwd:str):
    result = zxcvbn(pwd)["score"]
    if result<4:
        custom_message_info(parent=parent,title="Error!",message="Stronger password required.")
        return
    msg=password_strength_score(result)
    return custom_message_askokcancel(parent=parent, title=f"Confirm master password.",message=(
                    f"This password is {msg}!\n\n"
                    f"Saving master password...\n\n"
                    "Press 'OK' to continue or 'Cancel'.")
    )
             

def toggle_password(btn:Button,ent:Entry,state:dict):
    # Toggle password visibility in Entry widget
    state["visible"] = not state["visible"]
    if state["visible"]:
        ent.config(show="")
        if btn:
            btn.config(text="Hide")
    else:
        ent.config(show="*")
        if btn:
            btn.config(text="Show")  

class AccountService:
    def __init__(self, store: EncryptedStore) -> None:
        self.store= store
        self.master_password:str  | None = None
        self.data : dict[str,Any]={}
        


    # Returns True if the vault file does not exists yet.
    def is_first_run(self)-> bool:
        return not self.store.path.exists()
    
    def initialize_vault(self,window:Tk, master_pwd:str,confirm_pwd:str ) -> bool:
        if not master_pwd.strip() or not confirm_pwd.strip():
            custom_message_info(
                parent=window,
                title="Error!",
                message="Please don't leave any fields empty.",
            )
            return False

        if master_pwd != confirm_pwd:
            custom_message_info(
                parent=window,
                title="Error!",
                message="The passwords don't match. Please verify and try again.",
            )
            return False

        if not master_password_msg(parent=window, pwd=master_pwd):
            return False

        try:
            # EncryptedStore.load(...) irá:
            # - criar vault vazio se o ficheiro não existir
            # - devolver {} nessa primeira vez
            self.data = self.store.load(master_pwd)
            self.master_password = master_pwd
        except Exception as e:
            custom_message_info(
                parent=window,
                title="Error!",
                message=f"Unexpected error while creating vault:\n{e}",
            )
            return False

        custom_message_info(parent=window, title="Success!", message="Master password set!")
        return True
    
## WORKING HERE - separar em duas funcoes
    def verify_master(self, window: Tk, master_pwd: str) -> bool:
        """
        Normal login: verify master password and load data into memory.
        """
        if not master_pwd.strip():
            custom_message_info(
                parent=window,
                title="Error!",
                message="Please provide the master password.",
            )
            return False

        try:
            self.data = self.store.load(master_pwd)
            self.master_password = master_pwd
        except VaultDecryptionError:
            custom_message_info(
                parent=window,
                title="Error!",
                message="Provide the correct password to continue.",
            )
            return False


        except Exception as e:
            custom_message_info(
                parent=window,
                title="Error!",
                message=f"Unexpected error while loading vault:\n{e}",
            )
            return False

        custom_message_info(parent=window, title="Success!", message="Welcome back!")
        return True
    
    def confirm_current_master(self, window: Tk, master_pwd: str) -> bool:
        """
        Used inside the app (not at login) to confirm the current master password.

        Does NOT reload the vault, only compares against the master already in memory.
        """
        if not master_pwd.strip():
            custom_message_info(
                parent=window,
                title="Error!",
                message="Please provide the master password.",
            )
            return False

        if master_pwd != self.master_password:
            custom_message_info(
                parent=window,
                title="Error!",
                message="Provide the correct password to continue.",
            )
            return False

        return True


## WORKING HERE


#done
    def find(self,site:str,username:str):
        key = normalize_site(site)
        for acc in self.data.get(key,[]):
            if acc["username"]==username:
                return acc 
        return None
    


#done
#checks if userinpt allready exists in data
    def check_acc(self,entry,check_user:str,username_inpt:str):
        for acc in entry:
            if (username_inpt== acc["username"]) and (username_inpt!=check_user):
                return True

#done
    def add(self,window:Tk, site:str, username:str, password: str):
        key = normalize_site(site)
        #checks for empty entries
        if not site.strip() or not username.strip() or not password.strip():
            custom_message_info(parent=window,title="Error!",message="Please don't leave any fields empty.")
            return False

        #Checking for duplicate username for same plataform
        check_user=self.data.get(key)
        if check_user:
            for acc in check_user:
                if username ==acc["username"]:
                    custom_message_info(parent=window,title="Error",message=f"{username} account allready saved for {site.capitalize()}!")
                    return False
                
        #Checks for password strenght
        if not add_password_msg(parent=window,site=site,pwd=password):
            return False
        if key not in self.data:
            self.data[key]=[]
        
        self.data[key].append({"username":username,"password":password})

        try:
            self.store.save(self.master_password,self.data)
            custom_message_info(parent=window,title="Success!",message=f"{site.capitalize()} account saved.")
        except Exception as e:
            custom_message_info(parent=window,title="Error",message= f"Failed to save data: {e}")
            return False
        finally:
            return True
        

# done
# edits accounts, before checking and blocking for unwanted interactions
    def edit (self,main_window:Tk,window:Tk,site:str,username:str,new_username:str,new_password:str):
        key = normalize_site(site)
        entry=self.data.get(key)

        if self.check_acc(entry=entry,check_user=username,username_inpt=new_username):
            custom_message_info(
                        parent=window,
                        title="Error!",
                        message=(f"This account already exits for {site.capitalize()}."),
                        )
            return

        for acc in entry:
            if username == acc["username"]:
                #checking for invalid inputs
                if (new_username == acc["username"]) and (new_password == acc ["password"]):
                    custom_message_info(parent=window, title="Error!", message=(
                        "No changes detected."
                    ))
                    return
                
                if (not new_username.strip()) or (not new_password.strip()):
                    custom_message_info(parent=window, title="Error!", message=(
                        "Don't leave any fields empty"
                    ))
                    return
                
                #confirm change
                if edit_password_msg(parent=window,site=site,pwd=new_password):
                    if self.master_password is None:
                        custom_message_info(
                            parent=window,
                            title="Error",
                            message="Internal error: master password not set.",
                        )
                        return False


                    acc["username"]= new_username
                    acc["password"]= new_password
                    self.store.save(self.master_password,self.data)

                    custom_message_info(parent=window,title="Success!", message=f"{site.capitalize()} account saved.")
                    window.destroy()
                    main_window.destroy()
                    break
                else:
                    return


# done
    def delete (self,main_window:Tk,window:Tk,site:str,username:str,pwd:str):
        if custom_message_askokcancel(
            parent=window,
            title=f"Deleting data for {site.capitalize()}",
            message=f"Press 'OK' to continue or press 'Cancel'."
            ):
            key = normalize_site(site)
            arr = self.data.get(key,[])
            for i, a in enumerate(arr):
                if a ["username"]== username:
                    arr.pop(i)
                    if not arr: 
                        self.data.pop(key,None)
                    self.store.save(self.master_password,self.data)
            
            custom_message_info(parent=window,title="Success!",message=f"{site.capitalize()} account deleted.")
            window.destroy()
            main_window.destroy()
        else:
            return
        
#done
    def master_pwd_set (self,main_window:Tk,window:Tk,master_pwd:str,confirm_m_pwd):
        if not master_pwd.strip():
            custom_message_info(parent=window, title="Error!", message="To continue, set a new master password.")
            return
        
        if master_pwd != confirm_m_pwd:
            custom_message_info(parent=window,title="Error!",message="The passwords don't match. Please verify and try again.")
            return

        if master_pwd == self.master_password:
            custom_message_info(parent=window,title="Error!",message="No changes detected.")
            return

        
        if not master_password_msg(parent=window,pwd=master_pwd):
            return False
        
        self.store.save(master_password=master_pwd,data=self.data)
        self.master_password = master_pwd
        
        custom_message_info(parent=window, title="Success!", message="Master password set!")
        return True

            
