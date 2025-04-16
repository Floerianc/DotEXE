from PyQt5.QtWidgets import QGraphicsItem, QGraphicsEllipseItem, QGraphicsScene, QGraphicsView, QApplication
from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtCore import Qt, QRectF, QTimer
import sys

class MyCircle(QGraphicsEllipseItem):
    def __init__(self, x, y, r):
        super().__init__(-r, -r, 2*r, 2*r)
        self.setPos(x, y)
        self._radius = r
        self.setBrush(QBrush(Qt.blue))
        self.setPen(QPen(Qt.black))

    def set_radius(self, r):
        if self._radius != r:
            self._radius = r
            self.setRect(-r, -r, 2*r, 2*r)  # Redefine the bounding rectangle
            self.update()  # Trigger redraw

    def radius(self):
        return self._radius

# Example setup
app = QApplication(sys.argv)
scene = QGraphicsScene()
view = QGraphicsView(scene)
# view.setRenderHint(view.renderHints())
view.setWindowTitle("Auto-updating Scene")
view.resize(400, 300)

circle = MyCircle(0, 0, 50)
scene.addItem(circle)

# Animate radius change
r = [50]
def grow():
    r[0] += 5
    if r[0] > 100: r[0] = 10
    circle.set_radius(r[0])

timer = QTimer()
timer.timeout.connect(grow)
timer.start(50)

view.show()
sys.exit(app.exec_())
