#!/usr/bin/env python3
"""Тест алгоритма решения кубика Рубика."""
from backend.rubik.state import solved, scramble, apply_sequence, is_solved
from backend.rubik.solver_optimal import solve_optimal  # Используем оптимальный метод
from backend.rubik.solver import _check_invariants
from backend.rubik.pieces import pieces_solved

def test_solve_simple_scrambles(debug=False):
    """Тестирует решение простых скрэмблов."""
    test_cases = [
        ("Собранный куб", []),
        ("Один ход R", ["R"]),
        ("Один ход U", ["U"]),
        ("Два хода R R", ["R", "R"]),
        ("Ход U D", ["U", "D"]),
        ("5 случайных ходов", None),  # будет сгенерирован ниже
        ("20 случайных ходов", None),
    ]
    
    for desc, scramble_seq in test_cases:
        if scramble_seq is None:
            # Сгенерируем случайную скрэмбл
            if "5" in desc:
                state, scramble_seq = scramble(n=5, seed=42)
            else:
                state, scramble_seq = scramble(n=20, seed=43)
        else:
            state = apply_sequence(solved(), scramble_seq)
        
        print(f"\n{'='*60}")
        print(f"Тест: {desc}")
        print(f"Скрэмбл: {' '.join(scramble_seq)}")
        print(f"Куб собран до скрэмбла: {is_solved(state)}")
        print(f"Детали расположены правильно: {pieces_solved(state)}")
        
        # Получаем информацию о деталях
        from backend.rubik.pieces import read_corners, read_edges
        cp, co = read_corners(state)
        ep, eo = read_edges(state)
        corners_wrong = sum(1 for s in range(len(cp)) if cp[s] != s)
        edges_wrong = sum(1 for s in range(len(ep)) if ep[s] != s)
        corners_misoriented = sum(1 for o in co if o != 0)
        edges_misoriented = sum(1 for o in eo if o != 0)
        
        print(f"Углов не на месте: {corners_wrong}/8")
        print(f"Углов разориентировано: {corners_misoriented}/8")
        print(f"Рёбер не на месте: {edges_wrong}/12")
        print(f"Рёбер разориентировано: {edges_misoriented}/12")
        
        try:
            # Решаем куб
            solution = solve_optimal(state)
            
            # Проверяем что решение работает
            final_state = apply_sequence(state, solution)
            
            print(f"Решение найдено: {' '.join(solution[:20])}{'...' if len(solution) > 20 else ''}")
            print(f"Длина решения: {len(solution)} ходов")
            print(f"Куб собран после решения: {is_solved(final_state)}")
            print(f"[V] УСПЕШНО")
            
            if not is_solved(final_state):
                print(f"[X] ОШИБКА: куб не собран после решения!")
                return False
                
        except Exception as e:
            print(f"[X] ОШИБКА: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

def test_invariants():
    """Тестирует проверку инвариантов."""
    print(f"\n{'='*60}")
    print("Тест инвариантов")
    
    # Тест на собранном кубе
    state = solved()
    valid, msg = _check_invariants(state)
    print(f"Собранный куб: {msg}")
    if not valid:
        print("[X] ОШИБКА: инварианты не выполнены на собранном кубе!")
        return False
    
    # Тест на скрэмбленном кубе
    state, _ = scramble(n=10, seed=100)
    valid, msg = _check_invariants(state)
    print(f"Скрэмбленный куб: {msg}")
    if not valid:
        print(f"[X] ОШИБКА: инварианты не выполнены на скрэмбленном кубе! ({msg})")
        return False
    
    print(f"[V] УСПЕШНО")
    return True

if __name__ == "__main__":
    print("Начало тестирования алгоритма решения кубика Рубика")
    print("=" * 60)
    
    # Проверяем инварианты
    if not test_invariants():
        print("\n[X] Тесты не пройдены")
        exit(1)
    
    # Тестируем решение
    if not test_solve_simple_scrambles(debug=True):
        print("\n[X] Тесты не пройдены")
        exit(1)
    
    print("\n" + "=" * 60)
    print("[V] ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
