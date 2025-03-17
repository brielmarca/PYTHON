import http.server
import socketserver
import logging
import os
import time
import sys
import json
import cgi
from urllib.parse import parse_qs
import random

PORT = 8000
DIRECTORY = "."

print("=== Iniciando Servidor Web ===")
print(f"Para acessar, abra seu navegador e digite: http://localhost:{PORT}")
print("Pressione Ctrl+C para parar o servidor")

def generate_card():
    # Gerar número do cartão (16 dígitos)
    card_number = ''.join([str(random.randint(0, 9)) for _ in range(16)])
    # Gerar CVV (3 dígitos)
    cvv = ''.join([str(random.randint(0, 9)) for _ in range(3)])
    # Gerar data de expiração (MM/YY)
    month = str(random.randint(1, 12)).zfill(2)
    year = str(random.randint(23, 28))
    expiry = f"{month}/{year}"
    
    return card_number, expiry, cvv

def generate_confirmation_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.users_file = "users.json"
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        logging.info("%s - - [%s] %s\n" %
                     (self.client_address[0],
                      self.log_date_time_string(),
                      format % args))

    def send_error(self, code, message=None, explain=None):
        self.send_response(code)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        error_page = f'''
        <html>
            <head>
                <meta charset="UTF-8">
                <title>Erro {code}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; background: #f0f2f5; text-align: center; padding: 40px; }}
                    .error-container {{ background: white; max-width: 400px; margin: 0 auto; padding: 20px; 
                                     border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .error-code {{ color: #dc3545; font-size: 24px; }}
                    .back-link {{ display: inline-block; margin-top: 20px; color: #4CAF50; 
                                text-decoration: none; padding: 10px 20px; border: 1px solid #4CAF50; 
                                border-radius: 4px; }}
                </style>
            </head>
            <body>
                <div class="error-container">
                    <h2 class="error-code">Erro {code}</h2>
                    <p>{message if message else 'Ocorreu um erro'}</p>
                    <p>{explain if explain else ''}</p>
                    <a href="/" class="back-link">Voltar para página inicial</a>
                </div>
            </body>
        </html>
        '''
        self.wfile.write(error_page.encode('utf-8'))

    def send_response_page(self, content, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def do_POST(self):
        if self.path == '/login':  # Changed from '/auth' to '/login'
            self.handle_login()
        elif self.path == '/register':
            self.handle_register()
        elif self.path == '/deposit':
            self.handle_deposit()
        elif self.path == '/withdraw':
            self.handle_withdraw()
        elif self.path == '/transfer':
            self.handle_transfer()
        elif self.path == '/logout':
            self.handle_logout()
        elif self.path == '/cancel_transfer':
            self.handle_cancel_transfer()
        else:
            self.send_error(404)

    def load_users(self):
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"users": {}}

    def save_users(self, users_data):
        with open(self.users_file, 'w') as f:
            json.dump(users_data, f, indent=4)

    def handle_login(self):
        length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(length).decode('utf-8')
        data = parse_qs(post_data)
        
        username = data.get('username', [''])[0]
        password = data.get('password', [''])[0]
        
        users_data = self.load_users()
        
        if username in users_data['users'] and users_data['users'][username]['password'] == password:
            self.show_bank_page(username, users_data)
        else:
            self.send_error(401, "Credenciais inválidas")

    def handle_register(self):
        length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(length).decode('utf-8')
        data = parse_qs(post_data)
        
        username = data.get('username', [''])[0]
        password = data.get('password', [''])[0]
        
        users_data = self.load_users()
        
        if username in users_data['users']:
            self.send_response(409)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write("Username já existe!".encode('utf-8'))
        else:
            # Gerar cartão automático
            card_number, expiry, cvv = generate_card()
            users_data['users'][username] = {
                'password': password,
                'card_info': {
                    'number': card_number,
                    'expiry': expiry,
                    'cvv': cvv
                },
                'balance': 1000.0  # Saldo inicial
            }
            self.save_users(users_data)
            
            # Mostrar informações do cartão gerado
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            card_info = f'''
            <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Conta Criada</title>
                    <meta http-equiv="refresh" content="10;url=/" />
                    <style>
                        body {{ font-family: Arial, sans-serif; background: #f0f2f5; text-align: center; padding: 40px; }}
                        .card-info {{ background: white; max-width: 400px; margin: 0 auto; padding: 20px; border-radius: 8px; }}
                        .success {{ color: #4CAF50; }}
                    </style>
                </head>
                <body>
                    <div class="card-info">
                        <h2 class="success">Conta criada com sucesso!</h2>
                        <h3>Seu Cartão Virtual:</h3>
                        <p>Número: {card_number}</p>
                        <p>Validade: {expiry}</p>
                        <p>CVV: {cvv}</p>
                        <p>Saldo Inicial: R$ 1.000,00</p>
                        <p>Redirecionando para página inicial em 10 segundos...</p>
                    </div>
                </body>
            </html>
            '''
            self.wfile.write(card_info.encode())

    def handle_card_update(self):
        length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(length).decode('utf-8')
        data = parse_qs(post_data)
        
        username = data.get('username', [''])[0]
        card_number = data.get('card_number', [''])[0]
        card_expiry = data.get('card_expiry', [''])[0]
        card_cvv = data.get('card_cvv', [''])[0]
        
        users_data = self.load_users()
        
        if username in users_data['users']:
            users_data['users'][username]['card_info'] = {
                'number': card_number,
                'expiry': card_expiry,
                'cvv': card_cvv
            }
            self.save_users(users_data)
            
            # Redirecionar para o menu após salvar o cartão
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            menu_page = f'''
            <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Menu</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 20px auto; padding: 20px; }}
                        .menu-container {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
                        .welcome {{ color: #4CAF50; }}
                    </style>
                </head>
                <body>
                    <div class="menu-container">
                        <h2 class="welcome">Welcome, {username}!</h2>
                        <h3>Your Menu Options:</h3>
                        <ul>
                            <li>Option 1</li>
                            <li>Option 2</li>
                            <li>Option 3</li>
                        </ul>
                    </div>
                </body>
            </html>
            '''
            self.wfile.write(menu_page.encode())

    def show_bank_page(self, username, users_data):
        balance = users_data['users'][username].get('balance', 0)
        card_info = users_data['users'][username]['card_info']
        bank_page = f'''
        <html>
            <head>
                <meta charset="UTF-8">
                <title>Banco Virtual - Conta</title>
                <style>
                    body {{ font-family: Arial, sans-serif; background: #f0f2f5; margin: 0; padding: 20px; }}
                    .container {{ max-width: 800px; margin: 0 auto; }}
                    .card {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .balance {{ font-size: 24px; color: #4CAF50; margin: 20px 0; }}
                    .card-info {{ background: #f8f9fa; padding: 15px; border-radius: 4px; margin: 10px 0; }}
                    .operations {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }}
                    .btn {{ background: #4CAF50; color: white; padding: 10px 15px; border: none;
                           border-radius: 4px; cursor: pointer; width: 100%; }}
                    .btn:hover {{ background: #45a049; }}
                    input[type=number] {{ width: 100%; padding: 8px; margin: 8px 0; border: 1px solid #ddd;
                                        border-radius: 4px; }}
                    .error {{ color: #dc3545; }}
                    .success {{ color: #28a745; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="card">
                        <h2>Bem-vindo, {username}</h2>
                        <div class="balance">Saldo: R$ {balance:.2f}</div>
                        <div class="card-info">
                            <h3>Seu Cartão Virtual</h3>
                            <p>Número: {card_info['number']}</p>
                            <p>Validade: {card_info['expiry']}</p>
                            <p>CVV: {card_info['cvv']}</p>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>Operações</h3>
                        <div class="operations">
                            <form action="/deposit" method="post">
                                <input type="hidden" name="username" value="{username}">
                                <input type="number" name="amount" placeholder="Valor" step="0.01" required>
                                <button class="btn" type="submit">Depositar</button>
                            </form>
                            
                            <form action="/withdraw" method="post">
                                <input type="hidden" name="username" value="{username}">
                                <input type="number" name="amount" placeholder="Valor" step="0.01" required>
                                <button class="btn" type="submit">Sacar</button>
                            </form>
                            
                            <form action="/transfer" method="post">
                                <input type="hidden" name="username" value="{username}">
                                <input type="text" name="recipient" placeholder="Destinatário" required>
                                <input type="number" name="amount" placeholder="Valor" step="0.01" required>
                                <button class="btn" type="submit">Transferir</button>
                            </form>
                            
                            <form action="/logout" method="post">
                                <input type="hidden" name="username" value="{username}">
                                <button class="btn" type="submit" style="background: #dc3545;">Sair</button>
                            </form>
                        </div>
                    </div>
                </div>
            </body>
        </html>
        '''
        self.send_response_page(bank_page)

    def handle_deposit(self):
        length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(length).decode('utf-8')
        data = parse_qs(post_data)
        
        username = data.get('username', [''])[0]
        try:
            amount = float(data.get('amount', ['0'])[0])
        except ValueError:
            self.send_error(400, "Valor inválido")
            return

        users_data = self.load_users()
        if username in users_data['users']:
            users_data['users'][username]['balance'] = users_data['users'][username].get('balance', 0) + amount
            self.save_users(users_data)
            self.show_bank_page(username, users_data)

    def handle_withdraw(self):
        length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(length).decode('utf-8')
        data = parse_qs(post_data)
        
        username = data.get('username', [''])[0]
        try:
            amount = float(data.get('amount', ['0'])[0])
        except ValueError:
            self.send_error(400, "Valor inválido")
            return

        users_data = self.load_users()
        if username in users_data['users']:
            current_balance = users_data['users'][username].get('balance', 0)
            if current_balance >= amount:
                users_data['users'][username]['balance'] = current_balance - amount
                self.save_users(users_data)
                self.show_bank_page(username, users_data)
            else:
                self.send_error(400, "Saldo insuficiente")

    def handle_transfer(self):
        length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(length).decode('utf-8')
        data = parse_qs(post_data)
        
        username = data.get('username', [''])[0]
        recipient = data.get('recipient', [''])[0]
        confirmation = data.get('confirmation', [''])[0]
        code = data.get('code', [''])[0]
        
        users_data = self.load_users()
        
        if not confirmation:
            # Primeira etapa: Verificação do destinatário
            if recipient not in users_data['users']:
                self.send_error(400, "Destinatário não encontrado", 
                              "Verifique se o nome de usuário está correto")
                return
                
            try:
                amount = float(data.get('amount', ['0'])[0])
            except ValueError:
                self.send_error(400, "Valor inválido")
                return

            if amount <= 0:
                self.send_error(400, "Valor inválido", 
                              "O valor deve ser maior que zero")
                return

            # Gerar código de confirmação
            confirmation_code = generate_confirmation_code()
            users_data['users'][username]['pending_transfer'] = {
                'recipient': recipient,
                'amount': amount,
                'code': confirmation_code,
                'timestamp': time.time()
            }
            self.save_users(users_data)
            
            # Mostrar página de confirmação
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            confirm_page = f'''
            <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Confirmar Transferência</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; background: #f0f2f5; }}
                        .container {{ max-width: 500px; margin: 50px auto; padding: 20px;
                                    background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                        .details {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 4px; }}
                        .code {{ font-size: 24px; color: #4CAF50; font-weight: bold; margin: 20px 0; }}
                        .btn {{ background: #4CAF50; color: white; padding: 10px 20px; border: none;
                               border-radius: 4px; cursor: pointer; width: 100%; }}
                        .cancel {{ background: #dc3545; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2>Confirmar Transferência</h2>
                        <div class="details">
                            <p><strong>Destinatário:</strong> {recipient}</p>
                            <p><strong>Valor:</strong> R$ {amount:.2f}</p>
                        </div>
                        <p>Código de confirmação:</p>
                        <div class="code">{confirmation_code}</div>
                        <form action="/transfer" method="post">
                            <input type="hidden" name="username" value="{username}">
                            <input type="hidden" name="recipient" value="{recipient}">
                            <input type="hidden" name="amount" value="{amount}">
                            <input type="hidden" name="confirmation" value="true">
                            <input type="text" name="code" placeholder="Digite o código de confirmação" required>
                            <button type="submit" class="btn">Confirmar Transferência</button>
                        </form>
                        <br>
                        <form action="/cancel_transfer" method="post">
                            <input type="hidden" name="username" value="{username}">
                            <button type="submit" class="btn cancel">Cancelar</button>
                        </form>
                    </div>
                </body>
            </html>
            '''
            self.wfile.write(confirm_page.encode('utf-8'))
            return
            
        # Segunda etapa: Confirmação e execução da transferência
        if username in users_data['users']:
            pending = users_data['users'][username].get('pending_transfer')
            if not pending:
                self.send_error(400, "Nenhuma transferência pendente")
                return
                
            # Verificar se o código expirou (15 minutos)
            if time.time() - pending['timestamp'] > 900:
                del users_data['users'][username]['pending_transfer']
                self.save_users(users_data)
                self.send_error(400, "Código expirado", 
                              "Por favor, inicie uma nova transferência")
                return
                
            if code != pending['code']:
                self.send_error(400, "Código inválido", 
                              "Verifique o código e tente novamente")
                return
                
            # Executar a transferência
            amount = pending['amount']
            recipient = pending['recipient']
            
            if users_data['users'][username].get('balance', 0) >= amount:
                users_data['users'][username]['balance'] -= amount
                users_data['users'][recipient]['balance'] = \
                    users_data['users'][recipient].get('balance', 0) + amount
                    
                # Limpar transferência pendente
                del users_data['users'][username]['pending_transfer']
                self.save_users(users_data)
                
                # Mostrar sucesso
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                success_page = f'''
                <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>Transferência Realizada</title>
                        <meta http-equiv="refresh" content="3;url=/bank" />
                        <style>
                            body {{ font-family: Arial, sans-serif; background: #f0f2f5; text-align: center; padding: 40px; }}
                            .success-container {{ background: white; max-width: 400px; margin: 0 auto; padding: 20px;
                                               border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                            .success {{ color: #4CAF50; }}
                        </style>
                    </head>
                    <body>
                        <div class="success-container">
                            <h2 class="success">Transferência realizada com sucesso!</h2>
                            <p>Valor: R$ {amount:.2f}</p>
                            <p>Para: {recipient}</p>
                            <p>Redirecionando para sua conta...</p>
                        </div>
                    </body>
                </html>
                '''
                self.wfile.write(success_page.encode('utf-8'))
            else:
                self.send_error(400, "Saldo insuficiente")
        else:
            self.send_error(400, "Usuário não encontrado")

    def handle_logout(self):
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def handle_cancel_transfer(self):
        length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(length).decode('utf-8')
        data = parse_qs(post_data)
        
        username = data.get('username', [''])[0]
        users_data = self.load_users()
        
        if username in users_data['users']:
            if 'pending_transfer' in users_data['users'][username]:
                del users_data['users'][username]['pending_transfer']
                self.save_users(users_data)
            
            self.show_bank_page(username, users_data)

    def do_GET(self):
        if self.path == '/':
            html_content = '''
            <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Banco Virtual</title>
                    <style>
                        body { font-family: Arial, sans-serif; background: #f0f2f5; }
                        .container { max-width: 600px; margin: 100px auto; text-align: center; }
                        .btn { display: inline-block; padding: 15px 30px; margin: 10px;
                              background: #4CAF50; color: white; text-decoration: none;
                              border-radius: 5px; font-size: 18px; }
                        .btn:hover { background: #45a049; }
                        h1 { color: #333; margin-bottom: 30px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Bem-vindo ao Banco Virtual</h1>
                        <a href="/login" class="btn">Login</a>
                        <a href="/register" class="btn">Criar Conta</a>
                    </div>
                </body>
            </html>
            '''
            self.send_response_page(html_content)
            
        elif self.path == '/login':
            # Página de login
            html_content = '''
            <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Login - Banco Virtual</title>
                    <style>
                        body { font-family: Arial, sans-serif; background: #f0f2f5; }
                        .form-container { max-width: 400px; margin: 100px auto; padding: 20px;
                                        background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }
                        input[type=submit] { background: #4CAF50; color: white; border: none; cursor: pointer; }
                        .back-link { display: block; margin-top: 20px; text-align: center; color: #666; }
                    </style>
                </head>
                <body>
                    <div class="form-container">
                        <h2>Login</h2>
                        <form action="/login" method="post">
                            <input type="text" name="username" placeholder="Usuário" required>
                            <input type="password" name="password" placeholder="Senha" required>
                            <input type="submit" value="Entrar">
                        </form>
                        <a href="/" class="back-link">Voltar</a>
                    </div>
                </body>
            </html>
            '''
            self.send_response_page(html_content)
            
        elif self.path == '/register':
            html_content = '''
            <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Criar Conta - Banco Virtual</title>
                    <style>
                        body { font-family: Arial, sans-serif; background: #f0f2f5; }
                        .form-container { max-width: 400px; margin: 100px auto; padding: 20px;
                                        background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }
                        input[type=submit] { background: #4CAF50; color: white; border: none; cursor: pointer; }
                        .back-link { display: block; margin-top: 20px; text-align: center; color: #666; }
                    </style>
                </head>
                <body>
                    <div class="form-container">
                        <h2>Criar Nova Conta</h2>
                        <form action="/register" method="post">
                            <input type="text" name="username" placeholder="Escolha um usuário" required>
                            <input type="password" name="password" placeholder="Escolha uma senha" required>
                            <input type="submit" value="Criar Conta">
                        </form>
                        <a href="/" class="back-link">Voltar</a>
                    </div>
                </body>
            </html>
            '''
            self.send_response_page(html_content)
        else:
            self.send_error(404, "Página não encontrada", "A página que você está procurando não existe.")

handler = MyHttpRequestHandler

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_server():
    while True:
        try:
            with socketserver.TCPServer(("", PORT), handler) as httpd:
                clear_screen()
                logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
                logging.info("Serving at port %d", PORT)
                httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutdown requested... Press 'R' to restart or any other key to exit")
            try:
                choice = input().lower()
                if choice != 'r':
                    sys.exit(0)
                clear_screen()
            except KeyboardInterrupt:
                sys.exit(0)
        except Exception as e:
            logging.error(f"Error: {e}")
            print("\nError occurred. Press 'R' to restart or any other key to exit")
            try:
                choice = input().lower()
                if choice != 'r':
                    sys.exit(1)
                clear_screen()
                time.sleep(1)  # Wait before restart
            except KeyboardInterrupt:
                sys.exit(1)

if __name__ == "__main__":
    print("\nServidor web iniciando...")
    print("="*50)
    run_server()
