import random
import math

def main():

    f = open("labirinto1_10.txt", "r")

    tamanho_matriz = int(f.readline())

    # Labirinto conforme no arquivo de entrada
    # [0]: informacao original - E: entrada - S: saída - 0: pode andar - 1: parede
    labirinto = []
    for i in range(tamanho_matriz):
        labirinto.append(f.readline().split())

    cromossomo = Cromossomo(labirinto, tamanho_matriz)

    # cromossomo.visitados[0][0] = 9

    print(cromossomo)

    POPULACAO_INICIAL=10        
    MUTACAO=0.5
    PREFERENCIA_NOVO=0.2

    cromossomo.executa()
    print(cromossomo)

class Cromossomo:
    def __init__(self, labirinto, tamanho_matriz):
        self.tamanho_matriz = tamanho_matriz
        self.labirinto = labirinto
        self.posicao = (0,0)
        self.posicao_anterior = (0,0)

        self.tentativas = 1000
        self.ultimo_caminho = []
        self.percentual_mutacao = 20
        
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

        self.encontrou_saida = False
        

    def cria_visitados(self):
        matriz = [[0 for col in range(self.tamanho_matriz)] for row in range(self.tamanho_matriz)]
        for i in range(self.tamanho_matriz):
            for j in range(self.tamanho_matriz):
                matriz[i][j] = 0 if self.labirinto[i][j] != "1" else 1

        # Marca entrada como 1, supondo entrada sempre (0,0)
        matriz[0][0] = 1
        return matriz

    def cria_direcoes(self):
        direcoes = [[0 for col in range(self.tamanho_matriz)] for row in range(self.tamanho_matriz)]
        for i in range(self.tamanho_matriz):
            for j in range(self.tamanho_matriz):
                if self.labirinto[i][j] != '1':
                    self.posicao = (i,j)
                    direcoes[i][j] = self.nova_direcao()
        self.posicao = (0,0)
        self.posicao_anterior = (0,0)
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

    def executa(self):

        for i in range(self.tentativas):
            print(i, str(self.posicao))
            if(self.deve_mudar_direcao()):
                direcao = self.nova_direcao()
                self.direcoes[self.posicao[0]][self.posicao[1]] = direcao
            else:
                direcao = self.direcoes[self.posicao[0]][self.posicao[1]]

            self.movimenta(direcao)

    def deve_mudar_direcao(self):
        # Campo sem direção ainda
        if self.direcoes[self.posicao[0]][self.posicao[1]] == 0:
            return True
        
        # Mutação
        elif random.randrange(100) < self.percentual_mutacao:
            return True
        return False

    def nova_direcao(self):
        posicao_valida = False
        direcao = 5
        while(not posicao_valida):
            direcao = random.randint(1,9)
            while direcao == 5:
                direcao = random.randint(1,9)
            nova_posicao = self.calcula_nova_posicao(direcao)

            if 0 <= nova_posicao[0] < self.tamanho_matriz and 0 <= nova_posicao[1] < self.tamanho_matriz:
                if self.labirinto[nova_posicao[0]][nova_posicao[1]] != "1":
                    posicao_valida = True

        return direcao

    def movimenta(self, direcao):
        self.posicao_anterior = self.posicao
        self.posicao = self.calcula_nova_posicao(direcao)

    def heuristica(self):
        return math.sqrt(math.pow(self.posicao[0], 2) + math.pow(self.posicao[1], 2))

    def __str__(self):
        to_string = ""
        for i in range(self.tamanho_matriz):
            to_string += str(self.labirinto[i]) + " - " + str(self.visitados[i]) + " - " + str(self.direcoes[i]) + "\n"
        to_string += "Heurística: " + str(self.heuristica()) + " - Posição: " + str(self.posicao) + " - Encontrou: " + str(self.encontrou_saida)
        return to_string

def replica_direcoes(c1, c2, linha_inicial, linha_final):
    n = c1.tamanho_matriz
    for i in range(linha_inicial, n):
        for j in range(n):
            c2.direcoes[i][j] = c1.direcoes[i][j]

def cruza_cromossomos(c1, c2):
    n = c1.tamanho_matriz
    filho_1 = Cromossomo(c1.labirinto, c1.tamanho_matriz)
    filho_2 = Cromossomo(c1.labirinto, c1.tamanho_matriz)
    
    replica_direcoes(c1, filho_1, 0, ((n/2)-1))
    replica_direcoes(c2, filho_1, n/2, n)
    replica_direcoes(c2, filho_2, 0, ((n/2)-1))
    replica_direcoes(c1, filho_2, n/2, n)

if __name__ == "__main__":
    main()