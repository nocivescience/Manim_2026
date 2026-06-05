from manim import *
class RectaNumerica(Scene):
    def construct(self):
        track = ValueTracker(0)
        track_1 = track.get_value()
        track_2 = np.sin(track.get_value())*11
        track_3 = np.cos(track.get_value())*5
        tracks = [track_1, track_2, track_3]
        recta_1 = self.recta_tipo(-10, 10, PI/7).move_to(3*LEFT+2*UP)
        recta_2 = self.recta_tipo(-12,12, 0).move_to(2*DOWN)
        recta_3 = self.recta_tipo(-8,8).move_to(3*RIGHT+ 2*UP)
        rects= Group(recta_1, recta_2, recta_3)
        vector_1 = self.set_vectores(rects, tracks)
        self.play(Create(recta_1), Create(recta_2), Create(recta_3), DrawBorderThenFill(vector_1))
        self.play(track.animate.set_value(2))
        self.wait()
    def recta_tipo(self, x_min, x_max,rot=-PI/8):
        recta = NumberLine(
            x_range= [x_min, x_max, 2],
            tick_size=0.1,
            length = 4,
            include_numbers=True,
            include_tip= True,
            font_size= 13,
            stroke_width=1,
            unit_size=.1,
            rotation= rot,
        )
        return recta
    def set_vectores(self, rects, tracks):
        vectores = VGroup()
        for rect, track in zip(rects, tracks):
            vector = Arrow(
                stroke_width=.8,
                max_stroke_width_to_length_ratio=.1,
                max_tip_length_to_length_ratio=.1,
            )
            vector.rotate(-PI/2)
            vector.move_to(
                rect.n2p(track), vector.get_end()
            )
            vector.add_updater(
                lambda t: vector.move_to(rect.n2p(track))
            )
            vectores.add(vector)
        return(vectores)