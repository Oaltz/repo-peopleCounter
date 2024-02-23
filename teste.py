import numpy as np
import cv2
import time
import os
from datetime import datetime
import pandas as pd

# Função para calcular o centro de um retângulo
def center(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)
    cx = x + x1
    cy = y + y1
    return cx, cy

# Função para salvar os resultados em um arquivo CSV
def save_results_to_csv(results, csv_file_path):
    df = pd.DataFrame(results, columns=["Data e Hora", "Total", "Subindo", "Descendo"])
    if os.path.exists(csv_file_path):
        df.to_csv(csv_file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(csv_file_path, index=False)

# Pasta para armazenar os resultados
result_folder = "Resultados"

# Cria a pasta se não existir
if not os.path.exists(result_folder):
    os.makedirs(result_folder)

# Inicializa a captura de vídeo a partir de um arquivo
cap = cv2.VideoCapture('teste.mp4')

# Novas dimensões desejadas para o vídeo
new_width = 640
new_height = 480

# Cria um objeto para subtração de fundo
fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()

# Lista para armazenar os objetos detectados
detects = []

# Dicionário para rastrear os IDs dos objetos
object_ids = {}

# ID único inicial
next_object_id = 1

# Posição da linha horizontal de contagem
posL = 250
offset = 30

# Configura as posições iniciais e finais da linha de contagem
xy1 = (40, posL)
xy2 = (600, posL)

# Contadores de passagens
total = 0
up = 0
down = 0

# Tempo máximo de execução em segundos (1 hora)
max_execution_time = 60 * 60  # Uma hora

# Tempo de início
start_time = time.time()

# Nome do arquivo de resultados
result_csv_path = os.path.join(result_folder, "Relatório.csv")

# Lista para armazenar os resultados
all_results = []

# Tempo de início para controle do reset da contagem a cada 1 hora
start_reset_time = time.time()

# Loop principal
while 1:
    # Lê um frame do vídeo
    ret, frame = cap.read()

    # Redimensiona o frame para as novas dimensões
    frame = cv2.resize(frame, (new_width, new_height))

    # Aplica a subtração de fundo
    fgmask = fgbg.apply(frame)

    # Aplica um limiar para binarizar a imagem
    retval, th = cv2.threshold(fgmask, 150, 255, cv2.THRESH_BINARY)

    # Converte o frame para o espaço de cor HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define intervalo de cor laranja
    lower_orange = np.array([0, 100, 100])
    upper_orange = np.array([30, 255, 255])

    # Cria uma máscara para a cor laranja
    mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)

    # Cria um kernel para operações morfológicas
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    # Aplica operações morfológicas para melhorar a detecção
    opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel, iterations=2)

    dilation = cv2.dilate(opening, kernel, iterations=8)

    closing = cv2.morphologyEx(dilation, cv2.MORPH_CLOSE, kernel, iterations=8)
    cv2.imshow('closing', closing)

    cv2.line(frame, xy1, xy2, (255, 0, 0), 3)

    cv2.line(frame, (xy1[0], posL - offset), (xy2[0], posL - offset), (255, 255, 0), 2)

    cv2.line(frame, (xy1[0], posL + offset), (xy2[0], posL + offset), (255, 255, 0), 2)

    _, contours, hierarchy = cv2.findContours(dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    i = 0
    for cnt in contours:
        (x, y, w, h) = cv2.boundingRect(cnt)

        area = cv2.contourArea(cnt)

        # Ajuste da área mínima
        if int(area) > 2000:
            # Calcula o centro do retângulo delimitador
            centro = center(x, y, w, h)

            # Verifica se o centro está na altura da linha de contagem e fora da máscara laranja
            if (
                    centro[1] > posL - offset
                    and centro[1] < posL + offset
                    and mask_orange[centro[1], centro[0]] == 0
            ):
                # Verifica se o objeto já possui um ID
                if i not in object_ids:
                    object_ids[i] = next_object_id
                    next_object_id += 1

                # Adiciona o ID ao centro do objeto
                centro_with_id = (centro[0], centro[1], object_ids[i])

                # Garante que a lista 'detects' tenha comprimento suficiente
                while len(detects) <= i:
                    detects.append([])

                # Verifica a distância para evitar contagem duplicada
                add_object = True
                for (c, l) in enumerate(detects[i]):
                    distance = np.sqrt((centro[0] - l[0]) ** 2 + (centro[1] - l[1]) ** 2)
                    if distance < 20:  # Ajuste a distância conforme necessário
                        add_object = False
                        break

                if add_object:
                    detects[i].append(centro_with_id)

                # Adiciona texto, círculo e retângulo ao frame
                cv2.putText(frame, str(i), (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                cv2.circle(frame, centro, 4, (0, 0, 255), -1)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Atualiza a lista de detecções
                if len(detects) <= i:
                    detects.append([])

                # Verifica se o centro está na altura da linha de contagem
                if centro[1] > posL - offset and centro[1] < posL + offset:
                    # Verifica se o objeto já possui um ID
                    if i not in object_ids:
                        object_ids[i] = next_object_id
                        next_object_id += 1

                    # Adiciona o ID ao centro do objeto
                    centro_with_id = (centro[0], centro[1], object_ids[i])

                    detects[i].append(centro_with_id)
                else:
                    detects[i].clear()
                i += 1

    # Limpa a lista de detecções se nenhum contorno é encontrado
    if i == 0:
        detects.clear()

    i = 0

    # Verifica o cruzamento da linha de contagem
    if len(contours) == 0:
        detects.clear()
    else:
        for detect in detects:
            for (c, l) in enumerate(detect):

                # Conta quando um objeto cruza a linha de contagem
                if detect[c - 1][1] < posL and l[1] > posL:
                    detect.clear()
                    up += 1
                    total += 1
                    cv2.line(frame, xy1, xy2, (0, 255, 0), 5)
                    continue

                if detect[c - 1][1] > posL and l[1] < posL:
                    detect.clear()
                    down += 1
                    total += 1
                    cv2.line(frame, xy1, xy2, (0, 0, 255), 5)
                    continue

                # Desenha linhas conectando os centros dos objetos detectados
                if c > 0:
                    cv2.line(frame, (int(detect[c - 1][0]), int(detect[c - 1][1])), (int(l[0]), int(l[1])), (0, 0, 255), 1)

    # Exibe informações sobre o número total de objetos, subindo e descendo
    cv2.putText(frame, "TOTAL: " + str(total), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
    cv2.putText(frame, "SUBINDO: " + str(up), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.putText(frame, "DESCENDO: " + str(down), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Exibe o frame resultante
    cv2.imshow("frame", frame)

    # Verifica se a tecla 'q' foi pressionada para encerrar o loop
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

    # Verifica o tempo de execução
    current_time = time.time()
    elapsed_time = current_time - start_time

    # Se o tempo de execução exceder o limite, exibe os resultados, salva e reinicia o loop
    if elapsed_time > max_execution_time:
        # Exibe os resultados finais
        print("Tempo total de execução:", elapsed_time)
        print("Total de pessoas subindo:", up)
        print("Total de pessoas descendo:", down)

        # Adiciona os resultados à lista
        current_timestamp = datetime.now()
        partial_result = [current_timestamp, total, up, down]

        # Salva os resultados em um arquivo CSV com o nome "Relatório.csv"
        save_results_to_csv([partial_result], result_csv_path)

        # Reinicia o tempo de início e o tempo de reset
        start_time = time.time()
        start_reset_time = time.time()

        # Reinicia os contadores
        total = 0
        up = 0
        down = 0

        # Reinicia a lista de detecções
        detects.clear()

    # Verifica o tempo para resetar a contagem a cada 1 hora
    current_reset_time = time.time()
    elapsed_reset_time = current_reset_time - start_reset_time

    if elapsed_reset_time > 3600:  # 3600 segundos = 1 hora
        # Reinicia os contadores e a lista de detecções
        total = 0
        up = 0
        down = 0
        detects.clear()

        # Adiciona os resultados à lista
        current_timestamp = datetime.now()
        partial_result = [current_timestamp, total, up, down]

        # Salva os resultados em um arquivo CSV com o nome "Relatório.csv"
        save_results_to_csv([partial_result], result_csv_path)

        # Reinicia o tempo de reset
        start_reset_time = time.time()

# Libera os recursos após o término do vídeo
cap.release()
cv2.destroyAllWindows()