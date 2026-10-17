
import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import { Button, Col, Container, Form, Row, Alert } from "react-bootstrap";

const h = React.createElement;
const API_VISITAS = "http://127.0.0.1:8000/api/visitas/";
const API_INTENCOES = "http://127.0.0.1:8000/api/intencoes/por-telefone/";

const nomesDias = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];

function formatarDataLocal(date) {
    const ano = date.getFullYear();
    const mes = String(date.getMonth() + 1).padStart(2, "0");
    const dia = String(date.getDate()).padStart(2, "0");
    return `${ano}-${mes}-${dia}`;
}

function AgendarVisita() {
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);

    const [telefone, setTelefone] = useState("");
    const [intencoes, setIntencoes] = useState([]);
    const [interesseId, setInteresseId] = useState("");
    const [data, setData] = useState("");
    const [horario, setHorario] = useState("");
    const [observacoes, setObservacoes] = useState("");
    const [mesCalendario, setMesCalendario] = useState(
        new Date(hoje.getFullYear(), hoje.getMonth(), 1)
    );
    const [buscando, setBuscando] = useState(false);
    const [enviando, setEnviando] = useState(false);
    const [feedback, setFeedback] = useState(null);

    const primeiroDia = new Date(
        mesCalendario.getFullYear(),
        mesCalendario.getMonth(),
        1
    ).getDay();

    const totalDias = new Date(
        mesCalendario.getFullYear(),
        mesCalendario.getMonth() + 1,
        0
    ).getDate();

    const nomeMes = mesCalendario.toLocaleDateString("pt-BR", {
        month: "long",
        year: "numeric"
    });

    const diasCalendario = [
        ...Array(primeiroDia).fill(null),
        ...Array.from({ length: totalDias }, (_, i) => i + 1)
    ];

    function mudarMes(direcao) {
        setMesCalendario((atual) =>
            new Date(
                atual.getFullYear(),
                atual.getMonth() + direcao,
                1
            )
        );
    }

    function selecionarDia(dia) {
        const selecionada = new Date(
            mesCalendario.getFullYear(),
            mesCalendario.getMonth(),
            dia
        );
        selecionada.setHours(0, 0, 0, 0);

        if (selecionada < hoje) return;

        setData(formatarDataLocal(selecionada));
    }

    async function buscarIntencoes(event) {
        event.preventDefault();
        if (buscando) return;

        setBuscando(true);
        setFeedback(null);
        setIntencoes([]);
        setInteresseId("");

        try {
            const url =
                `${API_INTENCOES}?telefone=${encodeURIComponent(telefone)}`;
            const response = await fetch(url);
            const resultado = await response.json();

            if (!response.ok) {
                throw new Error(
                    resultado.erro || "Não foi possível buscar suas intenções."
                );
            }

            const encontradas = resultado.intencoes || [];
            setIntencoes(encontradas);

            if (encontradas.length === 0) {
                setFeedback({
                    type: "warning",
                    message:
                        "Nenhuma intenção foi encontrada. Confira o telefone usado no cadastro de adoção."
                });
            } else {
                setFeedback({
                    type: "success",
                    message:
                        "Encontramos suas intenções! Selecione o gato para agendar a visita."
                });

                if (encontradas.length === 1) {
                    setInteresseId(String(encontradas[0].interesse_id));
                }
            }
        } catch (error) {
            setFeedback({
                type: "danger",
                message:
                    error.message || "Não foi possível conectar ao servidor."
            });
        } finally {
            setBuscando(false);
        }
    }

    async function solicitarVisita(event) {
        event.preventDefault();
        if (enviando) return;

        if (!interesseId) {
            setFeedback({
                type: "warning",
                message: "Selecione um gato antes de continuar."
            });
            return;
        }

        setEnviando(true);
        setFeedback(null);

        try {
            const response = await fetch(API_VISITAS, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    interesse_id: Number(interesseId),
                    data_hora: `${data}T${horario}`,
                    observacoes: observacoes.trim()
                })
            });

            const resultado = await response.json();

            if (!response.ok) {
                throw new Error(
                    resultado.erro || "Não foi possível solicitar a visita."
                );
            }

            setFeedback({
                type: "success",
                message: "Sua solicitação foi registrada com sucesso!"
            });

            // Confirmação visual após o registro bem-sucedido no servidor.
            window.alert(
                "Solicitação de visita enviada com sucesso!\n\n" +
                "Atenção: esta solicitação ainda não confirma o agendamento. " +
                "A responsável pelo Lar Bastet entrará em contato para " +
                "combinar e confirmar a data e o horário da visita.\n\n" +
                "Obrigado pelo interesse em nossos gatinhos!"
            );

            setTelefone("");
            setIntencoes([]);
            setInteresseId("");
            setData("");
            setHorario("");
            setObservacoes("");
            setMesCalendario(
                new Date(hoje.getFullYear(), hoje.getMonth(), 1)
            );
        } catch (error) {
            setFeedback({
                type: "danger",
                message:
                    error.message ||
                    "Não foi possível conectar ao servidor. Tente novamente."
            });
        } finally {
            setEnviando(false);
        }
    }

    const calendario = h("div", {
            className: "mb-3",
            style: {
                padding: "10px",
                maxWidth: "360px",
                borderRadius: "12px",
                border: "1px solid rgba(128, 128, 128, 0.35)"
            }
        },
        h("div", {
                className: "d-flex align-items-center justify-content-between mb-3"
            },
            h(Button, {
                type: "button",
                variant: "outline-secondary",
                size: "sm",
                disabled:
                    mesCalendario.getFullYear() === hoje.getFullYear() &&
                    mesCalendario.getMonth() === hoje.getMonth(),
                onClick: () => mudarMes(-1),
                "aria-label": "Mês anterior"
            }, "‹"),

            h("strong", {
                style: {
                    textTransform: "capitalize",
                    textAlign: "center"
                }
            }, nomeMes),

            h(Button, {
                type: "button",
                variant: "outline-secondary",
                size: "sm",
                onClick: () => mudarMes(1),
                "aria-label": "Próximo mês"
            }, "›")
        ),

        h("div", {
                style: {
                    display: "grid",
                    gridTemplateColumns: "repeat(7, minmax(0, 1fr))",
                    gap: "2px",
                    textAlign: "center"
                }
            },
            ...nomesDias.map((nome) =>
                h("div", {
                    key: nome,
                    style: {
                        fontSize: "0.78rem",
                        fontWeight: "600",
                        padding: "3px 0"
                    }
                }, nome)
            ),

            ...diasCalendario.map((dia, indice) => {
                if (dia === null) {
                    return h("div", { key: `vazio-${indice}` });
                }

                const diaDate = new Date(
                    mesCalendario.getFullYear(),
                    mesCalendario.getMonth(),
                    dia
                );
                diaDate.setHours(0, 0, 0, 0);

                const diaISO = formatarDataLocal(diaDate);
                const passado = diaDate < hoje;
                const selecionado = diaISO === data;
                const hojeSelecionado = diaISO === formatarDataLocal(hoje);

                return h("button", {
                    key: diaISO,
                    type: "button",
                    disabled: passado,
                    onClick: () => selecionarDia(dia),
                    "aria-label": `${dia} de ${nomeMes}`,
                    "aria-pressed": selecionado,
                    style: {
                        minWidth: 0,
                        width: "100%",
                        aspectRatio: "1 / 1",
                        borderRadius: "9px",
                        border: selecionado
                            ? "2px solid #8b5e3c"
                            : hojeSelecionado
                                ? "1px solid #8b5e3c"
                                : "1px solid transparent",
                        background: selecionado ? "#8b5e3c" : "transparent",
                        color: selecionado
                            ? "#ffffff"
                            : passado
                                ? "#999999"
                                : "inherit",
                        opacity: passado ? 0.4 : 1,
                        cursor: passado ? "not-allowed" : "pointer",
                        fontWeight: selecionado || hojeSelecionado ? "700" : "400",
                        padding: "0",
                        fontSize: "0.8rem"
                    }
                }, String(dia));
            })
        ),

        h("p", {
                className: "mb-0 mt-3",
                style: { fontSize: "0.9rem" }
            },
            data
                ? `Data selecionada: ${new Date(`${data}T12:00:00`).toLocaleDateString("pt-BR")}`
                : "Clique em um dia para selecionar a data da visita."
        )
    );

    return h("main", null,
        h("section", {
                className: "section section-light section-screen",
                style: { minHeight: "100vh" }
            },
            h(Container, { className: "py-4" },
                h("a", {
                    href: "./index.html",
                    className: "text-decoration-none"
                }, "← Voltar ao site Lar Bastet"),

                h(Row, { className: "g-4 align-items-start mt-3" },
                    h(Col, { lg: 5 },
                        h("div", { className: "adoption-box" },
                            h("p", { className: "eyebrow" }, "Lar Bastet"),
                            h("h1", null, "Vamos marcar uma visita?"),
                            h("p", null,
                                "Conheça os gatos de perto e descubra se um deles combina com sua família."
                            ),
                            h("article", { className: "adoption-step mt-4" },
                                h("span", null, "1"),
                                h("h3", null, "Localize sua intenção"),
                                h("p", null,
                                    "Informe o telefone usado no formulário de interesse de adoção."
                                )
                            ),
                            h("article", { className: "adoption-step mt-3" },
                                h("span", null, "2"),
                                h("h3", null, "Escolha a data"),
                                h("p", null,
                                    "Selecione o dia e o horário desejados. A visita será confirmada posteriormente pela equipe."
                                )
                            )
                        )
                    ),

                    h(Col, { lg: 7 },
                        h("div", { className: "form-card" },
                            h("h2", null, "Solicitar visita"),
                            h("p", null,
                                "Primeiro, localize sua intenção de adoção pelo telefone."
                            ),

                            h(Form, { onSubmit: buscarIntencoes },
                                h(Form.Group, {
                                        className: "mb-3",
                                        controlId: "telefone"
                                    },
                                    h(Form.Label, null, "Telefone cadastrado"),
                                    h(Form.Control, {
                                        type: "tel",
                                        value: telefone,
                                        onChange: (event) => setTelefone(event.target.value),
                                        placeholder: "Ex.: (19) 91234-5678",
                                        required: true,
                                        maxLength: 20
                                    }),
                                    h(Form.Text, { className: "text-light" },
                                        "Use o mesmo telefone informado no cadastro de adoção."
                                    )
                                ),
                                h(Button, {
                                    type: "submit",
                                    className: "button button-primary mb-4",
                                    disabled: buscando
                                }, buscando ? "Buscando..." : "Buscar minhas intenções")
                            ),

                            intencoes.length > 0 &&
                            h(Form, { onSubmit: solicitarVisita },
                                h(Form.Group, {
                                        className: "mb-4",
                                        controlId: "interesse"
                                    },
                                    h(Form.Label, null, "Gato para a visita"),
                                    h(Form.Select, {
                                            value: interesseId,
                                            onChange: (event) => setInteresseId(event.target.value),
                                            required: true
                                        },
                                        h("option", { value: "" }, "Selecione um gato"),
                                        ...intencoes.map((intencao) =>
                                            h("option", {
                                                key: intencao.interesse_id,
                                                value: String(intencao.interesse_id)
                                            }, intencao.pet)
                                        )
                                    )
                                ),

                                h(Form.Group, {
                                        className: "mb-3",
                                        controlId: "data"
                                    },
                                    h(Form.Label, null, "Escolha a data desejada"),
                                    calendario,
                                    h(Form.Control, {
                                        type: "hidden",
                                        value: data,
                                        required: true,
                                        readOnly: true
                                    })
                                ),

                                h(Form.Group, {
                                        className: "mb-3",
                                        controlId: "horario"
                                    },
                                    h(Form.Label, null, "Horário desejado"),
                                    h(Form.Control, {
                                        type: "time",
                                        value: horario,
                                        onChange: (event) => setHorario(event.target.value),
                                        required: true
                                    })
                                ),

                                h(Form.Group, {
                                        className: "mb-3",
                                        controlId: "observacoes"
                                    },
                                    h(Form.Label, null, "Observações (opcional)"),
                                    h(Form.Control, {
                                        as: "textarea",
                                        rows: 4,
                                        maxLength: 1000,
                                        value: observacoes,
                                        onChange: (event) => setObservacoes(event.target.value),
                                        placeholder: "Conte algo sobre sua disponibilidade, se necessário."
                                    })
                                ),

                                h(Button, {
                                    type: "submit",
                                    className: "button button-primary",
                                    disabled: enviando || !data
                                }, enviando ? "Enviando..." : "Solicitar visita")
                            ),

                            feedback && h(Alert, {
                                variant: feedback.type,
                                className: "mt-3 mb-0",
                                role: feedback.type === "danger" ? "alert" : "status"
                            }, feedback.message)
                        )
                    )
                )
            )
        )
    );
}

createRoot(document.getElementById("root")).render(h(AgendarVisita));