const API_URL = "https://pet-adoption-q581.onrender.com/api/gatos/";
const FALLBACK_IMAGE = "./src/img/logo.jpeg";

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

function normalizeText(value) {
  return String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

function includesAny(text, words) {
  return words.some((word) => text.includes(word));
}

function getEnergyMatch(cat) {
  const description = normalizeText(cat.descricao);
  const age = Number(cat.idade) || 0;

  if (age >= 60 || includesAny(description, ["calmo", "sereno", "tranquilo", "companheiro", "olhar", "adulto", "maduro"])) {
    return {
      label: "Guardiao",
      description: "Protetor sereno, de presenca profunda e energia de paz."
    };
  }

  if (includesAny(description, ["curioso", "independente", "observador", "misterio", "esperto", "explorador"])) {
    return {
      label: "Mago",
      description: "Observador, intuitivo e cheio de misterio no olhar."
    };
  }

  if (includesAny(description, ["carinhoso", "ronron", "colo", "docil", "amoroso", "apegado", "manso"])) {
    return {
      label: "Curandeiro",
      description: "Acolhedor, afetivo e sensivel a quem precisa de companhia."
    };
  }

  if ((age > 0 && age <= 12) || includesAny(description, ["brincalhao", "ativo", "energia", "agitado", "filhote", "aventureiro"])) {
    return {
      label: "Elemental",
      description: "Vivo, brincalhao e pronto para movimentar a energia da casa."
    };
  }

  const seed = normalizeText(`${cat.cor || ""}${cat.sexo || ""}${cat.idade || ""}${cat.descricao || ""}`).length % 4;
  const fallbackMatches = [
    {
      label: "Guardiao",
      description: "Presenca protetora para lares que buscam calma e lealdade."
    },
    {
      label: "Mago",
      description: "Alma observadora para quem respeita independencia e encanto."
    },
    {
      label: "Curandeiro",
      description: "Companhia terna para criar vinculo com paciencia e cuidado."
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

function createCatCard(cat) {
  const article = document.createElement("article");
  article.className = "cat-card";

  const image = document.createElement("img");
  image.src = getCatImage(cat.foto);
  image.alt = "Gato disponivel para adocao";
  image.loading = "lazy";
  image.onerror = () => {
    image.onerror = null;
    image.src = FALLBACK_IMAGE;
  };

  const content = document.createElement("div");
  content.className = "cat-card-content";

  const header = document.createElement("div");
  header.className = "cat-card-header";

  const title = document.createElement("h3");
  title.textContent = `${getCatGender(cat.sexo)} - ${cat.cor || "Pelagem especial"}`;

  const age = document.createElement("span");
  age.textContent = getCatAge(cat.idade);

  const energy = getEnergyMatch(cat);

  const vibe = document.createElement("span");
  vibe.className = "cat-vibe";
  vibe.textContent = `Vibe: ${energy.label}`;

  const description = document.createElement("p");
  description.textContent = cat.descricao || energy.description;

  const link = document.createElement("a");
  link.className = "button button-primary button-full";
  link.href = "./como-adotar.html";
  link.textContent = "Sentir essa conexao";

  header.append(title, age);
  content.append(header, vibe, description, link);
  article.append(image, content);

  return article;
}

function showCatGridState(grid, message) {
  const state = document.createElement("article");
  state.className = "cat-card";
  state.innerHTML = `
    <div class="cat-card-content">
      <div class="cat-card-header">
        <h3>Lar Bastet</h3>
        <span>Info</span>
      </div>
      <p>${message}</p>
      <a class="button button-secondary button-full" href="./contato.html">Falar com o projeto</a>
    </div>
  `;
  grid.replaceChildren(state);
}

async function fetchCats() {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 8000);

  try {
    return await fetch(API_URL, { signal: controller.signal });
  } finally {
    window.clearTimeout(timeout);
  }
}

async function renderCats() {
  const grid = document.getElementById("cat-grid");

  if (!grid) {
    return;
  }

  showCatGridState(grid, "Consultando a vitrine de almas felinas. Em instantes, as conexoes disponiveis aparecem por aqui.");

  try {
    const response = await fetchCats();

    if (!response.ok) {
      throw new Error(`Erro ao carregar gatos: ${response.status}`);
    }

    const cats = await response.json();

    if (!cats.length) {
      showCatGridState(grid, "No momento nao ha gatos cadastrados para exibir. Entre em contato para saber sobre novos resgates e novas conexoes.");
      return;
    }

    const fragment = document.createDocumentFragment();
    cats.forEach((cat) => fragment.appendChild(createCatCard(cat)));
    grid.replaceChildren(fragment);
  } catch {
    showCatGridState(grid, "Nao foi possivel carregar os gatos agora. Tente novamente em instantes ou fale com o Lar Bastet.");
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    void renderCats();
  });
} else {
  void renderCats();
}
