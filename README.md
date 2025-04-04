# A-Star-Heuristic-Visualizer

Um visualizador interativo do algoritmo A* que compara duas heurísticas diferentes: Manhattan e Euclidiana.

<div style="display: flex; justify-content: space-between;">
  <img src="https://github.com/user-attachments/assets/3b2f796a-26b6-42d7-bea7-dbdc1ad42843" width="49%">
  <img src="https://github.com/user-attachments/assets/01cd7680-720e-40c7-9647-c7da95df73a1" width="49%">
</div>


## Funcionalidades

- Visualização passo a passo do algoritmo A*
- Comparação entre heurísticas Manhattan e Euclidiana
- Interface interativa para criar obstáculos
- Exibição dos valores de custo (g(n)) para cada célula
- Painel informativo explicando cada heurística

## Como Usar

1. **Adicionar/Remover Obstáculos**:
   - Clique esquerdo: Adiciona um obstáculo
   - Clique direito: Remove um obstáculo

2. **Controles do Teclado**:
   - `Espaço`: Inicia a busca pelo caminho
   - `M`: Alterna para heurística Manhattan
   - `E`: Alterna para heurística Euclidiana

3. **Visualização**:
   - Célula verde: Ponto de partida
   - Célula vermelha: Ponto de destino
   - Células roxas: Células visitadas
   - Células azuis: Caminho final encontrado

## Heurísticas Implementadas

### Manhattan
- Ideal para movimentos em grade (cima, baixo, esquerda, direita)
- Fórmula: `|x₁ - x₂| + |y₁ - y₂|`

### Euclidiana
- Ideal para movimentos em qualquer direção
- Fórmula: `√((x₁ - x₂)² + (y₁ - y₂)²)`

## Requisitos

- Python 3.x
- Pygame

## Instalação

```bash
pip install pygame
