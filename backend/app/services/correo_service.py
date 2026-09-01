import logging
import smtplib
import threading
from email.message import EmailMessage

from app.config import Config
from app.repositories.pedido_repository import PedidoRepository
from app.services.pdf_service import PdfService

log = logging.getLogger(__name__)


class CorreoService:

    def __init__(self, pedido_repo=None, pdf_service=None):
        self._pedidos = pedido_repo or PedidoRepository()
        self._pdf = pdf_service or PdfService()

    @property
    def configurado(self):
        clave = Config.SMTP_CLAVE or ""
        return bool(Config.SMTP_USUARIO and clave and "PEGA_AQUI" not in clave)

    def _conectar(self):
        servidor = smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PUERTO, timeout=20)
        servidor.ehlo()

        if Config.SMTP_USAR_TLS:
            servidor.starttls()
            servidor.ehlo()

        servidor.login(Config.SMTP_USUARIO, Config.SMTP_CLAVE)
        return servidor

    def probar_conexion(self):
        if not self.configurado:
            return {"configurado": False,
                    "mensaje": "Falta SMTP_USUARIO o SMTP_CLAVE en backend/.env"}

        try:
            servidor = self._conectar()
            servidor.quit()
            return {"configurado": True, "conectado": True,
                    "mensaje": f"Autenticado en {Config.SMTP_HOST} como {Config.SMTP_USUARIO}"}
        except smtplib.SMTPAuthenticationError:
            return {"configurado": True, "conectado": False,
                    "mensaje": "Gmail rechazo las credenciales. Revisa la clave de aplicacion."}
        except Exception as error:
            return {"configurado": True, "conectado": False,
                    "mensaje": f"No se pudo conectar: {error}"}

    def _armar_mensaje(self, destinatario, asunto, pedido, adjunto):
        mensaje = EmailMessage()
        mensaje["From"] = Config.SMTP_REMITENTE or Config.SMTP_USUARIO
        mensaje["To"] = destinatario
        mensaje["Subject"] = asunto

        codigo = pedido.get("codigo_pedido", "")
        cliente = pedido.get("cliente", "")
        total = float(pedido.get("total") or 0)

        mensaje.set_content(
            f"Hola {cliente},\n\n"
            f"Recibimos tu pedido {codigo} por un total de ${total:,.2f}.\n"
            f"Adjuntamos el recibo en formato PDF.\n\n"
            f"Gracias por comprar en Red Goat Eyes.\n")

        mensaje.add_alternative(self._cuerpo_html(pedido), subtype="html")

        mensaje.add_attachment(adjunto, maintype="application", subtype="pdf",
                               filename=f"recibo_{codigo}.pdf")
        return mensaje

    @staticmethod
    def _cuerpo_html(pedido):
        codigo = pedido.get("codigo_pedido", "")
        cliente = pedido.get("cliente", "")
        total = float(pedido.get("total") or 0)
        subtotal = float(pedido.get("subtotal") or 0)
        iva = float(pedido.get("iva") or 0)
        direccion = pedido.get("direccion", "")
        metodo = pedido.get("metodo_pago", "")

        filas = ""
        for linea in pedido.get("detalles") or []:
            filas += (
                "<tr>"
                f"<td style='padding:8px;border-bottom:1px solid #eee'>{linea.get('producto','')}</td>"
                f"<td style='padding:8px;border-bottom:1px solid #eee;text-align:center'>{linea.get('cantidad',0)}</td>"
                f"<td style='padding:8px;border-bottom:1px solid #eee;text-align:right'>"
                f"${float(linea.get('subtotal_linea') or 0):,.2f}</td>"
                "</tr>")

        return f"""<html><body style="margin:0;padding:24px;background:#f5f5f5;
font-family:Arial,Helvetica,sans-serif;color:#111">
<div style="max-width:600px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden">
  <div style="background:#111;padding:24px">
    <h1 style="margin:0;color:#fff;font-size:22px;letter-spacing:1px">RED GOAT EYES</h1>
    <p style="margin:4px 0 0;color:#c81e1e;font-size:13px">Urban Clothing - Quito, Ecuador</p>
  </div>
  <div style="padding:24px">
    <h2 style="margin:0 0 4px;font-size:18px">Gracias por tu compra, {cliente}</h2>
    <p style="margin:0 0 16px;color:#666;font-size:14px">
      Tu pedido <strong style="color:#c81e1e">{codigo}</strong> fue confirmado.
    </p>
    <table style="width:100%;border-collapse:collapse;font-size:14px">
      <thead><tr style="background:#111;color:#fff">
        <th style="padding:10px;text-align:left">Producto</th>
        <th style="padding:10px;text-align:center">Cant.</th>
        <th style="padding:10px;text-align:right">Subtotal</th>
      </tr></thead>
      <tbody>{filas}</tbody>
    </table>
    <table style="width:100%;margin-top:16px;font-size:14px">
      <tr><td style="text-align:right;padding:3px">Subtotal</td>
          <td style="text-align:right;padding:3px;width:110px">${subtotal:,.2f}</td></tr>
      <tr><td style="text-align:right;padding:3px">IVA (15%)</td>
          <td style="text-align:right;padding:3px">${iva:,.2f}</td></tr>
      <tr><td style="text-align:right;padding:8px;font-size:17px;font-weight:bold">TOTAL</td>
          <td style="text-align:right;padding:8px;font-size:17px;font-weight:bold;color:#c81e1e">
          ${total:,.2f}</td></tr>
    </table>
    <div style="margin-top:20px;padding:14px;background:#f9f9f9;border-radius:6px;font-size:13px;color:#555">
      <p style="margin:0 0 6px"><strong>Entrega:</strong> {direccion}</p>
      <p style="margin:0"><strong>Metodo de pago:</strong> {metodo}</p>
    </div>
    <p style="margin:20px 0 0;font-size:13px;color:#666">
      Adjuntamos tu recibo en PDF. Consérvalo como respaldo de tu pedido.
    </p>
  </div>
  <div style="background:#111;padding:14px;text-align:center">
    <p style="margin:0;color:#888;font-size:11px">
      Correo automatico, por favor no respondas a esta direccion.
    </p>
  </div>
</div>
</body></html>"""

    def enviar_pendientes(self, limite=20):
        resumen = {"pendientes": 0, "enviados": 0, "fallidos": 0, "detalles": []}

        if not self.configurado:
            resumen["detalles"].append("SMTP no configurado: falta SMTP_CLAVE en backend/.env")
            return resumen

        try:
            pendientes = self._pedidos.correos_pendientes(limite)
        except Exception as error:
            resumen["detalles"].append(f"No se pudo leer la cola: {error}")
            return resumen

        resumen["pendientes"] = len(pendientes)

        if not pendientes:
            return resumen

        try:
            servidor = self._conectar()
        except Exception as error:
            detalle = f"No se pudo conectar a {Config.SMTP_HOST}: {error}"
            log.error(detalle)
            for correo in pendientes:
                self._pedidos.marcar_correo_fallido(correo["id_envio"], detalle)
                resumen["fallidos"] += 1
            resumen["detalles"].append(detalle)
            return resumen

        try:
            for correo in pendientes:
                self._procesar_uno(servidor, correo, resumen)
        finally:
            try:
                servidor.quit()
            except Exception:
                pass

        return resumen

    def _procesar_uno(self, servidor, correo, resumen):
        id_envio = correo["id_envio"]
        codigo = correo["codigo_pedido"]

        try:
            pedido = self._pedidos.obtener_por_codigo(codigo)

            if pedido is None:
                raise ValueError(f"El pedido {codigo} ya no existe")

            adjunto = self._pdf.generar_recibo(pedido)
            mensaje = self._armar_mensaje(correo["destinatario"], correo["asunto"],
                                          pedido, adjunto)
            servidor.send_message(mensaje)

            self._pedidos.marcar_correo_enviado(id_envio)
            resumen["enviados"] += 1
            resumen["detalles"].append(f"{codigo} enviado a {correo['destinatario']}")
            log.info("Recibo de %s enviado a %s", codigo, correo["destinatario"])

        except Exception as error:
            detalle = str(error)
            self._pedidos.marcar_correo_fallido(id_envio, detalle)
            resumen["fallidos"] += 1
            resumen["detalles"].append(f"{codigo} fallo: {detalle}")
            log.error("Fallo el envio de %s: %s", codigo, detalle)

        def notificar_mensaje_contacto(self, datos):
            if not self.configurado:
                log.warning("SMTP sin configurar: no se avisa del mensaje de contacto")
                return False

            destino = Config.SMTP_USUARIO

            mensaje = EmailMessage()
            mensaje["From"] = Config.SMTP_REMITENTE or Config.SMTP_USUARIO
            mensaje["To"] = destino
            mensaje["Reply-To"] = datos["email"]
            mensaje["Subject"] = "[Contacto] " + datos["asunto"] + " - " + datos["nombre"]

            mensaje.set_content(
                "Nuevo mensaje desde el formulario de contacto.\n\n"
                "Nombre : " + datos["nombre"] + "\n"
                "Correo : " + datos["email"] + "\n"
                "Ciudad : " + datos["ciudad"] + "\n"
                "Asunto : " + datos["asunto"] + "\n\n"
                "Mensaje:\n" + datos["descripcion"] + "\n\n"
                "Puedes responder directamente a este correo.\n")

            mensaje.add_alternative(self._html_contacto(datos), subtype="html")

            try:
                servidor = self._conectar()
            except Exception as error:
                log.error("No se pudo avisar del mensaje de contacto: %s", error)
                return False

            try:
                servidor.send_message(mensaje)
                log.info("Aviso de contacto enviado a %s", destino)
                return True
            except Exception as error:
                log.error("Fallo el aviso de contacto: %s", error)
                return False
            finally:
                try:
                    servidor.quit()
                except Exception:
                    pass

        @staticmethod
        def _html_contacto(datos):
            return f"""<html><body style="margin:0;padding:24px;background:#f5f5f5;
    font-family:Arial,Helvetica,sans-serif;color:#111">
    <div style="max-width:600px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden">
    <div style="background:#111;padding:20px">
        <h1 style="margin:0;color:#fff;font-size:18px;letter-spacing:1px">MENSAJE DE CONTACTO</h1>
        <p style="margin:4px 0 0;color:#c81e1e;font-size:12px">Red Goat Eyes</p>
    </div>
    <div style="padding:24px">
        <table style="width:100%;font-size:14px;border-collapse:collapse">
        <tr><td style="padding:6px 0;color:#666;width:90px"><strong>Nombre</strong></td>
            <td style="padding:6px 0">{datos["nombre"]}</td></tr>
        <tr><td style="padding:6px 0;color:#666"><strong>Correo</strong></td>
            <td style="padding:6px 0">{datos["email"]}</td></tr>
        <tr><td style="padding:6px 0;color:#666"><strong>Ciudad</strong></td>
            <td style="padding:6px 0">{datos["ciudad"]}</td></tr>
        <tr><td style="padding:6px 0;color:#666"><strong>Asunto</strong></td>
            <td style="padding:6px 0">{datos["asunto"]}</td></tr>
        </table>
        <div style="margin-top:18px;padding:16px;background:#f9f9f9;border-left:3px solid #c81e1e;
                    border-radius:4px;font-size:14px;line-height:1.6;white-space:pre-wrap">{datos["descripcion"]}</div>
        <p style="margin:20px 0 0;font-size:12px;color:#666">
        Responde a este correo para contestarle directamente al cliente.
        </p>
    </div>
    </div>
    </body></html>"""

        def notificar_contacto_en_segundo_plano(self, datos):
            if not self.configurado:
                return False

            hilo = threading.Thread(target=self.notificar_mensaje_contacto,
                                    args=(datos,), daemon=True)
            hilo.start()
            return True

    def enviar_pendientes_en_segundo_plano(self, limite=20):
        if not self.configurado:
            log.warning("SMTP sin configurar: el recibo queda en cola")
            return False

        hilo = threading.Thread(target=self._tarea_segundo_plano,
                                args=(limite,), daemon=True)
        hilo.start()
        return True

    def _tarea_segundo_plano(self, limite):
        try:
            resumen = self.enviar_pendientes(limite)
            log.info("Cola de correos: %s enviados, %s fallidos",
                     resumen["enviados"], resumen["fallidos"])
        except Exception:
            log.exception("Error inesperado procesando la cola de correos")