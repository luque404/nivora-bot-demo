const revealElements = document.querySelectorAll(".reveal");
const tiltCards = document.querySelectorAll(".tilt-card");
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const currentPage = document.body.dataset.page;
const shouldShowFloatingWidget = ["home", "precios", "sobre-nivora"].includes(currentPage);

if (shouldShowFloatingWidget) {
  const widgetScript = document.createElement("script");
  widgetScript.src = "https://nivora-bot-demo-production.up.railway.app/widget.js";
  widgetScript.defer = true;
  document.body.appendChild(widgetScript);
}

document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", (event) => {
    const targetId = anchor.getAttribute("href");
    if (!targetId || targetId === "#") return;

    const target = document.querySelector(targetId);
    if (!target) return;

    event.preventDefault();
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  });
});

if (!prefersReducedMotion) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    {
      threshold: 0.16,
      rootMargin: "0px 0px -48px 0px",
    }
  );

  revealElements.forEach((element) => observer.observe(element));

  tiltCards.forEach((card) => {
    card.addEventListener("mousemove", (event) => {
      const bounds = card.getBoundingClientRect();
      const offsetX = event.clientX - bounds.left;
      const offsetY = event.clientY - bounds.top;
      const rotateY = ((offsetX / bounds.width) - 0.5) * 5;
      const rotateX = (0.5 - (offsetY / bounds.height)) * 5;

      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
    });

    card.addEventListener("mouseleave", () => {
      card.style.transform = "";
    });
  });
} else {
  revealElements.forEach((element) => element.classList.add("is-visible"));
}

const demoChatRoot = document.querySelector("[data-demo-chat]");

if (demoChatRoot) {
  const messagesEl = demoChatRoot.querySelector("[data-demo-messages]");
  const quickEl = demoChatRoot.querySelector("[data-demo-quick]");
  const formEl = demoChatRoot.querySelector("[data-demo-form]");
  const inputEl = demoChatRoot.querySelector("[data-demo-input]");
  const apiBase =
    demoChatRoot.getAttribute("data-demo-api") ||
    "https://nivora-bot-demo-production.up.railway.app";

  const normalize = (text) =>
    text
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^\w\s]/g, " ")
      .replace(/\s+/g, " ")
      .trim();

  const scrollMessagesToBottom = () => {
    messagesEl.scrollTo({ top: messagesEl.scrollHeight, behavior: "smooth" });
  };

  const addDemoMessage = (text, who) => {
    const message = document.createElement("div");
    message.className = `demo-msg ${who === "user" ? "demo-msg-user" : "demo-msg-bot"}`;
    message.textContent = text;
    messagesEl.appendChild(message);
    requestAnimationFrame(scrollMessagesToBottom);
  };

  const renderSuggestions = (items) => {
    quickEl.innerHTML = "";
    (items || []).filter(Boolean).forEach((text) => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = text;
      button.addEventListener("click", () => sendDemoMessage(text));
      quickEl.appendChild(button);
    });
  };

  const loadDemoConfig = async () => {
    try {
      const response = await fetch(`${apiBase}/config`);
      const config = await response.json();

      messagesEl.innerHTML = "";
      addDemoMessage(config.greeting || "Hola 👋 ¿En qué puedo ayudarte?", "bot");

      const quickReplies = Array.isArray(config.quick_replies) ? config.quick_replies : [];
      renderSuggestions(quickReplies);
    } catch (error) {
      console.error("[demo-chat-config]", error);
      messagesEl.innerHTML = "";
      addDemoMessage("Hola 👋 ¿En qué puedo ayudarte?", "bot");
      renderSuggestions(["¿Qué tipo de preguntas responde?"]);
    }
  };

  const sendDemoMessage = async (rawText) => {
    const text = (rawText ?? inputEl.value).trim();
    if (!text) return;

    addDemoMessage(text, "user");
    inputEl.value = "";
    renderSuggestions([]);

    try {
      const response = await fetch(`${apiBase}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: text }),
      });

      const data = await response.json();

      window.setTimeout(() => {
        addDemoMessage(
          data.reply || "No tengo una respuesta precisa para eso en este demo 😊",
          "bot"
        );

        const suggestions = Array.isArray(data.suggestions) ? data.suggestions.slice(0, 1) : [];
        renderSuggestions(suggestions);
      }, 280);
    } catch (error) {
      console.error("[demo-chat-send]", error);
      window.setTimeout(() => {
        addDemoMessage(
          "No pude responder en este momento. Si querés, probá de nuevo en unos segundos.",
          "bot"
        );
        renderSuggestions(["¿Qué tipo de preguntas responde?"]);
      }, 280);
    }
  };

  quickEl.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => sendDemoMessage(button.textContent || ""));
  });

  formEl.addEventListener("submit", (event) => {
    event.preventDefault();
    sendDemoMessage();
  });

  inputEl.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendDemoMessage();
    }
  });

  loadDemoConfig();
}
