import tkinter as tk
from tkinter import messagebox
import getpass
from cryptography.fernet import Fernet
import logging
import os
import sqlite3
import cryptography
from cryptography.fernet import Fernet

# Configuração do registro
if not os.path.exists('atividades.log'):
    open('atividades.log', 'a').close()
    logging.basicConfig(filename='atividades.log', level=logging.INFO)
else:
    logging.basicConfig(filename='atividades.log', level=logging.INFO)

file_handler = logging.FileHandler('atividades.log')
file_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(file_handler)
logging.getLogger().setLevel(logging.INFO)

# Gerar chave secreta para criptografia
# chave_secreta = Fernet.generate_key()
# print(chave_secreta)
chave_secreta = b'XwL9kxogGgBwJjj9vOZIAuq9-43Wvyz0u4aWhQBINJ4='
fernet = Fernet(chave_secreta)

DB_PATH = r'C:\Users\bruno\Documents\Faculdade\AP2\Projeto\BD_teste.db'

# Inicializar banco de dados
def inicializar_banco_de_dados():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        privilege TEXT NOT NULL
                    )''')

    cursor.execute('''SELECT COUNT(*) FROM usuarios''')
    if cursor.fetchone()[0] == 0:
        usuarios_iniciais = [
            ('proprietario', fernet.encrypt('proprietario123'.encode()).decode(), 'proprietario'),
            ('administrador', fernet.encrypt('administrador123'.encode()).decode(), 'administrador'),
            ('usuario', fernet.encrypt('usuario123'.encode()).decode(), 'usuario')
        ]

        cursor.executemany('''INSERT INTO usuarios (username, password, privilege) VALUES (?,?,?)''', usuarios_iniciais)

    conn.commit()
    conn.close()

# Variavel global para armazenar o status de login
logged_in = False

# Define current_user_privilege in the global scope
current_user_privilege = None

# Função para registrar um novo usuário
def registrar_usuario():
    username = entry_username.get()
    password = entry_password.get()
    password_criptografada = fernet.encrypt(password.encode()).decode()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute('''INSERT INTO usuarios (username, password, privilege) VALUES (?,?,?)''', (username, password_criptografada, 'usuario'))
        conn.commit()
        logging.info(f'Usuário registrado: {username}')
        messagebox.showinfo("Sucesso", "Usuário registrado com sucesso.")
    except sqlite3.IntegrityError:
        conn.rollback()
        messagebox.showerror("Erro", "Nome de usuário já existe.")

    conn.close()

# Função para fazer login
# Função para fazer login
def fazer_login():
    username = entry_username.get()
    password = entry_password.get()
    global current_user_privilege

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute('''SELECT * FROM usuarios WHERE username=?''', (username,))
        usuario = cursor.fetchone()
        conn.commit()

        if usuario:
            decrypted_password = fernet.decrypt(usuario[2].encode()).decode()
            if decrypted_password == password:
                logging.info(f'Login bem-sucedido para {username}')
                messagebox.showinfo("Sucesso", f"Bem-vindo(a), {username}!")
                global logged_in
                logged_in = True
                current_user_privilege = usuario[3]
                update_ui()
                button_list_all_users.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
            else:
                messagebox.showerror("Erro", "Nome de usuário ou senha inválidos.")
        else:
            messagebox.showerror("Erro", "Nome de usuário ou senha inválidos.")
    except sqlite3.IntegrityError:
        conn.rollback()
        messagebox.showerror("Erro", "Nome de usuário ou senha inválidos.")
    except cryptography.fernet.InvalidToken:
        messagebox.showerror("Erro", "Senha inválida.")

    conn.close()
    
# funcao para fazer logout
def fazer_logout():
    global logged_in
    logged_in = False
    update_ui()

# Função para exibir senha criptografada
def exibir_senha_criptografada():
    username = entry_username.get()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''SELECT password, privilege FROM usuarios WHERE username=?''', (username,))
    result = cursor.fetchone()

    if result:
        password_criptografada, privilege = result
        if logged_in and privilege == 'usuario':
            messagebox.showinfo("Senha Criptografada", f"Senha criptografada do usuário {username}: {password_criptografada}")
        elif logged_in and privilege == 'administrador' and current_user_privilege == 'proprietario':
            messagebox.showinfo("Senha Descriptografada", f"Senha descriptografada do usuário {username}: {fernet.decrypt(password_criptografada.encode()).decode()}")
        elif logged_in and privilege == 'usuario' and current_user_privilege == 'administrador':
            messagebox.showinfo("Senha Descriptografada", f"Senha descriptografada do usuário {username}: {fernet.decrypt(password_criptografada.encode()).decode()}")
        elif logged_in and privilege == 'proprietario' and current_user_privilege == 'proprietario':
            messagebox.showinfo("Senha Descriptografada", f"Senha descriptografada do usuário {username}: {fernet.decrypt(password_criptografada.encode()).decode()}")
        else:
            messagebox.showerror("Erro", "Você não tem permissão para visualizar esta senha.")
    else:
        messagebox.showerror("Erro", "Usuário não encontrado.")

    conn.close()

# Função para deletar usuário
def deletar_usuario():
    username = entry_username.get()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute('''DELETE FROM usuarios WHERE username=?''', (username,))
        conn.commit()
        logging.info(f'Usuário deletado: {username}')
        messagebox.showinfo("Sucesso", "Usuário deletado com sucesso.")
    except sqlite3.IntegrityError:
        conn.rollback()
        messagebox.showerror("Erro", "Usuário não encontrado.")

    conn.close()

#funcao para verificar lista de usuarios
def verificar_lista_usuarios():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Listing all users...")
    cursor.execute('''SELECT * FROM usuarios''')
    usuarios = cursor.fetchall()
    if usuarios:
        if logged_in and current_user_privilege == 'usuario':
            messagebox.showinfo("Lista de Usuários", "Usuários e Senhas Criptografadas:\n" + "\n".join([f"{usuario[1]}: {usuario[2]}" for usuario in usuarios]))
        elif logged_in and current_user_privilege == 'administrador':
            messagebox.showinfo("Lista de Usuários", "Usuários e Senhas Descriptografadas:\n" + "\n".join([f"{usuario[1]}: {fernet.decrypt(usuario[2].encode()).decode()}" if usuario[3] == 'usuario' else f"{usuario[1]}: ***Senha escondida***" for usuario in usuarios]))
        elif logged_in and current_user_privilege == 'proprietario':
            messagebox.showinfo("Lista de Usuários", "Usuários e Senhas Descriptografadas:\n" + "\n".join([f"{usuario[1]}: {fernet.decrypt(usuario[2].encode()).decode()}" for usuario in usuarios]))
        else:
            messagebox.showerror("Erro", "Você não tem permissão para visualizar esta lista.")
    else:
        messagebox.showerror("Erro", "Nenhum usuário encontrado.")

    conn.close()

# atualizar interface se o usuario estiver logado
def update_ui():
    if logged_in:
        button_senha_criptografada.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        button_deletar_usuario.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        button_logout.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
    else:
        button_senha_criptografada.grid_forget()
        button_deletar_usuario.grid_forget()
        button_logout.grid_forget()

# Função principal
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
usuario = cursor.fetchone()
inicializar_banco_de_dados()

root = tk.Tk()
root.title("Sistema de Autenticação de Usuários")

# Definir tamanho da janela
root.geometry("400x250")

# Centralizar os campos de entrada e botões
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)

label_username = tk.Label(root, text="Nome de Usuário:")
label_username.grid(row=0, column=0, padx=5, pady=5, sticky="e")

entry_username = tk.Entry(root)
entry_username.grid(row=0, column=1, padx=5, pady=5)

label_password = tk.Label(root, text="Senha:")
label_password.grid(row=1, column=0, padx=5, pady=5, sticky="e")

entry_password = tk.Entry(root, show="*")
entry_password.grid(row=1, column=1, padx=5, pady=5)

button_registrar = tk.Button(root, text="Registrar", command=registrar_usuario)
button_registrar.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

button_login = tk.Button(root, text="Login", command=fazer_login)
button_login.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

button_senha_criptografada = tk.Button(root, text="Exibir Senha Criptografada", command=exibir_senha_criptografada)
if logged_in:
    button_senha_criptografada.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

button_deletar_usuario = tk.Button(root, text="Deletar Usuário", command=deletar_usuario)
if logged_in:
    button_deletar_usuario.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

button_logout = tk.Button(root, text="Logout", command=fazer_logout)
if logged_in:
    button_logout.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

button_list_all_users = tk.Button(root, text="List All Users", command=verificar_lista_usuarios)
if logged_in:
    button_list_all_users.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
 
root.mainloop()