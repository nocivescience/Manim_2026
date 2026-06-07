# contagio.py
from manim import *
import numpy as np

class SimulacionContagioCompleta(Scene):
    def construct(self):
        # Para que los resultados sean iguales en cada renderizado
        np.random.seed(42) 

        # --- PARÁMETROS DE LA SIMULACIÓN ---
        N_PUNTOS = 40
        RADIUS_PUNTO = 0.12
        COLOR_SANO = BLUE
        COLOR_ENFERMO = RED
        
        VELOCIDAD_INICIAL = 2.5
        TIEMPO_RECUPERACION = 5.0  # Segundos para volver a estar sano
        TIEMPO_TOTAL = 15

        # --- CONTENEDOR (RECTÁNGULO) ---
        # Definimos el área donde rebotan las bolitas
        ANCHO_CONT = 10
        ALTO_CONT = 4.5
        contenedor = Rectangle(
            width=ANCHO_CONT, 
            height=ALTO_CONT, 
            color=WHITE, 
            stroke_opacity=0.5
        ).to_edge(DOWN, buff=0.5)

        # --- CREACIÓN DE PUNTOS ---
        puntos = VGroup()
        for i in range(N_PUNTOS):
            # Posición aleatoria dentro del rectángulo
            pos = np.array([
                np.random.uniform(-ANCHO_CONT/2 + RADIUS_PUNTO, ANCHO_CONT/2 - RADIUS_PUNTO),
                np.random.uniform(-ALTO_CONT/2 + RADIUS_PUNTO, ALTO_CONT/2 - RADIUS_PUNTO),
                0
            ]) + contenedor.get_center()
            
            p = Dot(radius=RADIUS_PUNTO, color=COLOR_SANO).move_to(pos)
            
            # Atributos físicos y de estado
            p.vel = np.array([np.random.uniform(-1, 1), np.random.uniform(-1, 1), 0])
            p.vel = (p.vel / np.linalg.norm(p.vel)) * VELOCIDAD_INICIAL
            p.enfermo = False
            p.tiempo_enfermo = 0
            
            puntos.add(p)
        
        # Infectar al Paciente Cero
        puntos[0].enfermo = True
        puntos[0].set_color(COLOR_ENFERMO)

        # --- LÓGICA DE ACTUALIZACIÓN (Física y Contagio) ---
        def update_puntos(obj, dt):
            lista = obj.submobjects
            for i, p in enumerate(lista):
                # 1. Movimiento y recuperación
                p.shift(p.vel * dt)
                if p.enfermo:
                    p.tiempo_enfermo += dt
                    if p.tiempo_enfermo >= TIEMPO_RECUPERACION:
                        p.enfermo = False
                        p.set_color(COLOR_SANO)
                        p.tiempo_enfermo = 0

                # 2. Rebote en paredes del contenedor
                c_x, c_y = contenedor.get_center()[0], contenedor.get_center()[1]
                if abs(p.get_x() - c_x) > (ANCHO_CONT/2 - RADIUS_PUNTO):
                    p.vel[0] *= -1
                    # Corrección para no traspasar la pared
                    p.set_x(np.clip(p.get_x(), c_x - ANCHO_CONT/2 + RADIUS_PUNTO, c_x + ANCHO_CONT/2 - RADIUS_PUNTO))
                
                if abs(p.get_y() - c_y) > (ALTO_CONT/2 - RADIUS_PUNTO):
                    p.vel[1] *= -1
                    p.set_y(np.clip(p.get_y(), c_y - ALTO_CONT/2 + RADIUS_PUNTO, c_y + ALTO_CONT/2 - RADIUS_PUNTO))

                # 3. Colisiones elásticas entre puntos y contagio
                for j in range(i + 1, len(lista)):
                    otro = lista[j]
                    dist_vec = p.get_center() - otro.get_center()
                    dist = np.linalg.norm(dist_vec)
                    
                    if dist < 2 * RADIUS_PUNTO:
                        # Normal del choque
                        n = dist_vec / dist
                        # Velocidad relativa
                        v_rel = p.vel - otro.vel
                        v_normal = np.dot(v_rel, n)
                        
                        if v_normal < 0:
                            # Intercambio de momento lineal (masa 1:1)
                            p.vel = p.vel - v_normal * n
                            otro.vel = otro.vel + v_normal * n
                            
                            # Contagio
                            if p.enfermo and not otro.enfermo:
                                otro.enfermo = True
                                otro.set_color(COLOR_ENFERMO)
                            elif otro.enfermo and not p.enfermo:
                                p.enfermo = True
                                p.set_color(COLOR_ENFERMO)

        puntos.add_updater(update_puntos)

        # --- GRÁFICA SUPERIOR ---
        axes = Axes(
            x_range=[0, TIEMPO_TOTAL, 2],
            y_range=[0, N_PUNTOS, 10],
            x_length=7, y_length=2,
            axis_config={"include_tip": False}
        ).to_edge(UP, buff=0.5)

        # Etiquetas con Text (Sin LaTeX para evitar errores)
        eje_x_lab = Text("Tiempo", font_size=16).next_to(axes.x_axis, DOWN, buff=0.2)
        eje_y_lab = Text("Población", font_size=16).rotate(90*DEGREES).next_to(axes.y_axis, LEFT, buff=0.2)

        # Seguimiento de datos
        def get_enfermos(): return sum(1 for p in puntos if p.enfermo)
        
        # Guardamos la trayectoria de los infectados
        path_enfermos = TracedPath(lambda: axes.c2p(self.time, get_enfermos()), stroke_width=0)
        
        # Dibujo de áreas apiladas
        grafico_dinamico = VGroup()
        
        def update_grafico(obj):
            t = self.time
            if t < 0.1 or len(path_enfermos.points) < 2: return
            
            puntos_curva = path_enfermos.points
            
            # Área Roja (Infectados - Abajo)
            pol_rojo = Polygon(
                axes.c2p(0, 0),
                *puntos_curva,
                axes.c2p(t, 0),
                fill_opacity=0.8, stroke_width=0, color=RED
            )
            
            # Área Azul (Sanos - Arriba)
            pol_azul = Polygon(
                axes.c2p(0, N_PUNTOS),
                axes.c2p(t, N_PUNTOS),
                *reversed(puntos_curva),
                axes.c2p(0, get_enfermos()), # Punto de cierre inicial aproximado
                fill_opacity=0.5, stroke_width=0, color=BLUE
            )
            obj.set_submobjects([pol_rojo, pol_azul])

        grafico_dinamico.add_updater(update_grafico)

        # --- RENDERIZADO ---
        self.add(contenedor, puntos, axes, eje_x_lab, eje_y_lab, path_enfermos, grafico_dinamico)
        self.wait(TIEMPO_TOTAL)
        
        # Detener updaters al final
        puntos.remove_updater(update_puntos)
        grafico_dinamico.remove_updater(update_grafico)