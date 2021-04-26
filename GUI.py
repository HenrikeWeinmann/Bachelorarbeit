import sys
from PyQt6.QtWidgets import QApplication, QWidget

app = QApplication(sys.argv)

widget = QWidget()

widget.show()

sys.exit(app.exec())