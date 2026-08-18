# -*- coding: utf-8 -*-
"""
Calcolo Prezzo Stampa 3D — profili, checkbox e multilingua
----------------------------------------------------------
- Profili stampante in JSON nella cartella "profiles"
  (es. "Artillery Genius" -> profiles/artillery_genius.json)
- Ogni profilo contiene: nome, costo corrente, consumo stampante,
  costo materiale, costo orario progettazione, consumo W del PC
- Checkbox: arrotondamento (nascosto dentro il costo energia),
  includere o no le ore di progettazione
- Scontrino in testo semplice, pronto per il copia-incolla su WhatsApp
- Multilingua: legge languages.json (en default, it, es, fr);
  la lingua scelta viene ricordata in config.json
"""

import json
import math
import re
import sys
import unicodedata
from pathlib import Path

try:
    from PyQt6.QtWidgets import (
        QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
        QGridLayout, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox,
        QSpinBox, QComboBox, QDialog, QDoubleSpinBox, QListWidget,
        QDialogButtonBox, QGroupBox, QCheckBox
    )
    from PyQt6.QtGui import QFont, QGuiApplication
    from PyQt6.QtCore import Qt
except Exception as e:
    raise RuntimeError(
        "PyQt6 is required to run this application. Install with: pip install PyQt6"
    ) from e

# ----------------------------------------------------------------------
# Percorsi e valori predefiniti
# ----------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
PROFILES_DIR = BASE_DIR / "profiles"
LANG_FILE = BASE_DIR / "languages.json"
CONFIG_FILE = BASE_DIR / "config.json"

DEFAULT_PROFILE = {
    "nome": "Default",
    "costo_corrente": 0.25,      # €/kWh
    "consumo_w": 1300.0,         # W stampante
    "costo_materiale": 13.0,     # €/kg
    "costo_progettazione": 5.0,  # €/h
    "consumo_pc_w": 150.0,       # W del PC durante la progettazione
}

# Fallback minimo se languages.json manca (inglese)
FALLBACK_LANG = {"en": {"_name": "English"}}


# ----------------------------------------------------------------------
# Utility
# ----------------------------------------------------------------------

def euro(v: float) -> str:
    return f"{v:.2f} €"


def slugify(nome: str) -> str:
    """'Artillery Genius' -> 'artillery_genius'"""
    nome = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode("ascii")
    nome = nome.strip().lower()
    nome = re.sub(r"[^a-z0-9]+", "_", nome)
    return nome.strip("_") or "profile"


def load_languages() -> dict:
    try:
        with open(LANG_FILE, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        if isinstance(data, dict) and data:
            return data
    except Exception:
        pass
    return dict(FALLBACK_LANG)


def load_config() -> dict:
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as fp:
            return json.load(fp)
    except Exception:
        return {}


def save_config(cfg: dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as fp:
            json.dump(cfg, fp, indent=2, ensure_ascii=False)
    except Exception:
        pass


def load_profiles() -> dict:
    """{nome_profilo: dati} da tutti i .json in /profiles."""
    PROFILES_DIR.mkdir(exist_ok=True)
    profiles = {}
    for f in sorted(PROFILES_DIR.glob("*.json")):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                d = json.load(fp)
            nome = d.get("nome") or f.stem
            profiles[nome] = {
                "nome": nome,
                "costo_corrente": float(d.get("costo_corrente", DEFAULT_PROFILE["costo_corrente"])),
                "consumo_w": float(d.get("consumo_w", DEFAULT_PROFILE["consumo_w"])),
                "costo_materiale": float(d.get("costo_materiale", DEFAULT_PROFILE["costo_materiale"])),
                "costo_progettazione": float(d.get("costo_progettazione", DEFAULT_PROFILE["costo_progettazione"])),
                "consumo_pc_w": float(d.get("consumo_pc_w", DEFAULT_PROFILE["consumo_pc_w"])),
                "_file": str(f),
            }
        except Exception:
            continue
    return profiles


def save_profile(d: dict) -> Path:
    PROFILES_DIR.mkdir(exist_ok=True)
    path = PROFILES_DIR / f"{slugify(d['nome'])}.json"
    to_save = {k: d[k] for k in (
        "nome", "costo_corrente", "consumo_w", "costo_materiale",
        "costo_progettazione", "consumo_pc_w"
    )}
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(to_save, fp, indent=2, ensure_ascii=False)
    return path


# ----------------------------------------------------------------------
# Stylesheet
# ----------------------------------------------------------------------
STYLE = """
QWidget {
    background-color: #1e2430;
    color: #e8ecf1;
    font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
    font-size: 11pt;
}
QLabel#header {
    color: #7fd4ff;
    font-size: 20pt;
    font-weight: bold;
    padding: 8px;
}
QLabel#footer { color: #8a93a5; font-size: 9pt; }
QGroupBox {
    border: 1px solid #3a4356;
    border-radius: 10px;
    margin-top: 14px;
    padding: 10px;
    font-weight: bold;
    color: #a8c7e8;
}
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #2a3242;
    border: 1px solid #3f4a60;
    border-radius: 6px;
    padding: 6px 8px;
    selection-background-color: #4a90d9;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid #4a90d9;
}
QComboBox::drop-down { border: none; width: 26px; }
QComboBox QAbstractItemView {
    background-color: #2a3242;
    border: 1px solid #3f4a60;
    selection-background-color: #4a90d9;
}
QCheckBox { spacing: 8px; }
QCheckBox::indicator {
    width: 18px; height: 18px;
    border: 1px solid #3f4a60;
    border-radius: 4px;
    background-color: #2a3242;
}
QCheckBox::indicator:checked { background-color: #2f8f5b; border-color: #2f8f5b; }
QPushButton {
    background-color: #3b4a63;
    border: none;
    border-radius: 8px;
    padding: 9px 18px;
    font-weight: bold;
}
QPushButton:hover { background-color: #4a5d7d; }
QPushButton:pressed { background-color: #33415a; }
QPushButton#primary { background-color: #2f8f5b; }
QPushButton#primary:hover { background-color: #37a56a; }
QPushButton#danger { background-color: #8f3a3a; }
QPushButton#danger:hover { background-color: #a54646; }
QTextEdit {
    background-color: #141922;
    border: 1px solid #3a4356;
    border-radius: 10px;
    padding: 10px;
    color: #d7f0e2;
}
QListWidget {
    background-color: #2a3242;
    border: 1px solid #3f4a60;
    border-radius: 8px;
}
"""


# ----------------------------------------------------------------------
# Dialog impostazioni / profili
# ----------------------------------------------------------------------
class SettingsDialog(QDialog):
    def __init__(self, tr, parent=None):
        super().__init__(parent)
        self.tr_ = tr  # funzione di traduzione
        self.setWindowTitle(tr("dlg_title"))
        self.setMinimumSize(600, 480)
        self._build_ui()
        self._reload_list()

    def _build_ui(self):
        tr = self.tr_
        layout = QHBoxLayout(self)

        # ---- colonna sinistra: lista profili
        sx = QVBoxLayout()
        sx.addWidget(QLabel(tr("saved_profiles")))
        self.lista = QListWidget()
        self.lista.currentTextChanged.connect(self._load_in_form)
        sx.addWidget(self.lista)

        self.btn_delete = QPushButton(tr("delete_profile"))
        self.btn_delete.setObjectName("danger")
        self.btn_delete.clicked.connect(self._delete)
        sx.addWidget(self.btn_delete)
        layout.addLayout(sx, 1)

        # ---- colonna destra: form
        dx = QVBoxLayout()
        box = QGroupBox(tr("profile_data"))
        form = QGridLayout(box)
        form.setVerticalSpacing(10)

        r = 0
        form.addWidget(QLabel(tr("profile_name")), r, 0)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(tr("name_placeholder"))
        form.addWidget(self.name_edit, r, 1); r += 1

        form.addWidget(QLabel(tr("energy_cost")), r, 0)
        self.energy_spin = QDoubleSpinBox()
        self.energy_spin.setDecimals(3)
        self.energy_spin.setRange(0.0, 10.0)
        self.energy_spin.setSingleStep(0.01)
        self.energy_spin.setValue(DEFAULT_PROFILE["costo_corrente"])
        form.addWidget(self.energy_spin, r, 1); r += 1

        form.addWidget(QLabel(tr("printer_power")), r, 0)
        self.power_spin = QDoubleSpinBox()
        self.power_spin.setDecimals(0)
        self.power_spin.setRange(1.0, 10000.0)
        self.power_spin.setSingleStep(50.0)
        self.power_spin.setValue(DEFAULT_PROFILE["consumo_w"])
        form.addWidget(self.power_spin, r, 1); r += 1

        form.addWidget(QLabel(tr("material_cost")), r, 0)
        self.material_spin = QDoubleSpinBox()
        self.material_spin.setDecimals(2)
        self.material_spin.setRange(0.0, 1000.0)
        self.material_spin.setSingleStep(0.5)
        self.material_spin.setValue(DEFAULT_PROFILE["costo_materiale"])
        form.addWidget(self.material_spin, r, 1); r += 1

        form.addWidget(QLabel(tr("design_rate")), r, 0)
        self.design_spin = QDoubleSpinBox()
        self.design_spin.setDecimals(2)
        self.design_spin.setRange(0.0, 500.0)
        self.design_spin.setSingleStep(0.5)
        self.design_spin.setValue(DEFAULT_PROFILE["costo_progettazione"])
        form.addWidget(self.design_spin, r, 1); r += 1

        form.addWidget(QLabel(tr("pc_power")), r, 0)
        self.pc_spin = QDoubleSpinBox()
        self.pc_spin.setDecimals(0)
        self.pc_spin.setRange(0.0, 5000.0)
        self.pc_spin.setSingleStep(10.0)
        self.pc_spin.setValue(DEFAULT_PROFILE["consumo_pc_w"])
        form.addWidget(self.pc_spin, r, 1); r += 1

        dx.addWidget(box)

        self.btn_save = QPushButton("💾 " + tr("save_profile"))
        self.btn_save.setObjectName("primary")
        self.btn_save.clicked.connect(self._save)
        dx.addWidget(self.btn_save)

        self.btn_new = QPushButton("🆕 " + tr("new_profile"))
        self.btn_new.clicked.connect(self._new)
        dx.addWidget(self.btn_new)

        dx.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.button(QDialogButtonBox.StandardButton.Close).setText(tr("close"))
        buttons.rejected.connect(self.reject)
        dx.addWidget(buttons)
        layout.addLayout(dx, 2)

    # ------------------------------------------------------------------
    def _reload_list(self):
        self.lista.blockSignals(True)
        self.lista.clear()
        for nome in load_profiles():
            self.lista.addItem(nome)
        self.lista.blockSignals(False)

    def _load_in_form(self, nome):
        p = load_profiles().get(nome)
        if not p:
            return
        self.name_edit.setText(p["nome"])
        self.energy_spin.setValue(p["costo_corrente"])
        self.power_spin.setValue(p["consumo_w"])
        self.material_spin.setValue(p["costo_materiale"])
        self.design_spin.setValue(p["costo_progettazione"])
        self.pc_spin.setValue(p["consumo_pc_w"])

    def _new(self):
        self.lista.clearSelection()
        self.name_edit.clear()
        self.energy_spin.setValue(DEFAULT_PROFILE["costo_corrente"])
        self.power_spin.setValue(DEFAULT_PROFILE["consumo_w"])
        self.material_spin.setValue(DEFAULT_PROFILE["costo_materiale"])
        self.design_spin.setValue(DEFAULT_PROFILE["costo_progettazione"])
        self.pc_spin.setValue(DEFAULT_PROFILE["consumo_pc_w"])
        self.name_edit.setFocus()

    def _save(self):
        tr = self.tr_
        nome = self.name_edit.text().strip()
        if not nome:
            QMessageBox.warning(self, tr("msg_noname_title"), tr("msg_noname_text"))
            return
        d = {
            "nome": nome,
            "costo_corrente": self.energy_spin.value(),
            "consumo_w": self.power_spin.value(),
            "costo_materiale": self.material_spin.value(),
            "costo_progettazione": self.design_spin.value(),
            "consumo_pc_w": self.pc_spin.value(),
        }
        path = save_profile(d)
        self._reload_list()
        QMessageBox.information(self, tr("msg_saved_title"), f"{tr('msg_saved_text')}\n{path}")

    def _delete(self):
        tr = self.tr_
        item = self.lista.currentItem()
        if not item:
            QMessageBox.warning(self, tr("msg_nosel_title"), tr("msg_nosel_text"))
            return
        nome = item.text()
        conferma = QMessageBox.question(
            self, tr("confirm_del_title"),
            tr("confirm_del_text").format(name=nome),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if conferma != QMessageBox.StandardButton.Yes:
            return
        p = load_profiles().get(nome)
        if p and p.get("_file"):
            try:
                Path(p["_file"]).unlink(missing_ok=True)
            except Exception as e:
                QMessageBox.critical(self, tr("msg_export_err_title"), f"{tr('msg_delerr')} {e}")
                return
        self._reload_list()
        self._new()


# ----------------------------------------------------------------------
# Finestra principale
# ----------------------------------------------------------------------
class PriceCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.languages = load_languages()
        cfg = load_config()
        self.lang_code = cfg.get("language", "en")
        if self.lang_code not in self.languages:
            self.lang_code = "en" if "en" in self.languages else next(iter(self.languages))
        self.last_receipt = None
        self.setMinimumSize(780, 740)
        self._build_ui()
        self._reload_profiles()
        self._retranslate()

    # ------------------------------------------------------------------
    def tr_(self, key: str) -> str:
        lang = self.languages.get(self.lang_code, {})
        if key in lang:
            return lang[key]
        return self.languages.get("en", {}).get(key, key)

    # ------------------------------------------------------------------
    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 14, 18, 12)
        main_layout.setSpacing(10)

        self.header = QLabel()
        self.header.setObjectName("header")
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.header)

        # ---- riga profilo + lingua + impostazioni
        self.box_printer = QGroupBox()
        riga = QHBoxLayout(self.box_printer)
        self.lbl_profile = QLabel()
        riga.addWidget(self.lbl_profile)
        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(200)
        riga.addWidget(self.profile_combo, 1)

        self.lbl_language = QLabel()
        riga.addWidget(self.lbl_language)
        self.lang_combo = QComboBox()
        for code, d in self.languages.items():
            self.lang_combo.addItem(d.get("_name", code), code)
        idx = self.lang_combo.findData(self.lang_code)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        self.lang_combo.currentIndexChanged.connect(self._change_language)
        riga.addWidget(self.lang_combo)

        self.btn_settings = QPushButton()
        self.btn_settings.clicked.connect(self._open_settings)
        riga.addWidget(self.btn_settings)
        main_layout.addWidget(self.box_printer)

        # ---- dati di stampa
        self.box_data = QGroupBox()
        grid = QGridLayout(self.box_data)
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(10)

        self.lbl_hours = QLabel()
        grid.addWidget(self.lbl_hours, 0, 0)
        self.ore_edit = QLineEdit("0")
        self.ore_edit.setFixedWidth(90)
        grid.addWidget(self.ore_edit, 0, 1)

        self.lbl_minutes = QLabel()
        grid.addWidget(self.lbl_minutes, 0, 2)
        self.minuti_edit = QLineEdit("0")
        self.minuti_edit.setFixedWidth(90)
        grid.addWidget(self.minuti_edit, 0, 3)

        self.lbl_grams = QLabel()
        grid.addWidget(self.lbl_grams, 1, 0)
        self.grammi_edit = QLineEdit("0")
        self.grammi_edit.setFixedWidth(120)
        grid.addWidget(self.grammi_edit, 1, 1)

        self.lbl_design = QLabel()
        grid.addWidget(self.lbl_design, 2, 0)
        self.prog_edit = QLineEdit("0")
        self.prog_edit.setFixedWidth(120)
        grid.addWidget(self.prog_edit, 2, 1)

        self.lbl_pieces = QLabel()
        grid.addWidget(self.lbl_pieces, 3, 0)
        self.num_spin = QSpinBox()
        self.num_spin.setMinimum(1)
        self.num_spin.setMaximum(9999)
        self.num_spin.setValue(1)
        grid.addWidget(self.num_spin, 3, 1)
        grid.setColumnStretch(4, 1)
        main_layout.addWidget(self.box_data)

        # ---- checkbox opzioni
        chk_layout = QHBoxLayout()
        self.chk_design = QCheckBox()
        self.chk_design.setChecked(True)
        self.chk_design.toggled.connect(
            lambda on: self.prog_edit.setEnabled(on)
        )
        chk_layout.addWidget(self.chk_design)

        self.chk_round = QCheckBox()
        self.chk_round.setChecked(True)
        chk_layout.addWidget(self.chk_round)
        chk_layout.addStretch()
        main_layout.addLayout(chk_layout)

        # ---- pulsanti azione
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.calc_btn = QPushButton()
        self.calc_btn.setObjectName("primary")
        self.calc_btn.clicked.connect(self.calculate)
        btn_layout.addWidget(self.calc_btn)

        self.copy_btn = QPushButton()
        self.copy_btn.clicked.connect(self.copy_whatsapp)
        btn_layout.addWidget(self.copy_btn)

        self.export_btn = QPushButton()
        self.export_btn.clicked.connect(self.export_txt)
        btn_layout.addWidget(self.export_btn)

        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # ---- scontrino
        self.receipt = QTextEdit()
        self.receipt.setReadOnly(True)
        self.receipt.setFont(QFont("Consolas", 11))
        main_layout.addWidget(self.receipt, 1)

        self.footer = QLabel()
        self.footer.setObjectName("footer")
        self.footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.footer)

    # ------------------------------------------------------------------
    def _retranslate(self):
        tr = self.tr_
        self.setWindowTitle(tr("header"))
        self.header.setText("🖨️  " + tr("header"))
        self.box_printer.setTitle(tr("group_printer"))
        self.lbl_profile.setText(tr("profile"))
        self.lbl_language.setText(tr("language"))
        self.btn_settings.setText("⚙️  " + tr("settings"))
        self.box_data.setTitle(tr("group_data"))
        self.lbl_hours.setText(tr("time_hours"))
        self.lbl_minutes.setText(tr("minutes"))
        self.lbl_grams.setText(tr("grams"))
        self.lbl_design.setText(tr("design_hours"))
        self.lbl_pieces.setText(tr("pieces"))
        self.chk_design.setText(tr("chk_design"))
        self.chk_round.setText(tr("chk_round"))
        self.calc_btn.setText("🧮  " + tr("calc"))
        self.copy_btn.setText("📋  " + tr("copy_wa"))
        self.export_btn.setText("📄  " + tr("export_txt"))
        self.footer.setText(tr("footer"))

    def _change_language(self):
        code = self.lang_combo.currentData()
        if not code:
            return
        self.lang_code = code
        cfg = load_config()
        cfg["language"] = code
        save_config(cfg)
        self._retranslate()

    # ------------------------------------------------------------------
    def _reload_profiles(self, select: str | None = None):
        current = select or self.profile_combo.currentText()
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        self.profiles = load_profiles()
        if not self.profiles:
            self.profiles = {DEFAULT_PROFILE["nome"]: dict(DEFAULT_PROFILE)}
        for nome in self.profiles:
            self.profile_combo.addItem(nome)
        idx = self.profile_combo.findText(current)
        if idx >= 0:
            self.profile_combo.setCurrentIndex(idx)
        self.profile_combo.blockSignals(False)

    def _open_settings(self):
        dlg = SettingsDialog(self.tr_, self)
        dlg.exec()
        self._reload_profiles()

    # ------------------------------------------------------------------
    def calculate(self):
        tr = self.tr_
        try:
            ore = float((self.ore_edit.text() or "0").replace(",", "."))
            minuti = float((self.minuti_edit.text() or "0").replace(",", "."))
            grammi = float((self.grammi_edit.text() or "0").replace(",", "."))
            proj_ore = float((self.prog_edit.text() or "0").replace(",", "."))
            n_pezzi = int(self.num_spin.value() or 1)
        except ValueError:
            QMessageBox.warning(self, tr("msg_invalid_title"), tr("msg_invalid_text"))
            return

        p = self.profiles.get(self.profile_combo.currentText(), DEFAULT_PROFILE)

        tempo = ore + (minuti / 60.0)

        # Costi per pezzo
        material_cost = p["costo_materiale"] * (grammi / 1000.0)
        printer_kwh = (p["consumo_w"] / 1000.0) * tempo

        if self.chk_design.isChecked():
            # L'energia del PC in progettazione va nella voce ENERGIA
            # (è pur sempre corrente), la progettazione è solo la tariffa oraria
            pc_kwh = (p["consumo_pc_w"] / 1000.0) * proj_ore
            design_cost = p["costo_progettazione"] * proj_ore
        else:
            proj_ore = 0.0
            pc_kwh = 0.0
            design_cost = 0.0

        energy_kwh = printer_kwh + pc_kwh
        energy_cost = p["costo_corrente"] * energy_kwh

        per_piece_subtotal = material_cost + energy_cost + design_cost
        total_subtotal = per_piece_subtotal * n_pezzi

        if self.chk_round.isChecked():
            # Arrotonda per eccesso al prossimo euro, ma la differenza
            # finisce silenziosamente nel costo energia (la stampante
            # non si calibra da sola...)
            rounded_total = math.ceil(total_subtotal)
            extra = rounded_total - total_subtotal
            energy_shown = energy_cost + extra / n_pezzi
            per_piece_shown = material_cost + energy_shown + design_cost
            total_shown = float(rounded_total)
            total_str = f"{rounded_total:.0f} €"
        else:
            energy_shown = energy_cost
            per_piece_shown = per_piece_subtotal
            total_shown = total_subtotal
            total_str = euro(total_subtotal)

        price_per_piece = total_shown / n_pezzi

        self.last_receipt = self._format_receipt(
            p, n_pezzi, grammi, energy_kwh, proj_ore, tempo,
            material_cost, energy_shown, design_cost,
            per_piece_shown, total_shown, total_str, price_per_piece,
            show_design=self.chk_design.isChecked(),
        )
        self.receipt.setPlainText(self.last_receipt)

    # ------------------------------------------------------------------
    @staticmethod
    def _row(left: str, right: str, width: int) -> str:
        dots = max(width - len(left) - len(right), 2)
        return f"{left} {'.' * dots} {right}"

    def _format_receipt(self, p, n_pezzi, grammi, energy_kwh, proj_ore, tempo,
                        material_cost, energy_cost, design_cost,
                        per_piece_subtotal, total, total_str, price_per_piece,
                        show_design: bool):
        tr = self.tr_
        L = 34
        top = "━" * L
        sep = "─" * (L - 2)
        r = self._row
        row_w = L - 1

        lines = []
        lines.append(f"*{tr('r_title')}*")
        lines.append(f"{tr('r_time')}: {tempo:.2f} h    {tr('r_pieces')}: {n_pezzi}")
        lines.append(sep)
        lines.append(f"*{tr('r_costs_per_piece')}*")
        lines.append(r(f"{tr('r_material')} ({grammi:.0f} g)", euro(material_cost), row_w))
        lines.append(r(f"{tr('r_energy')} ({energy_kwh:.2f} kWh)", euro(energy_cost), row_w))
        if show_design:
            lines.append(r(f"{tr('r_design')} ({proj_ore:.1f} h)", euro(design_cost), row_w))
        lines.append(sep)
        lines.append(r(tr("r_price_per_piece"), f"{per_piece_subtotal:.2f}€", row_w))
        lines.append(r(tr("r_subtotal_total"), f"{(per_piece_subtotal * n_pezzi):.2f}€", row_w))
        lines.append(top)
        lines.append(f"*{tr('r_total')}: {total_str}*")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def copy_whatsapp(self):
        tr = self.tr_
        if not self.last_receipt:
            QMessageBox.warning(self, tr("msg_nocalc_title"), tr("msg_nocalc_text"))
            return
        text = f"```\n{self.last_receipt}\n```"
        QGuiApplication.clipboard().setText(text)
        QMessageBox.information(self, tr("msg_copied_title"), tr("msg_copied_text") + " ✅")

    def export_txt(self):
        tr = self.tr_
        if not self.last_receipt:
            QMessageBox.warning(self, tr("msg_nocalc_title"), tr("msg_nocalc_text"))
            return
        path, _ = QFileDialog.getSaveFileName(
            self, tr("save_receipt"), "receipt_3dprint.txt",
            "Text files (*.txt);;All files (*)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.last_receipt)
            QMessageBox.information(self, tr("msg_export_title"), f"{tr('msg_export_text')}\n{path}")
        except Exception as e:
            QMessageBox.critical(self, tr("msg_export_err_title"), f"{tr('msg_export_err_text')} {e}")


# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    w = PriceCalculator()
    w.show()
    sys.exit(app.exec())
