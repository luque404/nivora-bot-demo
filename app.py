from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import List

from flask import Flask, jsonify, request, render_template_string, Response

app = Flask(__name__)

# =========================
# Configuración básica
# =========================
BRAND_NAME = os.getenv("BRAND_NAME", "Nivora")
PRIMARY_COLOR = os.getenv("PRIMARY_COLOR", "#0f172a")
SECONDARY_COLOR = os.getenv("SECONDARY_COLOR", "#7c3aed")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "hola@nivora.com")
INSTAGRAM_URL = os.getenv("INSTAGRAM_URL", "https://instagram.com/nivora")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "")


@dataclass
class FAQ:
    key: str
    title: str
    answer: str
    keywords: List[str]
    follow_ups: List[str] = field(default_factory=list)


FAQS: List[FAQ] = [
    FAQ(
        key="funciona",
        title="¿Cómo funciona?",
        answer=(
            "Funciona así 👇\n\n"
            "1. El cliente entra a tu tienda\n"
            "2. Hace una pregunta en el chat\n"
            "3. El asistente responde automáticamente\n"
            "4. Resuelve la duda en segundos\n"
            "5. Eso ayuda a que no se enfríe la compra\n\n"
            "La idea no es vender agresivo, sino acompañar, sacar fricción y responder rápido."
        ),
        keywords=["como funciona", "cómo funciona", "funciona", "demo", "ver demo", "como seria", "cómo sería"],
        follow_ups=["¿Qué tipo de preguntas responde?", "¿Se instala en Shopify?"],
    ),
    FAQ(
        key="preguntas",
        title="¿Qué tipo de preguntas responde?",
        answer=(
            "Puede responder muchas de las preguntas repetidas que frenan una compra 👍\n\n"
            "Por ejemplo:\n"
            "- envíos\n"
            "- medios de pago\n"
            "- cómo se usa un producto\n"
            "- tiempos de entrega\n"
            "- seguimiento\n"
            "- dudas frecuentes antes de comprar\n\n"
            "Además, se adapta al negocio y a las preguntas reales que te hacen tus clientes."
        ),
        keywords=["que responde", "qué responde", "preguntas", "que tipo de preguntas", "faq", "faqs", "dudas", "consultas"],
        follow_ups=["¿Se puede adaptar a mi tienda?", "¿Tengo que saber programar?"],
    ),
    FAQ(
        key="shopify",
        title="¿Se instala en Shopify?",
        answer=(
            "Sí, se puede instalar en Shopify 👍\n\n"
            "Se agrega como un chat flotante dentro de la tienda, sin tocar el checkout.\n\n"
            "También se puede adaptar a otras webs simples, pero hoy está pensado especialmente para ecommerce."
        ),
        keywords=["shopify", "se instala en shopify", "tienda", "ecommerce", "web", "pagina", "página"],
        follow_ups=["¿Tengo que saber programar?", "¿Cuánto tarda la instalación?"],
    ),
    FAQ(
        key="programar",
        title="¿Tengo que saber programar?",
        answer=(
            "No. La idea es justamente que no tengas que meterte en algo técnico 👍\n\n"
            "Se deja instalado y funcionando para tu tienda.\n\n"
            "Después, si querés, se pueden ir ajustando respuestas y mejoras con el tiempo."
        ),
        keywords=["programar", "codigo", "código", "tecnico", "técnico", "saber programar", "developer", "desarrollador"],
        follow_ups=["¿Cuánto tarda la instalación?", "¿Se puede adaptar a mi tienda?"],
    ),
    FAQ(
        key="adaptar",
        title="¿Se puede adaptar a mi tienda?",
        answer=(
            "Sí. No es un bot genérico tirado así nomás 👍\n\n"
            "Se puede ajustar al tipo de producto, a tu tono de marca y a las preguntas reales que recibís.\n\n"
            "La idea es que se sienta útil, claro y natural para tus clientes."
        ),
        keywords=["adaptar", "personalizar", "personalizado", "mi tienda", "mi marca", "se puede adaptar", "custom"],
        follow_ups=["¿Qué tipo de preguntas responde?", "¿Cuánto tarda la instalación?"],
    ),
    FAQ(
        key="instalacion",
        title="¿Cuánto tarda la instalación?",
        answer=(
            "Depende del caso, pero la instalación base suele ser bastante rápida 👍\n\n"
            "Primero se prepara el bot con tus preguntas frecuentes y después se conecta a tu tienda.\n\n"
            "La idea es dejar algo simple, prolijo y funcional desde el comienzo."
        ),
        keywords=["cuanto tarda", "cuánto tarda", "instalacion", "instalación", "tiempo", "rapido", "rápido", "cuanto demora"],
        follow_ups=["¿Tengo que saber programar?", "¿Se puede adaptar a mi tienda?"],
    ),
    FAQ(
        key="ventas",
        title="¿Esto ayuda a vender más?",
        answer=(
            "Sí, puede ayudar mucho 👍\n\n"
            "No porque empuje al cliente, sino porque responde rápido, saca dudas y evita que se enfríe la compra.\n\n"
            "Muchas veces la venta no se cae por el producto, sino porque nadie respondió a tiempo."
        ),
        keywords=["vende mas", "vende más", "conversion", "conversión", "ventas", "sirve para vender", "convierte", "conversiones"],
        follow_ups=["¿Cómo funciona?", "¿Qué tipo de preguntas responde?"],
    ),
    FAQ(
        key="precio",
        title="¿Cuánto cuesta?",
        answer=(
            "Eso puede variar según lo que necesite tu tienda 👍\n\n"
            "La base es dejarte un asistente simple, útil y bien integrado.\n\n"
            f"Si querés, escribinos a {SUPPORT_EMAIL} y te contamos opciones según tu caso."
        ),
        keywords=["precio", "cuanto cuesta", "cuánto cuesta", "valor", "sale cuanto", "sale cuánto", "costa", "plan"],
        follow_ups=["¿Se puede adaptar a mi tienda?", "¿Cómo funciona?"],
    ),
    FAQ(
        key="contacto",
        title="Quiero hablar con alguien",
        answer=(
            f"Claro. Podés escribirnos a {SUPPORT_EMAIL} y vemos tu caso sin compromiso."
        ),
        keywords=["hablar", "contacto", "mail", "correo", "email", "asesor", "persona", "humano"],
        follow_ups=["¿Cómo funciona?", "¿Cuánto cuesta?"],
    ),
]

BASE_QUICK_REPLIES = [
    "¿Cómo funciona?",
    "¿Se instala en Shopify?",
    "¿Tengo que saber programar?",
]

GREETING = (
    f"Hola, soy el asistente virtual de {BRAND_NAME}. "
    "Te muestro cómo un chat automático puede responder dudas, ahorrar tiempo y ayudar a vender más."
)

FALLBACK = (
    "No encontré una respuesta exacta para eso.\n\n"
    f"Si querés, escribinos a {SUPPORT_EMAIL} y lo vemos con tu caso."
)

BUY_INTENT_KEYWORDS = {
    "me interesa",
    "quiero esto",
    "lo quiero",
    "quiero instalarlo",
    "quiero ponerlo",
    "quiero automatizar",
    "precio",
    "cuanto cuesta",
    "cuánto cuesta",
}

DEMO_INTENT_KEYWORDS = {
    "ver demo",
    "demo",
    "mostrame",
    "muestreme",
    "mostrar",
    "como funciona",
    "cómo funciona",
}

TECH_INTENT_KEYWORDS = {
    "programar",
    "codigo",
    "código",
    "tecnico",
    "técnico",
    "developer",
    "desarrollador",
}

CONTACT_INTENT_KEYWORDS = {
    "hablar con alguien",
    "contacto",
    "mail",
    "correo",
    "email",
    "humano",
    "persona",
}


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    replacements = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ñ": "n",
    }
    for a, b in replacements.items():
        text = text.replace(a, b)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def default_suggestions() -> List[str]:
    return BASE_QUICK_REPLIES.copy()


def find_best_faq(message: str) -> FAQ | None:
    text = normalize_text(message)
    best_faq = None
    best_score = 0

    for faq in FAQS:
        score = 0
        for keyword in faq.keywords:
            keyword_norm = normalize_text(keyword)
            if keyword_norm in text:
                score += 3

        title_words = normalize_text(faq.title).split()
        score += sum(1 for w in title_words if len(w) > 3 and w in text)

        if score > best_score:
            best_score = score
            best_faq = faq

    return best_faq if best_score > 0 else None


def build_reply(message: str) -> tuple[str, List[str]]:
    msg = normalize_text(message)

    if msg in {"hola", "buenas", "buen dia", "buenos dias", "buenas tardes", "buenas noches"}:
        return GREETING, default_suggestions()

    if any(keyword in msg for keyword in BUY_INTENT_KEYWORDS):
        return (
            "Buenísimo 👍\n\n"
            "La idea es instalarte un asistente simple, claro y útil para tu tienda.\n\n"
            f"Si querés ver opciones o contarme tu caso, escribinos a {SUPPORT_EMAIL}."
        ), ["¿Cómo funciona?", "¿Se puede adaptar a mi tienda?"]

    if any(keyword in msg for keyword in DEMO_INTENT_KEYWORDS):
        faq = next((f for f in FAQS if f.key == "funciona"), None)
        if faq:
            return faq.answer, faq.follow_ups or default_suggestions()

    if any(keyword in msg for keyword in TECH_INTENT_KEYWORDS):
        faq = next((f for f in FAQS if f.key == "programar"), None)
        if faq:
            return faq.answer, faq.follow_ups or default_suggestions()

    if any(keyword in msg for keyword in CONTACT_INTENT_KEYWORDS):
        faq = next((f for f in FAQS if f.key == "contacto"), None)
        if faq:
            return faq.answer, faq.follow_ups or default_suggestions()

    faq = find_best_faq(message)
    if faq:
        return faq.answer, faq.follow_ups or default_suggestions()

    return FALLBACK, default_suggestions()


@app.get("/")
def home():
    return render_template_string(HOME_HTML, brand_name=BRAND_NAME)


@app.get("/health")
def health():
    return jsonify({"ok": True, "service": BRAND_NAME})


@app.get("/config")
def config():
    return jsonify(
        {
            "brand_name": BRAND_NAME,
            "primary_color": PRIMARY_COLOR,
            "secondary_color": SECONDARY_COLOR,
            "quick_replies": default_suggestions(),
            "support_email": SUPPORT_EMAIL,
        }
    )


@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    print("USER:", message)

    if not message:
        return jsonify(
            {
                "reply": "Escribime tu consulta y te ayudo.",
                "suggestions": default_suggestions(),
            }
        ), 400

    reply, suggestions = build_reply(message)
    return jsonify({"reply": reply, "suggestions": suggestions})


@app.get("/widget")
def widget():
    return render_template_string(
        WIDGET_HTML,
        brand_name=BRAND_NAME,
        primary_color=PRIMARY_COLOR,
        secondary_color=SECONDARY_COLOR,
        support_email=SUPPORT_EMAIL,
    )


@app.get("/widget.js")
def widget_js():
    base_url = request.host_url.rstrip("/")
    script = WIDGET_JS.replace("__BASE_URL__", base_url)
    return Response(script, mimetype="application/javascript")


HOME_HTML = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ brand_name }} Bot</title>
  <style>
    body{font-family:Arial,Helvetica,sans-serif;margin:0;padding:40px;background:#f8fafc;color:#0f172a}
    .card{max-width:820px;margin:0 auto;background:white;border-radius:18px;padding:32px;box-shadow:0 10px 30px rgba(15,23,42,.08)}
    h1{margin-top:0}
    code{background:#e2e8f0;padding:2px 6px;border-radius:6px}
    .demo{margin-top:18px;padding:14px 16px;background:#f5f3ff;border:1px solid #ddd6fe;border-radius:12px}
  </style>
</head>
<body>
  <div class="card">
    <h1>{{ brand_name }} Bot</h1>
    <p>La app está funcionando correctamente.</p>
    <div class="demo">
      <strong>Endpoints:</strong><br>
      <code>/health</code><br>
      <code>/widget</code><br>
      <code>/widget.js</code><br>
      <code>/chat</code>
    </div>
    <p>Para embeberlo en Shopify, pegá este script antes de <code>&lt;/body&gt;</code>:</p>
    <pre><code>&lt;script src="{{ request.host_url.rstrip('/') }}/widget.js" defer&gt;&lt;/script&gt;</code></pre>
  </div>
</body>
</html>
"""


WIDGET_HTML = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ brand_name }} Chat</title>
  <style>
    :root {
      --primary: {{ primary_color }};
      --secondary: {{ secondary_color }};
      --bg: #f8fafc;
      --text: #0f172a;
      --muted: #64748b;
      --border: #e2e8f0;
      --bubble-bot: #ede9fe;
      --bubble-user: #0f172a;
    }
    *{box-sizing:border-box}
    body{margin:0;font-family:Arial,Helvetica,sans-serif;background:#fff;color:var(--text)}
    .chat{display:flex;flex-direction:column;height:100vh}
    .header{
        position: relative;
        padding:14px 16px;
        background:linear-gradient(135deg,var(--primary),var(--secondary));
        color:#fff
    }

    .close-btn{
        position:absolute;
        top:10px;
        right:12px;
        background:transparent;
        border:none;
        color:#fff;
        font-size:22px;
        cursor:pointer;
    }

    @media (max-width: 600px){
      .close-btn{
        font-size:26px;
      }
    }

    .header-title{font-weight:700}
    .header-sub{font-size:13px;opacity:.95;margin-top:4px}
    .messages{flex:1;overflow:auto;padding:14px;background:var(--bg)}
    .msg{max-width:86%;padding:12px 14px;border-radius:16px;margin:8px 0;line-height:1.45;white-space:pre-wrap}
    .bot{background:var(--bubble-bot);border-top-left-radius:6px}
    .user{background:var(--bubble-user);color:#fff;margin-left:auto;border-top-right-radius:6px}
    .quick{padding:12px;background:#fff;border-top:1px solid var(--border);display:flex;gap:8px;flex-wrap:wrap}
    .quick button{border:none;border-radius:999px;padding:8px 12px;background:#e2e8f0;color:#0f172a;cursor:pointer;font-size:12px}
    .composer{display:flex;gap:8px;padding:12px;background:#fff;border-top:1px solid var(--border)}
    .composer input{
      flex:1;
      border:1px solid var(--border);
      border-radius:999px;
      padding:12px 14px;
      font-size:16px;
    }
    .composer button{border:none;border-radius:999px;padding:12px 16px;background:var(--primary);color:#fff;font-weight:700;cursor:pointer}
    .footer{padding:10px 14px;font-size:12px;color:var(--muted);background:#fff;border-top:1px solid var(--border)}
    a{color:inherit}
  </style>
</head>
<body>
  <div class="chat">
    <div class="header">
        <button id="closeBtn" class="close-btn">✕</button>
        <div class="header-title">{{ brand_name }}</div>
        <div class="header-sub">Mostrá cómo responde dudas, ahorra tiempo y acompaña la compra</div>
    </div>

    <div id="messages" class="messages"></div>

    <div class="quick" id="quickReplies"></div>

    <div class="composer">
      <input id="messageInput" type="text" placeholder="Escribí tu consulta..." />
      <button id="sendBtn">Enviar</button>
    </div>

    <div class="footer">
      Si querés hablar con alguien: <a href="mailto:{{ support_email }}">{{ support_email }}</a>
    </div>
  </div>

<script>
  const messagesEl = document.getElementById('messages');
  const quickRepliesEl = document.getElementById('quickReplies');
  const inputEl = document.getElementById('messageInput');
  const sendBtn = document.getElementById('sendBtn');

  function addMessage(text, who) {
    const el = document.createElement('div');
    el.className = 'msg ' + who;
    el.textContent = text;
    messagesEl.appendChild(el);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function renderQuickReplies(items) {
    quickRepliesEl.innerHTML = '';
    (items || []).forEach((item) => {
      const btn = document.createElement('button');
      btn.textContent = item;
      btn.onclick = () => sendMessage(item);
      quickRepliesEl.appendChild(btn);
    });
  }

  async function loadConfig() {
    const res = await fetch('/config');
    const config = await res.json();
    renderQuickReplies(config.quick_replies || []);
    addMessage(
      `Hola, soy el asistente virtual de ${config.brand_name}. Te muestro cómo un chat automático puede responder dudas y ayudar a vender más. ¿En qué querés que te lo muestre?`,
      'bot'
    );
  }

  async function sendMessage(message) {
    const text = (message ?? inputEl.value).trim();
    if (!text) return;
    addMessage(text, 'user');
    inputEl.value = '';

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      addMessage(data.reply || 'Hubo un error al responder.', 'bot');
      renderQuickReplies(data.suggestions || []);
    } catch (err) {
      addMessage('Hubo un problema al responder. Intentá de nuevo en unos segundos.', 'bot');
    }
  }

  sendBtn.addEventListener('click', () => sendMessage());
  inputEl.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendMessage();
  });

  loadConfig();

  document.getElementById('closeBtn').addEventListener('click', function () {
    window.parent.postMessage('closeChat', '*');
  });
</script>
</body>
</html>
"""


WIDGET_JS = r"""
(function () {
  if (window.__NIVORA_BOT_LOADED__) return;
  window.__NIVORA_BOT_LOADED__ = true;

  var baseUrl = "__BASE_URL__";

  var button = document.createElement('button');
  var label = document.createElement('div');
  label.innerText = '¿Dudas?';
  label.style.position = 'fixed';
  label.style.right = '20px';
  label.style.bottom = '82px';
  label.style.background = '#0f172a';
  label.style.color = '#fff';
  label.style.padding = '4px 10px';
  label.style.borderRadius = '999px';
  label.style.fontSize = '12px';
  label.style.fontWeight = '600';
  label.style.boxShadow = '0 6px 15px rgba(0,0,0,0.2)';
  label.style.zIndex = '999999';
  label.style.whiteSpace = 'nowrap';
  label.style.transform = 'translateX(10%)';

  button.setAttribute('aria-label', 'Abrir chat');
  button.innerHTML = '💬';
  button.style.position = 'fixed';
  button.style.right = '20px';
  button.style.bottom = '20px';
  button.style.width = '60px';
  button.style.height = '60px';
  button.style.border = 'none';
  button.style.borderRadius = '999px';
  button.style.background = 'linear-gradient(135deg, #0f172a, #7c3aed)';
  button.style.color = '#fff';
  button.style.fontSize = '26px';
  button.style.cursor = 'pointer';
  button.style.boxShadow = '0 10px 30px rgba(124, 58, 237, .35)';
  button.style.zIndex = '999999';

  var frame = document.createElement('iframe');
  frame.src = baseUrl + '/widget';
  frame.style.position = 'fixed';
  frame.style.right = '20px';
  frame.style.bottom = '92px';
  frame.style.width = '380px';
  frame.style.maxWidth = 'calc(100vw - 24px)';
  frame.style.height = '620px';
  frame.style.maxHeight = 'calc(100vh - 120px)';
  frame.style.border = 'none';
  frame.style.borderRadius = '18px';
  frame.style.boxShadow = '0 15px 50px rgba(15, 23, 42, .18)';
  frame.style.overflow = 'hidden';
  frame.style.background = '#fff';
  frame.style.zIndex = '999998';
  frame.style.display = 'none';

  button.addEventListener('click', function () {
    var isOpen = frame.style.display === 'block';
    frame.style.display = isOpen ? 'none' : 'block';
    label.style.display = isOpen ? 'block' : 'none';
  });

  document.body.appendChild(frame);
  document.body.appendChild(button);
  document.body.appendChild(label);

  window.addEventListener('message', function (event) {
    if (event.data === 'closeChat') {
      frame.style.display = 'none';
      label.style.display = 'block';
    }
  });
})();
"""


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=True)
