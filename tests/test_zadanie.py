from pytest import approx
from math import sqrt
from shadow.polyedr import Polyedr


class TestPolyedr:

    def test_polyedr_1(self):
        assert Polyedr(f"data/cube.geom").ploschad == approx(6.0)

    def test_polyedr_2(self):
        assert Polyedr(f"data/ccc.geom").ploschad == approx(50.0)

    def test_polyedr_3(self):
        assert Polyedr(f"data/cube2.geom").ploschad == approx(0.0)

    def test_polyedr_4(self):
        assert Polyedr(f"data/box.geom").ploschad == approx(5.0)

    def test_polyedr_5(self):
        assert Polyedr(f"data/cube3.geom").ploschad == approx(1.0)

    # python -B -m pytest -p no:cacheprovider tests/test_polyedr.py
