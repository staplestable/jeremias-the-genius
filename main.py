import pygame
import random
import sys
import pygame_menu
import pandas as pd
import os
#import openpyxl

from pygame import mixer

# Inicializa o Pygame
pygame.init()
mixer.init()


# Configurações mixer
mixer.music.set_volume(0.2)

# Configurações da tela
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Jeremias The Genius')

# Cores
COLORS = {
    'UP': (255, 0, 0),
    'DOWN': (0, 255, 0),
    'LEFT': (0, 0, 255),
    'RIGHT': (255, 255, 0),
}

# Cores claras para o efeito
LIGHT_COLORS = {
    'UP': (255, 128, 128),
    'DOWN': (128, 255, 128),
    'LEFT': (128, 128, 255),
    'RIGHT': (255, 255, 128),
}

# Cor de fundo
BACKGROUND_COLOR = (51,23,51)  # Roxo escuro

# Estado do jogo
sequence = []
user_sequence = []
score = 0
ranking = []  # Lista para armazenar os 10 melhores resultados
game_over = False
step_duration = 500
highlighted_button = None
player_name = "Jeremias"  # Nome padrão do jogador
ranking_file = "ranking.csv"

# Função para carregar o ranking do arquivo Excel
def load_ranking():
    global ranking
    if os.path.exists(ranking_file):
        df = pd.read_csv(ranking_file)
        ranking = list(zip(df['Score'], df['Name']))
    else:
        ranking = []

# Função para salvar o ranking em um arquivo Excel
def save_ranking():
    df = pd.DataFrame(ranking, columns=['Score', 'Name'])
    df.to_csv(ranking_file, index=False)

# Função para adicionar um novo passo à sequência
def add_step():
    step = random.choice(list(COLORS.keys()))
    sequence.append(step)
    show_sequence()

# Função para escurecer a tela
def dim_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(50)
    screen.blit(overlay, (0, 0))
    pygame.display.flip()
    pygame.time.delay(200)

# Função para desenhar os botões
def draw_buttons(highlight=None):
    screen.fill(BACKGROUND_COLOR)  # Muda a cor de fundo para roxo escuro
    
    for direction in COLORS.keys():
        color = LIGHT_COLORS[direction] if direction == highlight else COLORS[direction]
        if direction == 'UP':          
            pygame.draw.rect(screen, color, (150, 50, 100, 100))
        elif direction == 'DOWN':    
            pygame.draw.rect(screen, color, (150, 250, 100, 100))
        elif direction == 'LEFT':          
            pygame.draw.rect(screen, color, (50, 150, 100, 100))
        elif direction == 'RIGHT':
            pygame.draw.rect(screen, color, (250, 150, 100, 100))    
    pygame.display.flip()

# Função para mostrar a sequência para o jogador
def show_sequence():
    for step in sequence:
        draw_buttons(step)
        sound_file = f"assets/sounds/{step.lower()}.wav" 
        mixer.music.load(sound_file) 
        mixer.music.play()  
        pygame.time.delay(step_duration)
        draw_buttons()
        pygame.time.delay(200)

# Função para verificar a sequência do usuário
def check_sequence():
    global game_over
    if user_sequence == sequence:
        return True
    elif len(user_sequence) >= len(sequence):
        game_over = True
        return False
    return None

# Função para retornar a cor do botão pressionado
def reset_highlight():
    global highlighted_button
    highlighted_button = None
    draw_buttons()

# Função para iniciar o jogo
def start_game():
    mixer.music.load("assets\sounds\menu-selected.wav")
    mixer.music.play()

    global user_sequence, score, game_over
    user_sequence = []
    score = 0
    game_over = False
    sequence.clear()
    
    # Atraso de 1 segundo antes de começar o jogo
    pygame.time.wait(1000)
    
    add_step()  # Inicia o jogo após o atraso
    pygame.time.wait(100)
    game_loop()

# Loop principal do jogo
def game_loop():
    global user_sequence, score, game_over, highlighted_button, ranking

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game()

            if not game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        mixer.music.load("assets/sounds/up.wav")
                        mixer.music.play()
                        user_sequence.append('UP')
                        highlighted_button = 'UP'
                        draw_buttons('UP')
                    elif event.key == pygame.K_DOWN:
                        mixer.music.load("assets/sounds/down.wav")
                        mixer.music.play()
                        user_sequence.append('DOWN')
                        highlighted_button = 'DOWN'
                        draw_buttons('DOWN')
                    elif event.key == pygame.K_LEFT:
                        mixer.music.load("assets/sounds/left.wav")
                        mixer.music.play()
                        user_sequence.append('LEFT')
                        highlighted_button = 'LEFT'
                        draw_buttons('LEFT')
                    elif event.key == pygame.K_RIGHT:
                        mixer.music.load("assets/sounds/right.wav")
                        mixer.music.play()
                        user_sequence.append('RIGHT')
                        highlighted_button = 'RIGHT'
                        draw_buttons('RIGHT')

                    pygame.time.set_timer(pygame.USEREVENT, 500)
                    result = check_sequence()
                    if result is True:
                        dim_screen()
                        pygame.time.delay(500)
                        score += 1
                        user_sequence = []
                        add_step()
                    elif result is False:
                        game_over = True
                        update_ranking(score)

            if event.type == pygame.USEREVENT and highlighted_button:
                reset_highlight()
                pygame.time.set_timer(pygame.USEREVENT, 0)

        if game_over:
            display_game_over()
            pygame.time.wait(2000)
            show_menu()

        pygame.time.delay(50)

# Função para atualizar o ranking
def update_ranking(new_score):
    global ranking
    ranking.append((new_score, player_name))
    ranking = sorted(ranking, key=lambda x: x[0], reverse=True)[:10]  # Mantém os 10 melhores
    save_ranking()  # Salva o ranking atualizado

# Função para exibir a tela de Game Over
def display_game_over():
    mixer.music.load("assets/sounds/error.wav")
    mixer.music.play()

    screen.fill((255, 0, 0))
    font = pygame.font.Font(None, 74)
    text_game_over = font.render('Game Over', True, (255, 255, 255))
    text_score = font.render(f'Score: {score}', True, (255, 255, 255))
    screen.blit(text_game_over, (WIDTH // 4, HEIGHT // 4))
    screen.blit(text_score, (WIDTH // 4, HEIGHT // 2))
    pygame.display.flip()

# Função para sair do jogo corretamente
def exit_game():
    pygame.quit()
    sys.exit()

# Função para mostrar os créditos
def show_credits():
    mixer.music.load("assets\sounds\menu-selected.wav")
    mixer.music.play()

    credits = pygame_menu.Menu('Créditos', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)
    credits.add.label('Alunos:')
    credits.add.label('Lucas Damasceno da Cunha Lima')
    credits.add.label('10389222')
    credits.add.label('Lucas Iudi Corregliano Gallinari')
    credits.add.label('10389472')
    credits.add.button('Voltar', show_menu)
    credits.mainloop(screen)

# Função para criar o menu de entrada do nome do jogador
def enter_name_menu():
    mixer.music.load("assets\sounds\menu-selected.wav")
    mixer.music.play()

    global player_name
    name_menu = pygame_menu.Menu('Digite seu Nome', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)
    name_menu.add.text_input('Nome: ', default=player_name, onreturn=lambda name: set_player_name(name))
    name_menu.add.button('Salvar e Começar Jogo', start_game)
    name_menu.add.button('Voltar', show_menu)
    name_menu.mainloop(screen)

# Função para definir o nome do jogador
def set_player_name(name):
    global player_name
    player_name = name

# Função para criar o menu
def show_menu():
    menu = pygame_menu.Menu('Jeremias The Genius', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)

    menu.add.button('Novo Jogo', start_game)
    menu.add.button('Alterar Apelido', enter_name_menu)
    menu.add.button('Ranking', show_ranking) 
    menu.add.button('Créditos', show_credits)
    menu.add.button('Sair', exit_game)

    menu.mainloop(screen)

# Função para mostrar o ranking
def show_ranking():
    ranking_menu = pygame_menu.Menu('Ranking', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)
    ranking_menu.add.label('Melhores Resultados:')
    
    # Adiciona os 10 melhores resultados ao menu
    for idx, (score, name) in enumerate(ranking):
        ranking_menu.add.label(f'{idx + 1}. {name}: {score}')
    
    ranking_menu.add.button('Voltar', show_menu)
    ranking_menu.mainloop(screen)

if __name__ == "__main__":
    load_ranking()  # Carrega o ranking ao iniciar
    show_menu()
