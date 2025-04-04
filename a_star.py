import pygame
import math
import heapq
import time
from pygame import gfxdraw

# Initial settings / Configurações iniciais
pygame.init()

# Dimensions and proportions / Tamanhos e proporções
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
GRID_AREA_WIDTH = 600
CONFIG_AREA_WIDTH = SCREEN_WIDTH - GRID_AREA_WIDTH

# Colors / Cores
COLORS = {
    'background': (248, 248, 252),
    'sidebar': (232, 232, 240),
    'grid_line': (45, 45, 55),
    'button': (78, 137, 193),
    'button_hover': (98, 157, 213),
    'button_text': (255, 255, 255),
    'text': (60, 60, 70),
    'highlight': (100, 180, 255),
    'wall': (70, 70, 80),
    'start': (110, 210, 130),
    'end': (230, 100, 100),
    'path': (85, 125, 245),
    'visited': (167, 132, 239),
    'cell_text': (255, 235, 120),
    'slider': (200, 200, 210)
}

# Window configuration / Configuração da janela
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Premium A* Visualizer")

# Global variables / Variáveis globais
current_heuristic = 'euclidean'  # Current heuristic type / Tipo de heurística atual
animation_speed = 0.05  # Animation speed / Velocidade da animação
show_values = True  # Whether to show cell values / Se deve mostrar valores das células
show_visited = True  # Whether to show visited cells / Se deve mostrar células visitadas
dragging_start = False  # If start node is being dragged / Se o nó inicial está sendo arrastado
dragging_end = False  # If end node is being dragged / Se o nó final está sendo arrastado
is_running = False  # If algorithm is running / Se o algoritmo está executando
final_path = []  # Stores the final path / Armazena o caminho final
g_values = {}  # Stores g values for cells / Armazena valores g das células
path_length = 0  # Length of final path / Comprimento do caminho final
visited_count = 0  # Number of visited cells / Número de células visitadas

# Grid initialization / Inicialização da grade
GRID_CONFIG = {
    'rows': 20,  # Number of rows / Número de linhas
    'cols': 20,  # Number of columns / Número de colunas
    'cell_size': min(GRID_AREA_WIDTH // 20, SCREEN_HEIGHT // 20),  # Cell size / Tamanho da célula
    'offset_x': 0,  # Horizontal offset / Deslocamento horizontal
    'offset_y': 0  # Vertical offset / Deslocamento vertical
}

# Initialize grid / Inicializa a grid
grid = [[0 for _ in range(GRID_CONFIG['cols'])] for _ in range(GRID_CONFIG['rows'])]
start_pos = (GRID_CONFIG['rows'] // 5, GRID_CONFIG['cols'] // 5)  # Start position / Posição inicial
end_pos = (GRID_CONFIG['rows'] - GRID_CONFIG['rows'] // 5 - 1, 
           GRID_CONFIG['cols'] - GRID_CONFIG['cols'] // 5 - 1)  # End position / Posição final

# Fonts / Fontes
font_small = pygame.font.SysFont('Segoe UI', 14)
font_medium = pygame.font.SysFont('Segoe UI', 16, bold=True)
font_large = pygame.font.SysFont('Segoe UI', 20, bold=True)
font_title = pygame.font.SysFont('Segoe UI', 24, bold=True)

# Heuristic information / Informações das heurísticas
HEURISTIC_DATA = {
    'manhattan': {
        'name': "Manhattan",
        'desc': "City block distance: sum of absolute coordinate differences. Ideal for orthogonal movements.",
        'formula': "f(n) = g(n) + |x₁ - x₂| + |y₁ - y₂|",
        'best_for': "4-direction movement (up, down, left, right)",
        'complexity': "Faster but less precise"
    },
    'euclidean': {
        'name': "Euclidean",
        'desc': "Straight-line distance: Pythagorean theorem. Ideal for free movement in any direction.",
        'formula': "f(n) = g(n) + √((x₁ - x₂)² + (y₁ - y₂)²)",
        'best_for': "Movement in any direction",
        'complexity': "More precise but slightly slower"
    }
}

class Button:
    """Button class for UI elements / Classe de botão para elementos de UI"""
    def __init__(self, x, y, width, height, text, color=None, hover_color=None):
        self.rect = pygame.Rect(x, y, width, height)  # Button rectangle / Retângulo do botão
        self.text = text  # Button text / Texto do botão
        self.color = color or COLORS['button']  # Normal color / Cor normal
        self.hover_color = hover_color or COLORS['button_hover']  # Hover color / Cor ao passar mouse
        self.is_hovered = False  # Hover state / Estado de hover
        self.is_active = False  # Active state / Estado ativo
        
    def draw(self, surface):
        """Draw the button / Desenha o botão"""
        color = self.hover_color if self.is_hovered else self.color
        border_radius = 6  # Rounded corners / Cantos arredondados
        
        pygame.draw.rect(surface, color, self.rect, border_radius=border_radius)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2, border_radius=border_radius)
        
        text_surf = font_medium.render(self.text, True, COLORS['button_text'])
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        """Check if mouse is hovering over button / Verifica se mouse está sobre o botão"""
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, event):
        """Check if button was clicked / Verifica se botão foi clicado"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class Slider:
    """Slider class for UI / Classe de slider para UI"""
    def __init__(self, x, y, width, height, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, width, height)  # Slider rectangle / Retângulo do slider
        self.min = min_val  # Minimum value / Valor mínimo
        self.max = max_val  # Maximum value / Valor máximo
        self.value = initial_val  # Current value / Valor atual
        self.dragging = False  # Dragging state / Estado de arraste
        self.handle_radius = height // 2  # Handle radius / Raio do controle
        
    def draw(self, surface):
        """Draw the slider / Desenha o slider"""
        pygame.draw.rect(surface, COLORS['slider'], self.rect, border_radius=self.rect.height//2)
        fill_width = int((self.value - self.min) / (self.max - self.min) * self.rect.width)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(surface, COLORS['button'], fill_rect, border_radius=self.rect.height//2)
        
        handle_x = self.rect.x + fill_width
        pygame.draw.circle(surface, COLORS['button_hover'], (handle_x, self.rect.centery), self.handle_radius)
        pygame.draw.circle(surface, (0, 0, 0), (handle_x, self.rect.centery), self.handle_radius, 2)
        
        value_text = font_small.render(f"{self.value:.2f}s", True, COLORS['text'])
        surface.blit(value_text, (self.rect.right + 10, self.rect.centery - 10))
        
    def update(self, pos, event):
        """Update slider value / Atualiza valor do slider"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos) or \
               math.sqrt((pos[0] - (self.rect.x + int((self.value - self.min) / (self.max - self.min) * self.rect.width))**2 + 
                         (pos[1] - self.rect.centery)**2) < self.handle_radius + 5):
                self.dragging = True
                
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            
        if self.dragging and event.type == pygame.MOUSEMOTION:
            rel_x = max(0, min(pos[0] - self.rect.x, self.rect.width))
            self.value = self.min + (rel_x / self.rect.width) * (self.max - self.min)
            return True
        return False

# Create UI elements / Criação dos elementos da interface
buttons = [
    Button(GRID_AREA_WIDTH + 30, 40, 340, 45, "Start Search (Space)"),
    Button(GRID_AREA_WIDTH + 30, 220, 160, 40, "Manhattan (M)", 
           (120, 180, 80), (140, 200, 100)),
    Button(GRID_AREA_WIDTH + 210, 220, 160, 40, "Euclidean (E)", 
           (180, 120, 80), (200, 140, 100)),
    Button(GRID_AREA_WIDTH + 30, 270, 340, 40, "Reset (R)"),
    Button(GRID_AREA_WIDTH + 30, 320, 340, 40, "Clear Grid"),
]

grid_size_buttons = [
    Button(GRID_AREA_WIDTH + 30, 105, 100, 35, "20x20"),
    Button(GRID_AREA_WIDTH + 140, 105, 100, 35, "30x30"),
    Button(GRID_AREA_WIDTH + 250, 105, 100, 35, "40x40")
]

speed_slider = Slider(GRID_AREA_WIDTH + 35, 160, 250, 20, 0.01, 0.5, 0.05)

def reset_grid(rows=None, cols=None):
    """Reset grid to initial state / Reinicia a grade para o estado inicial"""
    global GRID_CONFIG, grid, start_pos, end_pos, is_running, final_path, path_length, visited_count
    
    is_running = False
    rows = rows or GRID_CONFIG['rows']
    cols = cols or GRID_CONFIG['cols']
    
    GRID_CONFIG = {
        'rows': rows,
        'cols': cols,
        'cell_size': min(GRID_AREA_WIDTH // cols, SCREEN_HEIGHT // rows),
        'offset_x': 0,
        'offset_y': 0
    }
    
    grid = [[0 for _ in range(cols)] for _ in range(rows)]
    start_pos = (rows // 5, cols // 5)
    end_pos = (rows - rows // 5 - 1, cols - cols // 5 - 1)
    final_path = []
    path_length = 0
    visited_count = 0

def calculate_heuristic(point_a, point_b, h_type):
    """Calculate heuristic value between two points / Calcula valor heurístico entre dois pontos"""
    x1, y1 = point_a
    x2, y2 = point_b
    
    if h_type == 'manhattan':
        return abs(x1 - x2) + abs(y1 - y2)
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def find_path(start, end, heuristic_type):
    """Find path using A* algorithm / Encontra caminho usando algoritmo A*"""
    global is_running, final_path, g_values, path_length, visited_count
    
    open_nodes = []
    heapq.heappush(open_nodes, (0, start))
    
    path_origin = {}
    g_scores = {(row, col): float('inf') for row in range(GRID_CONFIG['rows']) for col in range(GRID_CONFIG['cols'])}
    g_scores[start] = 0
    
    f_scores = {(row, col): float('inf') for row in range(GRID_CONFIG['rows']) for col in range(GRID_CONFIG['cols'])}
    f_scores[start] = calculate_heuristic(start, end, heuristic_type)
    
    explored = set()
    path_length = 0
    visited_count = 0
    is_running = True

    draw_interface(g_scores, None, path_length, visited_count)
    pygame.display.flip()
    time.sleep(1)

    while open_nodes and is_running:
        _, current = heapq.heappop(open_nodes)
        
        if current == end:
            path = []
            while current in path_origin:
                path.append(current)
                current = path_origin[current]
            final_path = path[::-1]
            path_length = len(final_path)
            is_running = False
            return
        
        explored.add(current)
        visited_count = len(explored)
        if show_visited:
            draw_interface(g_scores, explored, path_length, visited_count)
            pygame.display.flip()
            time.sleep(animation_speed)
        
        x, y = current
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            neighbor = (x + dx, y + dy)
            
            if (0 <= neighbor[0] < GRID_CONFIG['rows'] and 
                0 <= neighbor[1] < GRID_CONFIG['cols'] and 
                grid[neighbor[0]][neighbor[1]] != 1):
                
                tentative_g = g_scores[current] + 1
                
                if tentative_g < g_scores[neighbor]:
                    path_origin[neighbor] = current
                    g_scores[neighbor] = tentative_g
                    f_scores[neighbor] = tentative_g + calculate_heuristic(neighbor, end, heuristic_type)
                    heapq.heappush(open_nodes, (f_scores[neighbor], neighbor))
    
    is_running = False
    final_path = []
    path_length = 0

def draw_grid(g_values, explored=None):
    """Draw the grid / Desenha a grade"""
    for row in range(GRID_CONFIG['rows']):
        for col in range(GRID_CONFIG['cols']):
            rect = pygame.Rect(
                col * GRID_CONFIG['cell_size'] + GRID_CONFIG['offset_x'],
                row * GRID_CONFIG['cell_size'] + GRID_CONFIG['offset_y'],
                GRID_CONFIG['cell_size'],
                GRID_CONFIG['cell_size']
            )
            
            if grid[row][col] == 1:
                pygame.draw.rect(screen, COLORS['wall'], rect)
            elif (row, col) == start_pos:
                pygame.draw.rect(screen, COLORS['start'], rect)
            elif (row, col) == end_pos:
                pygame.draw.rect(screen, COLORS['end'], rect)
            elif explored and (row, col) in explored:
                pygame.draw.rect(screen, COLORS['visited'], rect)
            else:
                pygame.draw.rect(screen, COLORS['background'], rect)
            
            pygame.draw.rect(screen, COLORS['grid_line'], rect, 1)
            if show_values and g_values.get((row, col), float('inf')) != float('inf'):
                value_text = font_small.render(str(g_values[(row, col)]), True, COLORS['cell_text'])
                screen.blit(value_text, (col * GRID_CONFIG['cell_size'] + 5 + GRID_CONFIG['offset_x'], 
                                         row * GRID_CONFIG['cell_size'] + 5 + GRID_CONFIG['offset_y']))

def draw_config_panel(path_length, visited_count):
    """Draw configuration panel / Desenha painel de configuração"""
    config_rect = pygame.Rect(GRID_AREA_WIDTH, 0, CONFIG_AREA_WIDTH, SCREEN_HEIGHT)
    pygame.draw.rect(screen, COLORS['sidebar'], config_rect)
    
    title = font_title.render("A* Settings", True, COLORS['text'])
    screen.blit(title, (GRID_AREA_WIDTH + 30, 10))
    
    mouse_pos = pygame.mouse.get_pos()
    for button in buttons:
        button.check_hover(mouse_pos)
        button.draw(screen)
    
    grid_title = font_large.render("Grid Size:", True, COLORS['text'])
    screen.blit(grid_title, (GRID_AREA_WIDTH + 30, 80))
    
    for button in grid_size_buttons:
        button.is_active = (GRID_CONFIG['rows'] == int(button.text.split('x')[0]))
        button.check_hover(mouse_pos)
        button.draw(screen)
    
    speed_title = font_large.render("Speed:", True, COLORS['text'])
    screen.blit(speed_title, (GRID_AREA_WIDTH + 30, 135))
    speed_slider.draw(screen)
    
    heuristic_title = font_large.render("Heuristic:", True, COLORS['text'])
    screen.blit(heuristic_title, (GRID_AREA_WIDTH + 30, 190))
    
    info_box = pygame.Rect(GRID_AREA_WIDTH + 25, 370, 350, 150)
    pygame.draw.rect(screen, (255, 255, 255), info_box, border_radius=6)
    pygame.draw.rect(screen, COLORS['slider'], info_box, 2, border_radius=6)
    
    heuristic_name = font_large.render(HEURISTIC_DATA[current_heuristic]['name'], True, COLORS['highlight'])
    screen.blit(heuristic_name, (GRID_AREA_WIDTH + 30, 380))
    
    desc_lines = [HEURISTIC_DATA[current_heuristic]['desc'][i:i+55] for i in range(0, len(HEURISTIC_DATA[current_heuristic]['desc']), 40)]
    for i, line in enumerate(desc_lines[:3]):
        desc_text = font_small.render(line, True, COLORS['text'])
        screen.blit(desc_text, (GRID_AREA_WIDTH + 30, 410 + i * 20))
    
    formula_text = font_medium.render(HEURISTIC_DATA[current_heuristic]['formula'], True, (30, 80, 160))
    screen.blit(formula_text, (GRID_AREA_WIDTH + 30, 480))
    
    stats_text = font_large.render("Statistics:", True, COLORS['text'])
    screen.blit(stats_text, (GRID_AREA_WIDTH + 30, 520))
    
    stats = [
        f"Visited cells: {visited_count}",
        f"Path length: {path_length if path_length > 0 else 'N/A'}"
    ]
    
    for i, stat in enumerate(stats):
        stat_line = font_medium.render(stat, True, COLORS['text'])
        screen.blit(stat_line, (GRID_AREA_WIDTH + 30, 550 + i * 20))

def draw_interface(g_values, explored=None, path_length=0, visited_count=0):
    """Draw complete interface / Desenha interface completa"""
    screen.fill(COLORS['background'])
    
    draw_grid(g_values, explored)
    
    for cell in final_path:
        pygame.draw.rect(
            screen, COLORS['path'],
            (cell[1] * GRID_CONFIG['cell_size'] + GRID_CONFIG['offset_x'],
             cell[0] * GRID_CONFIG['cell_size'] + GRID_CONFIG['offset_y'],
             GRID_CONFIG['cell_size'],
             GRID_CONFIG['cell_size'])
        )
    
    draw_config_panel(path_length, visited_count)

def main():
    """Main function / Função principal"""
    global current_heuristic, animation_speed, start_pos, end_pos
    global show_values, show_visited, dragging_start, dragging_end
    global grid, final_path, g_values, path_length, visited_count, is_running
    
    running = True
    clock = pygame.time.Clock()
    
    reset_grid()
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if speed_slider.update(mouse_pos, event):
                animation_speed = speed_slider.value
            
            for button in buttons:
                if button.is_clicked(mouse_pos, event):
                    if button.text.startswith("Start Search") and not is_running:
                        find_path(start_pos, end_pos, current_heuristic)
                    elif "Manhattan" in button.text and not is_running:
                        current_heuristic = 'manhattan'
                        buttons[1].is_active = True
                        buttons[2].is_active = False
                    elif "Euclidean" in button.text and not is_running:
                        current_heuristic = 'euclidean'
                        buttons[1].is_active = False
                        buttons[2].is_active = True
                    elif "Reset" in button.text and not is_running:
                        reset_grid(GRID_CONFIG['rows'], GRID_CONFIG['cols'])
                    elif "Clear" in button.text and not is_running:
                        grid = [[0 for _ in range(GRID_CONFIG['cols'])] for _ in range(GRID_CONFIG['rows'])]
            
            for button in grid_size_buttons:
                if button.is_clicked(mouse_pos, event) and not is_running:
                    size = int(button.text.split('x')[0])
                    reset_grid(size, size)
            
            if 0 <= mouse_pos[0] < GRID_AREA_WIDTH and 0 <= mouse_pos[1] < SCREEN_HEIGHT and not is_running:
                row = (mouse_pos[1] - GRID_CONFIG['offset_y']) // GRID_CONFIG['cell_size']
                col = (mouse_pos[0] - GRID_CONFIG['offset_x']) // GRID_CONFIG['cell_size']
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if 0 <= row < GRID_CONFIG['rows'] and 0 <= col < GRID_CONFIG['cols']:
                        if (row, col) == start_pos:
                            dragging_start = True
                            dragging_end = False
                        elif (row, col) == end_pos:
                            dragging_start = False
                            dragging_end = True
                        else:
                            dragging_start = False
                            dragging_end = False
                
                if pygame.mouse.get_pressed()[0]:
                    if 0 <= row < GRID_CONFIG['rows'] and 0 <= col < GRID_CONFIG['cols']:
                        if dragging_start:
                            start_pos = (row, col)
                        elif dragging_end:
                            end_pos = (row, col)
                        elif (row, col) not in (start_pos, end_pos):
                            grid[row][col] = 1
                
                elif pygame.mouse.get_pressed()[2]:
                    if 0 <= row < GRID_CONFIG['rows'] and 0 <= col < GRID_CONFIG['cols']:
                        if (row, col) not in (start_pos, end_pos):
                            grid[row][col] = 0
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not is_running:
                    find_path(start_pos, end_pos, current_heuristic)
                elif event.key == pygame.K_m and not is_running:
                    current_heuristic = 'manhattan'
                    buttons[1].is_active = True
                    buttons[2].is_active = False
                elif event.key == pygame.K_e and not is_running:
                    current_heuristic = 'euclidean'
                    buttons[1].is_active = False
                    buttons[2].is_active = True
                elif event.key == pygame.K_r and not is_running:
                    reset_grid(GRID_CONFIG['rows'], GRID_CONFIG['cols'])
                elif event.key == pygame.K_v:
                    show_values = not show_values
                elif event.key == pygame.K_UP and animation_speed > 0.01:
                    animation_speed = max(0.01, animation_speed - 0.01)
                    speed_slider.value = animation_speed
                elif event.key == pygame.K_DOWN and animation_speed < 0.5:
                    animation_speed = min(0.5, animation_speed + 0.01)
                    speed_slider.value = animation_speed
        
        draw_interface(g_values, None, path_length, visited_count)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()