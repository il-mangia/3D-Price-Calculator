prezzo_corrente = 0.25 # Prezzo corrente per unità di energia in euro/kWh
prezzo_tpa = 13 # Prezzo TPA per unità di materiale di stampa in euro/kg
costo_progettazione = 5 # Costo di progettazione del modello 3D in euro/ora
# Potenza di riferimento impostata a 1300 W
potenza_stampante_w = 1300

import math
import sys

try:
    from PyQt6.QtWidgets import (
        QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
        QGridLayout, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QSpinBox
    )
    from PyQt6.QtGui import QFont
    from PyQt6.QtCore import Qt
except Exception as e:
    raise RuntimeError("PyQt6 is required to run this application. Install with: pip install PyQt6") from e


def euro(v):
    return f"{v:.2f} €"


class PriceCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calcolo Prezzo Stampa 3D")
        self.setMinimumSize(720, 560)
        self._build_ui()
        self.last_receipt = None

    def _build_ui(self):
        main_layout = QVBoxLayout()
        header = QLabel("Calcolo Prezzo Stampa 3D")
        header.setFont(QFont('Helvetica', 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(10)

        # Time inputs: ore e minuti
        grid.addWidget(QLabel("Tempo di stampa - Ore:"), 0, 0)
        self.ore_edit = QLineEdit("0")
        self.ore_edit.setFixedWidth(80)
        grid.addWidget(self.ore_edit, 0, 1)

        grid.addWidget(QLabel("Minuti:"), 0, 2)
        self.minuti_edit = QLineEdit("0")
        self.minuti_edit.setFixedWidth(80)
        grid.addWidget(self.minuti_edit, 0, 3)

        # Grammi
        grid.addWidget(QLabel("Grammi usati (g):"), 1, 0)
        self.grammi_edit = QLineEdit("0")
        self.grammi_edit.setFixedWidth(120)
        grid.addWidget(self.grammi_edit, 1, 1)

        # Ore progettazione
        grid.addWidget(QLabel("Ore progettazione 3D (ore):"), 2, 0)
        self.prog_edit = QLineEdit("0")
        self.prog_edit.setFixedWidth(120)
        grid.addWidget(self.prog_edit, 2, 1)

        # Numero pezzi
        grid.addWidget(QLabel("Numero pezzi:"), 3, 0)
        self.num_spin = QSpinBox()
        self.num_spin.setMinimum(1)
        self.num_spin.setValue(1)
        grid.addWidget(self.num_spin, 3, 1)

        # Note: potenza è fissa nel codice e non mostrata

        main_layout.addLayout(grid)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        self.calc_btn = QPushButton("Calcola")
        self.calc_btn.clicked.connect(self.calculate)
        btn_layout.addWidget(self.calc_btn)

        self.export_btn = QPushButton("Esporta TXT")
        self.export_btn.clicked.connect(self.export_txt)
        btn_layout.addWidget(self.export_btn)

        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # Receipt area
        self.receipt = QTextEdit()
        self.receipt.setReadOnly(True)
        self.receipt.setFont(QFont('Courier', 10))
        main_layout.addWidget(self.receipt)

        footer = QLabel("Nota: prezzi calcolati e arrotondati per eccesso al prossimo euro.")
        footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        footer.setStyleSheet('color: gray; font-size: 10pt')
        main_layout.addWidget(footer)

        self.setLayout(main_layout)

    def calculate(self):
        try:
            ore = float(self.ore_edit.text() or 0.0)
            minuti = float(self.minuti_edit.text() or 0.0)
            grammi = float(self.grammi_edit.text() or 0.0)
            proj_ore = float(self.prog_edit.text() or 0.0)
            n_pezzi = int(self.num_spin.value() or 1)
        except ValueError:
            QMessageBox.warning(self, "Input non valido", "Assicurati di inserire numeri validi.")
            return

        tempo = ore + (minuti / 60.0)

        material_cost = prezzo_tpa * (grammi / 1000.0)
        energy_kwh = (potenza_stampante_w / 1000.0) * tempo
        energy_cost = prezzo_corrente * energy_kwh
        design_cost = costo_progettazione * proj_ore

        per_piece_subtotal = material_cost + energy_cost + design_cost
        total_subtotal = per_piece_subtotal * n_pezzi

        # arrotonda sempre per eccesso al prossimo euro
        rounded_total = math.ceil(total_subtotal)
        arrotondamento = rounded_total - total_subtotal
        prezzo_per_pezzo = rounded_total / n_pezzi

        lines = []
        lines.append("--- SCONTRINO STAMPA 3D ---")
        lines.append(f"Pezzi: {n_pezzi}")
        lines.append("")
        lines.append(f"Costo materiale (per pezzo, {grammi:.0f} g): {euro(material_cost)}")
        lines.append(f"Costo energia (per pezzo, {energy_kwh:.3f} kWh): {euro(energy_cost)}")
        lines.append(f"Costo progettazione (per pezzo, {proj_ore:.2f} h): {euro(design_cost)}")
        lines.append(f"Subtotale (per pezzo): {euro(per_piece_subtotal)}")
        lines.append("")
        lines.append(f"Subtotale totale: {euro(total_subtotal)}")
        lines.append(f"Arrotondamento: {euro(arrotondamento)}")
        lines.append(f"TOTALE: {rounded_total:.0f} €")
        lines.append("")
        lines.append(f"Prezzo per singolo elemento: {prezzo_per_pezzo:.2f} €")

        receipt_text = "\n".join(lines)
        self.last_receipt = receipt_text
        self.receipt.setPlainText(receipt_text)

    def export_txt(self):
        if not self.last_receipt:
            QMessageBox.warning(self, "Nessun calcolo", "Esegui prima il calcolo per generare lo scontrino.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Salva scontrino", "scontrino_stampa3d.txt", "Text files (*.txt);;All files (*)")
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.last_receipt)
            QMessageBox.information(self, "Esportato", f"Scontrino esportato in: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Errore salvataggio", f"Impossibile salvare file: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = PriceCalculator()
    w.show()
    sys.exit(app.exec())
