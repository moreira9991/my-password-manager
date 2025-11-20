from __future__ import annotations
from tkinter import Tk
from app.gui import AppGUI, MasterGUI
from pathlib import Path
from app.service import AccountService
from app.encrypted_store import EncryptedStore

def run_app() -> None:
    store = EncryptedStore(path=Path("vault.pmdb"))
    service = AccountService(store)
    
    # Master password window
    master_root = Tk()
    master_gui = MasterGUI(master_root,service)
    master_root.mainloop()
    if master_gui.result:
        app_root = Tk()
        AppGUI(app_root,service)
        app_root.mainloop()


if __name__ == "__main__":
    run_app()