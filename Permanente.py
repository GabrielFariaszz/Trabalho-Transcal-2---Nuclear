import pygame
from sympy import symbols, lambdify
import numpy as np

# Definir variáveis simbólicas
S_n0, R_F, R_C, k_F, k_C, b, r, T_0 = symbols('S_n0 R_F R_C k_F k_C b r T_0')

# Definir equações de T_F e T_C
T_F_eq = (S_n0 * R_F**2 / (6 * k_F)) * (1 - (r / R_F)**2 + (3/10) * b * (1 - (r / R_F)**4)) \
      + (S_n0 * R_F**2 / (3 * k_C)) * (1 + (3/5) * b * (1 - (R_F / R_C))) + T_0

T_C_eq = (S_n0 * R_F**2 / (3 * k_C)) * (1 + (3/5) * b * ((R_F / r) - (R_F / R_C))) + T_0

# Funções lambdify para cálculo numérico
T_F_func = lambdify((S_n0, R_F, R_C, k_F, k_C, b, r, T_0), T_F_eq, 'numpy')
T_C_func = lambdify((S_n0, R_F, R_C, k_F, k_C, b, r, T_0), T_C_eq, 'numpy')

# Inicializando Pygame
pygame.init()

# Definir parâmetros da tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Simulação de Troca Térmica Nuclear')

# Parâmetros constantes para um reator PWR
S_n0_val = 4.0e6  # Densidade de potência em W/m³
R_F_val = 0.0041   # Raio da esfera de material fissionável em metros
R_C_val = 0.00475  # Raio do revestimento em metros
k_F_val = 0.1     # Condutividade térmica do material fissionável em W/(m·K)
k_C_val = 0.2     # Condutividade térmica do revestimento em W/(m·K)
b_val = 2     # Coeficiente adimensional (exemplo)
T_0_val = 290      # Temperatura inicial em graus Celsius

# Fator de escala para visualizar a esfera na tela
scale_factor = 60000

# Função para mapear temperatura para cor
def temperature_to_color(T, min_T, max_T):
    # Normaliza a temperatura entre 0 e 1
    norm_T = (T - min_T) / (max_T - min_T)
    norm_T = max(0, min(1, norm_T))  # Limitar entre 0 e 1

    # Define a cor com base na temperatura
    if norm_T < 0.5:
        # Gradiente de azul para verde
        r = 0
        g = int(255 * (norm_T * 2))  # De 0 a 255
        b = 255
    else:
        # Gradiente de verde para vermelho
        r = int(255 * ((norm_T - 0.5) * 2))  # De 0 a 255
        g = 255 - r  # Inverte a intensidade do verde
        b = 0

    return (r, g, b)

# Função para encontrar a temperatura mínima e máxima
def find_min_max_temperatures():
    min_temp = float('inf')
    max_temp = float('-inf')

    for r_val in np.linspace(0, R_C_val, 100):
        if r_val <= R_F_val:
            # Dentro da região do material fissionável
            T_val = T_F_func(S_n0_val, R_F_val, R_C_val, k_F_val, k_C_val, b_val, r_val, T_0_val)
        else:
            # Dentro da região do revestimento de alumínio
            T_val = T_C_func(S_n0_val, R_F_val, R_C_val, k_F_val, k_C_val, b_val, r_val, T_0_val)

        # Atualizar valores de temperatura mínima e máxima
        min_temp = min(min_temp, T_val)
        max_temp = max(max_temp, T_val)

    return min_temp, max_temp

# Função para calcular a temperatura no ponto (x, y)
def get_temperature_at_point(x, y, center_x, center_y):
    # Calcular a distância radial r do ponto até o centro da esfera
    r_val = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2) / scale_factor

    # Verificar se o ponto está dentro da esfera (r <= R_C)
    if r_val <= R_C_val:
        if r_val <= R_F_val:
            # Dentro da região do material fissionável
            T_val = T_F_func(S_n0_val, R_F_val, R_C_val, k_F_val, k_C_val, b_val, r_val, T_0_val)
        else:
            # Dentro da região do revestimento de alumínio
            T_val = T_C_func(S_n0_val, R_F_val, R_C_val, k_F_val, k_C_val, b_val, r_val, T_0_val)
        return T_val
    return None

# Loop principal
running = True
clock = pygame.time.Clock()

# Determinar a temperatura mínima e máxima no sistema
min_temp, max_temp = find_min_max_temperatures()

# Fonte para exibição de temperatura (agora em vermelho)
font = pygame.font.Font(None, 36)
font_color = (255, 0, 0)  # Vermelho

while running:
    # Verificar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Limpar a tela
    screen.fill((0, 0, 0))

    # Obter posição do mouse
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Calcular as temperaturas para diferentes valores de r
    for r_val in np.linspace(0, R_C_val, 300):
        scaled_r = int(r_val * scale_factor)
        if r_val <= R_F_val:
            # Dentro da região do material fissionável
            T_val = T_F_func(S_n0_val, R_F_val, R_C_val, k_F_val, k_C_val, b_val, r_val, T_0_val)
        else:
            # Dentro da região do revestimento de alumínio
            T_val = T_C_func(S_n0_val, R_F_val, R_C_val, k_F_val, k_C_val, b_val, r_val, T_0_val)

        # Determinar a cor baseada na temperatura (usando min/max ajustado)
        color = temperature_to_color(T_val, min_temp, max_temp)

        # Desenhar anéis concêntricos com cor correspondente à temperatura
        pygame.draw.circle(screen, color, (WIDTH // 2, HEIGHT // 2), scaled_r, 1)

    # Verificar se o mouse está sobre a esfera e exibir a temperatura
    temp_at_mouse = get_temperature_at_point(mouse_x, mouse_y, WIDTH // 2, HEIGHT // 2)
    if temp_at_mouse is not None:
        # Exibir a temperatura no ponto do mouse
        temp_text = font.render(f"Temp: {temp_at_mouse:.2f}°C", True, font_color)
        screen.blit(temp_text, (mouse_x + 10, mouse_y))

    # Atualizar a tela
    pygame.display.flip()

    # Controlar a taxa de frames
    clock.tick(30)

# Encerrar Pygame
pygame.quit()
