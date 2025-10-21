import argparse
import cv2
import numpy as np
import os
import time

# -------------------------------------------------------
# Segmentação por cor (HSV)
# -------------------------------------------------------
def segment_hsv(image, target, hmin, hmax, smin, smax, vmin, vmax):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    if target == "green" and (hmin is None):
        hmin, hmax, smin, smax, vmin, vmax = 35, 85, 50, 255, 50, 255
    elif target == "blue" and (hmin is None):
        hmin, hmax, smin, smax, vmin, vmax = 90, 130, 50, 255, 50, 255

    lower = np.array([hmin, smin, vmin])
    upper = np.array([hmax, smax, vmax])

    mask = cv2.inRange(hsv, lower, upper)
    return mask

# -------------------------------------------------------
# Segmentação por agrupamento (K-Means)
# -------------------------------------------------------
def segment_kmeans(image, k, target):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    data = hsv.reshape((-1, 3))
    data = np.float32(data)

    # Critério de parada do K-Means
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    centers = np.uint8(centers)

    # Define o alvo de cor desejado (verde ou azul)
    if target == "green":
        target_color = np.uint8([[[60, 255, 255]]])  # Verde aproximado em HSV
    else:
        target_color = np.uint8([[[120, 255, 255]]]) # Azul aproximado em HSV

    target_hsv = target_color[0][0]

    # Calcula distância de cada cluster até o alvo
    distances = np.linalg.norm(centers - target_hsv, axis=1)
    target_cluster = np.argmin(distances)

    # Gera a máscara binária (0/255)
    mask = (labels.flatten() == target_cluster).astype(np.uint8) * 255
    mask = mask.reshape((image.shape[0], image.shape[1]))
    return mask


# -------------------------------------------------------
# Cria imagem com overlay colorido
# -------------------------------------------------------
def create_overlay(image, mask, color=(0, 255, 0)):
    overlay = image.copy()
    overlay[mask == 255] = color
    blended = cv2.addWeighted(image, 0.6, overlay, 0.4, 0)
    return blended


# -------------------------------------------------------
# Função principal (CLI)
# -------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Segmentação de Imagem (Visão Computacional + IA)")
    parser.add_argument("--input", type=str, help="Caminho da imagem de entrada")
    parser.add_argument("--method", type=str, choices=["hsv", "kmeans"], required=True, help="Método de segmentação")
    parser.add_argument("--target", type=str, choices=["green", "blue"], default="green", help="Cor alvo")
    parser.add_argument("--hmin", type=int, default=None)
    parser.add_argument("--hmax", type=int, default=None)
    parser.add_argument("--smin", type=int, default=50)
    parser.add_argument("--smax", type=int, default=255)
    parser.add_argument("--vmin", type=int, default=50)
    parser.add_argument("--vmax", type=int, default=255)
    parser.add_argument("--k", type=int, default=3, help="Número de clusters para K-Means")
    parser.add_argument("--webcam", action="store_true", help="Usar webcam como entrada")
    args = parser.parse_args()

    start = time.time()

    # -------------------------------------------------------
    # Carrega imagem (arquivo ou webcam)
    # -------------------------------------------------------
    if args.webcam:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            print("[ERRO] Não foi possível capturar imagem da webcam.")
            return
        image = frame
        input_name = "webcam"
    else:
        image = cv2.imread(args.input)
        if image is None:
            print("[ERRO] Imagem não encontrada:", args.input)
            return
        input_name = os.path.splitext(os.path.basename(args.input))[0]

    # -------------------------------------------------------
    # Aplica o método escolhido
    # -------------------------------------------------------
    if args.method == "hsv":
        mask = segment_hsv(image, args.target, args.hmin, args.hmax, args.smin, args.smax, args.vmin, args.vmax)
    else:
        mask = segment_kmeans(image, args.k, args.target)
    
    # Define a cor do overlay (BGR para OpenCV) com base no alvo
    overlay_color = (0, 255, 0) if args.target == "green" else (255, 0, 0)
    overlay = create_overlay(image, mask, color=overlay_color)

    # -------------------------------------------------------
    # Salva os resultados dentro da pasta do projeto
    # -------------------------------------------------------

    script_dir = os.path.dirname(__file__) if os.path.dirname(__file__) else "."
    output_dir = os.path.join(script_dir, "outputs")
    os.makedirs(output_dir, exist_ok=True)

    mask_path = os.path.join(output_dir, f"{input_name}_mask.png")
    overlay_path = os.path.join(output_dir, f"{input_name}_overlay.png")

    cv2.imwrite(mask_path, mask)
    cv2.imwrite(overlay_path, overlay)

    # -------------------------------------------------------
    # Exibe informações no terminal
    # -------------------------------------------------------
    percent = np.sum(mask == 255) / mask.size * 100
    elapsed = time.time() - start

    print(f"[INFO] Método: {args.method.upper()}")
    print(f"[INFO] Cor alvo: {args.target}")
    print(f"[INFO] Pixels segmentados: {percent:.2f}%")
    print(f"[INFO] Resultados salvos em: {output_dir}")
    print(f"[INFO] Tempo total: {elapsed:.2f}s")


if __name__ == "__main__":
    main()