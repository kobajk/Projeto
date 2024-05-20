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

# Dados de usuários
usuarios = {
    'proprietario': {'username': 'proprietario', 'password': 'proprietario123', 'privilege': 'proprietario'},
    'administrador': {'username': 'administrador', 'password': 'administrador123', 'privilege': 'administrador'},
    'usuario': {'username': 'usuario', 'password': 'usuario123', 'privilege': 'usuario'}
}

def registrar():
    username = input('Digite um novo nome de usuário: ')
    password = getpass.getpass('Digite uma nova senha: ')

    if username not in usuarios:
        usuarios[username] = {'username': username, 'password': password, 'privilege': 'usuario'}
        logging.info(f'Novo usuário registrado: {username}')
        print('Usuário registrado com sucesso.')
    else:
        print('Nome de usuário já existe.')

def fazer_login():
    username = input('Digite seu nome de usuário: ')
    password = getpass.getpass('Digite sua senha: ')
    usuario = None

    if username in usuarios:
        usuario = usuarios[username]

    if usuario and usuario['password'] == password:
        logging.info(f'Login bem-sucedido para {username}')
        print(f'Bem-vindo(a), {username}!')
        return usuario['privilege']
    else:
        login_tentativas = 0
        while login_tentativas < 3:
            acao = input('Senha incorreta. Deseja recuperar a senha? (S/N): ')
            if acao.lower() == 's':
                if usuario and usuario['privilege'] == 'usuario':
                    print('Para recuperar a senha, contate o administrador.')
                elif usuario and usuario['privilege'] == 'administrador':
                    if usuario['username'] == 'proprietario':
                        print('Você não pode recuperar a senha do proprietário.')
                    else:
                        print(f'Senha do usuário {username} é: {usuarios[username]["password"]}')
                elif usuario and usuario['privilege'] == 'proprietario':
                    print('Você não pode recuperar a senha do proprietário.')
                else:
                    print('Para recuperar a senha, contate o administrador.')
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
    return None

def deletar_usuario(username):
    if username in usuarios:
        del usuarios[username]
        logging.info(f'Usuário deletado: {username}')
        print('Usuário deletado com sucesso.')
    else:
        print('Usuário não encontrado.')

def modificar_usuario(username, privilege):
    if username in usuarios:
        usuarios[username]['privilege'] = privilege
        logging.info(f'Privilégio de usuário modificado: {username}')
        print('Privilégio de usuário modificado com sucesso.')
    else:
        print('Usuário não encontrado.')

def recuperar_senha(usuario_logado, username):
    if username in usuarios and usuarios[username]['privilege'] <= usuario_logado['privilege']:
        logging.info(f'Solicitação de recuperação de senha para {username}')
        print(f'Senha do usuário {username} é: {usuarios[username]["password"]}')

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
                        privilege = input('Digite o novo privilégio (usuário, administrador, ou proprietário): ')
                        if privilege == 'usuário' or privilege == 'administrador' or privilege == 'proprietário':
                            if privilege == 'proprietário' and privilege != usuarios[username]['privilege'] and privilege != 'administrador':
                                print('Você não tem permissão para modificar o privilégio deste usuário.')
                            elif privilege == 'administrador' and privilege != usuarios[username]['privilege']:
                                print('Você não tem permissão para modificar o privilégio deste usuário.')
                            else:
                                modificar_usuario(username, privilege)
                        else:
                            print('Privilégio inválido.')
                    elif acao == 'recuperar':
                        username = input('Digite o nome de usuário do usuário a ter a senha recuperada: ')
                        if privilege == 'proprietario' or privilege == 'administrador':
                            recuperar_senha(usuarios[username], username)
                        else:
                            print('Você não tem permissão para recuperar a senha deste usuário.')
                    elif acao == 'sair':
                        break
                    else:
                        print('Comando inválido.')
            else:
                print('Nome de usuário ou senha inválidos.')
        elif acao == 'sair':
            break
        else:
            print('Comando inválido.')

if __name__ == '__main__':
    main()

