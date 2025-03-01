import pygame
import requests
import random

# Inicializa o Pygame
pygame.init()

# Definir cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)
VERMELHO = (255, 0, 0)

# Definir dimensões da tela
LARGURA = 800
ALTURA = 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo de Trivia")

# Definir fonte
fonte = pygame.font.SysFont(None, 36)

def obter_perguntas():
    """
    Obtém perguntas da Open Trivia DB.
    """
    url = "https://opentdb.com/api.php?amount=10&type=multiple"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        dados = resposta.json()
        return dados['results']
    else:
        print("Erro ao acessar a API.")
        return []

def exibir_texto(texto, cor, x, y):
    """
    Exibe um texto na tela.
    """
    texto_renderizado = fonte.render(texto, True, cor)
    tela.blit(texto_renderizado, (x, y))

def exibir_pergunta(pergunta, opcoes, resposta_correta, pontuacao):
    """
    Exibe uma pergunta e suas opções, e verifica se a resposta do usuário está correta.
    """
    tela.fill(BRANCO)
    exibir_texto(pergunta, PRETO, 20, 20)
    for i, opcao in enumerate(opcoes, 1):
        exibir_texto(f"{i}. {opcao}", PRETO, 20, 100 + (i - 1) * 50)
    exibir_texto(f"Pontuação: {pontuacao}", PRETO, 20, ALTURA - 40)
    pygame.display.update()

def jogo():
    """
    Função principal que gerencia o jogo de trivia.
    """
    perguntas = obter_perguntas()
    if not perguntas:
        return

    pontuacao = 0
    for pergunta in perguntas:
        enunciado = pergunta['question']
        resposta_correta = pergunta['correct_answer']
        opcoes = pergunta['incorrect_answers']
        opcoes.append(resposta_correta)
        random.shuffle(opcoes)

        exibir_pergunta(enunciado, opcoes, resposta_correta, pontuacao)
        esperando_resposta = True
        while esperando_resposta:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    return
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_1:
                        resposta = opcoes[0]
                    elif evento.key == pygame.K_2:
                        resposta = opcoes[1]
                    elif evento.key == pygame.K_3:
                        resposta = opcoes[2]
                    elif evento.key == pygame.K_4:
                        resposta = opcoes[3]
                    else:
                        continue

                    if resposta == resposta_correta:
                        pontuacao += 1
                    esperando_resposta = False

    tela.fill(BRANCO)
    exibir_texto(f"Fim do jogo! Sua pontuação final é: {pontuacao}/{len(perguntas)}", PRETO, 20, ALTURA // 2)
    pygame.display.update()
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    jogo()
