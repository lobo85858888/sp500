import yfinance as yf
import telebot
from datetime import datetime
import time
import schedule
import threading

# ================== CONFIGURACIÓN ==================
TOKEN = "8392616792:AAFgFccd5vOpJyZSoxnGnXj5U_9Y-TzUlDo"
CHAT_ID = 6584679404

bot = telebot.TeleBot(TOKEN)

# ================== OBTENER DATOS DEL S&P 500 ==================
def obtener_datos_sp500():
    try:
        spx = yf.Ticker("^GSPC")
        data = spx.history(period="2d")
        
        if len(data) < 1:
            return None, None, None, None, None, "❌ Sin datos hoy (fin de semana o festivo)"

        ultimo = data.iloc[-1]
        apertura = round(ultimo['Open'], 2)
        cierre = round(ultimo['Close'], 2)
        maximo = round(ultimo['High'], 2)
        minimo = round(ultimo['Low'], 2)
        cambio_pct = round(((cierre - apertura) / apertura) * 100, 2)
        fecha = ultimo.name.strftime("%d/%m/%Y")
        dia = ultimo.name.strftime("%A").capitalize()

        return apertura, cierre, maximo, minimo, cambio_pct, fecha, dia
    except Exception as e:
        print(f"❌ Error datos: {e}")
        return None, None, None, None, None, None, None

# ================== EMOJI SEGÚN VARIACIÓN ==================
def emoji_variacion(cambio):
    return "🟢" if cambio >= 0 else "🔴"

# ================== RESUMEN AUTOMÁTICO (15:30 y 22:00) ==================
def enviar_resumen():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Enviando resumen automático...")
    apertura, cierre, maximo, minimo, cambio_pct, fecha, dia = obtener_datos_sp500()
    
    if not cambio_pct:
        bot.send_message(CHAT_ID, "❌ Hoy no hay mercado (fin de semana o festivo).")
        return

    emoji = emoji_variacion(cambio_pct)
    
    mensaje = f"""🟢 **S&P 500 - {fecha} ({dia})**

{emoji} **Variación:** {cambio_pct:+.2f}%
📈 **Apertura:** {apertura}
📉 **Cierre:**   {cierre}
📊 **Máximo:**   {maximo}
📉 **Mínimo:**   {minimo}

¡Que tengas un excelente día de trading! 📊✨"""

    bot.send_message(CHAT_ID, mensaje, parse_mode="Markdown")
    print(f"✅ Resumen enviado | Variación: {cambio_pct:+.2f}%")

# ================== COMANDOS ==================
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id != CHAT_ID: return
    bot.send_message(CHAT_ID, "✅ **Bot S&P 500 PERFECTO activado**\n\n"
                              "Te avisaré automáticamente cada día:\n"
                              "• 15:30 → Apertura\n"
                              "• 22:00 → Cierre\n\n"
                              "Usa /info para ver el estado actual en cualquier momento.")

@bot.message_handler(commands=['info', 'ayuda', 'help'])
def info(message):
    if message.chat.id != CHAT_ID: return
    apertura, cierre, maximo, minimo, cambio_pct, fecha, dia = obtener_datos_sp500()
    
    if not cambio_pct:
        bot.send_message(CHAT_ID, "❌ No hay datos disponibles en este momento.")
        return

    emoji = emoji_variacion(cambio_pct)
    
    texto = f"""🟢 **S&P 500 - {fecha} ({dia}) (ACTUAL)**

{emoji} **Variación hoy:** {cambio_pct:+.2f}%
📍 **Precio actual:** {cierre}
📈 **Apertura:** {apertura}
📊 **Máximo del día:** {maximo}
📉 **Mínimo del día:** {minimo}

Escribe /info en cualquier momento para actualizar."""

    bot.send_message(CHAT_ID, texto, parse_mode="Markdown")

# ================== INICIO DEL BOT ==================
if __name__ == "__main__":
    print("🤖 Bot S&P 500 PERFECTO iniciado correctamente")
    
    # Mensaje de bienvenida
    bot.send_message(CHAT_ID, "🚀 **Bot S&P 500 PERFECTO listo y activo 24/7**\n\n"
                              "✅ Avisos automáticos configurados\n"
                              "• 15:30 → Resumen de apertura\n"
                              "• 22:00 → Resumen de cierre\n\n"
                              "Escribe /info para ver el estado actual del mercado.")

    # Thread para comandos
    def run_polling():
        print("🔌 Bot escuchando comandos de Telegram...")
        bot.infinity_polling(none_stop=True)

    threading.Thread(target=run_polling, daemon=True).start()

    # Programar horarios (hora España)
    for dia in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
        getattr(schedule.every(), dia).at("15:30").do(enviar_resumen)
        getattr(schedule.every(), dia).at("22:00").do(enviar_resumen)

    print("⏰ Horarios programados: 15:30 (apertura) y 22:00 (cierre)")

    # Bucle principal
    while True:
        schedule.run_pending()
        time.sleep(60)