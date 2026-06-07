from manim import *
import numpy as np

class Windmill(Scene):
    dicc={
        'windmill_length': config['frame_height'] * 2,
        'style_windmill': {
            'stroke_color': WHITE,
            'stroke_width': 2,
        },
        'dot_config': {
            'fill_color': RED,
            'radius': 0.08, # Un poco más grande para que se vea bien
        },
        'windmill_speed': .25,
        'leave_shadow': False,
    }
    
    def get_random_point_set(self, n_points=11, width=5, height=5):
        return np.array([
            [np.random.uniform(-width / 2, width / 2), np.random.uniform(-height / 2, height / 2), 0]
            for _ in range(n_points)
        ])
        
    def get_windmill(self, points, pivot=None, angle=TAU/6):
        line=Line(LEFT, RIGHT)
        line.set_angle(angle)
        line.set_length(self.dicc['windmill_length'])
        line.set_style(**self.dicc['style_windmill'])
        line.point_set=points
        if pivot is not None:
            line.pivot=pivot
        else:
            line.pivot=points[0]
        line.rot_speed= self.dicc['windmill_speed']
        line.add_updater(lambda l: l.move_to(l.pivot))
        return line
        
    def get_pivot_dot(self, windmill, color=YELLOW):
        pivot_dot= Dot(color=color, radius=0.1)
        pivot_dot.add_updater(lambda d: d.move_to(windmill.pivot))
        return pivot_dot
        
    def get_dots(self, points):
        # << CORREGIDO: Simplificado temporalmente para evitar errores con Integer
        return VGroup(*[Dot(p, **self.dicc['dot_config']) for p in points])

    def next_pivot_and_angle(self, windmill):
        curr_angle = windmill.get_angle()
        pivot = windmill.pivot
        points = windmill.point_set
        
        # << CORREGIDO: Cálculo de ángulos vectoriales consistentes respecto al pivote
        angles = np.array([
            -(angle_of_vector(p - pivot) - curr_angle) % PI 
            for p in points
        ])
        
        # Para evitar que el propio pivote sea elegido (su ángulo sería 0 o muy cercano)
        # le asignamos un ángulo falso muy grande (como PI)
        for i, p in enumerate(points):
            if np.allclose(p, pivot):
                angles[i] = PI
                
        # Tolerancia para evitar que el molino se quede atascado en el mismo punto recién tocado
        tiny_indices = angles < 0.0001
        angles[tiny_indices] = PI
        
        index = np.argmin(angles)
        return points[index], angles[index]

    def rotate_to_next_pivot(self, windmill, max_time= None, added_anims=None):
        new_pivot, angle = self.next_pivot_and_angle(windmill)
        
        if added_anims is None:
            added_anims=[]
        run_time = angle / windmill.rot_speed
        
        change_pivot_at_end = True
        if max_time is not None and run_time > max_time:
            ratio = max_time / run_time
            rate_func = (lambda t: ratio * t)
            run_time = max_time
            change_pivot_at_end = False
        else:
            rate_func = linear
            
        for anim in added_anims:
            if anim.run_time > run_time:
                anim.run_time = run_time
                
        self.play(
            Rotate(windmill, -angle, run_time=run_time, rate_func=rate_func), *added_anims
        )
        
        if change_pivot_at_end:
            self.handle_pivot_change(windmill, new_pivot)
            # << CORREGIDO: Pasamos "new_pivot" (las coordenadas) al destello, no el objeto windmill
            return [self.get_hit_flash(new_pivot)], run_time
            
        return [], run_time

    def handle_pivot_change(self, windmill, new_pivot):
        windmill.pivot = new_pivot

    def let_windmill_run(self, windmill, time):
        anims_from_last_hit = []
        while time > 0:
            anims_from_last_hit, last_run_time = self.rotate_to_next_pivot(
                windmill, max_time=time, added_anims=anims_from_last_hit
            )
            time -= last_run_time

    def get_hit_flash(self, point): 
        # << CORREGIDO: Ajustado para que el destello se posicione exactamente sobre el punto de colisión
        flash = Flash(point, line_length=0.1, flash_radius=0.3, color=WHITE, run_time=0.5)
        return flash

class IntroduceWindmill(Windmill):
    DICC = {
        'final_run_time': 15,
    }
    def construct(self):
        self.add_points()
        self.add_line()
        self.continue_and_count()
        
    def add_points(self):
        points = self.get_random_point_set(11)
        dots = self.get_dots(points)
        self.dots = dots
        
    def add_line(self):
        dots = self.dots
        points = np.array(list(map(lambda d: d.get_center(), dots))) 
        windmill = self.get_windmill(points, pivot=points[0], angle=TAU/6)
        
        p0 = points[0]
        pivot_dot = self.get_pivot_dot(windmill)
        
        # Agregamos los puntos primero para que la línea pase sobre/bajo ellos de forma fluida
        self.add(dots)
        self.play(Create(windmill), Create(pivot_dot))
        
        next_pivot, angle = self.next_pivot_and_angle(windmill)
        self.play(Rotate(windmill, -angle * 0.99, about_point=p0, rate_func=linear))
        
        self.pivot2 = next_pivot
        self.pivot_dot = pivot_dot
        self.windmill = windmill
        
    def continue_and_count(self):
        windmill = self.windmill
        pivot_dot = self.pivot_dot
        
        self.add(windmill.copy().fade(.75), pivot_dot.copy().fade(.75))
        windmill.rot_speed *= 2.5 # Aceleramos un poco para la demostración continua
        self.let_windmill_run(windmill, self.DICC['final_run_time'])