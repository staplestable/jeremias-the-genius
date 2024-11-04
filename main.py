import pygame
import random
import sys
import pygame_menu
import pandas as pd
import os
import csv
from pygame import mixer

# Inicializa o Pygame
pygame.init()
mixer.init()

# Configurações da tela
BACKGROUND_COLOR = (51, 23, 51) 
mixer.music.set_volume(0.2)
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Jeremias, The Genius')
first_game=True
Fase_unlimited = 1
lives = 3
menu_lives = lives
life_image_path = 'assets/Vida.png'  # Coloque o caminho para sua imagem de vida
life_image = pygame.image.load(life_image_path)
life_image = pygame.transform.scale(life_image, (70, 70))
# Carrega a imagem de fundo e redimensiona para caber na tela
background_image_path = 'assets/Tela_jogo.png'  # Coloque o caminho para sua imagem de fundo
background_image = pygame.image.load(background_image_path)
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Cores para destaque
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

# Estado do jogo
sequence = []
user_sequence = []
score = 0
ranking = []  # Lista para armazenar os 10 melhores resultados
game_over = False
step_duration = 500
highlighted_button = None
player_name = "Jeremias"  # Nome padrão do jogador
ranking_file = "assets/ranking.csv"

# Timer
time_limit = 3  # Tempo em segundos para o jogador pressionar uma tecla
timer_event = pygame.USEREVENT + 1
time_remaining = time_limit

# Variável para controlar o estado da demonstração
showing_sequence = False

def set_time_limit(limit, lives, settings):
    global time_limit
    mixer.music.load("assets/sounds/menu-selected.wav")
    mixer.music.play()
    set_lives(lives)
    time_limit = limit
    reset_timer()

def reset_timer():
    global time_remaining
    time_remaining = time_limit

def reset_timer1():
    global time_remaining
    time_remaining = time_limit + len(sequence)  # Tempo restante baseado no número de passos

# Função para carregar o ranking do arquivo Excel
def save_ranking():
    with open(ranking_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows([(score, name, fase) for score, name, fase in ranking]) 

def load_ranking():
    global ranking
    if os.path.exists(ranking_file):
        with open(ranking_file, mode='r') as file:
            reader = csv.reader(file)
            ranking = [(int(score), name, int(fase)) for score, name, fase in reader]
    else:
        ranking = []

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

# Função para desenhar os botões e o timer
def draw_game_elements(highlight=None):
    global Fase_unlimited, lives, score  # Adicione 'lives' aqui para exibir na tela

    # Define a imagem de fundo
    screen.blit(background_image, (0, 0))  # Aplica a imagem como plano de fundo
    var_height = HEIGHT // 3 + 50
    var_width = WIDTH // 6
    diamond_size = 50

    # Define os vértices dos diamantes
    diamonds = {
        'UP': [(var_height + 150, var_width + 50), (var_height + 150 + diamond_size, var_width + 50 + diamond_size), (var_height + 150, var_width + 50 + 2 * diamond_size), (var_height + 150 - diamond_size, var_width + 50 + diamond_size)],
        'DOWN': [(var_height + 150, var_width + 250), (var_height + 150 + diamond_size, var_width + 250 - diamond_size), (var_height + 150, var_width + 250 - 2 * diamond_size), (var_height + 150 - diamond_size, var_width + 250 - diamond_size)],
        'LEFT': [(var_height + 100, var_width + 100), (var_height + 100 + diamond_size, var_width + 100 + diamond_size), (var_height + 100, var_width + 100 + 2 * diamond_size), (var_height + 100 - diamond_size, var_width + 100 + diamond_size)],
        'RIGHT': [(var_height + 200, var_width + 200), (var_height + 200 + diamond_size, var_width + 200 - diamond_size), (var_height + 200, var_width + 200 - 2 * diamond_size), (var_height + 200 - diamond_size, var_width + 200 - diamond_size)]
    }

    # Desenha os botões
    for direction in COLORS.keys():
        color = LIGHT_COLORS[direction] if direction == highlight else COLORS[direction]
        pygame.draw.polygon(screen, color, diamonds[direction])

    # Desenha o timer e a fase
    font = pygame.font.Font(None, 36)
    info_surface = font.render(f'Tempo: {time_remaining}   Fase: {Fase_unlimited}   Score: {score}', True, (255, 255, 255))
    screen.blit(info_surface, (WIDTH // 4, 100))  # Posição das informações

    # Desenha o sprite de vida para cada vida restante
    for i in range(lives):
        screen.blit(life_image,( 75 + i * 35, 50))  # Ajusta o espaçamento entre cada imagem

    pygame.display.flip()  # Atualiza a tela

# Função para mostrar a sequência para o jogador
def show_sequence():
    global showing_sequence
    showing_sequence = True
    for step in sequence:
        draw_game_elements(step)
        sound_file = f"assets/sounds/{step.lower()}.wav"
        mixer.music.load(sound_file)
        mixer.music.play()
        pygame.time.delay(step_duration)
        draw_game_elements()  # Para limpar a tela
        pygame.time.delay(200)
    showing_sequence = False  # Permite a entrada do usuário após a sequência
    reset_timer1()  # Reinicia o timer com base na nova sequência

# Função para verificar a sequência do usuário
def check_sequence():
    global game_over, lives
    for i in range(len(user_sequence)):
        if user_sequence[i] != sequence[i]:
            lives -= 1  # Perde uma vida ao errar a sequência
            mixer.music.load("assets/sounds/error.wav")
            mixer.music.play()
            if lives <= 0:
                game_over = True  # Termina o jogo se as vidas acabarem
                return False
            else:
                return True 
    return True if len(user_sequence) == len(sequence) else None

# Função para retornar a cor do botão pressionado
def reset_highlight():
    global highlighted_button
    highlighted_button = None
    draw_game_elements()  # Redesenha sem destaque

# Função para iniciar o jogo
def start_game_unlimited():
    mixer.music.load("assets/sounds/menu-selected.wav")
    mixer.music.play()
    global user_sequence, score, game_over, lives
    user_sequence = []
    score = 0
    game_over = False
    lives = menu_lives  # Usa o valor de vidas ajustado no menu
    sequence.clear()

    countdown_timer(3)
    add_step()
    game_loop_unlimited()


# Função para exibir a contagem regressiva
def countdown_timer(seconds):
    for i in range(seconds, 0, -1):
        screen.fill(BACKGROUND_COLOR)  # Limpa a tela
        tela = pygame.image.load("assets/Tela.png")
        tela_image = pygame.transform.scale(tela, (WIDTH, HEIGHT))
        screen.blit(tela_image, (0, 0))
        font = pygame.font.Font(None, 74)
        countdown_surface = font.render(str(i), True, (255, 255, 255))  # Texto da contagem
        screen.blit(countdown_surface, (WIDTH // 3, HEIGHT //3))  # Centraliza o texto
        pygame.display.flip()  # Atualiza a tela
        pygame.time.delay(1000)
        mixer.music.load("assets/sounds/menu-selected.wav")
        mixer.music.play()
        reset_timer1()
    reset_timer()
    

# Função para acender o botão pressionado
def highlight_button(direction):
    global highlighted_button
    highlighted_button = direction
    draw_game_elements(highlighted_button)  # Desenha o botão destacado
    pygame.time.delay(200)  # Delay para mostrar o destaque
    reset_highlight()  # Limpa o destaque após o delay

# Loop principal do jogo
def game_loop_unlimited():
    global user_sequence, score, game_over, highlighted_button, ranking, time_remaining, first_game, Fase_unlimited
    Fase_unlimited = 1 
    # Inicializa o tempo restante
    if first_game:
        reset_timer()
    else:
        time_remaining = time_limit+3
    pygame.time.set_timer(timer_event, 1000)  # Inicia o timer
    time_sum = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game()

            if not game_over:
                if event.type == pygame.KEYDOWN and not showing_sequence:
                    if event.key == pygame.K_UP:
                        mixer.music.load("assets/sounds/up.wav")
                        mixer.music.play()
                        user_sequence.append('UP')
                        highlight_button('UP')
                        time_sum += time_remaining
                    elif event.key == pygame.K_DOWN:
                        mixer.music.load("assets/sounds/down.wav")
                        mixer.music.play()
                        user_sequence.append('DOWN')
                        highlight_button('DOWN')
                        time_sum += time_remaining
                    elif event.key == pygame.K_LEFT:
                        mixer.music.load("assets/sounds/left.wav")
                        mixer.music.play()
                        user_sequence.append('LEFT')
                        highlight_button('LEFT')
                        time_sum += time_remaining
                    elif event.key == pygame.K_RIGHT:
                        mixer.music.load("assets/sounds/right.wav")
                        mixer.music.play()
                        user_sequence.append('RIGHT')
                        highlight_button('RIGHT')
                        time_sum += time_remaining

                    reset_timer()  # Reinicia o tempo ao pressionar um botão
                    result = check_sequence()
                    if len(sequence)>=5*Fase_unlimited:
                        Fase_unlimited+=1
                    if result is True:
                        dim_screen()
                        pygame.time.delay(500)
                        score += 1 + int((time_sum * len(sequence))/(time_limit*lives))*Fase_unlimited
                        user_sequence = []
                        add_step()
                        time_sum = 0
                    elif result is False:
                        game_over = True
                        update_ranking(score, Fase_unlimited)

                if event.type == timer_event and not showing_sequence:
                    time_remaining -= 1
                    if time_remaining <= 0:
                        game_over = True

        # Desenha os botões e o timer
        draw_game_elements(highlighted_button)

        if game_over:
            first_game=False
            display_game_over()
            pygame.time.wait(2000)
            show_menu()
            
        pygame.time.delay(50)

# Função para atualizar o ranking
def update_ranking(new_score, fase_unlimited):
    global ranking
    ranking.append((new_score, player_name, fase_unlimited))
    ranking = sorted(ranking, key=lambda x: x[0], reverse=True)[:10]  # Mantém os 10 melhores
    save_ranking()  # Salva o ranking atualizado
    
def difficulty_menu():
    # Criação do submenu de dificuldade
    settings = pygame_menu.Menu('Configurações de Dificuldade', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)
    
    # Entrada de texto para o nome do jogador
    settings.add.text_input('Nome do Jogador: ', default=player_name, onchange=set_player_name)

    # Botões para ajustar a dificuldade, que afeta o tempo do timer
    settings.add.button('Fácil', lambda: set_time_limit(10, 5, settings))
    settings.add.button('Médio', lambda: set_time_limit(7, 3, settings))
    settings.add.button('Difícil', lambda: set_time_limit(5, 2, settings))
    settings.add.button('Jeremias', lambda: set_time_limit(3, 1, settings))
    settings.add.button('Voltar', show_menu)  # Botão para voltar ao menu principal
    
    settings.mainloop(screen)
# Função para exibir a tela de Game Over
def display_game_over():
    # Exibe a imagem de fundo
    screen.fill((255, 0, 0))
    tela = pygame.image.load("assets/Tela.png")
    tela_image = pygame.transform.scale(tela, (WIDTH, HEIGHT))
    screen.blit(tela_image, (0, 0))
    
    # Toca o som de erro
    #mixer.music.load("assets/sounds/error.wav")
    #mixer.music.play()
    
    # Configura a fonte e renderiza o texto de "Game Over" e "Score"
    font = pygame.font.Font(None, 74)
    text_game_over = font.render('Game Over', True, (255, 255, 255))
    text_score = font.render(f'Score: {score}', True, (255, 255, 255))
    
    # Exibe o texto sobre a tela com o fundo
    screen.blit(text_game_over, (WIDTH // 4, HEIGHT // 4))
    screen.blit(text_score, (WIDTH // 4, HEIGHT // 2))
    
    # Atualiza a tela para mostrar as alterações
    pygame.display.flip()

# Função para sair do jogo corretamente
def exit_game():
    pygame.quit()
    sys.exit()

# Função para mostrar os créditos
def show_credits():
    mixer.music.load("assets/sounds/menu-selected.wav")
    mixer.music.play()
    
    
    # Criar o menu de créditos
    credits = pygame_menu.Menu('Créditos', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)
    credits.add.label('Alunos:')
    credits.add.label('Lucas Damaceno da Cunha Lima \n 10389222')
    credits.add.label('Lucas Iudi Corregliano Gallinari \n 10389472')
    credits.add.button('Voltar', show_menu)
    
    # Executar o menu de créditos
    credits.mainloop(screen)

# Função para definir o nome do jogador
def set_player_name(name):
    global player_name
    player_name = name

# Função para criar o menu de configurações
def settings_menu():
    screen.blit(background_image, (0, 0))  # Aplica a imagem de fundo nas configurações
    mixer.music.load("assets/sounds/menu-selected.wav")
    mixer.music.play()
    global time_limit, lives, player_name  # Adicione a variável de vidas aqui para controle no menu
    
    # Inicializa o menu de configurações com tema escuro
    settings = pygame_menu.Menu('Configurações', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)
    
    # Entrada de texto para o nome do jogador
    settings.add.text_input('Nome do Jogador: ', default=player_name, onchange=set_player_name)
    # Slider para ajustar o tempo do timer em segundos
    settings.add.range_slider('Tempo do Timer (segundos):', 
                              default=time_limit, 
                              range_values=(1, 10), 
                              increment=1,
                              onchange=lambda value: set_timer(value))  # Atualiza o tempo do timer
    
    # Slider para ajustar o volume da música
    settings.add.range_slider('Volume da Música:', 
                              default=mixer.music.get_volume(),  # Pega o volume atual
                              range_values=(0.0, 1.0), 
                              increment=0.1,
                              onchange=lambda volume: mixer.music.set_volume(volume))  # Atualiza o volume
    
    # Slider para ajustar o número de vidas do jogador
    settings.add.range_slider('Número de Vidas:', 
                              default=lives, 
                              range_values=(1, 5), 
                              increment=1,
                              onchange=lambda value: set_lives(value))  # Atualiza o número de vidas
    
    # Botão para voltar ao menu principal
    settings.add.button('Voltar', show_menu)
    
    # Loop para exibir e atualizar o menu
    while True:
        events = pygame.event.get()  # Obtém os eventos do Pygame
        settings.update(events)  # Atualiza o menu com os eventos
        settings.draw(screen)  # Desenha o menu na tela
        pygame.display.flip()    # Atualiza a tela

def set_lives(value):
    global lives, menu_lives
    lives = int(value)  # Atualiza a variável global de vidas
    menu_lives = lives
# Função para definir o tempo do timer
def show_menu():
    screen.blit(background_image, (0, 0))  # Aplica a imagem de fundo no menu principal
    menu = pygame_menu.Menu('Genius Game', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)

    menu.add.button('Começar Jogo', start_game_unlimited)  # Opção para iniciar o jogo
    menu.add.button('Dificuldade', difficulty_menu)  # Opção para o menu de dificuldades
    menu.add.button('Configurações', settings_menu)  # Opção para configurações
    menu.add.button('Ranking', show_ranking)  # Modificado para "Ranking"
    menu.add.button('Créditos', show_credits)
    menu.add.button('Sair', exit_game) 

    menu.mainloop(screen)
def set_timer(value):
    global time_limit
    time_limit = int(value)  # Certifique-se de que o valor é um inteiro
    reset_timer()


# Função para mostrar o ranking
def show_ranking():
    ranking_menu = pygame_menu.Menu('Ranking', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)
    ranking_menu.add.label('Ranking dos Melhores Resultados:')
    
    # Adiciona os 10 melhores resultados ao menu com fase incluída
    for idx, (score, name, fase) in enumerate(ranking):
        ranking_menu.add.label(f'{idx + 1}. {name}: {score} (Fase {fase})')
    
    ranking_menu.add.button('Voltar', show_menu)
    ranking_menu.mainloop(screen)

if __name__ == "__main__":
    load_ranking()  # Carrega o ranking ao iniciar
    show_menu()
