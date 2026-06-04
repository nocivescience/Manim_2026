from manim import *
class BallScene(Scene):
    def construct(self):
        circulo = Circle(radius= .5)
        x_tracker = ValueTracker(0)
        
        self.wait()