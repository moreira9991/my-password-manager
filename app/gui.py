from tkinter import Tk, Canvas, PhotoImage, Label, Entry, Button, END,Toplevel, Frame, StringVar, Scrollbar
from pathlib import Path
import time
from app.service import generate_password, normalize_site, custom_message_info, toggle_password, AccountService, custom_message_askokcancel, email_message_askokcancel

class AppGUI:
    def __init__(self, root: Tk, service:AccountService, restart_callback)-> None:

        self.restart_callback = restart_callback
        self.last_activity = time.time()
        self.incativity_job= None

        self.root = root
        self.service=service

        ICON_PATH=Path("assets/icon.png")
        icon_img= PhotoImage(file=str(ICON_PATH))
        self.root.iconphoto(True,icon_img)


        self.root.title("My Password Manager")
        self.root.config(padx=20,pady=20)
        self.root.resizable(False,False)
        self._show_state= {"visible":False}

        self.root.bind("<Return>", lambda e:self.add_btn.invoke())
        self.root.bind("<KP_Enter>", lambda e:self.add_btn.invoke())

        self.root.bind("<Escape>",lambda e:self.close_window())

        for event in ("<Motion>","<Key>","<Button>"):
            self.root.bind(event, lambda e: self.reset_timer())

        self.canvas = Canvas (width=1000, height=340,highlightthickness=0)
        logo_path = Path("assets/logo.png")
        self.logo = PhotoImage(file=str(logo_path))
        
        self.canvas.create_image(500, 175, image=self.logo)
        self.canvas.grid(column=0,columnspan=3,row=0,sticky="we")

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

        self.search_btn = Button(text="My passwords", command=self.on_cls)
        self.search_btn.grid(column=2, row=1, sticky="WE")

        #Focus will start on the website entry box
        self.web_inpt.focus()

        self.check_inactivity()

    def close_window(self):
        if custom_message_askokcancel(parent=self.root,title="Closing app...",message="Press 'OK' to quit."):
            self.logout()
            self.root.destroy()
    

    # Generates a lvl4 password
    def on_generate(self) -> None:
        password = generate_password()
        # Replace any existing text in the password field
        self.pass_inpt.delete(0, END)
        self.pass_inpt.insert(0, password)


    #Adds account to JSON -> encripted DB soon
    def on_add(self) -> None:
        if self.service.add(window=self.root,site=self.web_inpt.get(),username=self.user_inpt.get(),password=self.pass_inpt.get()):
            # Reset fields (keep focus on website for next entry)
            self.web_inpt.delete(0, END)
            self.user_inpt.delete(0, END)
            self.pass_inpt.delete(0, END)
            self.web_inpt.focus_set()

 
    def on_cls(self)-> None:
        MyPasswords(self,self.service)


    def reset_timer(self):
        self.last_activity = time.time()


    def check_inactivity(self):
        if time.time() - self.last_activity > 60:
            self.logout()
            return
        self.incativity_job=self.root.after(1000,self.check_inactivity)


    def logout(self):
        self.service.clear_sensitive_data()

        try:
            self.root.destroy()
        except:
            pass
        self.restart_callback()


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

        self.inner_frame = Frame(self.canvas)
        self.window_id = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # bindings de layout e scroll
        self.inner_frame.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self._smooth_scroll(self.canvas)

        self.rows = []

    def _on_inner_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.window_id, width=self.canvas.winfo_width())


    def _smooth_scroll(self, canvas: Canvas, step=0.008):
        def clamp(x, lo=0.0, hi=1.0):
            return max(lo, min(hi, x))

        def move(sign: int):
            try:
                if not canvas.winfo_exists():
                    return
                first, _ = canvas.yview()
                canvas.yview_moveto(clamp(first + sign * step))
            except Exception:
                return

        if getattr(canvas, "_smooth_scroll_bound", False):
            return

        system = str(canvas.tk.call("tk", "windowingsystem"))

        if system == "x11":
            def on_linux_scroll(event):
                # we ignore diagional scrolls
                if event.state & 0x0001:  # bit de Shift
                    return

                if event.num == 4:       # wheel up
                    move(-1)
                elif event.num == 5:     # wheel down
                    move(+1)

            canvas.bind_all("<Button-4>", on_linux_scroll, add="+")
            canvas.bind_all("<Button-5>", on_linux_scroll, add="+")
        else:
            # Windows / macOS 
            canvas.bind_all(
                "<MouseWheel>",
                lambda e: move(-1 if e.delta > 0 else +1),
                add="+",
            )

        def _cleanup(_evt=None):
            try:
                canvas.unbind_all("<Button-4>")
                canvas.unbind_all("<Button-5>")
                canvas.unbind_all("<MouseWheel>")
            except Exception:
                pass
            finally:
                try:
                    canvas._smooth_scroll_bound = False
                except Exception:
                    pass

        canvas.bind("<Destroy>", _cleanup, add="+")
        canvas._smooth_scroll_bound = True


    def render(self, data: dict):
        state ={"visible":False}
        for r in self.rows:
            for w in r["widgets"]:
                w.destroy()
        self.rows.clear()

        cnt = 0
        bg_default = self.parent.cget("bg")

        for site, accounts in data.items():
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
                                 relief="flat", readonlybackground=bg, fg="black", width=20,show="*")

                pass_ent.bind("<Double-Button-1>",lambda w, ent=pass_ent, st=state: toggle_password(None,ent,st))

                site_ent.grid(column=0, row=cnt, sticky="w", padx=10, pady=5)
                user_ent.grid(column=1, row=cnt, sticky="w", padx=10, pady=5)
                pass_ent.grid(column=2, row=cnt, sticky="w", padx=10, pady=5)

                self.rows.append({
                    "widgets": (site_ent, user_ent, pass_ent),
                    "data": (site, username, password)
                })
                cnt += 1

class MyPasswords:
    def __init__(self, appgui, service :AccountService):
        self.appgui=appgui
        self.root1=Toplevel(appgui.root)

        for event in ("<Motion>","<Key>","<Button>"):
            self.root1.bind(event, lambda e: self.appgui.reset_timer())

        self.root1.transient(appgui.root)
        self.root1.grab_set() 
        self.root1.title("My Passwords")
        self.root1.config(padx=10,pady=10)
        self.root1.geometry("1580x1000")
        self.root1.resizable(False,False)

        self.service=service
        
        self.bg=self.root1.cget("bg")
  
        self.root1.grid_rowconfigure(0,weight=0)
        self.root1.grid_rowconfigure(1,weight=1)
        self.root1.grid_columnconfigure(0,weight=1)
        self.root1.grid_columnconfigure(1,weight=1)
        self.root1.grid_columnconfigure(2,weight=1)

        self.root1.bind("<Return>", lambda e:self.search_btn.invoke())
        self.root1.bind("<KP_Enter>", lambda e:self.search_btn.invoke())

        self.root1.bind("<Escape>",lambda e:self.root1.destroy())
        
        right_container = Frame(self.root1)
        right_container.grid(row=1,column=3,sticky="NSWE")

        Label(self.root1, text="Site", font=("Arial", 10, "bold")).grid(column=0, row=0, sticky="w", padx=10, pady=5)
        Label(self.root1, text="Email/Username", font=("Arial", 10, "bold")).grid(column=1, row=0, sticky="w", padx=10, pady=5)
        Label(self.root1, text="Password", font=("Arial", 10, "bold")).grid(column=2, row=0, sticky="w", padx=10, pady=5)

        left_container = Frame(self.root1)
        left_container.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=0, pady=0)

        self.password_list = PasswordListView(left_container)
        self.password_list.render(self.service.data)
        
        self.wbsite=Entry(self.root1,width=20)
        self.wbsite.grid(column=3,row=0)

        self.search_btn = Button(right_container,text="Search",command=self.onsearch)
        self.search_btn.pack(fill="x")

        self.manage_pwd_btn = Button(right_container,text="Manage Passwords",command=self.on_manage)
        self.manage_pwd_btn.pack(fill="x")

        self.manage_master_btn=Button(right_container,text="Manage\nMaster Password",command=lambda:self.on_manage_mpwd(backup=False))
        self.manage_master_btn.pack(fill="x")

        self.backup_btn=Button(right_container,text="Backup\nPasswords", command=lambda:self.on_manage_mpwd(backup=True))
        self.backup_btn.pack(fill="x",anchor="s",side="bottom")

        self.wbsite.focus()

    
    def onsearch(self) -> None:
        site = self.wbsite.get()
        if not site.strip():
            custom_message_info(parent=self.root1,title="Error!", message="Please type a website to search.")
            return
        #check if exists
        entry = self.service.data.get(normalize_site(site))

        if entry:
            root2=Toplevel(self.root1)
            for event in ("<Motion>","<Key>","<Button>"):
                root2.bind(event, lambda e: self.appgui.reset_timer())
            root2.title(site.capitalize())
            Label(root2, text="Email/Username", font=("Arial",10,"bold")).grid(column=0, row= 0 ,sticky="w",padx=10,pady=5)
            Label(root2, text="Password", font=("Arial",10,"bold")).grid(column=1, row= 0 ,sticky="w",padx=10,pady=5)
            root2.bind("<Escape>",lambda e:root2.destroy())

            root2.transient(self.root1) 
            root2.grab_set()
            state={"visible":False}

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
                                 width=25,show="*")
                pass_entry.grid(column=1,row=cnt,sticky="w",padx=10,pady=5)

                pass_entry.bind("<Double-Button-1>",lambda w, ent=pass_entry, st=state: toggle_password(None,ent,st))

                cnt+=1
        else:
            custom_message_info(parent=self.root1, title="Error!", message=f"No data saved for {site.capitalize()}")


    # to enable btns on_off= False
    # to disable btns on_off=True
    def disable_btns(self,on_off:bool):
        if on_off:
            self.manage_pwd_btn.config(state="disabled")
            self.manage_master_btn.config(state="disabled")
            self.search_btn.config(state="disabled")
            self.backup_btn.config(state="disabled")
            self.wbsite.config(state="disabled")
        else:
            self.manage_pwd_btn.config(state="normal")
            self.manage_master_btn.config(state="normal")
            self.search_btn.config(state="normal")
            self.backup_btn.config(state="normal")
            self.wbsite.config(state="normal")


    def on_manage(self):
        self.root3=Toplevel(self.root1)
        for event in ("<Motion>","<Key>","<Button>"):
            self.root3.bind(event, lambda e: self.appgui.reset_timer())
        self.root3.title("Manage Passwords")
        self.root3.config(padx=10,pady=10)
        self.root3.resizable(False,False)

        self.root3.bind("<Return>", lambda e:self.manage_search_btn.invoke())
        self.root3.bind("<KP_Enter>", lambda e:self.manage_search_btn.invoke())

        self.root3.bind("<Escape>",lambda e:self.root3.destroy())


        #disable previous buttons
        # Here we disable buttons to prevent doing anything on the previous page, other than being
        # possible to coppy info from the accounts
        self.disable_btns(on_off=True)

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
        state={"visible":False}
        if (not self.site.strip()) or (not self.user.strip()):
            custom_message_info(parent=self.root3, title="Error!", message="Please don't leave any fields empty.")
            return

        #checks if there is data saved for site
        if self.service.data.get(key):
            data = self.service.find(site=self.site,username=self.user)
            if data:
                password= data["password"]
            else:
                custom_message_info(parent=self.root3, title="Error!", message=f"Username/Email provided is not saved for {key.capitalize()}")
                return

            self.manage_search_btn.config(state="disabled")
            Label(self.root3, text="Password", font=("Arial",10,"bold")).grid(column=0, row= 2 ,sticky="w",padx=10,pady=5)
            self.pwd_entry=Entry(self.root3,width=30,show="*")
            self.pwd_entry.grid(column=1,row=2)
            self.pwd_entry.insert(0,f"{password}")

            delete_btn=Button(self.root3, text="Delete",command=lambda:self.on_delete(site=self.site,username=self.user))
            delete_btn.grid(column=2,row=2,sticky="WE")

            edit_btn=Button(self.root3,text="Edit",command=lambda:self.on_edit())
            edit_btn.grid(column=2,row=1,sticky="WE")

            self.pwd_entry.bind("<Double-Button-1>",lambda w, ent=self.pwd_entry, st=state: toggle_password(None,ent,st))
        else:
            custom_message_info(parent=self.root3,title="Error!",message=f"No data found for {key.capitalize()}")


    def on_edit(self):
        if self.service.edit(
                          window=self.root3,
                          site=self.site,
                          username=self.user,
                          new_username=self.user_inpt.get(),
                          new_password=self.pwd_entry.get()
                          ):
            self.password_list.render(self.service.data)

    # Deletes account data
    def on_delete(self,site,username): 
        if self.service.delete(
            window=self.root3,
            site=site,
            username=username,
            pwd=self.pwd_entry.get()):
            self.password_list.render(self.service.data)


    def on_manage_mpwd(self,backup):
        self.root4=Toplevel(self.root1)
        for event in ("<Motion>","<Key>","<Button>"):
            self.root4.bind(event, lambda e: self.appgui.reset_timer())
        self.root4.title("Provide master password to continue.")
        self.root4.config(padx=10,pady=10)
        self.root4.resizable(False,False)
        self.root4.transient(self.root1) 
        self.root4.grab_set() 

        self.root4.bind("<Return>", lambda e:self.enter_btn.invoke())
        self.root4.bind("<KP_Enter>", lambda e:self.enter_btn.invoke())

        self.root4.bind("<Escape>",lambda e:self.root4.destroy())

        self._show_state= {"visible":False}

        Label(self.root4, text="Master password: ").grid(column=0, row= 0 ,sticky="w",padx=10,pady=5)

        self.mpwd_inpt=Entry(self.root4,width=25,show="*")
        self.mpwd_inpt.grid(column=1,row=0)

        self.show_info=Button(self.root4,width=8,text="Show",command=lambda:toggle_password(btn=self.show_info,ent=self.mpwd_inpt,state=self._show_state))
        self.show_info.grid(row=0,column=2)
        
        if backup:
            self.enter_btn=Button(self.root4,text="Confirm",command=self.on_backup)
        else:
            self.enter_btn=Button(self.root4,text="Confirm",command=self.on_verify_mpwd)

        self.enter_btn.grid(row=0,column=3)

        self.mpwd_inpt.focus()


    def on_backup(self):
        if not self.service.confirm_current_master(window=self.root4,master_pwd=self.mpwd_inpt.get()):
            return
        self.root4.destroy()
        backup_email=email_message_askokcancel(parent=self.root1)
        if backup_email != None and backup_email.strip():
            if not custom_message_askokcancel(parent=self.root1,title="Confirmation",message=f"Please confirm your email:\n{backup_email}"):
                return
        try:
            self.service.backup_file(backup_email=backup_email)
            custom_message_info(parent=self.root1,title="Success!",message="Backup created and sent successefully")
        except Exception as e:
            custom_message_info(parent=self.root1,title="Error!",message=f"Backup Failed:\n{e}\n\nPlease check the configuration guide in docs/backup.md")
        

    def on_verify_mpwd(self)->None:
        if self.service.confirm_current_master(window=self.root4,master_pwd=self.mpwd_inpt.get()):
            custom_message_info(parent=self.root4,title="Success!",message="Press 'OK' to continue.")
            self.root4.destroy()

            #open window to set a new master password
            self.root5=Toplevel(self.root1)

            for event in ("<Motion>","<Key>","<Button>"):
                self.root5.bind(event, lambda e: self.appgui.reset_timer())

            self.root5.title("Set new master password.")
            self.root5.config(padx=10,pady=10)
            self.root5.transient(self.root1) 
            self.root5.grab_set()

            self.root5.bind("<Return>", lambda e:self.edit_enter_btn.invoke())
            self.root5.bind("<KP_Enter>", lambda e:self.edit_enter_btn.invoke())
            self.root5.bind("<Escape>",lambda e:self.root5.destroy())

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
        

    def on_edit_mpw(self)->None:
        if self.service.master_pwd_set(
            main_window=self.root1,
            window=self.root5,
            master_pwd=self._mpwd_inpt.get(),
            confirm_m_pwd=self.confirm_mpwd_inpt.get()
            ):
            self.root5.destroy()
            self.root1.destroy()
        else:
            return

class MasterGUI:
    def __init__(self, root: Tk, service:AccountService)-> None:
        self.root = root
        self.service = service
        self.root.title("Provide master password to continue")
        self.root.config(padx=20,pady=20)
        self.root.resizable(False,False)

        ICON_PATH=Path("assets/icon.png")
        icon_img= PhotoImage(file=str(ICON_PATH))
        self.root.iconphoto(True,icon_img)

        self.result = False

        self._show_state = {"visible":False}
        self._conf_show_state = {"visible":False}

        self.root.bind("<Return>", lambda e:self.add_btn.invoke())
        self.root.bind("<KP_Enter>", lambda e:self.add_btn.invoke())

        if self.service.is_first_run():
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
        #Initialize vault. If successful ,closes window and continue
        if self.service.initialize_vault(window=self.root,master_pwd=self.pass_inpt.get(),confirm_pwd=self.conf_pass_inpt.get()):
            self.result=True
            self.root.destroy()


    def on_verify(self)->None:
        if self.service.verify_master(window=self.root,master_pwd=self.pass_inpt.get()):
            self.result=True
            self.root.destroy()
