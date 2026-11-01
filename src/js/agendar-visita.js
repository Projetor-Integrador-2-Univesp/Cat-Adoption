import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import { Alert, Button, Col, Container, Form, Row } from "react-bootstrap";

const h = React.createElement;
const API_BASE = ["localhost", "127.0.0.1"].includes(window.location.hostname)
  ? "http://127.0.0.1:8000"
  : "https://larbastet.onrender.com";

function lerIntencoes() {
  try {
    const registros = JSON.parse(sessionStorage.getItem("larbastet_intencoes") || "[]");
    return Array.isArray(registros) ? registros.filter((item) => item.id && item.token) : [];
  } catch {
    return [];
  }
}

function AgendarVisita() {
  const [intencoes] = useState(lerIntencoes);
  const [interesseId, setInteresseId] = useState(intencoes.length === 1 ? String(intencoes[0].id) : "");
  const [dataHora, setDataHora] = useState("");
  const [observacoes, setObservacoes] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [feedback, setFeedback] = useState(null);

  async function solicitarVisita(event) {
    event.preventDefault();
    if (enviando) return;
    const selecionada = intencoes.find((item) => String(item.id) === interesseId);
    if (!selecionada) {
      setFeedback({ type: "danger", text: "Selecione uma intenção de adoção." });
      return;
    }
    const horario = new Date(dataHora);
    if (!dataHora || Number.isNaN(horario.getTime()) || horario <= new Date()) {
      setFeedback({ type: "danger", text: "Escolha uma data e horário futuros." });
      return;
    }
    setEnviando(true);
    setFeedback(null);
    try {
      const response = await fetch(`${API_BASE}/api/visitas/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          interesse_id: selecionada.id,
          token_visita: selecionada.token,
          data_hora: horario.toISOString(),
          observacoes: observacoes.trim()
        })
      });
      const resultado = await response.json();
      if (!response.ok) throw new Error(resultado.erro || "Não foi possível solicitar a visita.");
      setFeedback({ type: "success", text: "Solicitação registrada. A responsável confirmará a data e o horário posteriormente." });
      setDataHora("");
      setObservacoes("");
    } catch (error) {
      setFeedback({ type: "danger", text: error.message || "Não foi possível conectar ao servidor." });
    } finally {
      setEnviando(false);
    }
  }

  return h("main", null, h("section", { className: "section section-light section-screen" },
    h(Container, { className: "py-5" },
      h("a", { href: "./index.html", className: "text-decoration-none" }, "← Voltar ao Lar Bastet"),
      h(Row, { className: "g-4 mt-3" },
        h(Col, { lg: 5 }, h("div", { className: "adoption-box" },
          h("p", { className: "eyebrow" }, "Lar Bastet"),
          h("h1", null, "Solicitar visita"),
          h("p", null, "Escolha um gato para conhecer e informe a data desejada. A solicitação será analisada pela responsável pelo abrigo."),
          h("p", null, "Por segurança, o comprovante fica disponível nesta aba enquanto a sessão estiver aberta, por até 30 dias.")
        )),
        h(Col, { lg: 7 }, h("div", { className: "form-card" },
          h("h2", null, "Dados da visita"),
          intencoes.length === 0 ? h(Alert, { variant: "warning" },
            "Nenhuma intenção disponível nesta sessão. Volte ao site e preencha primeiro o formulário de adoção.") :
            h(Form, { onSubmit: solicitarVisita },
              h(Form.Group, { className: "mb-3", controlId: "interesse" },
                h(Form.Label, null, "Gato"),
                h(Form.Select, { required: true, value: interesseId, onChange: (event) => setInteresseId(event.target.value) },
                  h("option", { value: "" }, "Selecione o gato"),
                  ...intencoes.map((item) => h("option", { key: item.id, value: item.id }, item.pet || `Intenção #${item.id}`)))),
              h(Form.Group, { className: "mb-3", controlId: "data_hora" },
                h(Form.Label, null, "Data e horário desejados"),
                h(Form.Control, { type: "datetime-local", required: true, value: dataHora, onChange: (event) => setDataHora(event.target.value) })),
              h(Form.Group, { className: "mb-3", controlId: "observacoes" },
                h(Form.Label, null, "Observações (opcional)"),
                h(Form.Control, { as: "textarea", rows: 4, maxLength: 1000, value: observacoes, onChange: (event) => setObservacoes(event.target.value) })),
              h(Button, { type: "submit", className: "button button-primary", disabled: enviando },
                enviando ? "Enviando..." : "Solicitar visita")
            ),
          feedback && h(Alert, { className: "mt-3", variant: feedback.type, role: feedback.type === "danger" ? "alert" : "status" }, feedback.text)
        ))
      )
    )
  ));
}

createRoot(document.getElementById("root")).render(h(AgendarVisita));
