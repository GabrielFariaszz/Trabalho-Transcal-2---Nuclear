#importação de bibliotecas
import numpy as np
import time
import matplotlib.pyplot as plt


def novo_ui(alfaf,dt,rf,delta_rf,u_m,u_i,u_p,i,rhof,cpf,sno=1,b=1):
  """
  Calcula o novo valor de u(i) para a geração n+1
  Args:
    alfaf: difusividade térmica do combustível
    dt: passo de tempo
    rf: raio do combustível
    delta_rf: tamanho da malha para o combustível
    u_m: valor de u(i-1) da geração n
    u_i: valor de u(i) da geração n
    u_p: valor de u(i+1) da geração n
    i: posição i
    rhof: densidade do combustível
    cpf: calor sensível à pressão CTE do combustível
    sno: valor da geração de calor no centro do combustível
    b: coeficiente da parábola para o termo de geração de calor
  """

  #termo de difusão térmica:
  difusao = (alfaf*dt/delta_rf)*(((u_p-2*u_i+u_m)/delta_rf)+((u_p-u_m)/(i*delta_rf)))

  #termo de fonte de calor:
  fonte = ((dt*sno)/(rhof*cpf))*(1+b*((i*delta_rf)/rf)**2)

  #u(i) da geração nova:
  novo_ui = u_i + difusao + fonte

  return novo_ui


def novo_vi(alfac,dt,rf,rc,delta_rc,v_m,v_i,v_p,i,nf):
  """
  Calcula o novo valor de v(i) para a geração n+1
  Args:
    alfac: difusividade térmica do revestimento
    dt: passo de tempo
    rc: raio do revestimento
    delta_rc: tamanho da malha para o revestimento
    v_m: valor de v(i-1) da geração n
    v_i: valor de v(i) da geração n
    v_p: valor de v(i+1) da geração n
    i: posição i
    nf: número de pontos de malha para o combustível
  """

  rci = rf + (i - nf) * delta_rc

  #termo de difusão térmica:
  difusao = (alfac*dt/delta_rc)*(((v_p-2*v_i+v_m)/delta_rc)+((v_p-v_m)/(rci)))

  #v(i) da geração nova:
  novo_vi = v_i + difusao

  return novo_vi


def novo_wi(alfai,dt,rc,ri,delta_ri,w_m,w_i,w_p,i,nf,nc):
  """
  Calcula o novo valor de w(i) para a geração n+1
  Args:
    alfac: difusividade térmica do revestimento
    dt: passo de tempo
    rc: raio do revestimento
    delta_rc: tamanho da malha para o revestimento
    v_m: valor de v(i-1) da geração n
    v_i: valor de v(i) da geração n
    v_p: valor de v(i+1) da geração n
    i: posição i
    nf: número de pontos de malha para o combustível
  """

  rii = rc + (i - nf - nc) * delta_ri

  #termo de difusão térmica:
  difusao = (alfai*dt/delta_ri)*(((w_p-2*w_i+w_m)/delta_ri)+((w_p-w_m)/(rii)))

  #v(i) da geração nova:
  novo_wi = w_i + difusao

  return novo_wi


def anotar_vetor(vetor,filename):
    """Adiciona um vetor ao arquivo, cada vetor em uma nova linha."""
    with open(filename, 'a') as file:
      file.write(f"{vetor}\n")

def formatar_precisao(lista,precisao):
    """Retorna uma nova lista com os números formatados para duas casas decimais."""
    return [round(num, precisao) for num in lista]


def main(t,caso=False):
  """

  Args:
    t: tempo no qual para o qual a função será calculada.
  """

  gravador = []

  if caso == False: #caso default
    [[kf,kc,ki],[rhof,rhoc,rhoi],[cpf,cpc,cpi],[alfaf,alfac,alfai],[rf,rc,ri],[nf,nc,ni],[delta_rf,delta_rc,delta_ri],dt,ti,to,h,sno,b,alfaagua] = [[7,237,2.5],[10970,2700,5600],[240,900,450],[2.6587663324217565e-06,9.7530864197530864197530864197531e-5,9.9206349206349206349206349206349e-7],[5e-2,7.5e-2,1e-1],[51,25,25],[1e-3,1e-3,1e-3],4e-3,25,275,5e3,1e6,2,1.43e-7]

  arquivo = input('Dê o nome para o arquivo com os vetores de temperatura. \n') + '.txt'

  # Cria um arquivo em branco (se não existir)
  with open(arquivo, 'w') as file:
    pass  # apenas cria o arquivo vazio

  start_time = time.time()

  #iniciando a malha com a condição inicial
  malha = (np.ones(nf + nc + ni - 1) * ti)

  r = (np.linspace(0,ri,nf + nc + ni -1)).tolist()
  anotar_vetor(formatar_precisao(r,5) , arquivo)

  #número de iterações:
  ncontas = round(t / dt)

  for n in range(ncontas): #tempo

    if (n*dt) % 60 == 0: # Armazena o vetor de temperatura a cada 1 minuto
        vetor = formatar_precisao(malha.copy() , 1)
        vetor_convertido = [float(valor) for valor in vetor]
        tempo = n * dt
        dados_anotar = [vetor_convertido , tempo]
        anotar_vetor(dados_anotar , arquivo)

    for i in range(len(malha)): #espaço

      if i == 0:
        malha[i] = malha[i+1]

      if (i >= 1) and (i <= (nf - 2)):
        u_m = malha[i - 1]
        u_i = malha[i]
        u_p = malha[i + 1]
        malha[i] = novo_ui(alfaf,dt,rf,delta_rf,u_m,u_i,u_p,i,rhof,cpf,sno,b)

      if i == (nf - 1):
        malha[i] = (malha[i-1] * delta_rc * kf + malha[i+1] * delta_rf * kc) / (delta_rf * kc + delta_rc * kf)

      if (i >= nf) and (i <= (nf + nc - 3)):
        v_m = malha[i - 1]
        v_i = malha[i]
        v_p = malha[i + 1]
        malha[i] = novo_vi(alfac,dt,rf,rc,delta_rc,v_m,v_i,v_p,i,nf)

      if i == (nf + nc - 2):
        malha[i] = (malha[i-1] * delta_ri * kc + malha[i+1] * delta_rc * ki) / (delta_rc * ki + delta_ri * kc)

      if (i >= nc) and (i <= (nf + nc + ni - 3)):
        w_m = malha[i - 1]
        w_i = malha[i]
        w_p = malha[i + 1]
        malha[i] = novo_wi(alfai,dt,rc,ri,delta_ri,w_m,w_i,w_p,i,nf,nc)

      if i == (nf + nc + ni - 2):
        tot = to - (to - ti) * np.exp(- (alfaagua * h / 0.5545) * n * dt)
        malha[i] = (h * tot + (ki/delta_ri) * malha[i-1]) / (h + (ki/delta_ri) )

  end_time = time.time()

  execution_time = end_time - start_time

  print(f"O código demorou {execution_time:.6f} segundos para rodar.")
