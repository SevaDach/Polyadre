from math import pi, sqrt
from functools import reduce
from operator import add
from common.r3 import R3
from common.tk_drawer import TkDrawer


class Segment:
    """ Одномерный отрезок """
    # Параметры конструктора: начало и конец отрезка (числа)

    def __init__(self, beg, fin):
        self.beg, self.fin = beg, fin

    # Отрезок вырожден?
    def is_degenerate(self):
        return self.beg >= self.fin

    # Пересечение с отрезком
    def intersect(self, other):
        if other.beg > self.beg:
            self.beg = other.beg
        if other.fin < self.fin:
            self.fin = other.fin
        return self

    # Разность отрезков
    # Разность двух отрезков всегда является списком из двух отрезков!
    def subtraction(self, other):
        return [Segment(
            self.beg, self.fin if self.fin < other.beg else other.beg),
            Segment(self.beg if self.beg > other.fin else other.fin, self.fin)]


class Edge:
    """ Ребро полиэдра """
    # Начало и конец стандартного одномерного отрезка
    SBEG, SFIN = 0.0, 1.0

    # Параметры конструктора: начало и конец ребра (точки в R3)
    def __init__(self, beg, fin):
        self.beg, self.fin = beg, fin
        # Список «просветов»
        self.gaps = [Segment(Edge.SBEG, Edge.SFIN)]

    # Учёт тени от одной грани
    def shadow(self, facet):
        # «Вертикальная» грань не затеняет ничего
        if facet.is_vertical():
            return
        # Нахождение одномерной тени на ребре
        shade = Segment(Edge.SBEG, Edge.SFIN)
        for u, v in zip(facet.vertexes, facet.v_normals()):
            shade.intersect(self.intersect_edge_with_normal(u, v))
            if shade.is_degenerate():
                return

        shade.intersect(
            self.intersect_edge_with_normal(
                facet.vertexes[0], facet.h_normal()))
        if shade.is_degenerate():
            return
        # Преобразование списка «просветов», если тень невырождена
        gaps = [s.subtraction(shade) for s in self.gaps]
        self.gaps = [
            s for s in reduce(add, gaps, []) if not s.is_degenerate()]

    # Преобразование одномерных координат в трёхмерные
    def r3(self, t):
        return self.beg * (Edge.SFIN - t) + self.fin * t

    # Пересечение ребра с полупространством, задаваемым точкой (a)
    # на плоскости и вектором внешней нормали (n) к ней
    def intersect_edge_with_normal(self, a, n):
        f0, f1 = n.dot(self.beg - a), n.dot(self.fin - a)
        if f0 >= 0.0 and f1 >= 0.0:
            return Segment(Edge.SFIN, Edge.SBEG)
        if f0 < 0.0 and f1 < 0.0:
            return Segment(Edge.SBEG, Edge.SFIN)
        x = - f0 / (f1 - f0)
        return Segment(Edge.SBEG, x) if f0 < 0.0 else Segment(x, Edge.SFIN)


class Facet:
    """ Грань полиэдра """
    # Параметры конструктора: список вершин

    def __init__(self, vertexes):
        self.vertexes = vertexes

    # «Вертикальна» ли грань?
    def is_vertical(self):
        return self.h_normal().dot(Polyedr.V) == 0.0

    # Нормаль к «горизонтальному» полупространству
    def h_normal(self):
        n = (
            self.vertexes[1] - self.vertexes[0]).cross(
            self.vertexes[2] - self.vertexes[0])
        return n * (-1.0) if n.dot(Polyedr.V) < 0.0 else n

    # Нормали к «вертикальным» полупространствам, причём k-я из них
    # является нормалью к грани, которая содержит ребро, соединяющее
    # вершины с индексами k-1 и k
    def v_normals(self):
        return [self._vert(x) for x in range(len(self.vertexes))]

    # Вспомогательный метод
    def _vert(self, k):
        n = (self.vertexes[k] - self.vertexes[k - 1]).cross(Polyedr.V)
        return n * \
            (-1.0) if n.dot(self.vertexes[k - 1] - self.center()) < 0.0 else n

    # Центр грани
    def center(self):
        return sum(self.vertexes, R3(0.0, 0.0, 0.0)) * \
            (1.0 / len(self.vertexes))

def pl(tochki1,c):
    tochki = []
    for i in range(len(tochki1)):
        tochki.append(tochki1[i].__mul__(1/c))
    v1 = R3(tochki[0].x, tochki[0].y, tochki[0].z)
    ppl = 0
    for i in range(1, len(tochki)-1):
            
            
            
        v2 = R3(tochki[i].x, tochki[i].y, tochki[i].z)
        v3 = R3(tochki[i+1].x, tochki[i+1].y, tochki[i+1].z)
            
        v2v1 = R3(v2.x - v1.x, v2.y-v1.y, v2.z-v1.z)
        v3v1 = R3(v3.x - v1.x, v3.y-v1.y, v3.z-v1.z)
            #bb = R3(tochki[i-1].x-tochki[i].x, tochki[i-1].y-tochki[i].y, tochki[i-1].z-tochki[i].z)
        cc=  0.5*sqrt(v2v1.cross(v3v1).x*v2v1.cross(v3v1).x       +v2v1.cross(v3v1).y*v2v1.cross(v3v1).y    +v2v1.cross(v3v1).z*v2v1.cross(v3v1).z)
        ppl += cc
    return ppl

class Polyedr:
    """ Полиэдр """
    # вектор проектирования
    V = R3(0.0, 0.0, 1.0)

    # Параметры конструктора: файл, задающий полиэдр
    def __init__(self, file):
        self.ploschad = 0
        # списки вершин, рёбер и граней полиэдра
        self.vertexes, self.edges, self.facets = [], [], []
        
        self.plohie = []
        self.plohiexxx = []
        self.plohieyyy = []
        self.plohiezzz = []
        
        # список строк файла
        with open(file) as f:
            for i, line in enumerate(f):
                if i == 0:
                    # обрабатываем первую строку; buf - вспомогательный массив
                    buf = line.split()
                    # коэффициент гомотетии
                    c = float(buf.pop(0))
                    # углы Эйлера, определяющие вращение
                    alpha, beta, gamma = (float(x) * pi / 180.0 for x in buf)
                elif i == 1:
                    # во второй строке число вершин, граней и рёбер полиэдра
                    nv, nf, ne = (int(x) for x in line.split())
                elif i < nv + 2:
                    # задание всех вершин полиэдра
                    x, y, z = (float(x) for x in line.split())
                    
                    rasst = abs(x-2)
                    if rasst >= 1:
                        #print('plohaia')
                        self.plohie.append(R3(x, y, z).rz(
                        alpha).ry(beta).rz(gamma) * c)
                    
                    for i in range(len(self.plohie)):
                        self.plohiexxx.append(self.plohie[i].x)
                        self.plohieyyy.append(self.plohie[i].y)
                        self.plohiezzz.append(self.plohie[i].z)                    
                    
                    self.vertexes.append(R3(x, y, z).rz(
                        alpha).ry(beta).rz(gamma) * c)
                else:
                    # вспомогательный массив
                    buf = line.split()
                    # количество вершин очередной грани
                    size = int(buf.pop(0))
                    # массив вершин этой грани
                    vertexes = list(self.vertexes[int(n) - 1] for n in buf)
                    
                    schetcik_plohih_v_grane = 0

                    for i in range(len(vertexes)):
                        if vertexes[i].x in self.plohiexxx and vertexes[i].y in self.plohieyyy and vertexes[i].z in self.plohiezzz:
                            
                            
                            
                            
                            #print('suka')
                            schetcik_plohih_v_grane +=1
                    #print(schetcik_plohih_v_grane, len(vertexes))
                                      
                    
                    if schetcik_plohih_v_grane == len(vertexes):
                        #print('suka')
                        self.ploschad += pl(vertexes,c)
                                        
                    
                    # задание рёбер грани
                    for n in range(size):
                        self.edges.append(Edge(vertexes[n - 1], vertexes[n]))
                    # задание самой грани
                    self.facets.append(Facet(vertexes))

    # Метод изображения полиэдра
    def draw(self, tk):
        tk.clean()
        for e in self.edges:
            for f in self.facets:
                e.shadow(f)
            for s in e.gaps:
                tk.draw_line(e.r3(s.beg), e.r3(s.fin))
        print('Сумма лощадей граней, все вершины которых не являются "хорошими" точками =', round(self.ploschad,1))