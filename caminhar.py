import random
import math

GERACOES = 20
ELITISMO = 3
TORNEIO = 3
TAM_POPULACAO_INICIAL = ELITISMO + 2*TORNEIO
FATOR_MAXIMO_PASSOS = 2
MUTACAO_MINIMA = 2
MUTACAO_MAXIMA = 50

labirinto = []
tamanho_matriz = 0
maximo_passos = 0

contador_cromossomos = 1

alguem_achou_saida = False
mutacao = MUTACAO_MAXIMA

def main():

    f = open("labirinto4_20.txt", "r")

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
        executa_geracao(populacao)
        populacao = nova_geracao(populacao)



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
        movimentos[1] = [1, -1]
        movimentos[2] = [1, 0]
        movimentos[3] = [1, 1]
        movimentos[4] = [0, -1]
        movimentos[6] = [0, 1]
        movimentos[7] = [-1, -1]
        movimentos[8] = [-1, 0]
        movimentos[9] = [-1, 1]
        return movimentos

    def calcula_nova_posicao(self, direcao):
        diferenca = self.movimentos[direcao]
        return (self.posicao[0] + diferenca[0], self.posicao[1] + diferenca[1])

    def reinicia_cromossomo(self):
        self.visitados = self.cria_visitados()
        self.passos = []
        self.posicao = (0,0)
        self.posicao_anterior = (0,0)
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

    def __str__(self):
        to_string = "----------------------------------------------------------------\n"
                
        to_string += ("Cromossomo " + str(self.nome) + "\n")
        for i in range(tamanho_matriz):
            to_string += str(self.visitados[i]) + \
                " - " + str(self.direcoes[i]) + "\n"
        to_string += ("Heurística: " + str(self.heuristica()) + " - Posição: " + str(self.posicao) +
                      " - Encontrou: " + str(self.encontrou_saida) + " - Onde: " + str(self.saida) + " - Passos: " + str(len(self.passos)))
        return to_string.replace("'", "").replace(",", "")


def replica_direcoes(c1, c2, linha_inicial, linha_final):
    for i in range(linha_inicial, tamanho_matriz):
        for j in range(tamanho_matriz):
            c2.direcoes[i][j] = c1.direcoes[i][j]


def cruza_cromossomos(c1, c2):
    filho_1 = Cromossomo()
    filho_2 = Cromossomo()

    replica_direcoes(c1, filho_1, 0, ((tamanho_matriz//2)-1))
    replica_direcoes(c2, filho_1, tamanho_matriz//2, tamanho_matriz)
    replica_direcoes(c2, filho_2, 0, ((tamanho_matriz//2)-1))
    replica_direcoes(c1, filho_2, tamanho_matriz//2, tamanho_matriz)

    return filho_1, filho_2


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
    p = []
    
    for i in range(ELITISMO):
        p.append(populacao[i])

    for t in range(TORNEIO):
        print("Torneio " + str(t))
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

        filho_1, filho_2 = cruza_cromossomos(c1, c2)
        p.append(filho_1)
        p.append(filho_2)
    
    return p


def imprime_labirinto():
    print("Labirinto: ")

    for i in range(tamanho_matriz):
        print(str(labirinto[i]).replace("'", "").replace(",", ""))

def imprime_populacao(populacao):
    for i in range(TAM_POPULACAO_INICIAL):        
        print(populacao[i])

if __name__ == "__main__":
    main()
