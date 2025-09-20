import heapq

a = 87
c = 161
m = 4894967296
x = 1
l = 100000

numeros_teste = None


if numeros_teste is not None:
    print("MODO TESTE ATIVO - Usando array de números específicos")
    gerador = None
else:
    import gerador
    print("MODO NORMAL - Usando gerador congruencial linear")

def obter_proximo_numero():
    global x, indice_teste, numeros_usados, rng_esgotado
    if numeros_teste is not None:
        if indice_teste >= len(numeros_teste):
            rng_esgotado = True
            return None
        u = numeros_teste[indice_teste]
        indice_teste += 1
        numeros_usados += 1
        if indice_teste >= len(numeros_teste):
            rng_esgotado = True
        return u
    else:
        if gerador is None:
            raise RuntimeError("Gerador indisponível.")
        if numeros_usados >= l:
            rng_esgotado = True
            return None
        x = gerador.gerar(a, c, m, x)
        u = x / m
        numeros_usados += 1
        if numeros_usados >= l:
            rng_esgotado = True
        return u

def uniforme(a_, b_, u_):
    return a_ + ((b_ - a_) * u_)

PRIMEIRA_CHEGADA = 2.0
FILAS       = 3
SERVIDORES  = [1, 2, 2]
CAPACIDADES = [1000, 5, 10]
CHEG_MIN, CHEG_MAX   = 2.0, 4.0
SERV1_MIN, SERV1_MAX = 1.0, 2.0
SERV2_MIN, SERV2_MAX = 4.0, 8.0
SERV3_MIN, SERV3_MAX = 5.0, 15.0

P = [
    [(1, 0.8), (2, 0.2)],
    [(0, 0.3), (1, 0.5), (-1, 0.2)],
    [(2, 0.7), (-1, 0.3)],
]

def testa_passagem(fila_origem):
    u = obter_proximo_numero()
    if u is None:
        return None
    acc = 0.0
    for destino, p in P[fila_origem]:
        acc += p
        if u <= acc:
            return destino
    return P[fila_origem][-1][0]

tempo_atual      = 0.0
em_servico       = [0 for _ in range(FILAS)]
fila             = [0 for _ in range(FILAS)]
eventos          = []
clientes_servidos = [0 for _ in range(FILAS)]
clientes_perdidos = [0 for _ in range(FILAS)]
PRIO = {'SAIDA': 0, 'CHEGADA': 1}

indice_teste   = 0
numeros_usados = 0
rng_esgotado   = False

tempo_por_n     = [[0.0 for _ in range(CAPACIDADES[i] + 1)] for i in range(FILAS)]
tempo_anterior  = 0.0
n_anterior      = [0 for _ in range(FILAS)]

chegadas_externas = 0

# ==== Medição ====
def acumula_tempo():
    global tempo_anterior
    dt = tempo_atual - tempo_anterior
    if dt <= 0:
        return
    for i in range(FILAS):
        n = em_servico[i] + fila[i]
        if 0 <= n <= CAPACIDADES[i]:
            tempo_por_n[i][n] += dt

def atualiza_estado():
    global tempo_anterior, n_anterior
    tempo_anterior = tempo_atual
    for i in range(FILAS):
        n_anterior[i] = em_servico[i] + fila[i]

# ==== Dinâmica ====
def agenda_servico(fila_idx):
    u = obter_proximo_numero()
    if u is None:
        return False
    if fila_idx == 0:
        t = uniforme(SERV1_MIN, SERV1_MAX, u)
    elif fila_idx == 1:
        t = uniforme(SERV2_MIN, SERV2_MAX, u)
    else:
        t = uniforme(SERV3_MIN, SERV3_MAX, u)
    heapq.heappush(eventos, (tempo_atual + t, 'SAIDA', fila_idx, False))
    return True

def trata_chegada(fila_idx, externa):
    global clientes_perdidos, clientes_servidos, em_servico, fila, chegadas_externas

    n_atual = em_servico[fila_idx] + fila[fila_idx]
    if n_atual <= CAPACIDADES[fila_idx]:
        if em_servico[fila_idx] < SERVIDORES[fila_idx]:
            em_servico[fila_idx] += 1
            ok = agenda_servico(fila_idx)
            if not ok:
                # rollback se RNG acabou
                em_servico[fila_idx] -= 1
                clientes_servidos[fila_idx] -= 1
        else:
            fila[fila_idx] += 1
    else:
        clientes_perdidos[fila_idx] += 1

    # chegadas externas só para Q1
    if externa and fila_idx == 0 and not rng_esgotado:
        u = obter_proximo_numero()
        if u is not None:
            t_entre = uniforme(CHEG_MIN, CHEG_MAX, u)
            heapq.heappush(eventos, (tempo_atual + t_entre, 'CHEGADA', 0, True))
            chegadas_externas += 1

def trata_saida(fila_idx):
    global em_servico, fila, clientes_servidos
    if em_servico[fila_idx] > 0:
        em_servico[fila_idx] -= 1
        clientes_servidos[fila_idx] += 1

    # coloca próximo da fila em serviço
    if fila[fila_idx] > 0 and not rng_esgotado:
        fila[fila_idx] -= 1
        em_servico[fila_idx] += 1
        if not agenda_servico(fila_idx):
            # não consegue agendar, desfaz
            em_servico[fila_idx] -= 1
            clientes_servidos[fila_idx] -= 1
            return

    if not rng_esgotado:
        destino = testa_passagem(fila_idx)
        if destino is None:
            return
        if destino >= 0 and destino < FILAS:
            heapq.heappush(eventos, (tempo_atual, 'CHEGADA', destino, False))

# ==== Execução ====
print("=== SIMULAÇÃO: 3 FILAS COM ROTEAMENTO ===")
print("Q1: G/G/1, serviço 1..2; chegadas externas 2..4")
print("Q2: G/G/2/5, serviço 4..8; roteia 0.3->Q1, 0.5->Q2, 0.2->SAÍDA")
print("Q3: G/G/2/10, serviço 5..15; roteia 0.7->Q3, 0.3->SAÍDA")
print("=" * 55)

heapq.heappush(eventos, (PRIMEIRA_CHEGADA, 'CHEGADA', 0, True))
tempo_anterior = 0.0
for i in range(FILAS):
    n_anterior[i] = 0

while eventos:
    if rng_esgotado:
        break
    tempo_atual, tipo, fila_idx, externa = heapq.heappop(eventos)
    acumula_tempo()
    if tipo == 'CHEGADA':
        trata_chegada(fila_idx, externa)
    elif tipo == 'SAIDA':
        trata_saida(fila_idx)
    atualiza_estado()

acumula_tempo()

# ==== Resultados ====
print(f"\nNúmeros usados: {numeros_usados}")
print(f"Chegadas externas geradas: {chegadas_externas}")
print(f"Tempo final: {tempo_atual:.4f}")
print("=" * 55)

for idx in range(FILAS):
    tempo_total = sum(tempo_por_n[idx])
    if tempo_total > 0:
        prob_por_n = [(t/tempo_total) for t in tempo_por_n[idx]]
        EN = sum(n * prob_por_n[n] for n in range(len(prob_por_n)))
    else:
        prob_por_n = [0.0] * (CAPACIDADES[idx] + 1)
        EN = 0.0

    print(f"\nFila {idx+1}: G/G/{SERVIDORES[idx]}/{CAPACIDADES[idx]}")
    if idx == 0:
        print("Chegadas: 2.0 - 4.0 | Serviço: 1.0 - 2.0")
    elif idx == 1:
        print("Serviço: 4.0 - 8.0")
    else:
        print("Serviço: 5.0 - 15.0")
    print("-" * 40)
    print(f"Servidos: {clientes_servidos[idx]}  Perdidos: {clientes_perdidos[idx]}")
    print(f"Tempo acumulado: {tempo_total:.4f}")
    print("Probabilidades por estado:")
    for n, p in enumerate(prob_por_n):
        if p > 0:
            print(f"  N={n}: {p:.4f} ({p:.2%})")
    print(f"E[N]={EN:.4f}")

print("\n" + "="*55)
print(f"Tempo global: {tempo_atual:.4f}")
print(f"Total de números aleatórios: {numeros_usados}")
print("="*55)
