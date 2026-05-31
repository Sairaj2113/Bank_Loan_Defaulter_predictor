from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd
from PySide6.QtCharts import QBarCategoryAxis, QBarSeries, QBarSet, QChart, QChartView, QLineSeries, QPieSeries, QValueAxis
from PySide6.QtCore import QMargins, QEasingCurve, Property, QPointF, QPropertyAnimation, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.database.database import ping_database  # noqa: E402
from frontend.utils.api_client import (  # noqa: E402
    get_customer,
    get_customers,
    get_db_health,
    get_health,
    get_predictions,
    predict_customer,
)

def frame_from_items(items: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(items) if items else pd.DataFrame()


def parse_datetime_series(series: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(series, errors="coerce")
    return parsed.dropna()


def count_truthy(series: pd.Series) -> int:
    if series.empty:
        return 0
    normalized = series.fillna(False).astype(str).str.lower()
    truthy_values = {"true", "t", "1", "yes", "y"}
    return int(normalized.isin(truthy_values).sum())


def fetch_paged_records(fetcher, max_rows: int = 1000, page_size: int = 100) -> dict:
    items: list[dict] = []
    total = 0

    for offset in range(0, max_rows, page_size):
        response = fetcher(limit=page_size, offset=offset)
        page_items = response.get("items", [])
        if not page_items:
            total = int(response.get("total", total) or total)
            break
        items.extend(page_items)
        total = int(response.get("total", total) or total)
        if len(page_items) < page_size:
            break

    return {"items": items, "total": total or len(items)}


THEME = {
    "bg": "#0E1117",
    "surface": "#161B22",
    "card": "#1D2430",
    "sidebar": "#111827",
    "border": "#334155",
    "text": "#F8FAFC",
    "muted": "#94A3B8",
    "primary": "#2563EB",
    "primary_soft": "#1D4ED8",
    "teal": "#14B8A6",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "pink": "#EC4899",
}


class AnimatedCard(QFrame):
    def __init__(self, title: str, value: str, subtitle: str = "", accent: str = "#4f46e5") -> None:
        super().__init__()
        self.setObjectName("AnimatedCard")
        self.setMinimumHeight(110)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self._accent = accent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("CardTitle")
        value_label = QLabel(value)
        value_label.setObjectName("CardValue")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("CardSubtitle")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(subtitle_label)

        self.setStyleSheet(
            f"""
            QFrame#AnimatedCard {{
                background: #1D2430;
                border: 1px solid #334155;
                border-radius: 18px;
            }}
            QLabel#CardTitle {{
                color: #94A3B8;
                font-size: 12px;
                letter-spacing: 0.8px;
                text-transform: uppercase;
            }}
            QLabel#CardValue {{
                color: #F8FAFC;
                font-size: 28px;
                font-weight: 700;
            }}
            QLabel#CardSubtitle {{
                color: #94A3B8;
                font-size: 12px;
            }}
            """
        )


class ChartCard(QFrame):
    def __init__(self, title: str, subtitle: str = "") -> None:
        super().__init__()
        self.setObjectName("ChartCard")
        self.setStyleSheet(
            """
            QFrame#ChartCard {
                background: rgba(22, 27, 34, 235);
                border: 1px solid rgba(51, 65, 85, 120);
                border-radius: 18px;
            }
            """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(10)
        header_box = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: 700;")
        header_box.addWidget(title_label)
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("color: #94A3B8; font-size: 12px;")
            header_box.addWidget(subtitle_label)
        header.addLayout(header_box)
        header.addStretch(1)
        layout.addLayout(header)

        self.chart = QChart()
        self.chart.setBackgroundVisible(False)
        self.chart.setPlotAreaBackgroundVisible(False)
        self.chart.legend().setVisible(True)
        self.chart.legend().setLabelColor(QColor("#94A3B8"))
        self.chart.setAnimationOptions(QChart.AnimationOption.NoAnimation)
        self.chart.setMargins(QMargins(0, 0, 0, 0))

        self.view = QChartView(self.chart)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setStyleSheet("background: transparent; border: none;")
        self.view.setMinimumHeight(250)
        layout.addWidget(self.view)

    def clear(self) -> None:
        self.chart.removeAllSeries()
        for axis in list(self.chart.axes()):
            self.chart.removeAxis(axis)

    def draw_bar(self, frame: pd.DataFrame, column: str, title: str, color: str = "#38bdf8") -> None:
        self.clear()
        self.chart.setTitle(title)
        self.chart.setTitleBrush(QColor("#F8FAFC"))
        if frame.empty or column not in frame.columns:
            self.chart.setTitle(f"{title} · No data")
            return
        counts = frame[column].fillna("Unknown").astype(str).value_counts().head(8)
        if counts.empty:
            self.chart.setTitle(f"{title} · No data")
            return
        bar_set = QBarSet("Count")
        bar_set.setColor(QColor(color))
        for value in counts.sort_values().tolist():
            bar_set.append(float(value))
        series = QBarSeries()
        series.append(bar_set)
        self.chart.addSeries(series)
        axis_x = QBarCategoryAxis()
        axis_x.append(list(counts.sort_values().index))
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%d")
        axis_y.setTitleText("Count")
        axis_y.setLabelsColor(QColor("#94A3B8"))
        axis_y.setGridLineColor(QColor(71, 85, 105, 60))
        axis_x.setLabelsColor(QColor("#94A3B8"))
        self.chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        self.chart.legend().setVisible(False)

    def draw_hist(self, frame: pd.DataFrame, column: str, title: str, color: str = "#22c55e") -> None:
        self.clear()
        self.chart.setTitle(title)
        self.chart.setTitleBrush(QColor("#F8FAFC"))
        if frame.empty or column not in frame.columns:
            self.chart.setTitle(f"{title} · No data")
            return
        values = pd.to_numeric(frame[column], errors="coerce").dropna()
        if values.empty:
            self.chart.setTitle(f"{title} · No numeric values")
            return
        bins = min(10, max(5, int(len(values) ** 0.5)))
        hist, edges = pd.cut(values, bins=bins, retbins=True, duplicates="drop", include_lowest=True)
        counts = hist.value_counts().sort_index()
        categories = [f"{interval.left:.0f}-{interval.right:.0f}" for interval in counts.index]
        bar_set = QBarSet("Count")
        bar_set.setColor(QColor(color))
        for value in counts.tolist():
            bar_set.append(float(value))
        series = QBarSeries()
        series.append(bar_set)
        self.chart.addSeries(series)
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%d")
        axis_y.setTitleText("Count")
        axis_y.setLabelsColor(QColor("#94A3B8"))
        axis_y.setGridLineColor(QColor(71, 85, 105, 60))
        axis_x.setLabelsColor(QColor("#94A3B8"))
        self.chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        self.chart.legend().setVisible(False)

    def draw_pie(self, frame: pd.DataFrame, column: str, title: str) -> None:
        self.clear()
        self.chart.setTitle(title)
        self.chart.setTitleBrush(QColor("#F8FAFC"))
        if frame.empty or column not in frame.columns:
            self.chart.setTitle(f"{title} · No data")
            return
        counts = frame[column].fillna("Unknown").astype(str).value_counts()
        if counts.empty:
            self.chart.setTitle(f"{title} · No data")
            return
        pie = QPieSeries()
        colors = ["#22c55e", "#f59e0b", "#ef4444", "#3b82f6", "#8b5cf6", "#06b6d4"]
        for index, (label, value) in enumerate(counts.items()):
            slice_item = pie.append(label, float(value))
            slice_item.setLabelVisible(True)
            slice_item.setLabelColor(QColor("#F8FAFC"))
            slice_item.setColor(QColor(colors[index % len(colors)]))
        self.chart.addSeries(pie)
        self.chart.legend().setVisible(True)

    def draw_trend(self, frame: pd.DataFrame, column: str, title: str, color: str = "#38bdf8") -> None:
        self.clear()
        self.chart.setTitle(title)
        self.chart.setTitleBrush(QColor("#F8FAFC"))
        if frame.empty:
            self.chart.setTitle(f"{title} · No data")
            return
        ordered = frame.copy()
        if "predicted_at" in ordered.columns:
            ordered["predicted_at"] = pd.to_datetime(ordered["predicted_at"], errors="coerce")
            ordered = ordered.dropna(subset=["predicted_at"]).sort_values("predicted_at")
        values = pd.to_numeric(ordered.get(column, pd.Series(dtype=float)), errors="coerce").dropna().head(30)
        if values.empty:
            self.chart.setTitle(f"{title} · No numeric values")
            return
        series = QLineSeries()
        series.setName("Probability")
        series.setColor(QColor(color))
        series.setPointsVisible(True)
        for index, value in enumerate(values.tolist()):
            series.append(QPointF(float(index), float(value) * 100.0))
        self.chart.addSeries(series)
        axis_x = QValueAxis()
        axis_x.setRange(0, max(1, len(values) - 1))
        axis_x.setLabelFormat("%d")
        axis_x.setTitleText("Recent Predictions")
        axis_x.setLabelsColor(QColor("#94A3B8"))
        axis_x.setGridLineColor(QColor(71, 85, 105, 60))
        axis_y = QValueAxis()
        axis_y.setRange(0, 100)
        axis_y.setLabelFormat("%.0f%%")
        axis_y.setTitleText("Default Probability")
        axis_y.setLabelsColor(QColor("#94A3B8"))
        axis_y.setGridLineColor(QColor(71, 85, 105, 60))
        self.chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        self.chart.legend().setVisible(False)


class LoginPage(QWidget):
    def __init__(self, on_login_success) -> None:
        super().__init__()
        self.on_login_success = on_login_success
        self.setStyleSheet(
            """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #020617,
                    stop:0.55 #0f172a,
                    stop:1 #1e293b);
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                padding: 12px;
                border-radius: 12px;
                background: rgba(15, 23, 42, 220);
                color: white;
                border: 1px solid rgba(148, 163, 184, 70);
                font-size: 14px;
            }
            QPushButton {
                padding: 12px 16px;
                border-radius: 12px;
                background: #2563eb;
                color: white;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #1d4ed8;
            }
            """
        )

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        panel = QFrame()
        panel.setFixedWidth(460)
        panel.setStyleSheet(
            """
            QFrame {
                background: rgba(2, 6, 23, 225);
                border-radius: 24px;
                border: 1px solid rgba(148, 163, 184, 50);
            }
            """
        )
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 12)
        shadow.setColor(QColor(0, 0, 0, 120))
        panel.setGraphicsEffect(shadow)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        title = QLabel("Bank Risk Management")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        subtitle = QLabel("Login to access the loan risk dashboard.")
        subtitle.setStyleSheet("color: #cbd5e1;")

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.handle_login)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(10)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(login_button)

        outer.addWidget(panel)

    def handle_login(self) -> None:
        self.on_login_success()


class DashboardPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("DashboardPage")
        self.customer_frame = pd.DataFrame()
        self.prediction_frame = pd.DataFrame()

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        hero = QFrame()
        hero.setObjectName("HeroCard")
        hero.setStyleSheet(
            """
            QFrame#HeroCard {
                background: rgba(22, 27, 34, 235);
                border: 1px solid rgba(51, 65, 85, 120);
                border-radius: 20px;
            }
            """
        )
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(20, 18, 20, 18)
        hero_title = QLabel("Loan Risk Assessment Overview")
        hero_title.setStyleSheet("color: #F8FAFC; font-size: 22px; font-weight: 800;")
        hero_subtitle = QLabel("Live KPIs, customer mix, and model outputs powered by FastAPI + PostgreSQL")
        hero_subtitle.setStyleSheet("color: #94A3B8; font-size: 13px;")
        hero_layout.addWidget(hero_title)
        hero_layout.addWidget(hero_subtitle)
        layout.addWidget(hero)

        self.card_grid = QGridLayout()
        self.card_grid.setSpacing(14)
        layout.addLayout(self.card_grid)

        charts_grid = QGridLayout()
        charts_grid.setSpacing(14)
        self.gender_chart = ChartCard("Customer Gender", "Customer composition")
        self.income_chart = ChartCard("Income Distribution", "Portfolio income spread")
        self.education_chart = ChartCard("Education Mix", "Education profile")
        self.prediction_chart = ChartCard("Risk Breakdown", "Prediction risk categories")
        self.trend_chart = ChartCard("Probability Trend", "Latest default probability curve")
        charts_grid.addWidget(self.gender_chart, 0, 0)
        charts_grid.addWidget(self.income_chart, 0, 1)
        charts_grid.addWidget(self.education_chart, 1, 0)
        charts_grid.addWidget(self.prediction_chart, 1, 1)
        charts_grid.addWidget(self.trend_chart, 2, 0, 1, 2)
        layout.addLayout(charts_grid)

    def update_data(self, customers: dict, predictions: dict) -> None:
        self.customer_frame = frame_from_items(customers.get("items", []))
        self.prediction_frame = frame_from_items(predictions.get("items", []))

        total_customers = int(customers.get("total", 0) or 0)
        total_predictions = int(predictions.get("total", 0) or 0)
        avg_income = pd.to_numeric(self.customer_frame.get("income_total", pd.Series(dtype=float)), errors="coerce").mean()
        avg_income = float(0 if pd.isna(avg_income) else avg_income)
        avg_probability = pd.to_numeric(self.prediction_frame.get("probability_default", pd.Series(dtype=float)), errors="coerce").mean()
        avg_probability = float(0 if pd.isna(avg_probability) else avg_probability)
        high_risk = int((self.prediction_frame.get("risk_category", pd.Series(dtype=str)) == "HIGH_RISK").sum()) if not self.prediction_frame.empty else 0
        median_income = pd.to_numeric(self.customer_frame.get("income_total", pd.Series(dtype=float)), errors="coerce").median()
        median_income = float(0 if pd.isna(median_income) else median_income)
        avg_family = pd.to_numeric(self.customer_frame.get("family_members", pd.Series(dtype=float)), errors="coerce").mean()
        avg_family = float(0 if pd.isna(avg_family) else avg_family)
        car_owners = count_truthy(self.customer_frame.get("owns_car", pd.Series(dtype=bool)))
        realty_owners = count_truthy(self.customer_frame.get("owns_realty", pd.Series(dtype=bool)))

        cards = [
            AnimatedCard("Total Customers", f"{total_customers:,}", "Seeded from PostgreSQL", "#2563eb"),
            AnimatedCard("Total Predictions", f"{total_predictions:,}", "Stored model outputs", "#10b981"),
            AnimatedCard("Average Income", f"{avg_income:,.0f}", "Across loaded customers", "#f59e0b"),
            AnimatedCard("Median Income", f"{median_income:,.0f}", "Portfolio midpoint", "#8b5cf6"),
            AnimatedCard("Avg Family Members", f"{avg_family:.1f}", "Household size signal", "#14b8a6"),
            AnimatedCard("Avg Default Probability", f"{avg_probability * 100:.1f}%", "Current prediction pool", "#7c3aed"),
            AnimatedCard("High Risk Cases", f"{high_risk:,}", "Flagged predictions", "#ef4444"),
            AnimatedCard("Car Owners", f"{car_owners:,}", "Vehicle ownership", "#38bdf8"),
            AnimatedCard("Realty Owners", f"{realty_owners:,}", "Property ownership", "#22c55e"),
        ]

        while self.card_grid.count():
            item = self.card_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for index, card in enumerate(cards):
            self.card_grid.addWidget(card, index // 3, index % 3)

        self.gender_chart.draw_bar(self.customer_frame, "gender", "Customer Gender Distribution", "#60a5fa")
        self.income_chart.draw_hist(self.customer_frame, "income_total", "Income Distribution", "#22c55e")
        self.education_chart.draw_bar(self.customer_frame, "education_type", "Education Type Distribution", "#f97316")
        self.prediction_chart.draw_pie(self.prediction_frame, "risk_category", "Risk Category Share")
        self.trend_chart.draw_trend(self.prediction_frame, "probability_default", "Prediction Probability Trend", "#ef4444")


class CustomersPage(QWidget):
    def __init__(self, on_select_customer) -> None:
        super().__init__()
        self.on_select_customer = on_select_customer
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search by customer ID, gender, education, occupation...")
        self.search.textChanged.connect(self.refresh_table)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Customer ID", "Gender", "Income", "Occupation", "Created"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self._select_row)

        layout.addWidget(self.search)
        layout.addWidget(self.table)

        self.customers = []

    def update_data(self, customers: dict) -> None:
        self.customers = customers.get("items", [])
        self.refresh_table()

    def refresh_table(self, *_args) -> None:
        query = self.search.text().strip().lower()
        items = self.customers
        if query:
            def matches(item: dict) -> bool:
                values = [
                    str(item.get("customer_id", "")).lower(),
                    str(item.get("gender", "")).lower(),
                    str(item.get("education_type", "")).lower(),
                    str(item.get("occupation_type", "")).lower(),
                ]
                return any(query in value for value in values)

            items = [item for item in self.customers if matches(item)]

        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            values = [
                str(item.get("customer_id", "")),
                str(item.get("gender", "")),
                f"{float(item.get('income_total', 0)):.0f}",
                str(item.get("occupation_type", "")),
                str(item.get("created_at", "")),
            ]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))
        self.table.resizeColumnsToContents()

    def _select_row(self, row: int, _column: int) -> None:
        if row < 0 or row >= self.table.rowCount():
            return
        customer_id = self.table.item(row, 0).text()
        self.on_select_customer(customer_id)


class CustomerDetailPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setSpacing(16)

        left = QVBoxLayout()
        right = QVBoxLayout()

        self.customer_box = QTextEdit()
        self.customer_box.setReadOnly(True)
        self.applications_box = QTextEdit()
        self.applications_box.setReadOnly(True)
        self.predictions_box = QTextEdit()
        self.predictions_box.setReadOnly(True)
        self.customer_selector = QComboBox()
        self.customer_selector.currentIndexChanged.connect(self._customer_selection_changed)

        self.credit_amount = QLineEdit("227520")
        self.credit_amount.setPlaceholderText("Enter requested loan amount")
        self.credit_amount.setToolTip("Total credit amount the customer is requesting.")
        self.annuity_amount = QLineEdit("13189.5")
        self.annuity_amount.setPlaceholderText("Enter monthly repayment amount")
        self.annuity_amount.setToolTip("Monthly installment amount for the loan.")
        self.goods_price = QLineEdit("180000")
        self.goods_price.setPlaceholderText("Enter asset / goods price")
        self.goods_price.setToolTip("Value of the purchased goods or asset.")
        self.loan_type = QComboBox()
        self.loan_type.addItems(["Cash loans", "Revolving loans", "Consumer loans"])
        self.loan_type.setToolTip("Select the type of loan to score.")
        self.predict_button = QPushButton("Calculate Risk")
        self.predict_button.clicked.connect(self.calculate_risk)

        self.result_label = QLabel("Probability: -")
        self.result_label.setStyleSheet("color: white; font-size: 18px; font-weight: 600;")
        self.risk_label = QLabel("Risk Category: -")
        self.risk_label.setStyleSheet("color: #94A3B8; font-size: 14px;")
        self.risk_progress = AnimatedProgressBar()

        left.addWidget(QLabel("Select Customer"))
        left.addWidget(self.customer_selector)
        left.addWidget(QLabel("Customer Information"))
        left.addWidget(self.customer_box, 1)
        left.addWidget(QLabel("Recent Applications"))
        left.addWidget(self.applications_box, 1)
        left.addWidget(QLabel("Previous Predictions"))
        left.addWidget(self.predictions_box, 1)

        form_card = QFrame()
        form_layout = QVBoxLayout(form_card)
        form_layout.addWidget(QLabel("Make Prediction"))
        form_hint = QLabel("Fill in the loan details below, then click Calculate Risk to estimate default probability.")
        form_hint.setWordWrap(True)
        form_hint.setStyleSheet("color: #94A3B8; font-size: 12px;")
        form_layout.addWidget(form_hint)
        form_layout.addWidget(QLabel("Credit Amount"))
        form_layout.addWidget(self.credit_amount)
        form_layout.addWidget(QLabel("Annuity Amount"))
        form_layout.addWidget(self.annuity_amount)
        form_layout.addWidget(QLabel("Goods Price"))
        form_layout.addWidget(self.goods_price)
        form_layout.addWidget(QLabel("Loan Type"))
        form_layout.addWidget(self.loan_type)
        form_layout.addWidget(self.predict_button)
        form_layout.addWidget(self.result_label)
        form_layout.addWidget(self.risk_label)
        form_layout.addWidget(self.risk_progress)

        right.addWidget(form_card)

        layout.addLayout(left, 1)
        layout.addLayout(right, 1)

        self.current_customer_id = None
        self.current_customer = {}
        self.on_prediction_complete = None
        self.customer_records: list[dict] = []

    def update_customers(self, customers: list[dict]) -> None:
        self.customer_records = customers or []
        current_id = str(self.current_customer_id) if self.current_customer_id else ""
        self.customer_selector.blockSignals(True)
        self.customer_selector.clear()
        for item in self.customer_records:
            customer_id = str(item.get("customer_id", ""))
            label = f"{customer_id} · {item.get('gender', 'Unknown')} · {float(item.get('income_total', 0) or 0):.0f}"
            self.customer_selector.addItem(label, customer_id)

        if self.customer_records:
            target_index = 0
            if current_id:
                for index, item in enumerate(self.customer_records):
                    if str(item.get("customer_id", "")) == current_id:
                        target_index = index
                        break
            self.customer_selector.setCurrentIndex(target_index)
            self.customer_selector.blockSignals(False)
            self._load_customer_from_index(target_index)
        else:
            self.customer_selector.blockSignals(False)
            self.customer_box.setPlainText("No customers available.")
            self.applications_box.setPlainText("No applications yet.")
            self.predictions_box.setPlainText("No previous predictions yet.")

    def _customer_selection_changed(self, index: int) -> None:
        if index < 0:
            return
        self._load_customer_from_index(index)

    def _load_customer_from_index(self, index: int) -> None:
        if index < 0 or index >= len(self.customer_records):
            return
        customer_id = str(self.customer_records[index].get("customer_id", ""))
        if customer_id:
            self.update_customer(customer_id)

    def update_customer(self, customer_id: str, predictions: list[dict] | None = None) -> None:
        detail = get_customer(customer_id)
        self.current_customer_id = customer_id
        self.current_customer = detail["customer"]
        self.customer_selector.blockSignals(True)
        for index in range(self.customer_selector.count()):
            if self.customer_selector.itemData(index) and str(self.customer_selector.itemData(index)) == str(customer_id):
                self.customer_selector.setCurrentIndex(index)
                break
        self.customer_selector.blockSignals(False)
        self.customer_box.setPlainText(pd.Series(self.current_customer).to_string())
        applications = detail.get("recent_applications", [])
        self.applications_box.setPlainText(pd.DataFrame(applications).to_string(index=False) if applications else "No applications yet.")
        relevant_predictions = detail.get("recent_predictions", [])
        if not relevant_predictions and predictions:
            relevant_predictions = [item for item in predictions if str(item.get("customer_id")) == str(customer_id)]
        self.predictions_box.setPlainText(
            pd.DataFrame(relevant_predictions).head(10).to_string(index=False) if relevant_predictions else "No previous predictions yet."
        )

    def calculate_risk(self) -> None:
        if not self.current_customer_id:
            QMessageBox.information(self, "No Customer", "Select a customer first.")
            return

        try:
            result = predict_customer(
                self.current_customer_id,
                {
                    "credit_amount": float(self.credit_amount.text()),
                    "annuity_amount": float(self.annuity_amount.text()),
                    "goods_price": float(self.goods_price.text()),
                    "loan_type": self.loan_type.currentText(),
                },
            )
        except Exception as exc:
            QMessageBox.critical(self, "Prediction Failed", str(exc))
            return

        probability = float(result["probability_default"])
        self.result_label.setText(f"Probability: {probability * 100:.1f}%")
        self.risk_label.setText(f"Risk Category: {result['risk_category']}")
        self.risk_progress.setValueAnimated(int(probability * 100))
        if callable(self.on_prediction_complete):
            self.on_prediction_complete()


class AnimatedProgressBar(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self._value = 0
        self.setFixedHeight(18)
        self.setStyleSheet(
            """
            QFrame {
                background: rgba(148, 163, 184, 60);
                border-radius: 9px;
            }
            """
        )
        self.fill = QFrame(self)
        self.fill.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #22c55e, stop:1 #06b6d4); border-radius: 9px;")
        self.fill.setGeometry(0, 0, 0, 18)
        self.animation = QPropertyAnimation(self, b"value", self)
        self.animation.setDuration(800)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.valueChanged.connect(self.setValue)

    def getValue(self) -> int:
        return self._value

    def setValue(self, value: int) -> None:
        self._value = max(0, min(100, value))
        width = int(self.width() * self._value / 100)
        self.fill.setGeometry(0, 0, width, self.height())

    value = Property(int, getValue, setValue)

    def resizeEvent(self, event):  # noqa: N802
        super().resizeEvent(event)
        self.setValue(self._value)

    def setValueAnimated(self, value: int) -> None:
        self.animation.stop()
        self.animation.setStartValue(self._value)
        self.animation.setEndValue(value)
        self.animation.start()


class PredictionsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Prediction ID", "Application ID", "Customer ID", "Risk", "Probability", "Model", "Predicted At"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

    def update_data(self, predictions: dict) -> None:
        items = predictions.get("items", [])
        self.table.setRowCount(len(items))
        for row, item in enumerate(items):
            values = [
                str(item.get("prediction_id", "")),
                str(item.get("application_id", "")),
                str(item.get("customer_id", "")),
                str(item.get("risk_category", "")),
                f"{float(item.get('probability_default', 0)):.4f}",
                str(item.get("model_version", "")),
                str(item.get("predicted_at", "")),
            ]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(value))
        self.table.resizeColumnsToContents()


class AnalyticsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.risk_chart = ChartCard("Risk Category Distribution")
        self.probability_chart = ChartCard("Probability Distribution")
        layout.addWidget(self.risk_chart)
        layout.addWidget(self.probability_chart)

    def update_data(self, predictions: dict) -> None:
        frame = frame_from_items(predictions.get("items", []))
        self.risk_chart.draw_pie(frame, "risk_category", "Risk Category Distribution")
        self.probability_chart.draw_hist(frame, "probability_default", "Default Probability Distribution", "#ef4444")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Bank Loan Risk Assessment")
        self.resize(1520, 960)
        self.setMinimumSize(1280, 840)

        self.setStyleSheet(
            """
            QMainWindow {
                background: #0E1117;
            }
            QLabel {
                color: #F8FAFC;
            }
            QLineEdit, QComboBox, QTextEdit, QTableWidget {
                background: rgba(22, 27, 34, 235);
                color: #F8FAFC;
                border: 1px solid rgba(51, 65, 85, 120);
                border-radius: 12px;
                padding: 10px;
                selection-background-color: #2563eb;
            }
            QPushButton {
                background: #1d4ed8;
                color: #F8FAFC;
                border: none;
                border-radius: 12px;
                padding: 11px 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #2563eb;
            }
            QTableWidget {
                gridline-color: rgba(148, 163, 184, 35);
            }
            """
        )

        self.central = QStackedWidget()
        self.setCentralWidget(self.central)

        self.main_shell = QWidget()
        self.main_layout = QHBoxLayout(self.main_shell)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.page_buttons: list[QPushButton] = []

        self.sidebar = self.build_sidebar()
        self.content_stack = QStackedWidget()
        self.dashboard_page = DashboardPage()
        self.customers_page = CustomersPage(self.open_customer_detail)
        self.customer_detail_page = CustomerDetailPage()
        self.customer_detail_page.on_prediction_complete = self.refresh_data
        self.predictions_page = PredictionsPage()
        self.analytics_page = AnalyticsPage()

        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.customers_page)
        self.content_stack.addWidget(self.customer_detail_page)
        self.content_stack.addWidget(self.predictions_page)
        self.content_stack.addWidget(self.analytics_page)

        self.latest_customers: dict = {"items": [], "total": 0}
        self.latest_predictions: dict = {"items": [], "total": 0}

        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_stack, 1)

        self.central.addWidget(self.main_shell)
        self.central.setCurrentWidget(self.main_shell)

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(60000)
        self.refresh_data()
        self.update_navigation(0)

    def build_sidebar(self) -> QWidget:
        side = QFrame()
        side.setFixedWidth(260)
        side.setStyleSheet(
            """
            QFrame {
                background: #111827;
                border-right: 1px solid rgba(51, 65, 85, 120);
            }
            """
        )
        layout = QVBoxLayout(side)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Bank Risk Management")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #F8FAFC;")
        subtitle = QLabel("FastAPI + PostgreSQL")
        subtitle.setStyleSheet("color: #94A3B8;")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        self.status_label = QLabel("API: waiting for refresh...")
        self.status_label.setStyleSheet("color: #60A5FA;")
        layout.addWidget(self.status_label)

        layout.addSpacing(8)
        buttons = [
            ("Dashboard", 0),
            ("Customers", 1),
            ("Make Predictions", 2),
            ("Predictions", 3),
            ("Analytics", 4),
        ]
        for label, index in buttons:
            button = QPushButton(label)
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setMinimumHeight(46)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            button.setStyleSheet(
                """
                QPushButton {
                    background: rgba(22, 27, 34, 220);
                    color: #CBD5E1;
                    border: 1px solid rgba(51, 65, 85, 140);
                    border-radius: 12px;
                    padding: 11px 14px;
                    font-size: 14px;
                    font-weight: 600;
                    text-align: left;
                }
                QPushButton:hover {
                    background: rgba(37, 99, 235, 140);
                    color: white;
                    border: 1px solid rgba(96, 165, 250, 140);
                }
                QPushButton:checked {
                    background: rgba(37, 99, 235, 210);
                    color: white;
                    border: 1px solid rgba(96, 165, 250, 170);
                }
                """
            )
            button.clicked.connect(lambda _checked=False, idx=index: self.switch_page(idx))
            layout.addWidget(button)
            self.page_buttons.append(button)

        layout.addStretch(1)
        refresh = QPushButton("Refresh Data")
        refresh.clicked.connect(self.refresh_data)
        layout.addWidget(refresh)
        return side

    def show_main_interface(self) -> None:
        self.central.setCurrentWidget(self.main_shell)
        self.refresh_data()
        self.update_navigation(0)

    def logout(self) -> None:
        self.refresh_data()

    def switch_page(self, index: int) -> None:
        widget = self.content_stack.widget(index)
        self.content_stack.setCurrentWidget(widget)
        self.update_navigation(index)

    def open_customer_detail(self, customer_id: str) -> None:
        self.customer_detail_page.update_customer(customer_id, self.latest_predictions.get("items", []))
        self.content_stack.setCurrentWidget(self.customer_detail_page)
        self.update_navigation(2)

    def update_navigation(self, active_index: int) -> None:
        for index, button in enumerate(self.page_buttons):
            button.setChecked(index == active_index)
            if index == active_index:
                button.setStyleSheet(
                    """
                    QPushButton {
                        background: rgba(37, 99, 235, 210);
                        color: white;
                        border: 1px solid rgba(255, 255, 255, 30);
                        border-radius: 12px;
                        padding: 11px 14px;
                        font-weight: 700;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background: rgba(59, 130, 246, 210);
                    }
                    """
                )
            else:
                button.setStyleSheet(
                    """
                    QPushButton {
                        background: rgba(22, 27, 34, 220);
                        color: #CBD5E1;
                        border: 1px solid rgba(51, 65, 85, 120);
                        border-radius: 12px;
                        padding: 11px 14px;
                        font-weight: 600;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background: rgba(37, 99, 235, 140);
                        color: white;
                    }
                    """
                )

    def refresh_data(self) -> None:
        try:
            health = get_health()
            db_health = get_db_health()
            customers = fetch_paged_records(get_customers, max_rows=100, page_size=100)
            predictions = fetch_paged_records(get_predictions, max_rows=100, page_size=100)
        except Exception as exc:
            self.status_label.setText(f"API error: {exc}")
            return

        self.setWindowTitle(
            f"Bank Loan Risk Assessment - API {health.get('status')} / DB {db_health.get('status')}"
        )
        self.status_label.setText(f"API: {health.get('status')} | DB: {db_health.get('status')}")
        self.latest_customers = customers
        self.latest_predictions = predictions
        self.dashboard_page.update_data(customers, predictions)
        self.customers_page.update_data(customers)
        self.predictions_page.update_data(predictions)
        self.analytics_page.update_data(predictions)
        self.customer_detail_page.update_customers(customers.get("items", []))
        if self.content_stack.currentWidget() == self.customer_detail_page and self.customer_detail_page.current_customer_id:
            self.customer_detail_page.update_customer(
                self.customer_detail_page.current_customer_id,
                self.latest_predictions.get("items", []),
            )


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Bank Loan Risk Assessment")
    app.setFont(QFont("Segoe UI", 10))

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#020617"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("white"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#0f172a"))
    palette.setColor(QPalette.ColorRole.Text, QColor("white"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#1d4ed8"))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
