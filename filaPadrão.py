import heapq

def uniforme(a, b, x):
    return a + (b - a) * x

numeros = [0.6, 0.8, 0.3, 0.7, 0.4, 0.1]

tempo_atual = 0.0
proxima_chegada = 1.0
ocupados = 0
eventos = []
clientes_servidos = 0
clientes_perdidos = 0

eventos_ocorridos = []
saida_clientes = []

heapq.heappush(eventos, (proxima_chegada, 'CHEGADA'))
indice = 0

while eventos and indice < len(numeros):
    eventos_ocorridos.append((tempo_atual, ocupados))
    tempo_atual, evento = heapq.heappop(eventos)

    if evento == 'CHEGADA':
        print(f"[{tempo_atual:.2f}] Evento: CHEGADA")

        if ocupados < 2:
            ocupados += 1
            clientes_servidos += 1

            tempo_servico = uniforme(1.0, 4.0, numeros[indice])
            indice += 1

            tempo_saida = tempo_atual + tempo_servico
            heapq.heappush(eventos, (tempo_saida, 'SAIDA'))

            print(f"  → Início do atendimento. Tempo de serviço: {tempo_servico:.2f}. Saída prevista: {tempo_saida:.2f}")
        else:
            clientes_perdidos += 1
            print(f"  → Capacidade cheia! Cliente perdido.")

        if indice < len(numeros):
            tempo_entre_chegadas = uniforme(1.0, 3.0, numeros[indice])
            indice += 1

            proxima_chegada = tempo_atual + tempo_entre_chegadas
            heapq.heappush(eventos, (proxima_chegada, 'CHEGADA'))
            print(f"  → Próxima chegada agendada para: {proxima_chegada:.2f}")

    elif evento == 'SAIDA':
        ocupados -= 1
        print(f"[{tempo_atual:.2f}] Evento: SAIDA")
        saida_clientes.append(tempo_atual)

eventos_ocorridos.append((tempo_atual, ocupados))

tempo_vazio = 0.0
tempo_com_um = 0.0
tempo_total = 0.0
soma_populacao_peso = 0.0

for i in range(1, len(eventos_ocorridos)):
    t0, n0 = eventos_ocorridos[i - 1]
    t1, _ = eventos_ocorridos[i]
    dt = t1 - t0
    tempo_total += dt
    soma_populacao_peso += n0 * dt
    if n0 == 0:
        tempo_vazio += dt
    elif n0 == 1:
        tempo_com_um += dt

prob_vazio = tempo_vazio / tempo_total if tempo_total else 0
populacao_media = soma_populacao_peso / tempo_total if tempo_total else 0

print("\n--- Resultados ---")
print(f"Clientes atendidos: {clientes_servidos}")
print(f"Clientes perdidos: {clientes_perdidos}")
print(f"Tempos de saída: {[round(t, 2) for t in saida_clientes]}")

print("\n--- Métricas da Fila ---")
print(f"Tempo total simulado: {tempo_total:.2f} minutos")
print(f"Probabilidade da fila estar vazia: {prob_vazio:.2%}")
print(f"Tempo com apenas 1 cliente: {tempo_com_um:.2f} minutos")
print(f"População média da fila: {populacao_media:.2f}")
