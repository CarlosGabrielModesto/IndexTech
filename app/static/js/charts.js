/**
 * Hygeia Digital — Gráficos do dashboard
 *
 * Este arquivo é carregado APENAS na página do dashboard.
 * Depende do objeto CHART_DATA injetado pelo Jinja2 no dashboard.html.
 *
 * Gráficos:
 *  1. chartStatus  — Rosca: distribuição de status dos convites
 *  2. chartUbs     — Barras horizontais: pacientes por UBS
 *  3. chartFaixas  — Barras verticais: distribuição por faixa etária
 */

"use strict";

/* ------------------------------------------------------------------
   Paleta de cores consistente com o CSS da aplicação
   ------------------------------------------------------------------ */

const CORES = {
  brand:  "#005D56",
  brand2: "#007A71",
  brand3: "#009E93",
  amber:  "#F59E0B",
  blue:   "#3B82F6",
  red:    "#EF4444",
  cinza:  "#CBD5E1",
  verde:  "#22C55E",
};

// Cores para o gráfico de status (rosca)
const CORES_STATUS = [
  CORES.verde,   // Enviados
  CORES.amber,   // Pendentes
  CORES.red,     // Erros
  CORES.cinza,   // Ignorados
];

// Cores para o gráfico de faixas etárias (barras)
const CORES_FAIXAS = [
  CORES.brand,
  CORES.brand2,
  CORES.brand3,
  "#00C4B4",
  CORES.cinza,
];

/* ------------------------------------------------------------------
   Configurações globais do Chart.js
   ------------------------------------------------------------------ */

Chart.defaults.font.family = "'DM Sans', system-ui, sans-serif";
Chart.defaults.font.size   = 13;
Chart.defaults.color       = "#64748B";
Chart.defaults.plugins.legend.display = false; // Legenda customizada no HTML

/* ------------------------------------------------------------------
   Utilitário: cria gradiente vertical para as barras
   ------------------------------------------------------------------ */

/**
 * Cria um gradiente linear de cima para baixo em um canvas.
 *
 * @param {CanvasRenderingContext2D} ctx
 * @param {string} corTopo    — cor mais intensa no topo
 * @param {string} corBase    — cor mais suave na base
 */
function criarGradiente(ctx, corTopo, corBase) {
  const gradiente = ctx.createLinearGradient(0, 0, 0, 300);
  gradiente.addColorStop(0,   corTopo);
  gradiente.addColorStop(1,   corBase);
  return gradiente;
}

/* ------------------------------------------------------------------
   1. GRÁFICO DE ROSCA — Status dos convites
   ------------------------------------------------------------------ */

function iniciarChartStatus() {
  const canvas = document.getElementById("chartStatus");
  if (!canvas || !window.CHART_DATA) return;

  const ctx    = canvas.getContext("2d");
  const dados  = CHART_DATA.status;

  // Filtra labels/dados com valor zero para não poluir a rosca
  const labels  = [];
  const valores = [];
  const cores   = [];

  dados.labels.forEach((label, i) => {
    if (dados.data[i] > 0) {
      labels.push(label);
      valores.push(dados.data[i]);
      cores.push(CORES_STATUS[i] ?? CORES.cinza);
    }
  });

  const total = valores.reduce((a, b) => a + b, 0);

  new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [{
        data:            valores,
        backgroundColor: cores,
        borderColor:     "#FFFFFF",
        borderWidth:     3,
        hoverOffset:     6,
      }],
    },
    options: {
      responsive:         true,
      maintainAspectRatio: true,
      cutout:             "68%",
      plugins: {
        tooltip: {
          callbacks: {
            // Exibe percentual no tooltip
            label(ctx) {
              const pct = total > 0
                ? ((ctx.parsed / total) * 100).toFixed(1)
                : 0;
              return ` ${ctx.label}: ${ctx.parsed} (${pct}%)`;
            },
          },
        },
      },
      // Texto central customizado (plugin inline)
      layout: { padding: 8 },
    },
    plugins: [{
      // Plugin inline: desenha o total no centro da rosca
      id: "centroRosca",
      beforeDraw(chart) {
        const { width, height, ctx: c } = chart;
        c.save();
        c.textAlign    = "center";
        c.textBaseline = "middle";
        const cx = width  / 2;
        const cy = height / 2;

        // Número total
        c.font = `700 26px 'DM Serif Display', Georgia, serif`;
        c.fillStyle = "#0F172A";
        c.fillText(total, cx, cy - 8);

        // Label
        c.font = `500 11px 'DM Sans', sans-serif`;
        c.fillStyle = "#94A3B8";
        c.fillText("convites", cx, cy + 14);

        c.restore();
      },
    }],
  });

  // Monta a legenda customizada no HTML
  const legendaEl = document.getElementById("legendStatus");
  if (!legendaEl) return;

  labels.forEach((label, i) => {
    const item = document.createElement("div");
    item.className = "legend-item";

    const dot = document.createElement("span");
    dot.className   = "legend-dot";
    dot.style.background = cores[i];

    const texto = document.createElement("span");
    const pct   = total > 0 ? ((valores[i] / total) * 100).toFixed(0) : 0;
    texto.textContent = `${label} (${pct}%)`;

    item.appendChild(dot);
    item.appendChild(texto);
    legendaEl.appendChild(item);
  });
}

/* ------------------------------------------------------------------
   2. GRÁFICO DE BARRAS HORIZONTAIS — Pacientes por UBS
   ------------------------------------------------------------------ */

function iniciarChartUbs() {
  const canvas = document.getElementById("chartUbs");
  if (!canvas || !window.CHART_DATA) return;

  const ctx   = canvas.getContext("2d");
  const dados = CHART_DATA.ubs;

  // Limita o nome das UBS para não quebrar o layout
  const labelsFormatados = dados.labels.map((l) =>
    l.length > 30 ? l.slice(0, 28) + "…" : l
  );

  // Gradiente horizontal (esquerda → direita)
  const gradH = ctx.createLinearGradient(0, 0, 500, 0);
  gradH.addColorStop(0,   CORES.brand);
  gradH.addColorStop(1,   CORES.brand3);

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: labelsFormatados,
      datasets: [{
        label:           "Pacientes",
        data:            dados.data,
        backgroundColor: gradH,
        borderRadius:    6,
        borderSkipped:   false,
        barThickness:    18,
      }],
    },
    options: {
      indexAxis:          "y",        // Barras horizontais
      responsive:         true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.parsed.x} paciente(s)`,
          },
        },
      },
      scales: {
        x: {
          beginAtZero: true,
          grid: {
            color:     "rgba(203,213,225,0.4)",
            drawBorder: false,
          },
          ticks: {
            precision: 0,
            color:     "#94A3B8",
          },
        },
        y: {
          grid:   { display: false },
          ticks: {
            color:    "#475569",
            font:     { weight: "500", size: 12 },
          },
        },
      },
      layout: { padding: { right: 8 } },
    },
  });
}

/* ------------------------------------------------------------------
   3. GRÁFICO DE BARRAS VERTICAIS — Faixas etárias
   ------------------------------------------------------------------ */

function iniciarChartFaixas() {
  const canvas = document.getElementById("chartFaixas");
  if (!canvas || !window.CHART_DATA) return;

  const ctx   = canvas.getContext("2d");
  const dados = CHART_DATA.faixas;

  // Gradiente vertical por barra (via função de callback)
  const gradientes = dados.data.map((_, i) => {
    const g = ctx.createLinearGradient(0, 0, 0, 250);
    g.addColorStop(0, CORES_FAIXAS[i] ?? CORES.brand);
    g.addColorStop(1, CORES_FAIXAS[i] + "88" ?? CORES.brand + "88");
    return g;
  });

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: dados.labels,
      datasets: [{
        label:           "Pacientes",
        data:            dados.data,
        backgroundColor: gradientes,
        borderRadius:    8,
        borderSkipped:   false,
        barThickness:    36,
      }],
    },
    options: {
      responsive:         true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title: (items) => `Faixa etária: ${items[0].label} anos`,
            label: (ctx)   => ` ${ctx.parsed.y} paciente(s)`,
          },
        },
      },
      scales: {
        x: {
          grid:  { display: false },
          ticks: {
            color: "#475569",
            font:  { weight: "600", size: 12 },
          },
        },
        y: {
          beginAtZero: true,
          grid: {
            color:     "rgba(203,213,225,0.4)",
            drawBorder: false,
          },
          ticks: {
            precision: 0,
            color:     "#94A3B8",
          },
        },
      },
      layout: { padding: { top: 8 } },
    },
  });
}

/* ------------------------------------------------------------------
   INICIALIZAÇÃO — aguarda o DOM estar pronto
   ------------------------------------------------------------------ */

document.addEventListener("DOMContentLoaded", () => {
  iniciarChartStatus();
  iniciarChartUbs();
  iniciarChartFaixas();
});