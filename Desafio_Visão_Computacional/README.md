# Teste Técnico – Visão Computacional + IA

## Objetivo 
Este projeto é um mini-aplicativo de linha de comando (CLI) construído em Python, capaz de carregar uma imagem e aplicar dois algoritmos distintos de segmentação de imagem: um baseado em limiares de cor no espaço **HSV** e outro baseado em agrupamento **K-Means**.

O aplicativo permite ao usuário escolher o método, a cor alvo (verde ou azul) e ajustar parâmetros específicos via flags de comando.

---

## Requisitos
* Python >= 3.9
* Bibliotecas: `opencv-python`, `numpy`

---

## Como Rodar (Método Rápido - Recomendado)
A maneira mais fácil de testar este projeto é diretamente no Google Colab, que cria um ambiente limpo e instala todas as dependências automaticamente.

1.  **Clique no link abaixo** para abrir o notebook de teste:

    [![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/andreischtz/desafio-visao-computacional/blob/main/Desafio_Visão_Computacional/Testar_Projeto_Aqui.ipynb)

2.  Quando o notebook carregar, clique em **"Executar tudo"** no menu "Ambiente de execução".

3.  Role para baixo e veja os logs de saída dos testes.

---

## 🛠️ Como Instalar e Rodar (Método Local)
Se preferir executar o projeto em sua máquina local, siga os passos abaixo em seu terminal:

1.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/andreischtz/desafio-visao-computacional.git
    ```

2.  **Acesse a Pasta Correta do Projeto:**
    Observe que os arquivos do projeto estão dentro de uma subpasta. Acesse-a:
    ```bash
    cd desafio-visao-computacional/Desafio_Visão_Computacional
    ```

3.  **Crie e Ative um Ambiente Virtual:**
    ```bash
    # Crie o ambiente (pode usar 'python' ou 'python3')
    python -m venv venv
    
    # Ative o ambiente (Linux/Mac)
    source venv/bin/activate
    
    # Ative o ambiente (Windows - PowerShell)
    .\venv\Scripts\Activate.ps1
    
    # Ative o ambiente (Windows - CMD)
    .\venv\Scripts\activate.bat
    ```

4.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Pronto! Execute os Testes:**
    Veja a seção "Exemplos de Uso" para os comandos.

### Exemplos de Uso

**Segmentação HSV (Verde)**
```bash
python segment.py --input samples/planta.jpg --method hsv --target green
````

**Segmentação K-Means (Verde)**

```bash
python segment.py --input samples/jardim.jpg --method kmeans --k 4 --target green
```

**Segmentação HSV (Azul - Céu)**

```bash
python segment.py --input samples/ceu.jpg --method hsv --target blue
```

**Segmentação HSV (Azul - Ajuste Manual)**
Este é um exemplo de ajuste fino dos limiares para isolar a placa de trânsito, ignorando o céu.

```bash
python segment.py --input samples/placa.png --method hsv --target blue --hmin 90 --hmax 130 --smin 100
```

**Segmentação K-Means (Azul - Placa)**

```bash
python segment.py --input samples/placa.png --method kmeans --k 4 --target blue
```

-----

## Explicação dos Métodos

### A) Segmentação por Cor (HSV)

Este método é uma abordagem de limiarização (thresholding). A imagem original (em RGB) é convertida para o espaço de cor **HSV (Hue, Saturation, Value)**.

  * **H (Matiz):** Define a cor pura (ex: o tom de verde ou azul).
  * **S (Saturação):** A "pureza" da cor. 0 é cinza, 255 é a cor mais vibrante.
  * **V (Valor):** O "brilho" da cor. 0 é preto, 255 é o mais brilhante.

A vantagem do HSV é que a **Cor (H)** é separada da **Iluminação (V)**. O script então cria uma máscara binária selecionando *apenas* os pixels que estão dentro do intervalo de H, S e V especificado para "verde" ou "azul".

### B) Segmentação por Agrupamento (K-Means)

Este é um método de aprendizado de máquina não supervisionado. Ele não precisa de limiares manuais.

1.  A imagem é convertida para HSV (para melhor separação de cores) e os pixels são "achatados" em uma lista de pontos de dados.
2.  O algoritmo K-Means agrupa todos os pixels em **K** clusters (grupos) com base na similaridade de suas cores.
3.  O script então encontra a cor média (centróide) de cada um dos **K** clusters.
4.  Ele calcula a distância entre cada centróide e uma cor "alvo" ideal (um tom de verde puro ou azul puro).
5.  O cluster cujo centróide for "mais próximo" da cor alvo é selecionado, e todos os pixels que pertencem a esse cluster formam a máscara final.

-----

## Observações sobre a Escolha dos Ranges HSV

Para este projeto, foram definidos intervalos padrão que representam bem tons **verdes** e **azuis** em condições de iluminação natural:

| Cor alvo | Hue (hmin–hmax) | Saturation (smin–smax) | Value (vmin–vmax) |
|-----------|----------------|------------------------|-------------------|
| Verde | 35 – 85 | 50 – 255 | 50 – 255 |
| Azul | 90 – 130 | 50 – 255 | 50 – 255 |

Esses intervalos foram ajustados empiricamente com base em observação visual dos resultados.  
Durante os testes, notou-se que:
- O canal **Hue** define a faixa principal da cor (matiz), sendo o verde localizado entre ~60 e o azul em torno de ~120.  
- A **Saturação (S)** foi mantida entre 50 e 255 para excluir tons acinzentados ou muito claros.  
- O **Value (V)** foi limitado a partir de 50 para evitar regiões escuras sem informação de cor.

Esses valores foram escolhidos visando **um equilíbrio entre precisão e generalização**, permitindo detectar tons naturais de vegetação (verde) e céu (azul) mesmo com pequenas variações de iluminação.

Vale observar que, em ambientes com luz artificial ou sombras intensas, os valores ideais podem variar. Por isso, o programa permite ajustar manualmente todos os limites (`--hmin`, `--hmax`, `--smin`, etc.) via linha de comando, garantindo flexibilidade e controle sobre o resultado.

 -----

## Limitações Conhecidas

  * **HSV e Saturação Baixa:** O método HSV tem dificuldade em distinguir cores com baixa saturação. No teste `ceu.jpg`, o HSV (77.15%) capturou o céu azul *e* as nuvens brancas, pois branco/cinza têm baixa saturação e podem "vazar" para dentro do range.
  * **K-Means (Precisão vs. Generalidade):** O K-Means foi mais "inteligente" no `ceu.jpg`, criando clusters separados para o céu (40.69%) e as nuvens, resultando em uma máscara mais limpa.
  * **K-Means e Tons da Mesma Cor:** O K-Means pode ser *muito* específico. No teste `planta_sombra.jpg`, ele criou clusters diferentes para "verde-claro" (36.79%) e "verde-escuro" (sombra). A lógica de "cluster mais próximo" selecionou apenas o verde-claro, ignorando as sombras. Já o método HSV (60.38%) foi mais generalista e capturou ambos os tons de verde.
  * **Velocidade:** K-Means é computacionalmente mais custoso, os testes com HSV levaram \~0.06s, enquanto K-Means levou \~1.80s.

<!-- end list -->

```
```
