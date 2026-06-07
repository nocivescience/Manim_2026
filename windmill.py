# windmill.py
from manim import *
class Windmill(Scene):
    dicc={
        'windmill_length': config['frame_height'] * 2,
        'style_windmill': {
            'stroke_color': WHITE,
            'stroke_width': 2,
        },
        'dot_config': {
            'fill_color': RED,
            'radius': 0.04,
            'background_stroke_color': 'black',
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
        line=Line(LEFT,RIGHT)
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
        pivot_dot= Dot(color=color)
        pivot_dot.add_updater(lambda d: d.move_to(windmill.pivot))
        return pivot_dot
    def start_leaving_shadow(self):
        self.leave_shadow=True
        self.add(self.get_windmill_shadow())
    def get_windmill_shadow(self):
        if not hasattr(self, 'leave_shadow'):
            self.windmill_shadow=VGroup()
        return self.windmill_shadow
    def get_dots(self, points):
        return VGroup(*[Dot(p, **self.dicc['dot_config']) for p in points])
    def nex_pivot_and_angle(self, windmill):
        curr_angle=windmill.get_angle()
        pivot=windmill.pivot
        non_pivot_points=list(filter(lambda p: not np.all(p==pivot), windmill.point_set))
        angles=np.array([-(angle_of_vector(p-pivot)- curr_angle)%PI for p in windmill.point_set])
        tiny_indices=angles<0.00001 # 0.01 radian = 0.57 degrees corrige esto
        if np.all(tiny_indices):  # corrige
            return non_pivot_points[0], PI # corrige
        angles[tiny_indices]=PI
        index=np.argmin(angles)
        print('index: ', index)
        print('angles[index]: ', angles[index])
        return non_pivot_points[index], angles[index] # corrige
    def rotate_to_next_pivot(self, windmill, max_time= None, added_anims=None):
        new_pivot, angle=self.nex_pivot_and_angle(windmill)
        print('angles: ', angle)
        change_pivot_at_end=True
        if added_anims is None:
            added_anims=[]
        run_time=angle/windmill.rot_speed
        
        if max_time is not None and run_time>max_time:
            ratio=max_time/run_time
            rate_func=(lambda t: ratio*t)
            run_time=max_time
            change_pivot_at_end=False
        else:
            rate_func=linear
        for anim in added_anims:
            if anim.run_time>run_time:
                anim.run_time=run_time
        self.play(
            Rotate(windmill, -angle, run_time=run_time, rate_func=rate_func), *added_anims
        )
        if change_pivot_at_end:
            self.handle_pivot_change(windmill, new_pivot)
        return [self.get_hit_flash(windmill)], run_time
    def handle_pivot_change(self, windmill, new_pivot):
        windmill.pivot=new_pivot
    def let_windmill_run(self, windmill, time):
        anims_from_last_hit=[]
        while time>0:
            anims_from_last_hit, last_run_time=self.rotate_to_next_pivot(windmill, max_time=time, added_anims=anims_from_last_hit)
            time-=last_run_time
    def add_dot_color_updaer(self, dots, windmill, **kwargs):
        for dot in dots:
            dot.add_updater(lambda d: self.update_dot_color(d, windmill, **kwargs))
    def update_dot_color(self, dot, windmill, color1=BLUE, color2=RED):
        perp=rotate_vector(windmill.get_vector(), TAU/4)
        dot_product=np.dot(perp, dot.get_center()-windmill.pivot)
        if dot_product>0:
            dot.set_color(color1)
        else:
            dot.set_color(color2)
        dot.set_stroke(WHITE, width=2)
    def get_hit_flash(self, point): # corrige
        flash= Flash(point, line_length=0.1, flash_radius=0.7, color=WHITE, remove=True)
        return flash

class IntroduceWindmill(Windmill):
    DICC={
        'final_run_time': 20,
    }
    def construct(self):
        self.add_points()
        self.add_line()
        self.continue_and_count()
    def add_points(self):
        points=self.get_random_point_set(11)
        dots=self.get_dots(points)
        self.dots=dots
    def add_line(self):
        dots=self.dots
        points= np.array(list(map(lambda d: d.get_center(), dots))) # corrige
        windmill=self.get_windmill(points, pivot=points[0], angle=TAU/6)
        p0= points[0]
        pivot_dot=self.get_pivot_dot(windmill)
        self.play(Create(windmill), Create(dots), Create(pivot_dot))
        next_pivot, angle=self.nex_pivot_and_angle(windmill)
        self.play(Rotate(windmill, -angle*.99, about_point=p0, rate_func=linear))
        self.pivot2=next_pivot
        self.pivot_dot=pivot_dot
        self.windmill=windmill
    def continue_and_count(self):
        windmill=self.windmill
        pivot_dot=self.pivot_dot
        self.add(windmill.copy().fade(.75), pivot_dot.copy().fade(.75))
        windmill.rot_speed*=2
        self.let_windmill_run(windmill, self.DICC['final_run_time'])
        
        
