import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from datetime import datetime
import io

dates = ["2024-01-01", "2024-01-08", "2024-01-15", "2024-01-22", "2024-02-01"]
values = [72.0, 78.0, 75.0, 82.0, 79.0]

# Рисуем график
fig, ax = plt.subplots(figsize=(10, 4))
parsed_dates = [datetime.strptime(d, "%Y-%m-%d") for d in dates]

ax.plot(parsed_dates, values, color="#6650A4", linewidth=2, marker='o', markersize=4)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
ax.grid(axis='y', linestyle='--', alpha=0.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.xticks(rotation=45)
plt.tight_layout()

# Сохраняем в буфер
img_buffer = io.BytesIO()
fig.savefig(img_buffer, format='PNG', dpi=150, bbox_inches='tight')
img_buffer.seek(0)
plt.close()

# Генерируем PDF
pdf_buffer = io.BytesIO()
c = canvas.Canvas(pdf_buffer, pagesize=A4)
width, height = A4

c.setFont("Helvetica-Bold", 18)
c.drawString(40, height - 60, "Статистика")
c.setFont("Helvetica", 11)
c.setFillColorRGB(0.4, 0.4, 0.4)
c.drawString(40, height - 85, f"Сформировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

img_reader = ImageReader(img_buffer)
c.drawImage(img_reader, 30, height - 400, width=535, height=270)

avg = sum(values) / len(values)
c.setFont("Helvetica", 11)
c.setFillColorRGB(0, 0, 0)
c.drawString(40, height - 430, f"Среднее: {avg:.1f}")
c.drawString(180, height - 430, f"Минимум: {min(values):.1f}")
c.drawString(320, height - 430, f"Максимум: {max(values):.1f}")

c.save()

# Сохраняем на диск
with open("test_output.pdf", "wb") as f:
    f.write(pdf_buffer.getvalue())

print("PDF сохранён: test_output.pdf")