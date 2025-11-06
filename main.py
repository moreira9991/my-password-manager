from __future__ import annotations
from tkinter import Tk
from app.gui import AppGUI,MasterGUI

def main() -> None:
    root = Tk()
    AppGUI(root)
    root.mainloop()

def mastercheck() -> None:
    global mpawd
    root1= Tk()
    tst=MasterGUI(root1)
    root1.mainloop()
    mpawd=tst.result

mastercheck()
if  mpawd== True:
    main()


# Credenciais todas em uma janela - DONE
# Filtrar por site as pass com barra de pesquisa e botao - DONE
# Escrever pass's devem estar escondidas "**" e ter um botao para mostrar - DONE
# Ser possível copiar passes e users de mypasswords - DONE
# Organizar layout janela principal - DONE
# Manage passwords -> abrir janela para poder remover/alterar data - DONE
# Criar mensagens info custom - DONE
# Criar mensagens okcancel custom - DONE
# Ao dar Set na master password, mostrar pass e perguntar ok/cancel antes de avançar - DONE
# Ao abrir app, focar na entry para mal abrir poder escrever - DONE
# Manage master password- DONE
# Ver o porque de existir tantos self.result= True. penso tar a fazer nada - DONE
# Sempre que abrir uma janela nova, impedir de interagir com janela pai enquanto janela inferior estiver aberta - DONE
#   janelas =
#   Mypassword(parent->mypassword manager) - done
#   search (parent -> mypassword) - done
#   manage passwords ( parent -> mypassword) - eu quero que seja possivel interagir parcialmente, para poder copiar usernames e colar
#   tenho que desabilitar os outros botoes quando esta janela esta aberta. - done
#   manage master password( parent -> mypasswrod) - done
# Implementar carregar "enter" ativa os botoes de entrar - DONE
#   Masterpassword verify window - done
#   Mypasswordmanager main window - done
#   ManagePasswords search - done
#   ManagePasswords managepwd - done
# Focous em todos os textos ao abrir janela - DONE
# Tirar a opção de redimensionar e full screen de maior parte das janelas, as que nao fazem sentido pelo menos - DONE
# Dimensionar janela de mypasswords para tamanho fixo e scroll nas passwords - DONE
# Ao editar passwords ou master passwords, aparecer mensagem de erro se nada for alterado - DONE
# When editing passwords, block if the username is allready in user for that plataform. It should not be possible to have 2 acc for the
#   same plataform - DONE
# Add more and stronger requirements for creating a password or master password - DONE
#   When creating master password, type twice - DONE
#   toggle visibility button fix size - DONE
# Show password strength when confirming - DONE
# Nao deixar criar conta para mesmo site e mesmo username - DONE
# Bug FOUND in manage passwords! When pressing search and either there 
#   is no saved data for the search or entrys are empty, the search
#   btn becomes disabled, becouse on the next stage it has to become disabled. - FIXED
# Migrar para SQLite + SQLcipher-
# Logo mais original -

# --- Working 
# Organizar/refactor código - Inicio 1050 linhas
#   Criar uma class para os dialogos - DONE - 150 linhas -> ~900 linhas
# Resolver bug de editar acc
# Correção de .grid()
# 

# Bug found! When editing an account, erasing the password and pressing edit doesnt do nothing. It should show
#   error not leave any field empty. Do that for both password and username check
# Comentar código em ingles
# Arranjar maneira de fazer backup do ficheiro encryptado para email.
#   No canto inferior direito da janela "My Password's", ter um botao que,
#   ao providencionar master password, pede email e envia JSON file com as passwords encriptadas,
#   com instruções de onde o path do ficheiro deve ficar  -
# readme -
# requirements -



