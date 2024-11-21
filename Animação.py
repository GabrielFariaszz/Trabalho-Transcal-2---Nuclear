import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import Normalize

# Função para carregar dados do arquivo
def carregar_dados(arquivo):
    with open(arquivo, 'r') as f:
        linhas = f.readlines()
    
    # A primeira linha é a malha radial
    malha_r = eval(linhas[0].strip())
    
    # As demais linhas contêm os vetores de temperatura e o tempo
    temperaturas = []
    tempos = []
    for linha in linhas[1:]:
        dado = eval(linha.strip())
        temperaturas.append(dado[0])  # Vetor de temperatura em cada tempo
        tempos.append(dado[1] / 60)        # Tempo associado ao vetor de temperatura
    
    return np.array(malha_r), np.array(temperaturas), np.array(tempos)

# Função de animação
def animar_temperatura(arquivo_dados, salvar_gif=False, vmin=None, vmax=None):
    # Carrega os dados do arquivo
    malha_r, temperaturas, tempos = carregar_dados(arquivo_dados)
    
    # Ajuste do número de pontos angulares
    num_angular = 360
    theta = np.linspace(0, 2 * np.pi, num_angular, endpoint=False)
    r = malha_r

    # Criação da matriz 2D de temperatura com a dimensão radial e angular correta
    temp_2d = np.array([np.tile(temp, (num_angular, 1)).T for temp in temperaturas])

    # Define o alcance da escala de cores (caso vmin e vmax não sejam especificados)
    if vmin is None:
        vmin = np.min(temperaturas)
    if vmax is None:
        vmax = np.max(temperaturas)

    # Prepara o gráfico
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)

    # Ajusta a malha para o pcolormesh
    theta_grid, r_grid = np.meshgrid(theta, r)

    # Cria o gráfico inicial com pcolormesh, aplicando a escala de cor fixa
    norm = Normalize(vmin=vmin, vmax=vmax)
    cax = ax.pcolormesh(theta_grid, r_grid, temp_2d[0], shading='auto', cmap='jet', norm=norm)
    fig.colorbar(cax, ax=ax, label='Temperatura [°C]')

    # Função de atualização para cada quadro da animação
    def atualizar_quadro(i):
        ax.set_title(f'Tempo: {tempos[i]:.0f} min')  # Atualiza o título com o tempo atual
        cax.set_array(temp_2d[i].ravel())  # Atualiza os dados de temperatura
        return cax,

    # Cria a animação
    ani = animation.FuncAnimation(fig, atualizar_quadro, frames=300, interval=200, blit=True, repeat=True)
    
    # Salvar como GIF
    if salvar_gif:
        ani.save("animacao_temperatura.gif", writer='pillow')

    plt.show()

# Chamada da função principal de animação com vmin e vmax definidos pelo usuário
animar_temperatura('24 h.txt', salvar_gif=True, vmin=25, vmax=435)
