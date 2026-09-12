import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";

const h = React.createElement;

const API_URL = "https://pet-adoption-q581.onrender.com/api/gatos/";
const FALLBACK_IMAGE = "./src/img/logo.jpeg";

const navLinks = [
  { id: "animais", label: "Animais" },
  { id: "como-adotar", label: "Como adotar" },
  { id: "contato", label: "Contato" }
];

const energyGuides = [
  {
    title: "Guardiões",
    text: "Maduros, serenos e presentes. Felinos que parecem proteger a casa com o olhar."
  },
  {
    title: "Magos",
    text: "Curiosos, independentes e observadores. Companheiros para quem respeita mistério."
  },
  {
    title: "Curandeiros",
    text: "Afetuosos, ronronadores e sensíveis ao estado emocional do tutor."
  },
  {
    title: "Elementais",
    text: "Ativos, brincalhões e solares. Energia de movimento, descoberta e alegria."
  }
];

function scrollToSection(event, id) {
  event.preventDefault();
  const section = document.getElementById(id);

  if (!section) {
    return;
  }

  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const scrollMarginTop = Number.parseFloat(window.getComputedStyle(section).scrollMarginTop) || 0;
  const start = window.scrollY;
  const target = Math.max(0, section.getBoundingClientRect().top + start - scrollMarginTop);
  const distance = target - start;

  if (prefersReducedMotion || Math.abs(distance) < 2) {
    window.scrollTo(0, target);
    window.history.pushState(null, "", `#${id}`);
    return;
  }

  const duration = Math.min(1100, Math.max(680, Math.abs(distance) * 0.45));
  const startedAt = window.performance.now();
  const easeInOutCubic = (value) =>
    value < 0.5 ? 4 * value * value * value : 1 - Math.pow(-2 * value + 2, 3) / 2;

  document.documentElement.classList.add("is-animated-scrolling");
  section.classList.remove("scroll-arrived");

  function animateScroll(now) {
    const progress = Math.min((now - startedAt) / duration, 1);
    window.scrollTo(0, start + distance * easeInOutCubic(progress));

    if (progress < 1) {
      window.requestAnimationFrame(animateScroll);
      return;
    }

    document.documentElement.classList.remove("is-animated-scrolling");
    window.history.pushState(null, "", `#${id}`);
    section.classList.add("scroll-arrived");
    window.setTimeout(() => section.classList.remove("scroll-arrived"), 700);
  }

  window.requestAnimationFrame(animateScroll);
}

function normalizeText(value) {
  return String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

function includesAny(text, words) {
  return words.some((word) => text.includes(word));
}

function getCatGender(value) {
  if (value === "M") {
    return "Energia masculina";
  }

  if (value === "F") {
    return "Energia feminina";
  }

  return "Perfil felino";
}

function getCatAge(value) {
  if (!value) {
    return "Ciclo reservado";
  }

  return `${value} mes(es)`;
}

function getEnergyMatch(cat) {
  const description = normalizeText(cat.descricao);
  const age = Number(cat.idade) || 0;

  if (age >= 60 || includesAny(description, ["calmo", "sereno", "tranquilo", "companheiro", "olhar", "adulto", "maduro"])) {
    return {
      label: "Guardião",
      description: "Protetor sereno, de presença profunda e energia de paz."
    };
  }

  if (includesAny(description, ["curioso", "independente", "observador", "misterio", "esperto", "explorador"])) {
    return {
      label: "Mago",
      description: "Observador, intuitivo e cheio de mistério no olhar."
    };
  }

  if (includesAny(description, ["carinhoso", "ronron", "colo", "docil", "amoroso", "apegado", "manso"])) {
    return {
      label: "Curandeiro",
      description: "Acolhedor, afetivo e sensível a quem precisa de companhia."
    };
  }

  if ((age > 0 && age <= 12) || includesAny(description, ["brincalhao", "ativo", "energia", "agitado", "filhote", "aventureiro"])) {
    return {
      label: "Elemental",
      description: "Vivo, brincalhão e pronto para movimentar a energia da casa."
    };
  }

  const seed = normalizeText(`${cat.cor || ""}${cat.sexo || ""}${cat.idade || ""}${cat.descricao || ""}`).length % 4;
  const fallbackMatches = [
    {
      label: "Guardião",
      description: "Presença protetora para lares que buscam calma e lealdade."
    },
    {
      label: "Mago",
      description: "Alma observadora para quem respeita independência e encanto."
    },
    {
      label: "Curandeiro",
      description: "Companhia terna para criar vínculo com paciência e cuidado."
    },
    {
      label: "Elemental",
      description: "Energia leve para lares abertos a descoberta e brincadeira."
    }
  ];

  return fallbackMatches[seed];
}

function getCatImage(value) {
  if (!value) {
    return FALLBACK_IMAGE;
  }

  if (value.startsWith("http://") || value.startsWith("https://")) {
    return value;
  }

  const apiOrigin = new URL(API_URL).origin;
  const cleanPath = value.startsWith("/") ? value : `/media/${value}`;
  return `${apiOrigin}${cleanPath}`;
}

function useRevealAnimation() {
  useEffect(() => {
    const items = document.querySelectorAll(".reveal");

    if (!("IntersectionObserver" in window)) {
      items.forEach((item) => item.classList.add("is-visible"));
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -12% 0px", threshold: 0.16 }
    );

    items.forEach((item) => observer.observe(item));

    return () => observer.disconnect();
  }, []);
}

function useActiveSection() {
  const [activeSection, setActiveSection] = useState("inicio");

  useEffect(() => {
    const sections = ["inicio", ...navLinks.map((link) => link.id), "ajudar"]
      .map((id) => document.getElementById(id))
      .filter(Boolean);

    if (!("IntersectionObserver" in window)) {
      return undefined;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

        if (visible) {
          setActiveSection(visible.target.id);
        }
      },
      { rootMargin: "-25% 0px -55% 0px", threshold: [0.1, 0.35, 0.6] }
    );

    sections.forEach((section) => observer.observe(section));

    return () => observer.disconnect();
  }, []);

  return activeSection;
}

function Header() {
  const activeSection = useActiveSection();

  return h(
    "header",
    { className: "site-header" },
    h(
      "div",
      { className: "container topbar" },
      h(
        "a",
        {
          className: "brand",
          href: "#inicio",
          "aria-label": "Voltar ao início do Lar Bastet",
          onClick: (event) => scrollToSection(event, "inicio")
        },
        h("img", {
          className: "brand-logo",
          src: FALLBACK_IMAGE,
          alt: "Logo do projeto Lar Bastet"
        }),
        h(
          "div",
          { className: "brand-copy" },
          h("strong", null, "Lar Bastet"),
          h("span", null, "Proteção, magia e adoção responsável")
        )
      ),
      h(
        "nav",
        { className: "main-nav", "aria-label": "Principal" },
        navLinks.map((link) =>
          h(
            "a",
            {
              key: link.id,
              href: `#${link.id}`,
              className: activeSection === link.id ? "is-active" : "",
              onClick: (event) => scrollToSection(event, link.id)
            },
            link.label
          )
        )
      )
    )
  );
}

function Hero() {
  return h(
    "section",
    { className: "hero-section section-screen", id: "inicio" },
    h(
      "div",
      { className: "container hero" },
      h(
        "div",
        { className: "hero-copy reveal is-visible" },
        h("p", { className: "eyebrow" }, "Projeto independente de proteção felina"),
        h("h1", null, "Deixe a magia entrar no seu lar."),
        h(
          "p",
          { className: "hero-text" },
          "O Lar Bastet acolhe gatos em vulnerabilidade, cuida de suas feridas visíveis e invisíveis e cria encontros de almas entre felinos resgatados e famílias preparadas para proteger. Em ",
          h("strong", null, "Campo Limpo Paulista/SP"),
          ", cada adoção é tratada como um pacto de cuidado, presença e recomeço."
        ),
        h(
          "div",
          { className: "hero-actions" },
          h(
            "a",
            {
              className: "button button-primary",
              href: "#animais",
              onClick: (event) => scrollToSection(event, "animais")
            },
            "Ver animais"
          ),
          h(
            "a",
            {
              className: "button button-secondary",
              href: "#como-adotar",
              onClick: (event) => scrollToSection(event, "como-adotar")
            },
            "Como adotar"
          )
        )
      ),
      h(
        "aside",
        { className: "hero-panel reveal is-visible" },
        h(
          "div",
          { className: "panel-card panel-card-highlight" },
          h("span", { className: "panel-label" }, "Missão"),
          h("p", null, "Transformar dor em passagem, abandono em proteção e cada resgate em uma ponte segura para um lar destinado.")
        ),
        h(
          "div",
          { className: "panel-card stats-card" },
          h("div", null, h("strong", null, "+100"), h("span", null, "adoções e resgates apoiados")),
          h("div", null, h("strong", null, "100%"), h("span", null, "feito com coragem, cuidado e rede solidária"))
        )
      )
    )
  );
}

function AboutSection() {
  const cards = [
    {
      title: "Resgate com coragem",
      text: "Cada gato acolhido recebe atendimento dedicado, observação e suporte para recuperar a saúde, a confiança e o brilho no olhar."
    },
    {
      title: "Preparação para a conexão",
      text: "O processo prioriza lares seguros, rotinas compatíveis e famílias que entendam que adotar é assumir proteção por toda uma vida."
    },
    {
      title: "Comunidade que sustenta",
      text: "O projeto cresce com pessoas que doam recursos, rações, divulgam os gatos e ajudam a multiplicar encontros responsáveis."
    }
  ];

  return h(
    "section",
    { className: "section section-light", id: "sobre" },
    h(
      "div",
      { className: "container" },
      h(
        "div",
        { className: "section-heading section-heading-simple reveal" },
        h("h2", null, "Sobre o projeto")
      ),
      h(
        "div",
        { className: "about-grid" },
        cards.map((card) =>
          h(
            "article",
            { className: "about-card reveal", key: card.title },
            h("h3", null, card.title),
            h("p", null, card.text)
          )
        )
      )
    )
  );
}

function CatCard({ cat }) {
  const energy = useMemo(() => getEnergyMatch(cat), [cat]);

  return h(
    "article",
    { className: "cat-card reveal is-visible" },
    h("img", {
      src: getCatImage(cat.foto),
      alt: cat.cor ? `Gato de pelagem ${cat.cor}` : "Gato disponível para adoção",
      loading: "lazy",
      onError: (event) => {
        event.currentTarget.src = FALLBACK_IMAGE;
      }
    }),
    h(
      "div",
      { className: "cat-card-content" },
      h(
        "div",
        { className: "cat-card-header" },
        h("h3", null, `${getCatGender(cat.sexo)} - ${cat.cor || "Pelagem especial"}`),
        h("span", null, getCatAge(cat.idade))
      ),
      h("span", { className: "cat-vibe" }, `Vibe: ${energy.label}`),
      h("p", null, cat.descricao || energy.description),
      h(
        "a",
        {
          className: "button button-primary button-full",
          href: "#como-adotar",
          onClick: (event) => scrollToSection(event, "como-adotar")
        },
        "Sentir essa conexão"
      )
    )
  );
}

function CatGridState({ message, action }) {
  return h(
    "article",
    { className: "cat-card cat-card-state reveal is-visible" },
    h(
      "div",
      { className: "cat-card-content" },
      h(
        "div",
        { className: "cat-card-header" },
        h("h3", null, "Lar Bastet"),
        h("span", null, "Info")
      ),
      h("p", null, message),
      action
    )
  );
}

function AnimalsSection() {
  const [status, setStatus] = useState("loading");
  const [cats, setCats] = useState([]);

  useEffect(() => {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 8000);

    async function loadCats() {
      try {
        const response = await fetch(API_URL, { signal: controller.signal });

        if (!response.ok) {
          throw new Error(`Erro ao carregar gatos: ${response.status}`);
        }

        const data = await response.json();
        setCats(Array.isArray(data) ? data : []);
        setStatus(Array.isArray(data) && data.length ? "ready" : "empty");
      } catch {
        setStatus("error");
      } finally {
        window.clearTimeout(timeout);
      }
    }

    loadCats();

    return () => {
      window.clearTimeout(timeout);
      controller.abort();
    };
  }, []);

  return h(
    "section",
    { className: "section featured-section section-screen", id: "animais" },
    h(
      "div",
      { className: "container" },
      h(
        "div",
        { className: "section-heading section-heading-inline reveal" },
        h(
          "div",
          null,
          h("p", { className: "eyebrow" }, "Animais"),
          h("h2", null, "Conheça felinos por temperamento, energia e história.")
        )
      ),
      h(
        "div",
        { className: "animals-cta-row reveal" },
        h(
          "a",
          {
            className: "button button-accent animals-adoption-link",
            href: "#como-adotar",
            onClick: (event) => scrollToSection(event, "como-adotar")
          },
          "Começar adoção"
        )
      ),
      h(
        "div",
        { className: "vibe-guide", "aria-label": "Categorias de energia dos gatos" },
        energyGuides.map((guide) =>
          h(
            "article",
            { className: "reveal", key: guide.title },
            h("span", null, guide.title),
            h("p", null, guide.text)
          )
        )
      ),
      h(
        "div",
        { className: "cat-grid" },
        status === "loading" &&
          h(CatGridState, {
            message: "Consultando a vitrine de almas felinas. Em instantes, as conexões disponíveis aparecem por aqui."
          }),
        status === "empty" &&
          h(CatGridState, {
            message: "No momento não há gatos cadastrados para exibir. Entre em contato para saber sobre novos resgates e novas conexões.",
            action: h(
              "a",
              {
                className: "button button-secondary button-full",
                href: "#contato",
                onClick: (event) => scrollToSection(event, "contato")
              },
              "Falar com o projeto"
            )
          }),
        status === "error" &&
          h(CatGridState, {
            message: "Não foi possível carregar os gatos agora. Tente novamente em instantes ou fale com o Lar Bastet.",
            action: h(
              "a",
              {
                className: "button button-secondary button-full",
                href: "#contato",
                onClick: (event) => scrollToSection(event, "contato")
              },
              "Falar com o projeto"
            )
          }),
        status === "ready" && cats.map((cat, index) => h(CatCard, { cat, key: cat.id_pet || cat.id || index }))
      )
    )
  );
}

function AdoptionSection() {
  const [sent, setSent] = useState(false);

  function handleSubmit(event) {
    event.preventDefault();
    setSent(true);
  }

  return h(
    "section",
    { className: "section section-light section-screen", id: "como-adotar" },
    h(
      "div",
      { className: "container adoption-layout" },
      h(
        "div",
        { className: "adoption-box reveal" },
        h("p", { className: "eyebrow" }, "Como adotar"),
        h("h2", null, "Adotar é um encontro que pede preparo, presença e compromisso."),
        h(
          "div",
          { className: "adoption-steps" },
          [
            ["1", "Sinta a conexão", "Conheça a energia do gato e perceba se ela conversa com sua rotina."],
            ["2", "Abra o caminho", "Preencha a intenção de adoção com suas informações e forma de contato."],
            ["3", "Prepare o lar", "Organize um ambiente telado, seguro, protegido e acolhedor para a chegada."]
          ].map(([number, title, text]) =>
            h(
              "article",
              { key: number },
              h("span", null, number),
              h("h3", null, title),
              h("p", null, text)
            )
          )
        )
      ),
      h(
        "form",
        { className: "form-card form-grid reveal", onSubmit: handleSubmit },
        h("h3", null, "Formulário de intenção de adoção"),
        h(
          "div",
          { className: "field" },
          h("label", { htmlFor: "nome" }, "Nome completo"),
          h("input", { id: "nome", name: "nome", type: "text", placeholder: "Digite seu nome completo", required: true })
        ),
        h(
          "div",
          { className: "field" },
          h("label", { htmlFor: "telefone" }, "Telefone"),
          h("input", { id: "telefone", name: "telefone", type: "tel", placeholder: "(00) 00000-0000", required: true })
        ),
        h(
          "div",
          { className: "field" },
          h("label", { htmlFor: "email" }, "Email"),
          h("input", { id: "email", name: "email", type: "email", placeholder: "voce@email.com" })
        ),
        h(
          "div",
          { className: "field" },
          h("label", { htmlFor: "animal" }, "Gato ou energia de interesse"),
          h("input", { id: "animal", name: "animal", type: "text", placeholder: "Ex.: Nala, Guardião, Curandeiro" })
        ),
        h(
          "div",
          { className: "field" },
          h("label", { htmlFor: "mensagem" }, "Fale sobre sua rotina, seu lar e sua conexão"),
          h("textarea", {
            id: "mensagem",
            name: "mensagem",
            placeholder: "Conte se mora em casa ou apartamento, se há telas de proteção e como será o cuidado.",
            required: true
          })
        ),
        h("button", { className: "button button-primary", type: "submit" }, "Enviar intenção"),
        h(
          "p",
          { className: sent ? "form-feedback is-visible" : "form-feedback" },
          "Intenção registrada na página. Para finalizar o contato, envie também seus dados pelo WhatsApp ou email do Lar Bastet."
        )
      )
    )
  );
}

function HelpSection() {
  const donations = [
    ["Chave Pix", "CNPJ: 55.183.245/0001-93"],
    ["Ração como cuidado", "Golden gatos ou Special Cat. Qualquer quantidade fortalece a rotina dos resgatados."],
    ["Itens de proteção", "Vermífugos, granulado de madeira, potes, areia, mantas e medicamentos fazem diferença real."],
    ["Divulgação", "Compartilhar os gatos, suas histórias e necessidades também salva vidas."]
  ];

  return h(
    "section",
    { className: "section support-section", id: "ajudar" },
    h(
      "div",
      { className: "container support-box reveal" },
      h(
        "div",
        null,
        h("p", { className: "eyebrow" }, "Quero ajudar"),
        h("h2", null, "Nem todo mundo pode adotar agora, mas toda ajuda sustenta uma vida em travessia."),
        h("p", null, "Sua ajuda vira alimento, cuidado veterinário, abrigo e tempo para que cada gato volte a confiar.")
      ),
      h(
        "div",
        { className: "donation-grid donation-grid-compact" },
        donations.map(([title, text]) =>
          h("article", { className: "donation-card", key: title }, h("h3", null, title), h("p", null, text))
        )
      )
    )
  );
}

function ContactSection() {
  const contacts = [
    ["Telefone", "(11) 96498-4749"],
    ["Email", "teles.katy@gmail.com"],
    [
      "Instagram",
      h(
        "a",
        {
          href: "https://www.instagram.com/katy_teles_bastet",
          target: "_blank",
          rel: "noopener noreferrer"
        },
        "@katy_teles_bastet"
      )
    ]
  ];

  return h(
    "section",
    { className: "section section-screen contact-section", id: "contato" },
    h(
      "div",
      { className: "container" },
      h(
        "div",
        { className: "section-heading reveal" },
        h("p", { className: "eyebrow" }, "Contato"),
        h("h2", null, "Fale com o Lar Bastet para tirar dúvidas, apoiar ou iniciar uma adoção.")
      ),
      h(
        "div",
        { className: "contact-grid" },
        contacts.map(([title, content]) =>
          h("article", { className: "contact-card reveal", key: title }, h("h3", null, title), h("p", null, content))
        )
      )
    )
  );
}

function Footer() {
  return h(
    "footer",
    { className: "site-footer" },
    h(
      "div",
      { className: "container footer-grid" },
      h(
        "a",
        {
          className: "brand brand-footer",
          href: "#inicio",
          onClick: (event) => scrollToSection(event, "inicio")
        },
        h("img", { className: "brand-logo", src: FALLBACK_IMAGE, alt: "Logo do Lar Bastet" }),
        h(
          "div",
          { className: "brand-copy" },
          h("strong", null, "Lar Bastet"),
          h("span", null, "Cuidando de vidas, conectando almas")
        )
      ),
      h(
        "div",
        { className: "footer-links" },
        [...navLinks, { id: "ajudar", label: "Quero ajudar" }].map((link) =>
          h(
            "a",
            {
              href: `#${link.id}`,
              key: link.id,
              onClick: (event) => scrollToSection(event, link.id)
            },
            link.label
          )
        )
      ),
      h(
        "div",
        { className: "footer-contact" },
        h("p", null, "Projeto de adoção e apoio a gatos resgatados."),
        h(
          "a",
          {
            href: "#contato",
            onClick: (event) => scrollToSection(event, "contato")
          },
          "Ver telefone, email e redes sociais"
        )
      )
    )
  );
}

function App() {
  useRevealAnimation();

  return h(
    React.Fragment,
    null,
    h(Header),
    h(
      "main",
      null,
      h(Hero),
      h(AboutSection),
      h(AnimalsSection),
      h(AdoptionSection),
      h(HelpSection),
      h(ContactSection)
    ),
    h(Footer)
  );
}

createRoot(document.getElementById("root")).render(h(App));
