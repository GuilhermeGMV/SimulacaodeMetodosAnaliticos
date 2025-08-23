import heapq
import gerador

def uniforme(a, b, u):
    return a + ((b - a) * u)

SERVIDORES = 2
CAPACIDADE = 5
CHEG_MIN, CHEG_MAX = 2.0, 5.0
SERV_MIN, SERV_MAX = 3.0, 5.0


tempo_atual = 0.0
proxima_chegada = 1.0
em_servico = 0
fila = 0
eventos = []
clientes_servidos = 0
clientes_perdidos = 0

a = 87
c = 161
m = 4894967296
x = 1
xs = []

eventos_ocorridos = []

heapq.heappush(eventos, (proxima_chegada, 'CHEGADA'))
indice = 0
l = 100000
saida_clientes = []

while eventos and indice <= l:
    xs.append(x / m)
    n_atual = em_servico + fila
    eventos_ocorridos.append((tempo_atual, n_atual))

    tempo_atual, evento = heapq.heappop(eventos)

    if evento == 'CHEGADA':
        n_atual = em_servico + fila
        if n_atual < CAPACIDADE:
            if em_servico < SERVIDORES:
                em_servico += 1
                clientes_servidos += 1
                x = gerador.gerar(a, c, m, x)
                tempo_servico = uniforme(SERV_MIN, SERV_MAX, x / m)
                indice += 1
                tempo_saida = tempo_atual + tempo_servico
                heapq.heappush(eventos, (tempo_saida, 'SAIDA'))
            else:
                fila += 1
        else:
            clientes_perdidos += 1

        if indice < l:
            x = gerador.gerar(a, c, m, x)
            tempo_entre_chegadas = uniforme(CHEG_MIN, CHEG_MAX, x / m)
            indice += 1
            proxima_chegada = tempo_atual + tempo_entre_chegadas
            heapq.heappush(eventos, (proxima_chegada, 'CHEGADA'))

    elif evento == 'SAIDA':
        saida_clientes.append(tempo_atual)
        if fila > 0:
            fila -= 1
            clientes_servidos += 1
            x = gerador.gerar(a, c, m, x)
            tempo_servico = uniforme(SERV_MIN, SERV_MAX, x / m)
            indice += 1
            tempo_saida = tempo_atual + tempo_servico
            heapq.heappush(eventos, (tempo_saida, 'SAIDA'))
        else:
            em_servico -= 1

eventos_ocorridos.append((tempo_atual, em_servico + fila))

tempo_total = 0.0
tempo_por_n = [0.0 for _ in range(CAPACIDADE + 1)]
soma_populacao_peso = 0.0

for i in range(1, len(eventos_ocorridos)):
    t0, n0 = eventos_ocorridos[i - 1]
    t1, _  = eventos_ocorridos[i]
    dt = t1 - t0
    if dt < 0:
        continue
    tempo_total += dt
    soma_populacao_peso += n0 * dt
    if 0 <= n0 <= CAPACIDADE:
        tempo_por_n[n0] += dt

prob_por_n = [ (t/tempo_total if tempo_total else 0.0) for t in tempo_por_n ]
populacao_media = soma_populacao_peso / tempo_total if tempo_total else 0.0

print(f"\n--- Resultados (G/G/{SERVIDORES}/{CAPACIDADE}) ---")
print(f"Clientes servidos (iniciaram serviço): {clientes_servidos}")
print(f"Clientes perdidos (sistema cheio): {clientes_perdidos}")

print("\n--- Métricas da Fila ---")
print(f"Tempo total simulado: {tempo_total:.2f} minutos")
for n, p in enumerate(prob_por_n):
    print(f"P[n={n}] = {p:.2%}")
print(f"População média do sistema E[N]: {populacao_media:.3f}")