# punto_moviendose_sobre_recta.py
from manim import *

class PuntoConRecta(Scene):
    def construct(self):
        np.random.seed(2)
        cuenta = 0
        self.x_tracker = ValueTracker(-2)
        recta = self.set_recta(-12, 12)
        punto = self.set_punto(recta)
        nota = self. anotacion(punto)
        self.play(
            Create(recta),
            Create(punto),
            Write(nota),
        )
        self.wait()
        while cuenta < 5:
            rand = np.random.random_integers(-12, 12)
            self.play(self.x_tracker.animate.set_value(rand))
            cuenta+=1
        self.wait()
    def set_recta(self, x_min, x_max):
        recta = NumberLine(
            x_range= [x_min, x_max+1, 1],
            include_numbers=True,
            tick_size= 0.1,
            font_size=12,
            longer_tick_multiple=.4,
            numbers_with_elongated_ticks=np.arange(-12,12,2),
            length= 8,
            stroke_width=.5
        )
        return recta
    def set_punto(self, recta):
        punto = Dot(color= RED)
        punto.move_to(recta.n2p(self.x_tracker.get_value()))
        punto.add_updater(lambda t: t.move_to(recta.n2p(self.x_tracker.get_value())))
        return punto
    def anotacion(self, dot):
        nota = DecimalNumber(self.x_tracker.get_value(), num_decimal_places=2, font_size =13)
        nota.next_to(dot.get_center(), UP, buff= 0.3)
        def update_nota(mob):
            mob.set_value(self.x_tracker.get_value())
            mob.next_to(dot.get_center(), UP, buff= 0.3)
        nota.add_updater(lambda t: update_nota(t))
        return nota
    def set_grupo(self):
        grupo = VGroup()
        for _, r in zip(range(0,2), [[-12, 12, 1], [-1,1,.2]]):
            recta = self.set_recta(r[0], r[1], r[2])
        grupo.to_edge(UP, buff=.3)
        grupo.arrange(DOWN, buff=.2)
        return