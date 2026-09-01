# ============================================================
# PDF SERVICE
# Arma el recibo en PDF con la libreria fpdf2.
# Se adjunta al correo que recibe el cliente al comprar.
# ============================================================
from datetime import datetime

from fpdf import FPDF

NEGRO = (17, 17, 17)
ROJO = (200, 30, 30)
GRIS = (110, 110, 110)
GRIS_CLARO = (238, 238, 238)



# ---------------- Limpiar texto para el PDF ----------------
# Las fuentes basicas de PDF solo aceptan latin-1
def _texto(valor):
    if valor is None:
        return ""
    return str(valor).encode("latin-1", "replace").decode("latin-1")



# ---------------- Formato de dinero y fechas ----------------
def _dinero(valor):
    return "$" + format(float(valor or 0), ",.2f")


def _fecha(valor):
    if not valor:
        return ""
    try:
        return datetime.fromisoformat(str(valor)).strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return _texto(valor)



# ---------------- Plantilla del documento ----------------
class ReciboPDF(FPDF):

    def __init__(self, codigo_pedido):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.codigo_pedido = codigo_pedido
        self.set_auto_page_break(auto=True, margin=20)


# ---------------- Cabecera de cada pagina ----------------
    def header(self):
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(*NEGRO)
        self.cell(0, 10, "RED GOAT EYES", new_x="LMARGIN", new_y="NEXT")

        self.set_font("Helvetica", "", 9)
        self.set_text_color(*GRIS)
        self.cell(0, 5, "Urban Clothing  -  Quito - Ecuador", new_x="LMARGIN", new_y="NEXT")

        self.set_draw_color(*ROJO)
        self.set_line_width(0.8)
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.ln(8)


# ---------------- Pie de cada pagina ----------------
    def footer(self):
        self.set_y(-18)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*GRIS)
        self.cell(0, 4, _texto("Este documento es un comprobante generado automaticamente."),
                  new_x="LMARGIN", new_y="NEXT", align="C")
        self.cell(0, 4, _texto("Pedido " + self.codigo_pedido + "  -  Pagina " + str(self.page_no())),
                  align="C")



# ---------------- El servicio que arma el recibo ----------------
class PdfService:


# ---------------- Armar el PDF completo ----------------
    def generar_recibo(self, pedido):
        pdf = ReciboPDF(_texto(pedido.get("codigo_pedido", "")))
        pdf.add_page()

        self._titulo(pdf, pedido)
        self._datos_cliente(pdf, pedido)
        self._tabla_productos(pdf, pedido.get("detalles") or [])
        self._totales(pdf, pedido)
        self._cierre(pdf)

        return bytes(pdf.output())


# ---------------- Titulo y codigo del pedido ----------------
    def _titulo(self, pdf, pedido):
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*NEGRO)
        pdf.cell(0, 8, _texto("RECIBO DE COMPRA"), new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*ROJO)
        pdf.cell(0, 7, _texto(pedido.get("codigo_pedido", "")), new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*GRIS)
        pdf.cell(0, 6, _texto("Fecha: " + _fecha(pedido.get("fecha_pedido"))),
                 new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, _texto("Estado: " + str(pedido.get("estado", ""))),
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)


# ---------------- Datos de entrega ----------------
    def _datos_cliente(self, pdf, pedido):
        filas = [
            ("Cliente", pedido.get("cliente")),
            ("Correo", pedido.get("email")),
            ("Entrega", pedido.get("direccion")),
            ("Referencia", pedido.get("referencia")),
            ("Metodo de pago", pedido.get("metodo_pago")),
        ]

        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*NEGRO)
        pdf.cell(0, 7, _texto("DATOS DE ENTREGA"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

        for etiqueta, valor in filas:
            if not valor:
                continue
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*GRIS)
            pdf.cell(35, 6, _texto(etiqueta))
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*NEGRO)
            pdf.multi_cell(0, 6, _texto(valor), new_x="LMARGIN", new_y="NEXT")

        pdf.ln(4)


# ---------------- Tabla de productos comprados ----------------
    def _tabla_productos(self, pdf, detalles):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*NEGRO)
        pdf.cell(0, 7, _texto("PRODUCTOS"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

        anchos = (28, 82, 18, 30, 32)
        cabeceras = ("Codigo", "Producto", "Cant.", "P. unitario", "Subtotal")

        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(*NEGRO)
        pdf.set_text_color(255, 255, 255)

        for ancho, titulo in zip(anchos, cabeceras):
            alineacion = "R" if titulo in ("Cant.", "P. unitario", "Subtotal") else "L"
            pdf.cell(ancho, 8, _texto(titulo), border=0, align=alineacion, fill=True)
        pdf.ln()

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*NEGRO)
        alterno = False

        for linea in detalles:
            alterno = not alterno
            pdf.set_fill_color(*GRIS_CLARO)

            valores = (
                _texto(linea.get("codigo")),
                _texto(linea.get("producto")),
                str(linea.get("cantidad", 0)),
                _dinero(linea.get("precio_unitario")),
                _dinero(linea.get("subtotal_linea")),
            )

            for ancho, valor, alineacion in zip(anchos, valores, ("L", "L", "R", "R", "R")):
                pdf.cell(ancho, 7, valor, border=0, align=alineacion, fill=alterno)
            pdf.ln()

        pdf.ln(4)


# ---------------- Subtotal, IVA y total ----------------
    def _totales(self, pdf, pedido):
        filas = [
            ("Subtotal", pedido.get("subtotal")),
            ("IVA (15%)", pedido.get("iva")),
            ("Envio", pedido.get("costo_envio")),
        ]

        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*NEGRO)

        for etiqueta, valor in filas:
            pdf.cell(128)
            pdf.cell(30, 7, _texto(etiqueta), align="R")
            pdf.cell(32, 7, _dinero(valor), align="R")
            pdf.ln()

        pdf.set_draw_color(*NEGRO)
        pdf.set_line_width(0.3)
        pdf.line(138, pdf.get_y() + 1, 200, pdf.get_y() + 1)
        pdf.ln(3)

        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(*ROJO)
        pdf.cell(128)
        pdf.cell(30, 9, _texto("TOTAL"), align="R")
        pdf.cell(32, 9, _dinero(pedido.get("total")), align="R")
        pdf.ln(14)


# ---------------- Mensaje final ----------------
    def _cierre(self, pdf):
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*NEGRO)
        pdf.cell(0, 6, _texto("Gracias por tu compra."), new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*GRIS)
        pdf.multi_cell(0, 5, _texto(
            "Conserva este recibo como respaldo de tu pedido. "
            "Si tienes alguna consulta escribenos desde la seccion de contacto "
            "de la tienda indicando el codigo de tu pedido."))