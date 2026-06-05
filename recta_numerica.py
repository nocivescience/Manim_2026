from manim import *
import numpy as np

class RectaNumerica(Scene):
    def construct(self):
        # 1. El ValueTracker principal
        track = ValueTracker(0)

        # 2. Creamos las rectas
        recta_1 = self.recta_tipo(-10, 10, PI/7).move_to(3*LEFT + 2*UP)
        recta_2 = self.recta_tipo(-12, 12, 0).move_to(2*DOWN)
        recta_3 = self.recta_tipo(-8, 8).move_to(3*RIGHT + 2*UP)
        
        # 3. Definimos las funciones matemáticas dinámicas para cada recta
        # Pasamos lambdas que leen el tracker en tiempo real
        funciones = [
            lambda: track.get_value(),
            lambda: np.sin(track.get_value()) * 11,
            lambda: np.cos(track.get_value()) * 5
        ]
        
        rects = [recta_1, recta_2, recta_3]
        
        # 4. Construimos los vectores usando always_redraw
        vectores = self.set_vectores(rects, funciones)

        # Animación
        self.play(
            Create(recta_1), 
            Create(recta_2), 
            Create(recta_3), 
            FadeIn(vectores) # Usamos FadeIn ya que always_redraw maneja la creación continua
        )
        self.wait(1)
        
        # Al mover el track, las funciones se recalculan solas y las flechas se redibujan en su sitio
        self.play(track.animate.set_value(2), run_time=4)
        self.wait()

    def recta_tipo(self, x_min, x_max, rot=-PI/8):
        recta = NumberLine(
            x_range=[x_min, x_max, 2],
            tick_size=0.1,
            length=4,
            include_numbers=True,
            include_tip=True,
            font_size=13,
            stroke_width=1,
            rotation=rot,
        )
        return recta

    def set_vectores(self, rects, funciones):
        vectores = VGroup()
        
        # Usamos un bucle para añadir cada vector individualmente con su comportamiento
        for rect, func in zip(rects, funciones):
            # 'always_redraw' recrea la flecha en cada frame basándose en la posición actual
            vector_dinamico = always_redraw(
                lambda r=rect, f=func: Arrow(
                    start=r.n2p(f()) + UP * 0.5, # Un poco arriba de la recta elegida
                    end=r.n2p(f()),             # Apuntando directo al número exacto
                    stroke_width=1.2,
                    max_stroke_width_to_length_ratio=1,
                    max_tip_length_to_length_ratio=0.3,
                    buff=0,
                    color=YELLOW
                )
            )
            vectores.add(vector_dinamico)
            
        return vectores