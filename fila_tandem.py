import heapq
import gerador

def uniforme(a, b, u):
    return a + ((b - a) * u)

FILAS = 2
SERVIDORES = [2, 1]
CAPACIDADES = [3, 5]
CHEG_MIN, CHEG_MAX = 1.0, 4.0
SERV_MIN, SERV_MAX = 3.0, 4.0
SERV2_MIN, SERV2_MAX = 2.0, 3.0

tempo_atual = 0.0
proxima_chegada = 1.5
em_servico = [0 for _ in range(FILAS)]
fila = [0 for _ in range(FILAS)]
eventos = []
clientes_servidos = [0 for _ in range(FILAS)]
clientes_perdidos = [0 for _ in range(FILAS)]

a = 87
c = 161
m = 4894967296
x = 1
l = 100000
indice = 0

heapq.heappush(eventos, (proxima_chegada, 'CHEGADA', 0)) 

saida_clientes = [[] for _ in range(FILAS)]
eventos_ocorridos = [[] for _ in range(FILAS)]

while eventos and indice <= l:
    tempo_atual, evento, fila_idx = heapq.heappop(eventos)
    n_atual = em_servico[fila_idx] + fila[fila_idx]
    eventos_ocorridos[fila_idx].append((tempo_atual, n_atual))

    if evento == 'CHEGADA':
        if n_atual < CAPACIDADES[fila_idx]:
            if em_servico[fila_idx] < SERVIDORES[fila_idx]:
                em_servico[fila_idx] += 1
                clientes_servidos[fila_idx] += 1
                x = gerador.gerar(a, c, m, x)
                if fila_idx == 0:
                    tempo_servico = uniforme(SERV_MIN, SERV_MAX, x / m)
                else:
                    tempo_servico = uniforme(SERV2_MIN, SERV2_MAX, x / m)
                tempo_saida = tempo_atual + tempo_servico
                heapq.heappush(eventos, (tempo_saida, 'SAIDA', fila_idx))
            else:
                fila[fila_idx] += 1
        else:
            clientes_perdidos[fila_idx] += 1

        if fila_idx == 0 and indice < l:
            x = gerador.gerar(a, c, m, x)
            tempo_entre_chegadas = uniforme(CHEG_MIN, CHEG_MAX, x / m)
            proxima_chegada = tempo_atual + tempo_entre_chegadas
            heapq.heappush(eventos, (proxima_chegada, 'CHEGADA', 0))
            indice += 1

    elif evento == 'SAIDA':
        saida_clientes[fila_idx].append(tempo_atual)
        if fila[fila_idx] > 0:
            fila[fila_idx] -= 1
            clientes_servidos[fila_idx] += 1
            x = gerador.gerar(a, c, m, x)
            if fila_idx == 0:
                tempo_servico = uniforme(SERV_MIN, SERV_MAX, x / m)
            else:
                tempo_servico = uniforme(SERV2_MIN, SERV2_MAX, x / m)
            tempo_saida = tempo_atual + tempo_servico
            heapq.heappush(eventos, (tempo_saida, 'SAIDA', fila_idx))
        else:
            em_servico[fila_idx] -= 1
        if fila_idx + 1 < FILAS:
            heapq.heappush(eventos, (tempo_atual, 'CHEGADA', fila_idx + 1))

for idx in range(FILAS):
    eventos_fila = eventos_ocorridos[idx]
    tempo_total = 0.0
    soma_populacao_peso = 0.0
    CAP = CAPACIDADES[idx]
    tempo_por_n = [0.0 for _ in range(CAP + 1)]

    for i in range(1, len(eventos_fila)):
        t0, n0 = eventos_fila[i-1]
        t1, _ = eventos_fila[i]
        dt = t1 - t0
        tempo_total += dt
        soma_populacao_peso += n0 * dt
        if 0 <= n0 <= CAP:
            tempo_por_n[n0] += dt

    prob_por_n = [ (t/tempo_total if tempo_total else 0.0) for t in tempo_por_n ]
    populacao_media = soma_populacao_peso / tempo_total if tempo_total else 0.0

    print(f"\n--- Resultados Fila {idx+1} (G/G/{SERVIDORES[idx]}/{CAPACIDADES[idx]}) ---")
    print(f"Clientes servidos (iniciaram serviço): {clientes_servidos[idx]}")
    print(f"Clientes perdidos (sistema cheio): {clientes_perdidos[idx]}")
    print("\n--- Métricas da Fila ---")
    print(f"Tempo total simulado: {tempo_total:.2f} minutos")
    for n, p in enumerate(prob_por_n):
        print(f"P[n={n}] = {p:.2%}")
    print(f"População média do sistema E[N]: {populacao_media:.3f}")
