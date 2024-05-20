import tkinter as tk ##
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

# Local do banco de dados
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
    
    fernet = Fernet(b'XwL9kxogGgBwJjj9vOZIAuq9-43Wvyz0u4aWhQBINJ4=')

    usuarios_iniciais = [
        ('proprietario', fernet.encrypt('proprietario123'.encode()).decode(), 'proprietario'),
        ('administrador', fernet.encrypt('administrador123'.encode()).decode(), 'administrador'),
        ('usuario', fernet.encrypt('usuario123'.encode()).decode(), 'usuario')
    ]

    cursor.executemany('''INSERT INTO usuarios (username, password, privilege) VALUES (?,?,?)''', usuarios_iniciais)

    conn.commit()
    conn.close()

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
def fazer_login():
    username = entry_username.get()
    password = entry_password.get()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Select the user from the database
        cursor.execute('''SELECT * FROM usuarios WHERE username=?''', (username,))
        usuario = cursor.fetchone()
        conn.commit()

        print(usuario[2])
    except sqlite3.IntegrityError:
        conn.rollback()
        messagebox.showerror("Erro", "Nome de usuário ou senha inválidos.")
        return
    
    # if usuario:
    try:
        fernet_login = Fernet(b'XwL9kxogGgBwJjj9vOZIAuq9-43Wvyz0u4aWhQBINJ4=')  # Criar uma nova instância de Fernet
        decrypted_password = fernet_login.decrypt(usuario[2].encode()).decode()
        print(decrypted_password)

        if decrypted_password == password:
            logging.info(f'Login bem-sucedido para {username}')
            messagebox.showinfo("Sucesso", f"Bem-vindo(a), {username}!")
        else:
            messagebox.showerror("Erro", "Nome de usuário ou senha inválidos.")
    except cryptography.fernet.InvalidToken:
        messagebox.showerror("Erro", "Senha inválida.")

    conn.close()


# Função para exibir senha criptografada
def exibir_senha_criptografada():
    username = entry_username.get()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute('''SELECT * FROM usuarios WHERE username=?''', (username,))
        usuario = cursor.fetchone()
        conn.commit()

        if usuario:
            fernet_login =Fernet(b'XwL9kxogGgBwJjj9vOZIAuq9-43Wvyz0u4aWhQBINJ4=')  # Criar uma nova instância de Fernet
            decrypted_password = fernet_login.decrypt(usuario[2].encode()).decode()

            messagebox.showinfo("Senha criptografada", decrypted_password)
        else:
            messagebox.showerror("Erro", "Usuário não encontrado.")
    except sqlite3.IntegrityError:
        conn.rollback()
    
    conn.close()

# Criar a janela principal
janela = tk.Tk()

# Configure o tamanho da janela e quais botões minimizar e fechar serão exibidos
janela.geometry('300x150')
janela.resizable(False, False)
# janela.maxsize(width=300, height=150)
# janela.minsize(width=300, height=150)
janela.title("Login")

# Criar as labels, entradas, botões e checkbox

label_username = tk.Label(janela, text="Nome de usuário:")
label_username.place(x=10, y=20)

entry_username = tk.Entry(janela, width=25)
entry_username.place(x=10, y=40)

label_password = tk.Label(janela, text="Senha:")
label_password.place(x=10, y=60)

entry_password = tk.Entry(janela, width=25, show='*')
entry_password.place(x=10, y=80)

button_login = tk.Button(janela, text="Login", command=fazer_login)
button_login.place(x=220, y=40)

button_registrar = tk.Button(janela, text="Registrar", command=registrar_usuario)
button_registrar.place(x=220, y=80)

button_ver_senha = tk.Button(janela, text="Ver senha", command=exibir_senha_criptografada)
button_ver_senha.place(x=140, y=110)

janela.mainloop()