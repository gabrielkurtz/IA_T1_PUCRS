import random
import math
import sys
import copy

UNICODE = False
LOG_COMPLETO = False
GERACOES_ENTRE_LOG_SIMPLES = 5

GERACOES = 100
FATOR_MAXIMO_PASSOS = 2
ELITISMO = 2
TORNEIO = 4
MUTACAO_MINIMA = 4
MUTACAO_MAXIMA = 50

TAM_POPULACAO_INICIAL = ELITISMO + 2*TORNEIO
labirinto = []
tamanho_matriz = 0
maximo_passos = 0

contador_cromossomos = 1

alguem_achou_saida = False
mutacao = MUTACAO_MAXIMA

contador_geracoes = 1
melhor = None


def main():
    f = open(str(sys.argv[1]), "r")

    global tamanho_matriz
    tamanho_matriz = int(f.readline())

    global maximo_passos
    maximo_passos = int(math.pow(tamanho_matriz, FATOR_MAXIMO_PASSOS))

    # Labirinto conforme no arquivo de entrada
    # [0]: informacao original - E: entrada - S: saída - 0: pode andar - 1: parede
    global labirinto
    for _ in range(tamanho_matriz):
        labirinto.append(f.readline().split())

    imprime_labirinto()

    populacao = inicializa_populacao()

    for i in range(GERACOES):
        global contador_geracoes

        executa_geracao(populacao)

        if not LOG_COMPLETO:
            if contador_geracoes == 1 or (contador_geracoes % GERACOES_ENTRE_LOG_SIMPLES == 0):
                logar_simples(populacao)
        contador_geracoes += 1

        populacao = nova_geracao(populacao)

    print("----------------------------------------------------------------")
    print("MELHOR CROMOSSOMO")
    print(melhor)


class Cromossomo:
    def __init__(self):
        global contador_cromossomos
        self.nome = contador_cromossomos
        contador_cromossomos += 1

        self.saida = None
        self.encontrou_saida = False
        self.posicao = (0, 0)
        self.posicao_anterior = (0, 0)
        self.passos = []

        self.tentativas = maximo_passos
        self.percentual_mutacao = mutacao

        # Movimentos possiveis e efeito na posição
        self.movimentos = self.cria_movimentos()

        # Acrescenta informacao extra para cada campo no formato [str,int,int], onde:
        # [1]: 0: campo ainda não foi visitado pelo algoritmo - 1: já foi visitado
        # Guarda a versao inicial para reiniciar nas fases de seleção genética
        self.visitados_inicial = self.cria_visitados()
        self.visitados = self.cria_visitados()

        # Último movimento gravado no campo pelo algoritmo - fator de melhoria genética,
        # segue as direções do numpad, ex: 2 para baixo, 9 diagonal superior direita, etc.
        # onde 0 é ausencia de preferencia e 5 não existe.
        self.direcoes = self.cria_direcoes()

    def cria_visitados(self):
        matriz = [["0" for col in range(tamanho_matriz)]
                  for row in range(tamanho_matriz)]
        for i in range(tamanho_matriz):
            for j in range(tamanho_matriz):
                matriz[i][j] = "0" if labirinto[i][j] != "1" else "1"

        # Marca entrada como $, supondo entrada sempre (0,0)
        matriz[0][0] = "$"

        return matriz

    def cria_direcoes(self):
        direcoes = [[0 for col in range(tamanho_matriz)]
                    for row in range(tamanho_matriz)]
        for i in range(tamanho_matriz):
            for j in range(tamanho_matriz):
                if labirinto[i][j] != '1':
                    self.posicao = (i, j)
                    direcoes[i][j] = self.nova_direcao()
        self.posicao = (0, 0)
        self.posicao_anterior = (0, 0)
        return direcoes

    def cria_movimentos(self):
        movimentos = {}
        if UNICODE:
            movimentos[1] = [1, -1, "↙"]
            movimentos[2] = [1, 0, "↓"]
            movimentos[3] = [1, 1, "↘"]
            movimentos[4] = [0, -1, "←"]
            movimentos[6] = [0, 1, "→"]
            movimentos[7] = [-1, -1, "↖"]
            movimentos[8] = [-1, 0, "↑"]
            movimentos[9] = [-1, 1, "↗"]
            movimentos[0] = [0, 0, "X"]  # Ocorre somente em caso de erro
        else:
            movimentos[1] = [1, -1, "1"]
            movimentos[2] = [1, 0, "2"]
            movimentos[3] = [1, 1, "3"]
            movimentos[4] = [0, -1, "4"]
            movimentos[6] = [0, 1, "6"]
            movimentos[7] = [-1, -1, "7"]
            movimentos[8] = [-1, 0, "8"]
            movimentos[9] = [-1, 1, "9"]
            movimentos[0] = [0, 0, "X"]  # Ocorre somente em caso de erro
        return movimentos

    def calcula_nova_posicao(self, direcao):
        diferenca = self.movimentos[direcao]
        return (self.posicao[0] + diferenca[0], self.posicao[1] + diferenca[1])

    def reinicia_cromossomo(self):
        self.visitados = self.cria_visitados()
        self.passos = []
        self.posicao = (0, 0)
        self.posicao_anterior = (0, 0)
        self.encontrou_saida = False
        self.percentual_mutacao = mutacao

    def executa(self):
        self.reinicia_cromossomo()

        for _ in range(self.tentativas):
            if(self.deve_mudar_direcao()):
                direcao = self.nova_direcao()
                self.direcoes[self.posicao[0]][self.posicao[1]] = direcao
            else:
                direcao = self.direcoes[self.posicao[0]][self.posicao[1]]

            self.movimenta(direcao)
            self.passos.append(self.posicao)
            if self.encontrou_saida:
                break

    def deve_mudar_direcao(self):
        # Campo sem direção ainda
        if self.direcoes[self.posicao[0]][self.posicao[1]] == 0:
            return True

        # Mutação
        elif random.randrange(100) < self.percentual_mutacao:
            return True
        return False

    def nova_direcao(self):
        count = 0
        posicao_valida = False
        direcao = 5
        while(not posicao_valida):
            # Posicao provavelmente nao oferece movimento valido
            if direcao == 0 and count > 1000:
                break
            direcao = random.randint(1, 9)
            while direcao == 5:
                direcao = random.randint(1, 9)
            nova_posicao = self.calcula_nova_posicao(direcao)

            if 0 <= nova_posicao[0] < tamanho_matriz and 0 <= nova_posicao[1] < tamanho_matriz and labirinto[nova_posicao[0]][nova_posicao[1]] != "1":
                posicao_valida = True
            else:
                count += 1
                direcao = 0

        return direcao

    def movimenta(self, direcao):
        self.posicao_anterior = self.posicao
        self.posicao = self.calcula_nova_posicao(direcao)
        if self.visitados[self.posicao[0]][self.posicao[1]] != '$':
            self.visitados[self.posicao[0]][self.posicao[1]] = '$'
        if labirinto[self.posicao[0]][self.posicao[1]] == 'S':
            self.encontrar_saida()

    def encontrar_saida(self):
        self.saida = list(self.posicao)
        self.encontrou_saida = True
        global alguem_achou_saida
        alguem_achou_saida = True

    def heuristica(self):
        if not self.encontrou_saida:
            aptidao = math.sqrt(
                math.pow(self.posicao[0], 2) + math.pow(self.posicao[1], 2))
        else:
            aptidao = maximo_passos - \
                len(self.passos) + math.sqrt(2*math.pow(tamanho_matriz, 2))
        return aptidao

    def imprime_setas(self):
        matriz_direcoes = []
        for i in range(tamanho_matriz):
            linha_nova = []
            for j in range(tamanho_matriz):
                linha_nova.append(self.movimentos[self.direcoes[i][j]][2])
            matriz_direcoes.append(linha_nova)
        return matriz_direcoes

    def __str__(self):
        to_string = "----------------------------------------------------------------\n"

        to_string += ("Cromossomo " + str(self.nome) + "\n")
        for i in range(tamanho_matriz):
            to_string += str(self.visitados[i]) + \
                " - " + str(self.imprime_setas()[i]) + "\n"
        to_string += ("Heurística: " + str(self.heuristica()) + " - Posição: " + str(self.posicao) +
                      " - Encontrou: " + str(self.encontrou_saida) + " - Onde: " + str(self.saida) + " - Passos: " + str(len(self.passos)))
        return to_string.replace("'", "").replace(",", "")


def cruza_cromossomos(c1, c2):
    filho_1 = Cromossomo()
    filho_2 = Cromossomo()

    mascara = gera_mascara()

    for i in range(tamanho_matriz):
        for j in range(tamanho_matriz):
            if mascara[i][j] == 1:
                filho_1.direcoes[i][j] = c1.direcoes[i][j]
                filho_2.direcoes[i][j] = c2.direcoes[i][j]
            else:
                filho_1.direcoes[i][j] = c2.direcoes[i][j]
                filho_2.direcoes[i][j] = c1.direcoes[i][j]

    return filho_1, filho_2

def gera_mascara():
    mascara = []
    for i in range(tamanho_matriz):
        linha_nova = []
        for j in range(tamanho_matriz):
            linha_nova.append(random.randint(0, 1))
        mascara.append(linha_nova)
    return mascara

def inicializa_populacao():
    populacao_inicial = []
    for i in range(TAM_POPULACAO_INICIAL):
        populacao_inicial.append(Cromossomo())
    return populacao_inicial

def executa_geracao(populacao):
    global alguem_achou_saida
    alguem_achou_saida = False

    for i in range(TAM_POPULACAO_INICIAL):
        populacao[i].executa()
    populacao.sort(key=lambda c: c.heuristica(), reverse=True)
    global melhor

    if (melhor == None) or (populacao[0].heuristica() > melhor.heuristica()):
        melhor = copy.copy(populacao[0])

    imprime_labirinto()
    imprime_populacao(populacao)

    global mutacao
    if alguem_achou_saida:
        mutacao = MUTACAO_MINIMA
    else:
        mutacao += 5

    if mutacao < MUTACAO_MINIMA:
        mutacao = MUTACAO_MINIMA
    if mutacao > MUTACAO_MAXIMA:
        mutacao = MUTACAO_MAXIMA

def nova_geracao(populacao):
    logar("----------------------------------------------------------------")

    p = []

    for i in range(ELITISMO):
        p.append(populacao[i])
        logar("-> Elitismo - Carregando " + str(populacao[i].nome))

    for t in range(TORNEIO):

        i = random.randint(0, len(populacao)-1)
        c_temp1 = populacao[i]
        i = random.randint(0, len(populacao)-1)
        c_temp2 = populacao[i]
        c1 = c_temp1 if c_temp1.heuristica() > c_temp2.heuristica() else c_temp2
        populacao.remove(c1)

        i = random.randint(0, len(populacao)-1)
        c_temp1 = populacao[i]
        i = random.randint(0, len(populacao)-1)
        c_temp2 = populacao[i]
        c2 = c_temp1 if c_temp1.heuristica() > c_temp2.heuristica() else c_temp2
        populacao.remove(c2)

        logar("-> Torneio " + str(t) + " - Cruzando: " +
              str(c1.nome) + " e " + str(c2.nome))

        filho_1, filho_2 = cruza_cromossomos(c1, c2)
        p.append(filho_1)
        p.append(filho_2)

    return p

def logar(s):
    if LOG_COMPLETO:
        print(s)

def logar_simples(populacao):
    m = populacao[0]
    print("-> Melhor Atual - Geracao: " + str(contador_geracoes) + " - Melhor: Cromossomo " + str(m.nome) + " - Aptidão: " +
          str(m.heuristica()) + " - Encontrou: " + str(m.encontrou_saida) + " - Passos: " + str(len(m.passos)))
    print("-> Melhor Global - Geracao: " + str(contador_geracoes) + " - Melhor: Cromossomo " + str(melhor.nome) + " - Aptidão: " +
          str(melhor.heuristica()) + " - Encontrou: " + str(melhor.encontrou_saida) + " - Passos: " + str(len(melhor.passos)))

def imprime_labirinto():
    logar("----------------------------------------------------------------")
    logar("Labirinto: ")

    for i in range(tamanho_matriz):
        logar(str(labirinto[i]).replace("'", "").replace(",", ""))

def imprime_populacao(populacao):
    for i in range(TAM_POPULACAO_INICIAL):
        logar(populacao[i])

if __name__ == "__main__":
    main()
