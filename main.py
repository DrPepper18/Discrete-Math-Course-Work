import copy

class RubiksCube:
    def __init__(self):
        self.state = list(range(0, 55))
        
    def copy(self):
        """Создает полную копию текущего состояния кубика."""
        new_cube = RubiksCube()
        new_cube.state = copy.deepcopy(self.state)
        return new_cube

    def apply_permutation(self, perm_dict):
        """
        Применяет перестановку к текущему состоянию кубика.
        perm_dict: словарь, где ключ — начальная позиция, значение — куда переходит элемент.
        """
        new_state = copy.deepcopy(self.state)
        for src, dest in perm_dict.items():
            new_state[dest] = self.state[src]
        self.state = new_state

    def _convert_cycles_to_dict(self, cycles):
        """Вспомогательный метод для превращения записи циклов в словарь перестановки[cite: 144]."""
        perm_dict = {}
        for cycle in cycles:
            for i in range(len(cycle)):
                src = cycle[i]
                dest = cycle[(i + 1) % len(cycle)]
                perm_dict[src] = dest
        return perm_dict


    def rotate_phi_1_minus_pi_2_z(self):
        r"""
        Поворот phi_1 = \Phi_{1}^{-\frac{\pi}{2}}(z) 
        Вращение первой плоскости по оси Z на -90 градусов[cite: 97, 100].
        Задано циклами из текста методички[cite: 101, 106, 114, 115].
        """
        cycles = [
            (1, 54, 27, 37),
            (2, 53, 26, 38),
            (3, 52, 25, 39),
            (16, 10, 12, 18),
            (13, 11, 15, 17)
        ]
        perm_dict = self._convert_cycles_to_dict(cycles)
        self.apply_permutation(perm_dict)

    def rotate_phi_1_minus_pi_z(self):
        r"""
        Поворот phi_2 = \Phi_{1}^{-\pi}(z) [cite: 116]
        Вращение первой плоскости по оси Z на 180 градусов[cite: 116, 118].
        Эквивалентно двукратному применению phi_1[cite: 125].
        """
        cycles = [
            (1, 27), (2, 26), (3, 25),
            (37, 54), (38, 53), (39, 52),
            (13, 15), (16, 12), (17, 11), (18, 10)
        ]
        perm_dict = self._convert_cycles_to_dict(cycles)
        self.apply_permutation(perm_dict)

    def rotate_phi_1_pi_2_z(self):
        r"""
        Поворот phi_3 = \Phi_{1}^{\frac{\pi}{2}}(z) [cite: 126]
        Вращение первой плоскости по оси Z на +90 градусов[cite: 126, 130].
        Обратный поворот к phi_1[cite: 131, 141].
        """
        cycles = [
            (1, 37, 27, 54),
            (2, 38, 26, 53),
            (3, 39, 25, 52),
            (10, 16, 18, 12),
            (13, 17, 15, 11)
        ]
        perm_dict = self._convert_cycles_to_dict(cycles)
        self.apply_permutation(perm_dict)


    def is_solved(self):
        """Проверяет, собран ли кубик (тождественная ли перестановка)[cite: 88]."""
        return self.state == list(range(0, 55))

    def print_face_simple(self, face_name, start_idx):
        """Выводит в консоль одну грань 3х3 по её начальному индексу сегмента[cite: 32]."""
        print(f"Грань {face_name}:")
        for i in range(3):
            row = [self.state[start_idx + i*3 + j] for j in range(3)]
            print(f"  {row}")

    def __repr__(self):
        """Краткое текстовое состояние кубика."""
        if self.is_solved():
            return "<RubiksCube: СОБРАН>"
        return f"<RubiksCube: Измененное состояние, первые 10 сегментов: {self.state[1:11]}>"


if __name__ == "__main__":
    print("1. Инициализируем собранный кубик...")
    cube = RubiksCube()
    print(cube)
    print(f"Кубик в исходном состоянии собран? -> {cube.is_solved()}\n")

    print("2. Выведем начальное состояние условной первой грани (индексы 1-9):")
    cube.print_face_simple("I", start_idx=1)
    
    print("\n3. Делаем поворот плоскости Z на -90 градусов (phi_1)...")
    cube.rotate_phi_1_minus_pi_2_z()
    print(cube)
    cube.print_face_simple("I", start_idx=1)
    print(f"Кубик собран? -> {cube.is_solved()}\n")

    print("4. Делаем поворот плоскости Z на +90 градусов (phi_3), чтобы вернуть в исходное состояние...")
    cube.rotate_phi_1_pi_2_z()
    print(cube)
    print(f"Кубик снова собран? -> {cube.is_solved()}")