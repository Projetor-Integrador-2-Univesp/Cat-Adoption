import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { Button, Card, Col, Container, Form, Nav, Navbar, Row } from "react-bootstrap";

const h = React.createElement;
//Link da api das imagens e informações dos gatos
const API_URL = "https://pet-adoption-q581.onrender.com/api/gatos/";
const FALLBACK_IMAGE = "./src/img/logo.jpeg";
const navLinks = [
  { id: "animais", label: "Animais" },
  { id: "como-adotar", label: "Como adotar" },
  { id: "contato", label: "Contato" }
];

const energyGuides = [
  ["Guardiões", "Maduros, serenos e presentes. Felinos que parecem proteger a casa com o olhar."],
  ["Magos", "Curiosos, independentes e observadores. Companheiros para quem respeita mistério."],
  ["Curandeiros", "Afetuosos, ronronadores e sensíveis ao estado emocional do tutor."],
  ["Elementais", "Ativos, brincalhões e solares. Energia de movimento, descoberta e alegria."]
];

function scrollToSection(event, id) {
  event.preventDefault();
  const section = document.getElementById(id);
  if (!section) return;
  section.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" });
  window.history.pushState(null, "", `#${id}`);
}

function normalizeText(value) {
  return String(value || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
}

function getCatGender(value) {
  return value === "M" ? "Energia masculina" : value === "F" ? "Energia feminina" : "Perfil felino";
}

function getEnergyMatch(cat) {
  const description = normalizeText(cat.descricao);
  const age = Number(cat.idade) || 0;
  const has = (terms) => terms.some((term) => description.includes(term));
  if (age >= 60 || has(["calmo", "sereno", "tranquilo", "companheiro", "adulto", "maduro"])) 
    return ["Guardião", "Protetor sereno, de presença profunda e energia de paz."];
  if (has(["curioso", "independente", "observador", "misterio", "esperto", "explorador"])) 
    return ["Mago", "Observador, intuitivo e cheio de mistério no olhar."];
  if (has(["carinhoso", "ronron", "colo", "docil", "amoroso", "apegado", "manso"])) 
    return ["Curandeiro", "Acolhedor, afetivo e sensível a quem precisa de companhia."];
  if ((age > 0 && age <= 12) || has(["brincalhao", "ativo", "energia", "agitado", "filhote", "aventureiro"])) 
    return ["Elemental", "Vivo, brincalhão e pronto para movimentar a energia da casa."];
  const fallbacks = [
    ["Guardião", "Presença protetora para lares que buscam calma e lealdade."], 
    ["Mago", "Alma observadora para quem respeita independência e encanto."], 
    ["Curandeiro", "Companhia terna para criar vínculo com paciência e cuidado."], 
    ["Elemental", "Energia leve para lares abertos a descoberta e brincadeira."]];
  return fallbacks[normalizeText(`${cat.cor || ""}${cat.sexo || ""}${cat.idade || ""}${cat.descricao || ""}`).length % fallbacks.length];
}

function getCatImage(value) {
  if (!value) return FALLBACK_IMAGE;
  if (value.startsWith("http://") || value.startsWith("https://")) return value;
  return `${new URL(API_URL).origin}${value.startsWith("/") ? value : `/media/${value}`}`;
}

function useRevealAnimation() {
  useEffect(() => {
    const items = document.querySelectorAll(".reveal");
    if (!("IntersectionObserver" in window)) {
      items.forEach((item) => item.classList.add("is-visible"));
      return undefined;
    }
    const observer = new IntersectionObserver((entries) => entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    }), { rootMargin: "0px 0px -12% 0px", threshold: 0.16 });
    items.forEach((item) => observer.observe(item));
    return () => observer.disconnect();
  }, []);
}

function useActiveSection() {
  const [active, setActive] = useState("inicio");
  useEffect(() => {
    if (!("IntersectionObserver" in window)) return undefined;
    const sections = ["inicio", ...navLinks.map((link) => link.id), "ajudar"].map((id) => document.getElementById(id)).filter(Boolean);
    const observer = new IntersectionObserver((entries) => {
      const current = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (current) setActive(current.target.id);
    }, { rootMargin: "-25% 0px -55% 0px", threshold: [0.1, 0.35, 0.6] });
    sections.forEach((section) => observer.observe(section));
    return () => observer.disconnect();
  }, []);
  return active;
}

function SectionButton({ children, id, className = "", variant = "primary" }) {
  return h(Button, { as: "a", href: `#${id}`, variant, className: `button ${className}`.trim(), onClick: (event) => scrollToSection(event, id) }, children);
}

function Header() {
  const active = useActiveSection();
  return h(Navbar, { as: "header", className: "site-header", expand: "md" }, h(Container, { className: "topbar" },
    h(Navbar.Brand, { href: "#inicio", className: "brand m-0", onClick: (event) => scrollToSection(event, "inicio") }, 
    h("img", { className: "brand-logo", src: FALLBACK_IMAGE, alt: "Logo do Lar Bastet" }), 
    h("span", { className: "brand-copy" }, 
    h("strong", null, "Lar Bastet"), 
    h("small", null, "Proteção, magia e adoção responsável"))),
    h(Navbar.Toggle, { "aria-controls": "main-navigation", className: "nav-toggle" }),
    h(Navbar.Collapse, { id: "main-navigation" }, 
    h(Nav, { as: "nav", className: "main-nav ms-md-auto", "aria-label": "Principal" }, 
      navLinks.map((link) => h(Nav.Link, { key: link.id, href: `#${link.id}`, className: active === link.id ? "is-active" : "", 
      onClick: (event) => scrollToSection(event, link.id) }, link.label))))
  ));
}

function Hero() {
  return h("section", { className: "hero-section section-screen", id: "inicio" }, 
    h(Container, null, h(Row, { className: "g-4 align-items-stretch" },
    h(Col, { lg: 8 }, h("div", { className: "hero-copy reveal is-visible h-100" }, 
      h("p", { className: "eyebrow" }, "Projeto independente de proteção felina"), h("h1", null, "Deixe a magia entrar no seu lar."), 
      h("p", { className: "hero-text" }, "O Lar Bastet acolhe gatos em vulnerabilidade, cuida de suas feridas visíveis e invisíveis e cria encontros de almas entre felinos resgatados e famílias preparadas para proteger. Em ", 
      h("strong", null, "Campo Limpo Paulista/SP"), ", cada adoção é tratada como um pacto de cuidado, presença e recomeço."), 
      h("div", { className: "d-flex flex-column flex-sm-row gap-3 mt-4" }, 
      h(SectionButton, { id: "animais", className: "button-primary" }, "Ver animais"), 
      h(SectionButton, { id: "como-adotar", className: "button-ghost", variant: "outline-light" }, "Como adotar")))),

    h(Col, { lg: 4 }, h("aside", { className: "hero-panel reveal is-visible h-100" }, 
      h(Card, { className: "panel-card panel-card-highlight border-0" }, 
      h(Card.Body, null, h("span", { className: "panel-label" }, "Missão"), 
      h(Card.Text, { className: "mb-0" }, "Transformar dor em passagem, abandono em proteção e cada resgate em uma ponte segura para um lar destinado."))), 
      h(Card, { className: "panel-card stats-card border-0" }, 
      h(Card.Body, { className: "d-flex flex-column flex-sm-row flex-lg-column gap-4" }, 
      h("div", null, h("strong", null, "+100"), h("span", null, "adoções e resgates apoiados")), 
      h("div", null, h("strong", null, "100%"), h("span", null, "feito com coragem, cuidado e rede solidária"))))))
  )));
}

function AboutSection() {
  const cards = [
    ["Resgate com coragem", "Cada gato acolhido recebe atendimento dedicado, observação e suporte para recuperar a saúde, a confiança e o brilho no olhar."],
    ["Preparação para a conexão", "O processo prioriza lares seguros, rotinas compatíveis e famílias que entendam que adotar é assumir proteção por toda uma vida."], 
    ["Comunidade que sustenta", "O projeto cresce com pessoas que doam recursos, rações, divulgam os gatos e ajudam a multiplicar encontros responsáveis."]
  ];
  return h("section", { className: "section section-light", id: "sobre" }, 
    h(Container, null, h("div", { className: "section-heading reveal" }, 
      h("h2", null, "Sobre o projeto")), h(Row, { className: "g-4" },
      cards.map(([title, text]) => h(Col, { md: 6, lg: 4, key: title }, 
    h(Card, { className: "about-card reveal h-100" }, 
       h(Card.Body, null, h(Card.Title, { as: "h3" }, title), h(Card.Text, { className: "mb-0" }, text))))))));
}

function CatCard({ cat }) {
  const [vibe, description] = useMemo(() => getEnergyMatch(cat), [cat]);
  return h(Card, { className: "cat-card reveal is-visible h-100" }, 
      h(Card.Img, { variant: "top", src: getCatImage(cat.foto), alt: cat.cor ? `Gato de pelagem ${cat.cor}` : "Gato disponível para adoção", 
      loading: "lazy", onError: (event) => { event.currentTarget.src = FALLBACK_IMAGE; } }), 
      h(Card.Body, { className: "cat-card-content" }, 
        h("div", { className: "d-flex align-items-start justify-content-between gap-2" }, 
          h(Card.Title, { as: "h3", className: "mb-0" }, `${getCatGender(cat.sexo)} - ${cat.cor || "Pelagem especial"}`), 
          h("span", { className: "cat-age" }, cat.idade ? `${cat.idade} mes(es)` : "Ciclo reservado")), 
          h("span", { className: "cat-vibe" }, `Vibe: ${vibe}`), h(Card.Text, null, cat.descricao || description), h (SectionButton, { id: "como-adotar", className: "button-primary w-100 mt-auto" }, "Sentir essa conexão")));
}

function CatGridState({ message, action }) {
  return h(Card, { className: "cat-card cat-card-state reveal is-visible h-100" }, 
    h(Card.Body, { className: "cat-card-content" }, h(Card.Title, { as: "h3" }, "Lar Bastet"), h(Card.Text, null, message), action));
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
        if (!response.ok) throw new Error(`Erro ao carregar gatos: ${response.status}`);
        const data = await response.json();
        setCats(Array.isArray(data) ? data : []);
        setStatus(Array.isArray(data) && data.length ? "ready" : "empty");
      } catch { setStatus("error"); } finally { window.clearTimeout(timeout); }
    }
    loadCats();
    return () => { window.clearTimeout(timeout); controller.abort(); };
  }, []);
  
const message = status === "loading" ? "Consultando a vitrine de almas felinas. Em instantes, as conexões disponíveis aparecem por aqui." : status === "empty" ? "No momento não há gatos cadastrados para exibir. Entre em contato para saber sobre novos resgates e novas conexões." : "Não foi possível carregar os gatos agora. Tente novamente em instantes ou fale com o Lar Bastet.";
  return h("section", { className: "section featured-section section-screen", id: "animais" }, h(Container, null,
    h(Row, { className: "align-items-end g-3 mb-3" },
      h(Col, { lg: 8 }, h("div", { className: "section-heading mb-0 reveal" }, h("p", { className: "eyebrow" }, "Animais"), h("h2", null, "Conheça felinos por temperamento, energia e história."))),
      h(Col, { lg: 4, className: "text-lg-end reveal" }, h(SectionButton, { id: "como-adotar", className: "button-accent animals-adoption-link" }, "Começar adoção"))
    ),
    h(Row, { className: "g-3 g-lg-4 mb-4", "aria-label": "Categorias de energia dos gatos" },
      energyGuides.map(([title, text]) => h(Col, { sm: 6, xl: 3, key: title }, h(Card, { className: "vibe-card reveal h-100" }, h(Card.Body, null, h(Card.Title, { as: "h3" }, title), h(Card.Text, { className: "mb-0" }, text)))))
    ),
    h(Row, { className: "g-4" }, status === "ready"
      ? cats.map((cat, index) => h(Col, { sm: 6, lg: 4, xl: 3, key: cat.id_pet || cat.id || index }, h(CatCard, { cat })))
      : h(Col, { md: 6, lg: 4 }, h(CatGridState, { message, action: status !== "loading" ? h(SectionButton, { id: "contato", className: "button-ghost w-100 mt-auto", variant: "outline-light" }, "Falar com o projeto") : null }))
    )
  ));
}

function AdoptionSection() {
  const [sent, setSent] = useState(false);
  const initialFormData = {
    nome: "",
    telefone: "",
    email: "",
    interesse: "",
    rotina: ""
  };

  const [formData, setFormData] = useState(initialFormData);
  const steps = [["1", "Sinta a conexão", "Conheça a energia do gato e perceba se ela conversa com sua rotina."], ["2", "Abra o caminho", "Preencha a intenção de adoção com suas informações e forma de contato."], ["3", "Prepare o lar", "Organize um ambiente telado, seguro, protegido e acolhedor para a chegada."]];
  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((currentData) => ({ ...currentData, [name]: value }));
  };

  //envio do formulário para o WhatsApp da proprietária do Lar Bastet
  const handleSubmit = (event) => {
    event.preventDefault();
    const NUMERO_WHATSAPP = "5511964984749";

    const emojis = {
      pata: String.fromCodePoint(0x1F43E),
      perfil: String.fromCodePoint(0x1F464),
      telefone: String.fromCodePoint(0x1F4F1),
      email: String.fromCodePoint(0x1F4E7),
      brilho: String.fromCodePoint(0x2728),
      casa: String.fromCodePoint(0x1F3E1)
    };
    
    const mensagem = `${emojis.pata} *NOVA INTENÇÃO DE ADOÇÃO - LAR BASTET* ${emojis.pata}\n\n${emojis.perfil} *Nome:* ${formData.nome}\n${emojis.telefone} *Telefone de contato:* ${formData.telefone}\n${emojis.email} *E-mail:* ${formData.email}\n${emojis.brilho} *Interesse / Categoria:* ${formData.interesse}\n\n${emojis.casa} *Sobre o lar e rotina:*\n${formData.rotina}`;
    const mensagemFormatada = encodeURIComponent(mensagem);
    const url = `https://api.whatsapp.com/send/?phone=${NUMERO_WHATSAPP}&text=${mensagemFormatada}`;

    window.open(url, "_blank");
    setFormData(initialFormData);
    setSent(true);
  };

  //formulário
  return h("section", { className: "section section-light section-screen", id: "como-adotar" }, h(Container, null, h(Row, { className: "g-4 align-items-start" },
    h(Col, { lg: 5 }, h("div", { className: "adoption-box reveal" }, h("p", { className: "eyebrow" }, "Como adotar"), h("h2", null, "Adotar é um encontro que pede preparo, presença e compromisso."), h(Row, { className: "g-3 mt-1" }, steps.map(([number, title, text]) => h(Col, { sm: 4, lg: 12, key: number }, h("article", { className: "adoption-step" }, h("span", null, number), h("h3", null, title), h("p", null, text))))))),
    h(Col, { lg: 7 }, h(Form, { className: "form-card reveal", onSubmit: handleSubmit }, h("h3", null, "Formulário de intenção de adoção"),
     h(Row, { className: "g-3" },
      h(Col, { md: 6 }, h(Form.Group, { controlId: "nome" }, h(Form.Label, null, "Nome completo"), 
        h(Form.Control, { type: "text", name: "nome", value: formData.nome, onChange: handleChange, placeholder: "Digite seu nome completo", required: true }))),
      h(Col, { md: 6 }, h(Form.Group, { controlId: "telefone" }, h(Form.Label, null, "Telefone"), 
        h(Form.Control, { type: "tel", name: "telefone", value: formData.telefone, onChange: handleChange, placeholder: "(00) 00000-0000", required: true }))),
      h(Col, { md: 6 }, h(Form.Group, { controlId: "email" }, h(Form.Label, null, "Email"), 
        h(Form.Control, { type: "email", name: "email", value: formData.email, onChange: handleChange, placeholder: "voce@email.com" }))),
      h(Col, { md: 6 }, h(Form.Group, { controlId: "interesse" }, h(Form.Label, null, "Gato ou energia de interesse"), 
        h(Form.Control, { type: "text", name: "interesse", value: formData.interesse, onChange: handleChange, placeholder: "Ex.: Nala, Guardião, Curandeiro" }))),
      h(Col, { xs: 12 }, h(Form.Group, { controlId: "rotina" }, h(Form.Label, null, "Fale sobre sua rotina, seu lar e sua conexão"), 
        h(Form.Control, { as: "textarea", name: "rotina", value: formData.rotina, onChange: handleChange, rows: 5, placeholder: "Conte se mora em casa ou apartamento, se há telas de proteção e como será o cuidado.", required: true })))
      ),
     h(Button, { type: "submit", className: "button button-primary align-self-start mt-1" }, "Enviar intenção"), 
     sent && h("p", { className: "form-feedback mb-0" }, "Mensagem preparada. O WhatsApp será aberto em uma nova aba para enviar sua intenção.")))
  )));
}

function HelpSection() {
  const donations = [["Chave Pix", "CNPJ: 55.183.245/0001-93"], ["Ração como cuidado", "Golden gatos ou Special Cat. Qualquer quantidade fortalece a rotina dos resgatados."], ["Itens de proteção", "Vermífugos, granulado de madeira, potes, areia, mantas e medicamentos fazem diferença real."], ["Divulgação", "Compartilhar os gatos, suas histórias e necessidades também salva vidas."]];
  return h("section", { className: "section support-section", id: "ajudar" }, 
    h(Container, { className: "support-box reveal" }, 
    h(Row, { className: "g-4 align-items-center" }, h(Col, { lg: 5 }, 
    h("p", { className: "eyebrow" }, "Quero ajudar"), h("h2", null, "Nem todo mundo pode adotar agora, mas toda ajuda sustenta uma vida em travessia."), 
    h("p", { className: "mb-0 mt-3" }, "Sua ajuda vira alimento, cuidado veterinário, abrigo e tempo para que cada gato volte a confiar.")), 
    h(Col, { lg: 7 }, h(Row, { className: "g-3" }, donations.map(([title, text]) => h(Col, { sm: 6, key: title }, 
      h(Card, { className: "donation-card h-100" }, 
      h(Card.Body, null, h(Card.Title, { as: "h3" }, title), h(Card.Text, { className: "mb-0" }, text))))))))));
}

function ContactSection() {
  const contacts = [
    ["Telefone", "(11) 96498-4749"], ["Email", "teles.katy@gmail.com"], ["Instagram", 
      h("a", { href: "https://www.instagram.com/katy_8_bastet", target: "_blank", rel: "noopener noreferrer" }, "@katy_8_bastet")]
    ];
  return h("section", { className: "section section-screen contact-section", id: "contato" }, 
    h(Container, null, h("div", { className: "section-heading reveal" }, 
      h("p", { className: "eyebrow" }, "Contato"), h("h2", null, "Fale com o Lar Bastet para tirar dúvidas, apoiar ou iniciar uma adoção.")), 
      h(Row, { className: "g-4" }, contacts.map(([title, content]) => h(Col, { md: 4, key: title }, 
      h(Card, { className: "contact-card reveal h-100" }, h(Card.Body, null, h(Card.Title, { as: "h3" }, title), h(Card.Text, { className: "mb-0" }, content))))))));
}

function Footer() {
  return h("footer", { className: "site-footer" }, h(Container, { className: "footer-grid" }, 
    h(Row, { className: "g-4 align-items-center" }, h(Col, { lg: 5 }, 
    h("a", { className: "brand brand-footer", href: "#inicio", onClick: (event) => scrollToSection(event, "inicio") }, 
    h("img", { className: "brand-logo", src: FALLBACK_IMAGE, alt: "Logo do Lar Bastet" }), 
    h("span", { className: "brand-copy" }, h("strong", null, "Lar Bastet"), h("small", null, "Cuidando de vidas, conectando almas")))), 
    h(Col, { sm: 6, lg: 3 }, h(Nav, { className: "footer-links flex-column gap-2" }, [...navLinks, { id: "ajudar", label: "Quero ajudar" }].map((link) => 
      h(Nav.Link, { href: `#${link.id}`, 
    key: link.id, className: "p-0", onClick: (event) => 
      scrollToSection(event, link.id) }, link.label)))), h(Col, { sm: 6, lg: 4, className: "footer-contact" }, 
    h("p", null, "Projeto de adoção e apoio a gatos resgatados."), h("a", { href: "#contato", onClick: (event) => 
      scrollToSection(event, "contato") }, "Ver telefone, email e redes sociais")))));
}

function App() {
  useRevealAnimation();
  return h(React.Fragment, null, h(Header), 
    h("main", null, h(Hero), h(AboutSection), h(AnimalsSection), h(AdoptionSection), h(HelpSection), h(ContactSection)), h(Footer));
}

createRoot(document.getElementById("root")).render(h(App));
