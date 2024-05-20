import sqlite3
import logging
import getpass
import os

# Configuração do registro
if not os.path.exists('atividades.log'):
    open('atividades.log', 'a').close()
    logging.basicConfig(filename='atividades.log', level=logging.INFO)
else:
    logging.basicConfig(filename='atividades.log', level=logging.INFO)

# Adicionar um FileHandler ao registrador de logs
file_handler = logging.FileHandler('atividades.log')
file_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(file_handler)

# Definir o nível de log como INFO
logging.getLogger().setLevel(logging.INFO)

# Conexão com o banco de dados
conn = sqlite3.connect('BD_teste.bd')
c = conn.cursor()

# Criar tabela de usuários se não existir
c.execute('''CREATE TABLE IF NOT EXISTS usuarios
             (username text PRIMARY KEY, password text, privilege text)''')
conn.commit()

def registrar():
    username = input('Digite um novo nome de usuário: ')
    password = getpass.getpass('Digite uma nova senha: ')

    c.execute("SELECT * FROM usuarios WHERE username=?", (username,))
    if c.fetchone() is None:
        c.execute("INSERT INTO usuarios (username, password, privilege) VALUES (?,?, 'usuario')", (username, password))
        conn.commit()
        logging.info(f'Novo usuário registrado: {username}')
        print('Usuário registrado com sucesso.')
    else:
        print('Nome de usuário já existe.')

    # Add admin, proprietario, and usuario users
    admin_user = 'admin'
    admin_password = 'admin123'
    c.execute("SELECT * FROM usuarios WHERE username=?", (admin_user,))
    if c.fetchone() is None:
        c.execute("INSERT INTO usuarios (username, password, privilege) VALUES (?,?, 'admin')", (admin_user, admin_password))
        conn.commit()
        logging.info(f'Novo usuário registrado: {admin_user}')
        print('Usuário registrado com sucesso.')

    proprietario_user = 'proprietario'
    proprietario_password = 'proprietario123'
    c.execute("SELECT * FROM usuarios WHERE username=?", (proprietario_user,))
    if c.fetchone() is None:
        c.execute("INSERT INTO usuarios (username, password, privilege) VALUES (?,?, 'proprietario')", (proprietario_user, proprietario_password))
        conn.commit()
        logging.info(f'Novo usuário registrado: {proprietario_user}')
        print('Usuário registrado com sucesso.')

    usuario_user = 'usuario'
    usuario_password = 'usuario123'
    c.execute("SELECT * FROM usuarios WHERE username=?", (usuario_user,))
    if c.fetchone() is None:
        c.execute("INSERT INTO usuarios (username, password, privilege) VALUES (?,?, 'usuario')", (usuario_user, usuario_password))
        conn.commit()
        logging.info(f'Novo usuário registrado: {usuario_user}')
        print('Usuário registrado com sucesso.')

def fazer_login():
    username = input('Digite seu nome de usuário: ')
    password = getpass.getpass('Digite sua senha: ')

    c.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (username, password))
    usuario = c.fetchone()

    if usuario:
        logging.info(f'Login bem-sucedido para {username}')
        print(f'Bem-vindo(a), {username}!')
        return usuario[2]  # privilege
    else:
        login_tentativas = 0
        while login_tentativas < 3:
            acao = input('Senha incorreta. Deseja recuperar a senha? (S/N): ')
            if acao.lower() == '':
                # Recuperar senha lógica aqui
                break
            elif acao.lower() == 'n':
                login_tentativas += 1
                if login_tentativas < 3:
                    password = getpass.getpass('Digite sua senha: ')
                else:
                    logging.warning(f'Falha no login para {username}')
                    print('Número máximo de tentativas atingido.')
                    break
            else:
                print('Resposta inválida. Digite "S" ou "N".')

def deletar_usuario(username):
    c.execute("DELETE FROM usuarios WHERE username=?", (username,))
    conn.commit()
    logging.info(f'Usuário deletado: {username}')
    print('Usuário deletado com sucesso.')

def modificar_usuario(username, privilege):
    c.execute("UPDATE usuarios SET privilege=? WHERE username=?", (privilege, username))
    conn.commit()
    logging.info(f'Privilégio de usuário modificado: {username}')
    print('Privilégio de usuário modificado com sucesso.')

def recuperar_senha(usuario_logado, username):
    c.execute("SELECT password FROM usuarios WHERE username=?", (username,))
    senha = c.fetchone()
    if senha:
        logging.info(f'Solicitação de recuperação de senha para {username}')
        print(f'Senha do usuário {username} é: {senha[0]}')

def main():
    while True:
        acao = input('Digite "registrar" para se registrar, "logar" para fazer login, ou "sair" para sair: ')
        if acao == 'registrar':
            registrar()
        elif acao == 'logar':
            privilege = fazer_login()
            if privilege:
                print(f'Você tem {privilege} privilégios.')
                while True:
                    acao = input('Digite "deletar" para deletar um usuário, "modificar" para modificar um usuário, "recuperar" para recuperar uma senha, ou "sair" para sair: ')
                    if acao == 'deletar':
                        username = input('Digite o nome de usuário do usuário a ser deletado: ')
                        if privilege == 'proprietario':
                            deletar_usuario(username)
                        elif privilege == 'administrador':
                            deletar_usuario(username)
                        else:
                            print('Você não tem permissão para deletar usuários.')
                    elif acao == 'modificar':
                        username = input('Digite o nome de usuário do usuário a ser modificado: ')
                        if privilege == 'proprietario':
                            privilege = input('Digite o novo privilégio (proprietario, administrador, ou usuario): ')
                            if privilege in ['proprietario', 'administrador', 'usuario']:
                                modificar_usuario(username, privilege)
                                print('Modificação concluída.')
                            else:
                                print('Opção inválida. Tente novamente.')
                        elif privilege == 'administrador':
                            privilege = input('Digite o novo privilege (administrador, ou usuario): ')
                            if privilege in ['administrador', 'usuario']:
                                modificar_usuario(username, privilege)
                                print('Modificação concluída.')
                            else:
                                print('Opção inválida. Tente novamente.')
                        else:
                            print('Você não tem permissão para modificar usuários.')
                    elif acao == 'recuperar':
                        if privilege == 'proprietario':
                            username = input('Digite o nome de usuário: ')
                            recuperar_senha(privilege, username)
                        elif privilege == 'administrador':
                            username = input('Digite o nome de usuário: ')
                            recuperar_senha(privilege, username)
                        elif privilege == 'usuario':
                            print('Você não tem permissão para recuperar senhas.')
                        else:
                            print('Opção inválida. Tente novamente.')
                    elif acao == 'sair':
                        break
                    else:
                        print('Opção inválida. Tente novamente.')
            else:
                print('Não foi possível fazer login.')
        elif acao == 'sair':
            break
        else:
            print('Opção inválida. Tente novamente.')

if __name__ == '__main__':
    main()