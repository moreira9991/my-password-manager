from tkinter import Tk, Canvas, PhotoImage, Label, Entry, Button, END, messagebox,Toplevel, Frame, StringVar
import pyperclip
from pathlib import Path
from app.service import generate_password, normalize_site
from app.store_json import JsonStore

class AppGUI:
    def __init__(self, root: Tk)-> None:
        self.root = root
        self.root.title("My Password Manager")
        self.root.config(padx=20,pady=20)
        self.root.resizable(False,False)

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
        self.toggle_btn= Button(text="Show",width=6,command=self.toggle_password)
        self.toggle_btn.grid(column=2,row=3,sticky="we")
        self.generate_btn = Button(text="Generate password", command=self.on_generate).grid(column=2,row=2,sticky="we")

        self.add_btn = Button(text="Add", width=50, command=self.on_add)
        self.add_btn.grid(column=1, row=5, columnspan=2, sticky="W")


        self.search_btn = Button(text="My password's", command=self.on_cls)
        self.search_btn.grid(column=2, row=1, sticky="WE")

        self.web_inpt.focus()

    def toggle_password(self):
        self._show_state["visible"] = not self._show_state["visible"]
        if self._show_state["visible"]:
            self.pass_inpt.config(show="")
            self.toggle_btn.config(text="Hide")
        else:
            self.pass_inpt.config(show="*")
            self.toggle_btn.config(text="Show")


        #Callbacks
    def on_generate(self) -> None:
        password = generate_password()
        # Replace any existing text in the password field
        self.pass_inpt.delete(0, END)
        self.pass_inpt.insert(0, password)
        pyperclip.copy(password)

    def on_add(self) -> None:
        site = self.web_inpt.get()
        username = self.user_inpt.get()
        pwd = self.pass_inpt.get()

        key = normalize_site(site)

        if not site.strip() or not username.strip() or not pwd.strip():
            self.custom_message_info(self.root,title="Error!",message="Please don't leave any fields empty.")
            return
        
        # Checking for duplicate username
        checking_username = self.data.get(key)
        for acc in checking_username:
            if username == acc["username"]:
                self.custom_message_info(parent=self.root,title="Error!",message=f"{username} account allready saved for {site.capitalize()}!")
                return

        confirm = self.custom_message_askokcancel(parent=self.root,title=site.capitalize(),message=f"Email/Username: {username}\nPassword: {pwd}\n"
                                                  f"Press 'OK' to save data or press 'Cancel' to edit data.")
        if not confirm:
            return
            
        
        if key not in self.data:
            self.data[site]=[]
            
        self.data[key].append({"username": username, "password": pwd})
        try:
            self.store.save(self.data)
            self.custom_message_info(parent=self.root,title="Success",message=f"{site.capitalize()} account saved.")
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

    def custom_message_info(self, parent, title, message):
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


    def custom_message_askokcancel(self, parent, title, message)-> bool:
        self.result_message=False

        self.win= Toplevel(parent)
        self.win.withdraw()
        self.win.title(title)
        self.win.configure(padx=10,pady=10)

        self.win.resizable(False,False)
        self.win.attributes("-topmost",True)
        self.win.transient(parent)

        parent.update_idletasks()
        x = parent.winfo_rootx()+(parent.winfo_width()//2-150)
        y = parent.winfo_rooty()+(parent.winfo_height()//2-150)
        self.win.geometry(f"+{x}+{y}")

        lbl = Label(self.win, text=message,font=("Arial",12,"bold"),justify="center")
        lbl.pack(expand=True,pady=10)

        btn_frame = Frame(self.win)
        btn_frame.pack(pady=10)

        ok_btn = Button(btn_frame, text="OK",command=self.on_ok,width=10)
        ok_btn.pack(side="left",padx=20)

        cancel_btn = Button(btn_frame, text="Cancel",command=self.on_cancel,width=10)
        cancel_btn.pack(side="right",padx=20)

        self.win.deiconify()
        self.win.grab_set()
        ok_btn.focus_set()
        self.win.wait_window()

        return self.result_message

    def on_ok(self):
        self.result_message= True
        self.win.destroy()
    
    def on_cancel(self):
        self.result_message= False
        self.win.destroy()




class MyPasswords:
    def __init__(self, root1:Tk):
        #Store/data
        self.root1=Toplevel(root1) 
        self.store =JsonStore(Path("Passwords_data.json"))
        self.data = self.store.load()
        self.bg=self.root1.cget("bg")
        #Comporta se como dialogo do parent, para continuar é preciso fechar
        self.root1.transient(root1)
        #apenas deixa interagir com esta pagina
        self.root1.grab_set() 

        self.root1.bind("<Return>", lambda e:self.search_btn.invoke())
        self.root1.bind("<KP_Enter>", lambda e:self.search_btn.invoke())
        
        self.root1.title("My Password's")
        self.root1.config(padx=10,pady=10)
        cnt=1
        Label(self.root1, text="Site", font=("Arial",10,"bold")).grid(column=0, row= 0 ,sticky="w",padx=10,pady=5)
        Label(self.root1, text="Email/Username", font=("Arial",10,"bold")).grid(column=1, row= 0 ,sticky="w",padx=10,pady=5)
        Label(self.root1, text="Password", font=("Arial",10,"bold")).grid(column=2, row= 0 ,sticky="w",padx=10,pady=5)
        
        for sites,accounts in self.data.items():
            if sites == "__MASTERPASSWORD":
                continue
            for acc in accounts:
                username1= acc["username"]
                password1= acc["password"]

                #site
                site_var=StringVar(value=sites)
                site_entry= Entry(self.root1,
                                  textvariable=site_var,
                                  state="readonly",
                                  relief="flat",
                                  readonlybackground=self.bg,
                                  fg="black",
                                  exportselection=1,
                                  width=15)
                site_entry.grid(column=0,row=cnt,sticky="w",padx=10,pady=5)

                #user
                user_var = StringVar(value=username1)
                user_entry= Entry(self.root1,
                                  textvariable=user_var,
                                  state="readonly",
                                  relief="flat",
                                  readonlybackground=self.bg,
                                  fg="black",
                                  exportselection=1,
                                  width=25)
                user_entry.grid(column=1,row=cnt,sticky="w",padx=10,pady=5)

                #password
                pass_var=StringVar(value=password1)
                pass_entry=Entry(self.root1,
                                 textvariable=pass_var,
                                 state="readonly",
                                 relief="flat",
                                 readonlybackground=self.bg,
                                 fg="black",
                                 exportselection=1,
                                 width=20)
                pass_entry.grid(column=2,row=cnt,sticky="w",padx=10,pady=5) 

                cnt+=1
        
        self.wbsite=Entry(self.root1,width=20)
        self.wbsite.grid(column=3,row=0)

        self.search_btn = Button(self.root1,text="Search",command=self.onsearch)
        self.search_btn.grid(column=4,row=0,sticky="we")

        self.manage_pwd_btn = Button(self.root1,text="Manage Passwords",command=self.on_manage)
        self.manage_pwd_btn.grid(column=4,row=1)

        self.manage_master_btn=Button(self.root1,text="Manage\nMaster Password",command=self.on_manage_mpwd)
        self.manage_master_btn.grid(column=4,row=2,rowspan=2,sticky="WNE")

        self.backup_btn=Button(self.root1,text="Backup\npassword's")
        self.backup_btn.grid(column=4,row=4,rowspan=2,sticky="we")

        self.wbsite.focus()

    
    def onsearch(self) -> None:
        site = self.wbsite.get()
        if not site.strip():
            self.custom_message_info(parent=self.root1,title="Error!", message="Please type a website to search.")
            return
        key = normalize_site(site)
        entry = self.data.get(key)
        if entry:
            root2=Toplevel(self.root1)
            root2.title(key.capitalize())
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
            root2.mainloop()
        else:
            self.custom_message_info(parent=self.root1, title="Error!", message=f"No data saved for {site.capitalize()}")

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

        self.root3.bind("<Return>", lambda e:manage_search_btn.invoke())
        self.root3.bind("<KP_Enter>", lambda e:manage_search_btn.invoke())

        #disable previous buttons
        self.disable_btns(on_off=True)

        #Comporta se como dialogo do parent, para continuar é preciso fechar
        self.root3.transient(self.root1) 

        Label(self.root3, text="Site", font=("Arial",10,"bold")).grid(column=0, row= 0 ,sticky="w",padx=10,pady=5)
        Label(self.root3, text="Email/Username", font=("Arial",10,"bold")).grid(column=0, row= 1 ,sticky="w",padx=10,pady=5)

        self.site_inpt = Entry(self.root3,width=30)
        self.site_inpt.grid(column=1,row=0)

        self.user_inpt = Entry(self.root3,width=30)
        self.user_inpt.grid(column=1,row=1)

        manage_search_btn=Button(self.root3,text="Search",command=self.on_manage_search)
        manage_search_btn.grid(column=2, row=0,sticky="WE")

        self.root3.bind("<Destroy>", lambda e:self.disable_btns(on_off=False))

        self.site_inpt.focus()

        
    def on_manage_search(self):
        self.site = self.site_inpt.get()
        self.user = self.user_inpt.get()
        key = normalize_site(self.site)
        if (not self.site.strip()) or (not self.user.strip()):
            self.custom_message_info(parent=self.root3, title="Error!", message="Please don't leave any fields empty.")
            return
        self.entry= self.data.get(key)
        if self.entry:
            a=0
            for acc in self.entry:
                if self.user == acc["username"]:
                    password= acc["password"]
                    a=1
            if a==0:
                self.custom_message_info(parent=self.root3, title="Error!", message=f"Username/Email provided is not saved for {key.capitalize()}")
                return
            else:
                Label(self.root3, text="Password", font=("Arial",10,"bold")).grid(column=0, row= 2 ,sticky="w",padx=10,pady=5)
                self.pwd_entry=Entry(self.root3,width=30)
                self.pwd_entry.grid(column=1,row=2)
                self.pwd_entry.insert(0,f"{password}")

                delete_btn=Button(self.root3, text="Delete",command=self.on_delete)
                delete_btn.grid(column=2,row=2,sticky="WE")

                edit_btn=Button(self.root3,text="Edit",command=self.on_edit)
                edit_btn.grid(column=2,row=1,sticky="WE")
        else:
            self.custom_message_info(parent=self.root3,title="Error!",message=f"No data found for {key.capitalize()}")


    def on_edit(self):
        for acc in self.entry:
            if self.user == acc["username"]:
                #Checking if there are no changes
                if (self.user_inpt.get() == acc["username"]) and (self.pwd_entry.get()==acc["password"]):
                    self.custom_message_info(
                        parent=self.root3,
                        title="Error!",
                        message=(f"No changes detected."),
                        )
                    return
                else:
                    confirm = self.custom_message_askokcancel(
                        parent=self.root3,
                        title=f"Editing data for {self.site.capitalize()}",
                        message=(
                            f"Email/Username: {self.user_inpt.get()}\nPassword: {self.pwd_entry.get()}\n"
                            f"Press 'OK' to save data or press 'Cancel' to edit data"
                            )
                    )
                    
                    if not confirm:
                        return  
                    else:
                        acc["username"]= self.user_inpt.get()
                        acc["password"]= self.pwd_entry.get()
                        self.store.save(self.data)

                        self.custom_message_info(parent=self.root3,title="Success!", message=f"You edited {self.user_inpt.get()} account data for {self.site.capitalize()}")
                        self.root3.destroy()
                        self.root1.destroy()
                        break

    def on_delete(self):
        for i,acc in enumerate(self.entry):
            if self.user == acc["username"]:
                confirm=self.custom_message_askokcancel(
                    parent=self.root3,
                    title=f"Deleting data for {self.site.capitalize()}",
                    message=(
                        f"Username/Email: {self.user_inpt.get()}\nPassword: {self.pwd_entry.get()}\n"
                        f"Press 'OK' to delete data or press 'Cancel'."
                        )
                )
                if not confirm:
                    return  
                self.entry.pop(i)
                self.store.save(self.data)
                self.custom_message_info(parent=self.root3, title="Success!", message=f"You have deleted {self.user_inpt.get()} account data for {self.site.capitalize()}")
                self.root3.destroy()
                self.root1.destroy()
                break


    def on_manage_mpwd(self):
        self.root4=Toplevel(self.root1)
        self.root4.title("Provide master password to continue.")
        self.root4.config(padx=10,pady=10)
        self.root4.transient(self.root1) 
        self.root4.grab_set() 

        self.root4.bind("<Return>", lambda e:self.enter_btn.invoke())
        self.root4.bind("<KP_Enter>", lambda e:self.enter_btn.invoke())
        
        
        self._show_state= {"visible":False}
        Label(self.root4, text="Master password: ").grid(column=0, row= 0 ,sticky="w",padx=10,pady=5)
        self.mpwd_inpt=Entry(self.root4,width=25,show="*")
        self.mpwd_inpt.grid(column=1,row=0)

        self.show_info=Button(self.root4,text="Show",command=self.toggle_password)
        self.show_info.grid(row=0,column=2)

        self.enter_btn=Button(self.root4,text="Confirm",command=self.on_verify_mpwd)
        self.enter_btn.grid(row=0,column=3)

        self.mpwd_inpt.focus()
        

    
    def on_verify_mpwd(self)->None:
        mpswd=self.mpwd_inpt.get()
        if mpswd == self.data["__MASTERPASSWORD"]["password"]:
            self.custom_message_info(parent=self.root4,title="Success!",message="Press 'OK' to continue.")
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
            Label(self.root5, text="Master password: ").grid(column=0, row= 0 ,sticky="w",padx=10,pady=5)

            self.mpwd_inpt=Entry(self.root5,width=25,show="*")
            self.mpwd_inpt.grid(column=1,row=0)

            self.show_info=Button(self.root5,text="Show",command=self.toggle_password)
            self.show_info.grid(row=0,column=2)

            self.edit_enter_btn=Button(self.root5,text="Confirm",command=self.on_edit_mpw)
            self.edit_enter_btn.grid(row=0,column=3)

            self.mpwd_inpt.focus()

        else:
            self.custom_message_info(parent=self.root4, title="Error!",message="Provide the correct password to continue.")
            return
        
        
    def on_edit_mpw(self)->None:
        mpswd=self.mpwd_inpt.get()
        key="__MASTERPASSWORD"
        if mpswd == "":
            self.custom_message_info(
                parent=self.root5,title="Error!",
                message="To continue, set a new master password."
                )
        elif len(mpswd)<8:
            self.custom_message_info(
                self.root5,title="Error!",
                message=f"Your password is to small!\nMinimum 8 characters."
                )
        #working here
        elif mpswd == self.data[key]["password"]:
            self.custom_message_info(
                parent=self.root5,
                title="Error!",
                message="No changes detected."
            )
            return
        else:
            confirm=self.custom_message_askokcancel(
                parent=self.root5,
                title="Confirm master password",
                message=(
                    f"Set {mpswd} as master password?\n"
                    f"Press 'OK' to continue or press 'Cancel'."
                    )
            )
            if confirm:
                self.data[key]={"password":mpswd}
                self.store.save(self.data)
                self.custom_message_info(parent=self.root5, title="Success!", message="Master password set!")
                self.root5.destroy()
                self.root1.destroy()
            if not confirm:
                return



    def custom_message_info(self, parent, title, message):
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


    def custom_message_askokcancel(self, parent, title, message)-> bool:
            self.result_message=False

            self.win= Toplevel(parent)
            self.win.withdraw()
            self.win.title(title)
            self.win.configure(padx=10,pady=10)

            self.win.resizable(False,False)
            self.win.attributes("-topmost",True)
            self.win.transient(parent)

            parent.update_idletasks()
            x = parent.winfo_rootx()+(parent.winfo_width()//2-150)
            y = parent.winfo_rooty()+(parent.winfo_height()//2-150)
            self.win.geometry(f"+{x}+{y}")

            lbl = Label(self.win, text=message,font=("Arial",12,"bold"),justify="center")
            lbl.pack(expand=True,pady=10)

            btn_frame = Frame(self.win)
            btn_frame.pack(pady=10)

            ok_btn = Button(btn_frame, text="OK",command=self.on_ok,width=10)
            ok_btn.pack(side="left",padx=20)

            cancel_btn = Button(btn_frame, text="Cancel",command=self.on_cancel,width=10)
            cancel_btn.pack(side="right",padx=20)

            self.win.deiconify()
            self.win.grab_set()
            ok_btn.focus_set()
            self.win.wait_window()

            return self.result_message
    
    def on_ok(self):
        self.result_message= True
        self.win.destroy()
    
    def on_cancel(self):
        self.result_message= False
        self.win.destroy()

    def toggle_password(self):
        self._show_state["visible"] = not self._show_state["visible"]
        if self._show_state["visible"]:
            self.mpwd_inpt.config(show="")
            self.show_info.config(text="Hide")
        else:
            self.mpwd_inpt.config(show="*")
            self.show_info.config(text="Show")  
    


class MasterGUI:
    def __init__(self, root: Tk)-> None:
        self.root = root
        self.root.title("Provide master password to continue")
        self.root.config(padx=20,pady=20)

        self.store =JsonStore(Path("Passwords_data.json"))
        self.data = self.store.load()
        self.result=False
        self._show_state= {"visible":False}

        self.root.bind("<Return>", lambda e:self.add_btn.invoke())
        self.root.bind("<KP_Enter>", lambda e:self.add_btn.invoke())

        
        if not "__MASTERPASSWORD" in self.data:
            self.pass_text = Label(text="Set a master password:")
            self.pass_text.grid(column=0, row=0)
            self.pass_inpt = Entry(width=32,show="*")
            self.pass_inpt.grid(column=1, row=0, sticky="W")

            self.toggle_btn= Button(self.root,text="Show",command=self.toggle_password)
            self.toggle_btn.grid(row=0,column=2)

            self.add_btn = Button(self.root,text="Set", command=self.on_set)
            self.add_btn.grid(row=0,column=3)
            self.pass_inpt.focus()      
        else:
            self.pass_text = Label(text="Master password:")
            self.pass_text.grid(column=0, row=0)
            self.pass_inpt = Entry(width=32,show="*")
            self.pass_inpt.grid(column=1, row=0, sticky="W")

            self.toggle_btn= Button(self.root, text="Show",command=self.toggle_password)
            self.toggle_btn.grid(row=0,column=2)

            self.add_btn = Button(self.root,text="Confirm", width=10, command=self.on_verify)
            self.add_btn.grid(row=0,column=3)
            self.pass_inpt.focus()

        

    def toggle_password(self):
        self._show_state["visible"] = not self._show_state["visible"]
        if self._show_state["visible"]:
            self.pass_inpt.config(show="")
            self.toggle_btn.config(text="Hide")
        else:
            self.pass_inpt.config(show="*")
            self.toggle_btn.config(text="Show")  
        
    def on_set(self)->None:
        mpswd=self.pass_inpt.get()
        if mpswd == "":
            self.custom_message_info(parent=self.root,title="Error!",message="You have to set a master password to continue.")
        elif len(mpswd)<8:
            self.custom_message_info(self.root,title="Error!", message=f"Your password is to small!\nMinimum 8 characters.")
        else:
            confirm=self.custom_message_askokcancel(
                parent=self.root,
                title="Confirm master password",
                message=(
                    f"Set {mpswd} as master password?\n"
                    f"Press 'OK' to continue or press 'Cancel'."
                    )
            )
            if confirm:
                key="__MASTERPASSWORD"
                self.data[key]={"password":mpswd}
                self.store.save(self.data)
                self.custom_message_info(parent=self.root, title="Success!", message="Master password set!")
                self.result=True
                self.root.destroy()
            if not confirm:
                return

    def on_verify(self)->None:
        mpswd=self.pass_inpt.get()
        if mpswd == self.data["__MASTERPASSWORD"]["password"]:
            self.custom_message_info(parent=self.root,title="Success!",message="Welcome Back!")
            self.result=True
            self.root.destroy()
        else:
            self.custom_message_info(parent=self.root, title="Error!",message="Provide the correct password to continue.")
            return
    
    def custom_message_info(self, parent, title, message):
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

    def custom_message_askokcancel(self, parent, title, message)-> bool:
        self.result_message=False

        self.win= Toplevel(parent)
        self.win.withdraw()
        self.win.title(title)
        self.win.configure(padx=10,pady=10)

        self.win.resizable(False,False)
        self.win.attributes("-topmost",True)
        self.win.transient(parent)

        parent.update_idletasks()
        x = parent.winfo_rootx()+(parent.winfo_width()//2-150)
        y = parent.winfo_rooty()+(parent.winfo_height()//2-150)
        self.win.geometry(f"+{x}+{y}")

        lbl = Label(self.win, text=message,font=("Arial",12,"bold"),justify="center")
        lbl.pack(expand=True,pady=10)

        btn_frame = Frame(self.win)
        btn_frame.pack(pady=10)

        ok_btn = Button(btn_frame, text="OK",command=self.on_ok,width=10)
        ok_btn.pack(side="left",padx=20)

        cancel_btn = Button(btn_frame, text="Cancel",command=self.on_cancel,width=10)
        cancel_btn.pack(side="right",padx=20)

        self.win.deiconify()
        self.win.grab_set()
        ok_btn.focus_set()
        self.win.wait_window()

        return self.result_message


    def on_ok(self):
        self.result_message= True
        self.win.destroy()
    
    def on_cancel(self):
        self.result_message= False
        self.win.destroy()

