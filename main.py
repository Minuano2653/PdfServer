from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import matplotlib
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

from ChartData import PatientReport

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
import io

app = FastAPI()

FONT_REGULAR = "fonts/helvetica-regular.ttf"
FONT_BOLD = "fonts/helvetica-bold.ttf"

try:
    pdfmetrics.registerFont(TTFont('helvetica-regular', FONT_REGULAR))
    pdfmetrics.registerFont(TTFont('helvetica-bold', FONT_BOLD))
    print("Шрифты успешно загружены")
except Exception as e:
    print(f"Ошибка загрузки шрифтов: {e}")


def generate_psv_chart(dates: list[str], values: list[float]) -> io.BytesIO:
    parsed = [datetime.strptime(d, "%Y-%m-%d") for d in dates]

    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(7.43, 2.92))

    main_color = "#6750A4"

    ax.fill_between(parsed, values, color=main_color, alpha=0.3)
    ax.plot(parsed, values, color=main_color, linewidth=2.5,
            marker='o', markersize=5,
            markerfacecolor=main_color,
            markeredgecolor="white", markeredgewidth=1.5)

    for d, v in zip(parsed, values):
        ax.text(d, v + 5, f"{v:.1f}",
                ha='center', fontsize=8, color="#1C1B1F")

    ax.set_ylim(0, max(values) + 50)

    ax.grid(axis='y', linestyle='-', color="#E7E0EC")
    ax.set_axisbelow(True)

    ax.spines[['top', 'right']].set_visible(False)
    ax.spines['left'].set_color('#CAC4D0')
    ax.spines['bottom'].set_color('#CAC4D0')

    ax.tick_params(axis='x', labelsize=8, length=0)
    ax.tick_params(axis='y', labelsize=8)

    day_names = ['пн','вт','ср','чт','пт','сб','вс']
    labels = [f"{day_names[d.weekday()]}\n{d.strftime('%d %b')}" for d in parsed]

    ax.set_xticks(parsed)
    ax.set_xticklabels(labels)

    plt.subplots_adjust(left=0.07, right=0.98, top=0.95, bottom=0.2)

    buf = io.BytesIO()
    fig.savefig(buf, format='PNG', dpi=150, facecolor='white')
    buf.seek(0)
    plt.close(fig)
    return buf


def generate_ast_chart(dates: list[str], values: list[float]) -> io.BytesIO:
    parsed = [datetime.strptime(d, "%Y-%m-%d") for d in dates]

    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(7.43, 2.92))

    x = range(len(values))

    colors = ["#FF7043" if v < 18 else "#4CAF50" for v in values]

    bars = ax.bar(x, values, color=colors, width=0.6)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.5,
                f"{int(val)}",
                ha='center', fontsize=8, color="#1C1B1F")

    ax.set_ylim(0, 25)

    months = ['янв','фев','мар','апр','май','июн',
              'июл','авг','сен','окт','ноя','дек']

    labels = []
    for i, d in enumerate(parsed):
        if i == 0 or d.year != parsed[i-1].year:
            labels.append(f"{months[d.month-1]}\n{d.year}")
        else:
            labels.append(months[d.month-1])

    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    ax.grid(axis='y', linestyle='-', color="#E7E0EC")

    ax.spines[['top', 'right']].set_visible(False)
    ax.spines['left'].set_color('#CAC4D0')
    ax.spines['bottom'].set_color('#CAC4D0')

    ax.tick_params(axis='x', labelsize=8, length=0)
    ax.tick_params(axis='y', labelsize=8)

    plt.subplots_adjust(left=0.07, right=0.98, top=0.95, bottom=0.2)

    buf = io.BytesIO()
    fig.savefig(buf, format='PNG', dpi=150, facecolor='white')
    buf.seek(0)
    plt.close(fig)
    return buf


def _month_ru(month: int) -> str:
    months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
              'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    return months[month - 1]


def _month_ru_short(month: int) -> str:
    months = ['янв', 'фев', 'мар', 'апр', 'май', 'июн',
              'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']
    return months[month - 1]


@app.post("/generate-pdf")
async def generate_pdf(data: PatientReport):

    psv_buf = generate_psv_chart(
        [p.date for p in data.psv_data],
        [p.value for p in data.psv_data]
    )

    ast_buf = generate_ast_chart(
        [p.date for p in data.ast_data],
        [p.value for p in data.ast_data]
    )

    pdf = io.BytesIO()
    c = canvas.Canvas(pdf, pagesize=A4)
    W, H = A4

    # ───────── HEADER ─────────
    c.setFont("helvetica-bold", 22)
    c.drawString(30, 800, "Aesculapius")

    c.setStrokeColorRGB(0.79, 0.77, 0.81)
    c.line(30, 790, 565, 790)

    # ───────── PATIENT CARD ─────────
    c.roundRect(30, 670, 535, 110, 6)

    c.setFont("helvetica-regular", 10)
    c.drawString(44, 760, "ФИО пациента:")

    c.setFont("helvetica-bold", 10)
    c.drawString(150, 760, f"{data.full_name} ({data.activity})")

    c.line(44, 748, 551, 748)

    cols = [44, 160, 280, 420]
    labels = ["Рост", "Вес", "Дата рождения", "Почта"]
    values = [
        f"{data.height}см",
        f"{data.weight}кг",
        data.birth_date,
        data.email
    ]

    for x, l, v in zip(cols, labels, values):
        c.setFont("helvetica-regular", 8)
        c.drawString(x, 735, l)
        c.setFont("helvetica-bold", 10)
        c.drawString(x, 720, v)

    # ───────── PSV CARD ─────────
    c.roundRect(30, 430, 535, 210, 6)

    c.setFont("helvetica-bold", 12)
    c.drawString(44, 620, "Значения ПСВ, л/мин")

    c.drawImage(ImageReader(psv_buf),
                40, 440, width=515, height=170)

    # ───────── AST CARD ─────────
    c.roundRect(30, 200, 535, 210, 6)

    c.setFont("helvetica-bold", 12)
    c.drawString(44, 390, "АСТ тестирование")

    c.drawImage(ImageReader(ast_buf),
                40, 210, width=515, height=170)

    # ───────── FOOTER ─────────
    c.line(30, 190, 565, 190)

    c.setFont("helvetica-regular", 8)
    c.drawString(30, 175, "*активность пользователя")

    c.drawRightString(
        565, 175,
        f"Загрузка файла: {datetime.now().strftime('%d.%m.%Y')}"
    )

    c.save()
    pdf.seek(0)

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=report.pdf"}
    )


@app.get("/health")
async def health():
    return {"status": "ok"}