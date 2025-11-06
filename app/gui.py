from tkinter import Tk, Canvas, PhotoImage, Label, Entry, Button, END, messagebox,Toplevel, Frame, StringVar, Scrollbar,ttk
from pathlib import Path
from app.service import generate_password, normalize_site, custom_message_askokcancel, custom_message_info, toggle_password, AccountService, add_password_msg, edit_password_msg, master_password_msg
from app.store_json import JsonStore
from zxcvbn import zxcvbn

## CHECKING CODE --> REFACTORING
class AppGUI:
    def __init__(self, root: Tk)-> None:
        self.root = root
        self.root.title("My Password Manager")
        self.root.config(padx=20,pady=20)
        self.root.resizable(False,False)
        self._show_state= {"visible":False}

        self.root.bind("<Return>", lambda e:self.add_btn.invoke())
        self.root.bind("<KP_Enter>", lambda e:self.add_btn.invoke())

        #Store/data
        self.store =JsonStore(Path("Passwords_data.json"))
        self.data = self.store.load()

        self.canvas = Canvas (width=1000, height=340,highlightthickness=0)
        logo_path = Path("assets/logo.png")
        self.logo = PhotoImage(file=str(logo_path))
        
        self.canvas.create_image(500, 160, image=self.logo)
        self.canvas.grid(column=0,columnspan=3,row=0,sticky="w")

        #website
        self.web_text = Label(text="Website:")
        self.web_text.grid(column=0, row=1)
        self.web_inpt = Entry(width=33)
        self.web_inpt.grid(column=1, row=1, columnspan=2, sticky="W")

        #username/email
        self.user_text = Label(text="E-mail/Username:")
        self.user_text.grid(column=0, row=2)
        self.user_inpt = Entry(width=33)
        self.user_inpt.grid(column=1, row=2, columnspan=2, sticky="W")

        #password
        self._show_state= {"visible":False}
        self.pass_text = Label(text="Password:")
        self.pass_text.grid(column=0, row=3)
        self.pass_inpt = Entry(width=33,show="*")
        self.pass_inpt.grid(column=1, row=3, sticky="W")  

        #buttons
        self.toggle_btn= Button(
            text="Show",
            width=6,
            command=lambda:toggle_password(
                btn=self.toggle_btn,
                ent=self.pass_inpt,
                state=self._show_state
            )
        )
        self.toggle_btn.grid(column=2,row=3,sticky="we")
        self.generate_btn = Button(text="Generate password", command=self.on_generate)
        self.generate_btn.grid(column=2,row=2,sticky="we")

        self.add_btn = Button(text="Add", width=50, command=self.on_add)
        self.add_btn.grid(column=1, row=5, columnspan=2, sticky="W")

        self.search_btn = Button(text="My password's", command=self.on_cls)
        self.search_btn.grid(column=2, row=1, sticky="WE")

        #Focous will start on the web entry box
        self.web_inpt.focus()


    # Generates a lvl4 password
    def on_generate(self) -> None:
        password = generate_password()
        # Replace any existing text in the password field
        self.pass_inpt.delete(0, END)
        self.pass_inpt.insert(0, password)

## ---> ALL GOOD

    #Adds account to JSON -> encripted DB soon
    def on_add(self) -> None:
        site = self.web_inpt.get()
        username = self.user_inpt.get()
        pwd = self.pass_inpt.get()
        key = normalize_site(site)

        # checks if entrys are empty
        if not site.strip() or not username.strip() or not pwd.strip():
            custom_message_info(self.root,title="Error!",message="Please don't leave any fields empty.")
            return
        
## ---> ALL GOOD

        # Checking for duplicate username
        checking_username = self.data.get(key)
        if checking_username:
            for acc in checking_username:
                if username == acc["username"]:
                    custom_message_info(parent=self.root,title="Error!",message=f"{username} account allready saved for {site.capitalize()}!")
                    return
        #Checks for password strength
        if not add_password_msg(parent=self.root, site=site, pwd=pwd, user=username):
            return
        
        if key not in self.data:
            self.data[key]=[]
            
        self.data[key].append({"username": username, "password": pwd})
        try:
            self.store.save(self.data)
            custom_message_info(parent=self.root,title="Success",message=f"{site.capitalize()} account saved.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")
            return
        finally:
            # Reset fields (keep focus on website for next entry)
            self.web_inpt.delete(0, END)
            self.user_inpt.delete(0, END)
            self.pass_inpt.delete(0, END)
            self.web_inpt.focus_set()
 
    def on_cls(self)-> None:
        MyPasswords(self.root)


class PasswordListView:
    def __init__(self, parent:Tk):
        self.parent = parent
        self.canvas = Canvas(parent, highlightthickness=0)
        self.scrollbar = Scrollbar(parent, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # frame interno
        self.inner_frame = Frame(self.canvas)
        self.window_id = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # bindings de layout e scroll
        self.inner_frame.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self._smooth_scroll(self.canvas)

        # armazena refs de linhas
        self.rows = []

    def _on_inner_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.window_id, width=self.canvas.winfo_width())

    def _smooth_scroll(self, canvas:Canvas, step=0.008):
        def clamp(x, lo=0.0, hi=1.0): return max(lo, min(hi, x))
        def move(sign):
            first, _ = canvas.yview()
            canvas.yview_moveto(clamp(first + sign * step))

        system = str(canvas.tk.call('tk', 'windowingsystem'))
        if system == "x11":
            canvas.bind_all("<Button-4>", lambda e: move(-1), add="+")
            canvas.bind_all("<Button-5>", lambda e: move(+1), add="+")
        elif system == "aqua":
            canvas.bind_all("<MouseWheel>", lambda e: move(-1 if e.delta > 0 else +1), add="+")
        else:
            canvas.bind_all("<MouseWheel>", lambda e: move(-1 if e.delta > 0 else +1), add="+")

    def render(self, data: dict):
        #Renderiza as linhas a partir de um dicionário de sites e contas."""
        # Limpa linhas antigas
        for r in self.rows:
            for w in r["widgets"]:
                w.destroy()
        self.rows.clear()

        cnt = 0
        bg_default = self.parent.cget("bg")

        for site, accounts in data.items():
            if site == "__MASTERPASSWORD":
                continue
            for acc in accounts:
                username = acc["username"]
                password = acc["password"]

                bg = bg_default
                site_var = StringVar(value=site.capitalize())
                user_var = StringVar(value=username)
                pass_var = StringVar(value=password)

                site_ent = Entry(self.inner_frame, textvariable=site_var, state="readonly",
                                 relief="flat", readonlybackground=bg, fg="black", width=15)
                user_ent = Entry(self.inner_frame, textvariable=user_var, state="readonly",
                                 relief="flat", readonlybackground=bg, fg="black", width=25)
                pass_ent = Entry(self.inner_frame, textvariable=pass_var, state="readonly",
                                 relief="flat", readonlybackground=bg, fg="black", width=20)

                site_ent.grid(column=0, row=cnt, sticky="w", padx=10, pady=5)
                user_ent.grid(column=1, row=cnt, sticky="w", padx=10, pady=5)
                pass_ent.grid(column=2, row=cnt, sticky="w", padx=10, pady=5)

                self.rows.append({
                    "widgets": (site_ent, user_ent, pass_ent),
                    "data": (site, username, password)
                })
                cnt += 1

class MyPasswords:
    def __init__(self, root1:Tk):
        self.root1=Toplevel(root1) 
        self.root1.transient(root1)
        self.root1.grab_set() 
        self.root1.title("My Password's")
        self.root1.config(padx=10,pady=10)
        self.root1.geometry("1580x1000")
        self.root1.resizable(False,False)

        self.root1.grid_rowconfigure(0,weight=0)
        self.root1.grid_rowconfigure(1,weight=1)
        self.root1.grid_columnconfigure(0,weight=1)
        self.root1.grid_columnconfigure(1,weight=1)
        self.root1.grid_columnconfigure(2,weight=1)

        self.store =JsonStore(Path("Passwords_data.json"))
        self.service= AccountService(self.store)
        self.data = self.store.load()
        self.bg=self.root1.cget("bg")
        
        self.root1.bind("<Return>", lambda e:self.search_btn.invoke())
        self.root1.bind("<KP_Enter>", lambda e:self.search_btn.invoke())
        
        right_container = Frame(self.root1)
        right_container.grid(row=1,column=4,sticky="n")

        Label(self.root1, text="Site", font=("Arial", 10, "bold")).grid(column=0, row=0, sticky="w", padx=10, pady=5)
        Label(self.root1, text="Email/Username", font=("Arial", 10, "bold")).grid(column=1, row=0, sticky="w", padx=10, pady=5)
        Label(self.root1, text="Password", font=("Arial", 10, "bold")).grid(column=2, row=0, sticky="w", padx=10, pady=5)

        left_container = Frame(self.root1)
        left_container.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=0, pady=0)

        self.password_list = PasswordListView(left_container)
        self.password_list.render(self.data)
        
        self.wbsite=Entry(self.root1,width=20)
        self.wbsite.grid(column=3,row=0)

        self.search_btn = Button(self.root1,text="Search",command=self.onsearch)
        self.search_btn.grid(column=4,row=0,sticky="we")

        self.manage_pwd_btn = Button(right_container,text="Manage Passwords",command=self.on_manage)
        self.manage_pwd_btn.pack(fill="x")

        self.manage_master_btn=Button(right_container,text="Manage\nMaster Password",command=self.on_manage_mpwd)
        self.manage_master_btn.pack(fill="x")

        self.backup_btn=Button(right_container,text="Backup\npassword's")
        self.backup_btn.pack(fill="x",anchor="s")

        self.wbsite.focus()

    
    def onsearch(self) -> None:
        site = self.wbsite.get()
        if not site.strip():
            custom_message_info(parent=self.root1,title="Error!", message="Please type a website to search.")
            return
        #check if exists
        entry = self.data.get(normalize_site(site))

        if entry:
            root2=Toplevel(self.root1)
            root2.title(site.capitalize())
            Label(root2, text="Email/Username", font=("Arial",10,"bold")).grid(column=0, row= 0 ,sticky="w",padx=10,pady=5)
            Label(root2, text="Password", font=("Arial",10,"bold")).grid(column=1, row= 0 ,sticky="w",padx=10,pady=5)
            root2.transient(self.root1) 
            root2.grab_set()

            cnt=1
            for acc in entry:
                email = acc["username"]
                pwd = acc["password"]
                #user
                user_var = StringVar(value=email)
                user_entry= Entry(root2,
                                  textvariable=user_var,
                                  state="readonly",
                                  relief="flat",
                                  readonlybackground=self.bg,
                                  fg="black",
                                  exportselection=1,
                                  width=30)
                user_entry.grid(column=0,row=cnt,sticky="w",padx=10,pady=5)

                #pass
                pass_var=StringVar(value=pwd)
                pass_entry=Entry(root2,
                                 textvariable=pass_var,
                                 state="readonly",
                                 relief="flat",
                                 readonlybackground=self.bg,
                                 fg="black",
                                 exportselection=1,
                                 width=25)
                pass_entry.grid(column=1,row=cnt,sticky="w",padx=10,pady=5)

                cnt+=1
        else:
            custom_message_info(parent=self.root1, title="Error!", message=f"No data saved for {site.capitalize()}")


    # to enable btns on_off= False
    # to disable btns on_off=True
    def disable_btns(self,on_off:bool):
        if on_off == True:
            self.manage_pwd_btn.config(state="disabled")
            self.manage_master_btn.config(state="disabled")
            self.search_btn.config(state="disabled")
            self.backup_btn.config(state="disabled")
            self.wbsite.config(state="disabled")
        if on_off == False:
            self.manage_pwd_btn.config(state="normal")
            self.manage_master_btn.config(state="normal")
            self.search_btn.config(state="normal")
            self.backup_btn.config(state="normal")
            self.wbsite.config(state="normal")


    def on_manage(self):
        self.root3=Toplevel(self.root1)
        self.root3.title("Manage Passwords")
        self.root3.config(padx=10,pady=10)
        self.root3.resizable(False,False)

        self.root3.bind("<Return>", lambda e:self.manage_search_btn.invoke())
        self.root3.bind("<KP_Enter>", lambda e:self.manage_search_btn.invoke())

        #disable previous buttons
        # Here we disable buttons to prevent doing anything on the previous page, other than being
        # possible to coppy info from the accounts
        self.disable_btns(on_off=True)

        #Comporta se como dialogo do parent, para continuar é preciso fechar
        self.root3.transient(self.root1) 

        Label(self.root3, text="Site", font=("Arial",10,"bold")).grid(column=0, row= 0 ,sticky="w",padx=10,pady=5)
        Label(self.root3, text="Email/Username", font=("Arial",10,"bold")).grid(column=0, row= 1 ,sticky="w",padx=10,pady=5)

        self.site_inpt = Entry(self.root3,width=30)
        self.site_inpt.grid(column=1,row=0)

        self.user_inpt = Entry(self.root3,width=30)
        self.user_inpt.grid(column=1,row=1)

        self.manage_search_btn=Button(self.root3,text="Search",command=self.on_manage_search)
        self.manage_search_btn.grid(column=2, row=0,sticky="WE")

        self.root3.bind("<Destroy>", lambda e:self.disable_btns(on_off=False))

        self.site_inpt.focus()

        
    def on_manage_search(self):
        self.site = self.site_inpt.get()
        self.user = self.user_inpt.get()
        key = normalize_site(self.site)
        if (not self.site.strip()) or (not self.user.strip()):
            custom_message_info(parent=self.root3, title="Error!", message="Please don't leave any fields empty.")
            return
        
        self.entry= self.data.get(key)
        if self.entry:
            a=0
            for acc in self.entry:
                if self.user == acc["username"]:
                    password= acc["password"]
                    a=1
            if a==0:
                custom_message_info(parent=self.root3, title="Error!", message=f"Username/Email provided is not saved for {key.capitalize()}")
                return
            else:
                self.manage_search_btn.config(state="disabled")
                Label(self.root3, text="Password", font=("Arial",10,"bold")).grid(column=0, row= 2 ,sticky="w",padx=10,pady=5)
                self.pwd_entry=Entry(self.root3,width=30)
                self.pwd_entry.grid(column=1,row=2)
                self.pwd_entry.insert(0,f"{password}")

                delete_btn=Button(self.root3, text="Delete",command=lambda:self.on_delete(site=self.site,username=self.user))
                delete_btn.grid(column=2,row=2,sticky="WE")

                edit_btn=Button(self.root3,text="Edit",command=lambda:self.on_edit())
                edit_btn.grid(column=2,row=1,sticky="WE")
        else:
            custom_message_info(parent=self.root3,title="Error!",message=f"No data found for {key.capitalize()}")


    def on_edit(self):
        ## --> refactor here1
        #result=zxcvbn(self.pwd_entry.get())
        a=0
        for acc in self.entry:
            if (self.user_inpt.get()== acc["username"]) and (self.user_inpt.get()!=self.user):
                a+=1

        if a ==1:
            custom_message_info(
                        parent=self.root3,
                        title="Error!",
                        message=(f"This account already exits for {self.site.capitalize()}."),
                        )
            return
        
        for acc in self.entry:
            if self.user == acc["username"]:
                #Checking if there are any changes
                if (self.user_inpt.get() == acc["username"]) and (self.pwd_entry.get()==acc["password"]):
                    custom_message_info(
                        parent=self.root3,
                        title="Error!",
                        message=(f"No changes detected."),
                        )
                    return
                
                if not edit_password_msg(parent=self.root3,site=self.site,pwd=self.pwd_entry.get(),user=self.user_inpt.get()):    
            
                    return  
                else:
                    acc["username"]= self.user_inpt.get()
                    acc["password"]= self.pwd_entry.get()
                    self.store.save(self.data)

                    custom_message_info(parent=self.root3,title="Success!", message=f"You edited {self.user_inpt.get()} account data for {self.site.capitalize()}")
                    self.root3.destroy()
                    self.root1.destroy()
                    break
            ## --> refactor here1

    def on_delete(self,site,username):
        confirm=custom_message_askokcancel(
            parent=self.root3,
            title=f"Deleting data for {self.site.capitalize()}",
            message=(
                f"Username/Email: {self.user}\nPassword: {self.pwd_entry.get()}\n\n"
                f"Press 'OK' to delete data or press 'Cancel'."
                )
        )
        if not confirm:
            return
        
        self.service.delete(site,username)
        custom_message_info(parent=self.root3,title="Success!",message=f"You have deleted {username} account data.")
        # here we can instead of closing the window, dinamically update the pasword list view
        self.root3.destroy()
        self.root1.destroy()


    def on_manage_mpwd(self):
        self.root4=Toplevel(self.root1)
        self.root4.title("Provide master password to continue.")
        self.root4.config(padx=10,pady=10)
        self.root4.resizable(False,False)
        self.root4.transient(self.root1) 
        self.root4.grab_set() 
        self.root4.bind("<Return>", lambda e:self.enter_btn.invoke())
        self.root4.bind("<KP_Enter>", lambda e:self.enter_btn.invoke())
        self._show_state= {"visible":False}

        Label(self.root4, text="Master password: ").grid(column=0, row= 0 ,sticky="w",padx=10,pady=5)

        self.mpwd_inpt=Entry(self.root4,width=25,show="*")
        self.mpwd_inpt.grid(column=1,row=0)

        self.show_info=Button(self.root4,width=8,text="Show",command=lambda:toggle_password(btn=self.show_info,ent=self.mpwd_inpt,state=self._show_state))
        self.show_info.grid(row=0,column=2)

        self.enter_btn=Button(self.root4,text="Confirm",command=self.on_verify_mpwd)
        self.enter_btn.grid(row=0,column=3)

        self.mpwd_inpt.focus()
        

    def on_verify_mpwd(self)->None:
        mpswd=self.mpwd_inpt.get()
        if mpswd == self.data["__MASTERPASSWORD"]["password"]:
            custom_message_info(parent=self.root4,title="Success!",message="Press 'OK' to continue.")
            self.root4.destroy()

            #set new
            self.root5=Toplevel(self.root1)
            self.root5.title("Set new master password.")
            self.root5.config(padx=10,pady=10)
            self.root5.transient(self.root1) 
            self.root5.grab_set()
            self.root5.bind("<Return>", lambda e:self.edit_enter_btn.invoke())
            self.root5.bind("<KP_Enter>", lambda e:self.edit_enter_btn.invoke())
            self._show_state= {"visible":False}
            self.confirm_show_state= {"visible":False}

            Label(self.root5, text="Master password: ").grid(column=0, row= 0 ,sticky="w",padx=10,pady=5)
            Label(self.root5, text="Confirm password: ").grid(column=0,row=1, sticky= "w",padx=10,pady=5)

            self._mpwd_inpt=Entry(self.root5,width=25,show="*")
            self._mpwd_inpt.grid(column=1,row=0)

            self.confirm_mpwd_inpt=Entry(self.root5,width=25,show="*")
            self.confirm_mpwd_inpt.grid(column=1,row=1)

            self.show_info=Button(
                self.root5,
                width=8,
                text="Show",
                command=lambda:toggle_password(
                    btn=self.show_info,
                    ent=self._mpwd_inpt,
                    state=self._show_state
                )
            )
            self.show_info.grid(row=0,column=2)

            self.confirm_show_info=Button(
                self.root5,
                width=8,
                text="Show",
                command=lambda:toggle_password(
                    btn=self.confirm_show_info,
                    ent=self.confirm_mpwd_inpt,
                    state=self.confirm_show_state
                )
            )
            self.confirm_show_info.grid(row=1,column=2)

            self.edit_enter_btn=Button(self.root5,text="Confirm",command=self.on_edit_mpw)
            self.edit_enter_btn.grid(row=2,column=1,columnspan=2,sticky="we")

            self._mpwd_inpt.focus()

        else:
            custom_message_info(parent=self.root4, title="Error!",message="Provide the correct password to continue.")
            return
        
## -->  NEED TO REFACTOR HERE
    def on_edit_mpw(self)->None:
        mpswd=self._mpwd_inpt.get()
        key="__MASTERPASSWORD"

        ## --> refactor here

        if mpswd == "":
            custom_message_info(
                parent=self.root5,title="Error!",
                message="To continue, set a new master password."
                )
        
        elif mpswd != self.confirm_mpwd_inpt.get():
            custom_message_info(
                parent=self.root5,title="Error!",
                message="The passwords don't match. Please verify and try again."
                )

        elif mpswd == self.data[key]["password"]:
            custom_message_info(
                parent=self.root5,
                title="Error!",
                message="No changes detected."
            )

            ## --> refactor here
        
        else:
            if master_password_msg(parent=self.root5,pwd=mpswd):
                self.data[key]={"password":mpswd}
                self.store.save(self.data)
                custom_message_info(parent=self.root5, title="Success!", message="Master password set!")
                self.root5.destroy()
                self.root1.destroy()
            else:
                return
            
## --> NEED TO REFACTOR HERE
  

class MasterGUI:
    def __init__(self, root: Tk)-> None:
        self.root = root
        self.root.title("Provide master password to continue")
        self.root.config(padx=20,pady=20)
        self.root.resizable(False,False)

        self.store =JsonStore(Path("Passwords_data.json"))
        self.data = self.store.load()
        self.result = False
        self._show_state = {"visible":False}
        self._conf_show_state = {"visible":False}

        self.root.bind("<Return>", lambda e:self.add_btn.invoke())
        self.root.bind("<KP_Enter>", lambda e:self.add_btn.invoke())

        if not "__MASTERPASSWORD" in self.data:
            self.pass_text = Label(text="Set a master password:")
            self.pass_text.grid(column=0, row=0)

            self.pass_inpt = Entry(width=32,show="*")
            self.pass_inpt.grid(column=1, row=0, sticky="W")

            self.conf_pass_text = Label(text="Confirm master password:")
            self.conf_pass_text.grid(column=0, row=1)

            self.conf_pass_inpt = Entry(width=32,show="*")
            self.conf_pass_inpt.grid(column=1, row=1, sticky="W")

            self.toggle_btn= Button(
                self.root,
                width=8,
                text="Show",
                command= lambda:toggle_password(
                    btn=self.toggle_btn,
                    ent=self.pass_inpt,
                    state=self._show_state
                )
            )
            self.toggle_btn.grid(row=0,column=2,sticky="we")
            
            self.conf_toggle_btn= Button(
                self.root,
                width=8,
                text="Show",
                command= lambda: toggle_password(
                    btn=self.conf_toggle_btn,
                    ent=self.conf_pass_inpt,
                    state= self._conf_show_state
                )
            )
            self.conf_toggle_btn.grid(row=1,column=2,sticky="we")

            self.add_btn = Button(self.root,text="Set", command=self.on_set)
            self.add_btn.grid(row=2,column=1,columnspan=2,sticky="we")

            self.pass_inpt.focus()     

        else:
            self.pass_text = Label(text="Master password:")
            self.pass_text.grid(column=0, row=0)
            self.pass_inpt = Entry(width=32,show="*")
            self.pass_inpt.grid(column=1, row=0, sticky="W")

            self.toggle_btn= Button(self.root, width=8,text="Show",command= lambda: toggle_password(btn=self.toggle_btn,ent=self.pass_inpt,state=self._show_state))
            self.toggle_btn.grid(row=0,column=2)

            self.add_btn = Button(self.root,text="Confirm", width=10, command=self.on_verify)
            self.add_btn.grid(row=0,column=3)
            self.pass_inpt.focus()

    def on_set(self)->None:
        mpswd=self.pass_inpt.get()

        ## --> refactor here

        if mpswd !=self.conf_pass_inpt.get():
            custom_message_info(parent=self.root,title="Error!",message="The passwords do not match. Please verify and try again.")
            return
        elif mpswd == "":
            custom_message_info(parent=self.root,title="Error!",message="You have to set a master password to continue.")
            return
        
        ## --> refactor here

        if master_password_msg(parent=self.root,pwd=mpswd):
            ## --> refactor here
            key="__MASTERPASSWORD"
            self.data[key]={"password":mpswd}
            self.store.save(self.data)
            ## --> refactor here
            custom_message_info(parent=self.root, title="Success!", message="Master password set!")
            self.result=True
            self.root.destroy()
        else:
            return


    def on_verify(self)->None:
        mpswd=self.pass_inpt.get()
        if mpswd == self.data["__MASTERPASSWORD"]["password"]:
            custom_message_info(parent=self.root,title="Success!",message="Welcome Back!")
            self.result=True
            self.root.destroy()
        else:
            custom_message_info(parent=self.root, title="Error!",message="Provide the correct password to continue.")
            return
    
