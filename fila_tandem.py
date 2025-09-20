import heapq

a = 87
c = 161
m = 4894967296
x = 1
l = 100000

numeros_teste = [0.9312, 0.1231, 0.7745, 0.2850, 0.6598, 0.4821, 0.3987, 0.2104, 0.5432, 0.8891,
                0.3765, 0.6217, 0.0953, 0.8142, 0.4528, 0.1376, 0.9683, 0.7049, 0.2507, 0.5804]

if numeros_teste is not None:
    print("MODO TESTE ATIVO - Usando array de números específicos")
    gerador = None
else:
    import gerador
    print("MODO NORMAL - Usando gerador congruencial linear")

def uniforme(a_, b_, u_):
    return a_ + ((b_ - a_) * u_)

PRIMEIRA_CHEGADA = 2.0
FILAS       = 2
SERVIDORES  = [2, 1]
CAPACIDADES = [3, 5]
CHEG_MIN,  CHEG_MAX  = 1.0, 4.0
SERV_MIN,  SERV_MAX  = 3.0, 4.0
SERV2_MIN, SERV2_MAX = 2.0, 3.0


tempo_atual      = 0.0
em_servico       = [0 for _ in range(FILAS)]
fila             = [0 for _ in range(FILAS)]
eventos          = []
clientes_servidos = [0 for _ in range(FILAS)]
clientes_perdidos = [0 for _ in range(FILAS)]

indice_teste   = 0
numeros_usados = 0
rng_esgotado   = False

tempo_por_n     = [[0.0 for _ in range(CAPACIDADES[i] + 1)] for i in range(FILAS)]
tempo_anterior  = 0.0
n_anterior      = [0 for _ in range(FILAS)]

indice_chegadas_externas = 0

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

def acumula_tempo():
    global tempo_anterior
    dt = tempo_atual - tempo_anterior
    if dt <= 0:
        return
    for i in range(FILAS):
        n = n_anterior[i]
        if 0 <= n <= CAPACIDADES[i]:
            tempo_por_n[i][n] += dt

def atualiza_estado():
    global tempo_anterior, n_anterior
    tempo_anterior = tempo_atual
    for i in range(FILAS):
        n_anterior[i] = em_servico[i] + fila[i]

def trata_chegada(fila_idx):
    global clientes_perdidos, clientes_servidos, em_servico, fila, indice_chegadas_externas

    n_atual = em_servico[fila_idx] + fila[fila_idx]

    if n_atual <= CAPACIDADES[fila_idx]:
        if em_servico[fila_idx] < SERVIDORES[fila_idx]:
            em_servico[fila_idx] += 1
            clientes_servidos[fila_idx] += 1

            u = obter_proximo_numero()
            if u is None:
                em_servico[fila_idx] -= 1
                clientes_servidos[fila_idx] -= 1
                return
            if fila_idx == 0:
                tempo_serv = uniforme(SERV_MIN, SERV_MAX, u)
            else:
                tempo_serv = uniforme(SERV2_MIN, SERV2_MAX, u)
            heapq.heappush(eventos, (tempo_atual + tempo_serv, 'SAIDA', fila_idx))
        else:
            fila[fila_idx] += 1
    else:
        clientes_perdidos[fila_idx] += 1

    if fila_idx == 0 and not rng_esgotado:
        u = obter_proximo_numero()
        if u is not None:
            t_entre = uniforme(CHEG_MIN, CHEG_MAX, u)
            heapq.heappush(eventos, (tempo_atual + t_entre, 'CHEGADA', 0))
            indice_chegadas_externas += 1

def trata_saida(fila_idx):
    global em_servico, fila, clientes_servidos

    if em_servico[fila_idx] > 0:
        em_servico[fila_idx] -= 1

    if fila[fila_idx] > 0 and not rng_esgotado:
        u = obter_proximo_numero()
        if u is None:
            return
        fila[fila_idx] -= 1
        em_servico[fila_idx] += 1
        clientes_servidos[fila_idx] += 1

        if fila_idx == 0:
            tempo_serv = uniforme(SERV_MIN, SERV_MAX, u)
        else:
            tempo_serv = uniforme(SERV2_MIN, SERV2_MAX, u)

        heapq.heappush(eventos, (tempo_atual + tempo_serv, 'SAIDA', fila_idx))

def trata_passagem(fila_origem):
    fila_destino = fila_origem + 1
    if fila_destino < FILAS:
        heapq.heappush(eventos, (tempo_atual, 'CHEGADA', fila_destino))


print("=== SIMULAÇÃO DE FILAS EM TANDEM ===")
print("Fila 1: G/G/2/3 (chegadas 1-4, serviço 3-4)")
print("Fila 2: G/G/1/5 (serviço 2-3)")
print("Primeiro cliente chega no tempo " + str(PRIMEIRA_CHEGADA))
print("=" * 45)

tempo_anterior = 0.0
for i in range(FILAS):
    n_anterior[i] = 0

heapq.heappush(eventos, (PRIMEIRA_CHEGADA, 'CHEGADA', 0))

while eventos:
    if rng_esgotado:
        break

    tempo_atual, tipo, fila_idx = heapq.heappop(eventos)

    acumula_tempo()

    if tipo == 'CHEGADA':
        trata_chegada(fila_idx)
    elif tipo == 'SAIDA':
        trata_saida(fila_idx)
        if fila_idx == 0:
            trata_passagem(fila_idx)

    atualiza_estado()

acumula_tempo()

# Resultados
print(f"\n*** ESTATÍSTICAS DA SIMULAÇÃO ***")
print(f"Números aleatórios usados: {numeros_usados}")
print(f"Clientes chegaram na fila 1: {indice_chegadas_externas}")
print(f"Tempo final de simulação: {tempo_atual:.4f}")
if numeros_teste is not None:
    print("*** SIMULAÇÃO FINALIZADA: Array de números teste esgotado ***")
else:
    if numeros_usados >= l:
        print("*** SIMULAÇÃO COMPLETADA: 100.000 números aleatórios utilizados ***")
print("*" * 50)

print("\n" + "="*60)
print("                    RESULTADOS DA SIMULAÇÃO")
print("="*60)

for idx in range(FILAS):
    tempo_total = sum(tempo_por_n[idx])
    if tempo_total > 0:
        prob_por_n = [(t/tempo_total) for t in tempo_por_n[idx]]
        populacao_media = sum(n * prob_por_n[n] for n in range(len(prob_por_n)))
    else:
        prob_por_n = [0.0] * (CAPACIDADES[idx] + 1)
        populacao_media = 0.0

    print(f"\nFila {idx+1}: G/G/{SERVIDORES[idx]}/{CAPACIDADES[idx]}")
    if idx == 0:
        print("Chegadas: 1.0 - 4.0 min | Serviço: 3.0 - 4.0 min")
    else:
        print("Serviço: 2.0 - 3.0 min")
    print("-" * 50)

    print(f"Clientes servidos: {clientes_servidos[idx]}")
    print(f"Clientes perdidos: {clientes_perdidos[idx]}")
    print(f"Tempo acumulado total: {tempo_total:.4f} minutos")

    print("\nDistribuição de probabilidades por estado:")
    for n, p in enumerate(prob_por_n):
        if p > 0:
            print(f"  Estado {n}: {p:.4f} ({p:.2%})")

    print(f"População média E[N]: {populacao_media:.4f}")

print("\n" + "="*60)
print(f"Tempo global da simulação: {tempo_atual:.4f} minutos")
print(f"Total de números aleatórios utilizados: {numeros_usados}")
print("="*60)
