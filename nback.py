"""Offline N-Back task implemented with pygame.

Position-based N-Back: a single colored square lights up in one cell of a
3x3 grid on each trial. The participant presses the RESPONSE key when the
current position matches the position shown N trials ago.
"""
import random
import time
from typing import Dict, List, Optional, Tuple

import pygame

# ========================= CONFIGURATION =========================
GRID_SIZE: int = 3                      # 3x3 grid of cells
CELL_MARGIN_RATIO: float = 0.15         # spacing between cells, relative to cell size
GRID_AREA_RATIO: float = 0.6            # grid occupies this fraction of the shorter screen dimension

STIMULUS_COLOR: Tuple[int, int, int] = (30, 144, 255)   # DodgerBlue
CELL_COLOR: Tuple[int, int, int] = (60, 60, 60)
BACKGROUND_COLOR: Tuple[int, int, int] = (0, 0, 0)
TEXT_COLOR: Tuple[int, int, int] = (255, 255, 255)

STIMULUS_DURATION_MS: int = 500         # how long the colored square is shown
ISI_MS: int = 2000                      # inter-stimulus interval (gap after stimulus, still respondable)
TRIAL_DURATION_MS: int = STIMULUS_DURATION_MS + ISI_MS

RESPONSE_KEY: int = pygame.K_SPACE      # key pressed to indicate "match"
QUIT_KEY: int = pygame.K_ESCAPE         # key pressed to abort the running level early

MATCH_PROBABILITY: float = 0.3          # fraction of trials (after the first n) that are targets
MATCH_FEEDBACK_TEXT: str = "Match!"     # shown when the participant presses a correct match

# Which position-generation strategy to use for non-target trials (see
# POSITION_STRATEGIES below for the available options).
POSITION_STRATEGY: str = "no_immediate_repeat"
# ===================================================================


def _pick_position_no_immediate_repeat(positions: List[int], trial_index: int, n_back: int) -> int:
    """Pick a random cell, excluding the previous trial's cell and the n-back target cell."""
    choices = set(range(GRID_SIZE * GRID_SIZE))
    if trial_index >= 1:
        choices.discard(positions[trial_index - 1])
    if trial_index >= n_back:
        choices.discard(positions[trial_index - n_back])
    return random.choice(list(choices))


def _pick_position_pure_random(positions: List[int], trial_index: int, n_back: int) -> int:
    """Pick a fully random cell, only excluding the n-back target cell (repeats allowed)."""
    choices = set(range(GRID_SIZE * GRID_SIZE))
    if trial_index >= n_back:
        choices.discard(positions[trial_index - n_back])
    return random.choice(list(choices))


POSITION_STRATEGIES = {
    "no_immediate_repeat": _pick_position_no_immediate_repeat,
    "pure_random": _pick_position_pure_random,
}


def _grid_geometry(screen: pygame.Surface) -> Tuple[List[pygame.Rect], int]:
    """Compute cell rectangles for a centered GRID_SIZE x GRID_SIZE grid."""
    width, height = screen.get_size()
    grid_span = int(min(width, height) * GRID_AREA_RATIO)
    cell_size = int(grid_span / (GRID_SIZE + (GRID_SIZE - 1) * CELL_MARGIN_RATIO))
    gap = int(cell_size * CELL_MARGIN_RATIO)
    total_span = GRID_SIZE * cell_size + (GRID_SIZE - 1) * gap

    origin_x = (width - total_span) // 2
    origin_y = (height - total_span) // 2

    rects: List[pygame.Rect] = []
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = origin_x + col * (cell_size + gap)
            y = origin_y + row * (cell_size + gap)
            rects.append(pygame.Rect(x, y, cell_size, cell_size))

    return rects, cell_size


def _draw_grid(screen: pygame.Surface, cell_rects: List[pygame.Rect],
                active_position: Optional[int], status_lines: List[str],
                feedback_text: Optional[str] = None, debug: bool = False) -> None:
    screen.fill(BACKGROUND_COLOR)

    for idx, rect in enumerate(cell_rects):
        color = STIMULUS_COLOR if idx == active_position else CELL_COLOR
        pygame.draw.rect(screen, color, rect, border_radius=8)

    if debug:
        font = pygame.font.SysFont(None, 28)
        for line_idx, line in enumerate(status_lines):
            text_surface = font.render(line, True, TEXT_COLOR)
            screen.blit(text_surface, (20, 20 + line_idx * 30))

    if feedback_text:
        width, _ = screen.get_size()
        feedback_font = pygame.font.SysFont(None, 48)
        feedback_surface = feedback_font.render(feedback_text, True, STIMULUS_COLOR)
        feedback_rect = feedback_surface.get_rect(center=(width // 2, 60))
        screen.blit(feedback_surface, feedback_rect)

    pygame.display.flip()


def run_nback_level(screen: pygame.Surface, n_back: int, duration_seconds: int,
                     debug: bool = False) -> Dict[str, str]:
    """Run one N-Back level for the given duration and return summary results.

    The trial in progress when the time limit is reached is always completed
    before the level ends.
    """
    clock = pygame.time.Clock()
    cell_rects, _ = _grid_geometry(screen)

    hits = 0
    misses = 0
    false_alarms = 0
    correct_rejections = 0
    premature = 0
    response_times: List[float] = []

    positions: List[int] = []
    trial_index = 0
    level_start = time.monotonic()
    deadline = level_start + duration_seconds

    aborted = False

    position_picker = POSITION_STRATEGIES[POSITION_STRATEGY]

    while True:
        # Generate one more trial on demand
        if trial_index >= len(positions):
            if trial_index >= n_back and random.random() < MATCH_PROBABILITY:
                positions.append(positions[trial_index - n_back])
            else:
                positions.append(position_picker(positions, trial_index, n_back))

        current_position = positions[trial_index]
        is_target = trial_index >= n_back and current_position == positions[trial_index - n_back]

        trial_start = time.monotonic()
        responded = False
        response_time: Optional[float] = None
        feedback_text: Optional[str] = None

        while True:
            elapsed_ms = (time.monotonic() - trial_start) * 1000
            if elapsed_ms >= TRIAL_DURATION_MS:
                break

            show_stimulus = elapsed_ms < STIMULUS_DURATION_MS
            status_lines = [
                f"{n_back}-Back | Trial {trial_index + 1}",
                f"Hits: {hits}  Misses: {misses}  False Alarms: {false_alarms}",
                f"Correct Rejections: {correct_rejections}  Premature: {premature}",
            ]
            _draw_grid(screen, cell_rects, current_position if show_stimulus else None,
                       status_lines, feedback_text, debug)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    aborted = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == QUIT_KEY:
                        aborted = True
                    elif event.key == RESPONSE_KEY and not responded:
                        responded = True
                        response_time = (time.monotonic() - trial_start) * 1000
                        if trial_index < n_back:
                            premature += 1
                        elif is_target:
                            hits += 1
                            response_times.append(response_time)
                            feedback_text = MATCH_FEEDBACK_TEXT
                        else:
                            false_alarms += 1

            if aborted:
                break

            clock.tick(60)

        if aborted:
            break

        if not responded and trial_index >= n_back:
            if is_target:
                misses += 1
            else:
                correct_rejections += 1

        trial_index += 1

        if time.monotonic() >= deadline:
            break

    total_targets = hits + misses
    accuracy = (hits / total_targets * 100) if total_targets > 0 else 0.0
    avg_rt = (sum(response_times) / len(response_times)) if response_times else 0.0

    return {
        "Target Accuracy": f"{accuracy:.1f}%",
        "Avg Response Time": f"{avg_rt:.0f} ms",
        "Hits": str(hits),
        "Misses": str(misses),
        "False Alarms": str(false_alarms),
        "Correct Rejections": str(correct_rejections),
        "Premature": str(premature),
        "Total Trials": str(trial_index),
    }
