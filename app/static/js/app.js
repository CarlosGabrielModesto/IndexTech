/**
 * Hygeia Digital — JavaScript principal
 *
 * Responsabilidades:
 *  - Sistema de toast (notificações visuais)
 *  - Sidebar mobile (hambúrguer)
 *  - Upload de arquivo (drag-and-drop + click)
 *  - Importação de pacientes (fetch → /api/import)
 *  - Disparo de convites (fetch → /api/invite)
 *  - Agendamento manual (fetch → /api/schedule)
 *  - Opt-out de pacientes (fetch → /api/patients/:id/optout)
 *  - Atualização de status de agendamentos
 */

"use strict";

/* ==================================================================
   UTILITÁRIOS GERAIS
   ================================================================== */

/**
 * Busca um elemento do DOM com segurança.
 * Retorna null silenciosamente se não encontrar — evita erros em
 * páginas que não contêm determinado elemento.
 *
 * @param {string} seletor — seletor CSS
 * @param {Element} [raiz=document] — elemento raiz da busca
 */
function $(seletor, raiz = document) {
  return raiz.querySelector(seletor);
}

/**
 * Busca múltiplos elementos do DOM.
 *
 * @param {string} seletor
 * @param {Element} [raiz=document]
 */
function $$(seletor, raiz = document) {
  return Array.from(raiz.querySelectorAll(seletor));
}


/* ==================================================================
   SISTEMA DE TOAST
   ================================================================== */

const toastEl   = document.getElementById("toast");
let   toastTimer = null;

/**
 * Exibe uma notificação temporária no canto inferior direito.
 *
 * @param {string} mensagem  — texto a exibir
 * @param {"success"|"error"|"info"} tipo — estilo visual
 * @param {number} duracao   — tempo em ms antes de fechar (padrão: 4000)
 */
function showToast(mensagem, tipo = "success", duracao = 4000) {
  if (!toastEl) return;

  // Remove classes anteriores
  toastEl.className = "toast";

  // Ícones por tipo
  const icones = {
    success: "✅",
    error:   "❌",
    info:    "ℹ️",
  };

  toastEl.textContent = `${icones[tipo] ?? ""} ${mensagem}`;
  toastEl.classList.add(`toast--${tipo}`, "toast--visible");

  // Cancela o timer anterior se houver
  if (toastTimer) clearTimeout(toastTimer);

  toastTimer = setTimeout(() => {
    toastEl.classList.remove("toast--visible");
  }, duracao);
}


/* ==================================================================
   SIDEBAR MOBILE
   ================================================================== */

const sidebar        = document.getElementById("sidebar");
const sidebarOverlay = document.getElementById("sidebarOverlay");
const menuToggle     = document.getElementById("menuToggle");

/**
 * Abre ou fecha a sidebar no modo mobile.
 * Também bloqueia o scroll do body enquanto a sidebar estiver aberta.
 */
function toggleSidebar() {
  const aberta = sidebar?.classList.toggle("sidebar--open");
  sidebarOverlay?.classList.toggle("sidebar-overlay--open", aberta);
  document.body.style.overflow = aberta ? "hidden" : "";
}

menuToggle?.addEventListener("click", toggleSidebar);
sidebarOverlay?.addEventListener("click", toggleSidebar);

// Fecha a sidebar ao pressionar Escape
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && sidebar?.classList.contains("sidebar--open")) {
    toggleSidebar();
  }
});


/* ==================================================================
   HELPER: BOTÃO EM ESTADO DE CARREGAMENTO
   ================================================================== */

/**
 * Coloca um botão no estado de carregamento (spinner) ou restaura.
 *
 * @param {HTMLButtonElement} btn
 * @param {boolean} carregando
 * @param {string} [textoOriginal] — texto a restaurar quando carregando=false
 */
function setBtnLoading(btn, carregando, textoOriginal = "") {
  if (!btn) return;
  btn.disabled = carregando;

  if (carregando) {
    btn.dataset.originalHtml = btn.innerHTML;
    btn.classList.add("btn--loading");
    btn.innerHTML = "";          // O spinner vem via CSS ::after
  } else {
    btn.classList.remove("btn--loading");
    btn.innerHTML = btn.dataset.originalHtml || textoOriginal;
    // Reinicializa os ícones Lucide dentro do botão restaurado
    if (window.lucide) lucide.createIcons({ nodes: [btn] });
  }
}


/* ==================================================================
   HELPER: FORMATA datetime-local PARA "YYYY-MM-DD HH:MM"
   ================================================================== */

/**
 * O input datetime-local retorna "2025-08-16T10:30".
 * A API espera "2025-08-16 10:30".
 *
 * @param {string} valor — valor bruto do input datetime-local
 */
function formatarDatetime(valor) {
  return (valor || "").replace("T", " ").slice(0, 16);
}


/* ==================================================================
   IMPORTAÇÃO DE ARQUIVO
   ================================================================== */

const fileDrop  = document.getElementById("fileDrop");
const importFile = document.getElementById("importFile");
const fileLabel  = document.getElementById("fileLabel");
const btnImport  = document.getElementById("btnImport");

// Atualiza o label e habilita o botão quando um arquivo é selecionado
function aoSelecionarArquivo(arquivo) {
  if (!arquivo) return;
  if (fileLabel) fileLabel.textContent = arquivo.name;
  if (fileDrop)  fileDrop.classList.add("file-drop--active");
  if (btnImport) btnImport.disabled = false;
}

importFile?.addEventListener("change", () => {
  aoSelecionarArquivo(importFile.files?.[0]);
});

// Suporte a drag-and-drop na área de upload
fileDrop?.addEventListener("dragover", (e) => {
  e.preventDefault();
  fileDrop.classList.add("file-drop--active");
});

fileDrop?.addEventListener("dragleave", () => {
  if (!importFile?.files?.length) {
    fileDrop.classList.remove("file-drop--active");
  }
});

fileDrop?.addEventListener("drop", (e) => {
  e.preventDefault();
  const arquivo = e.dataTransfer?.files?.[0];
  if (!arquivo) return;

  // Injeta o arquivo no input (para reutilizar o mesmo fluxo)
  const dt = new DataTransfer();
  dt.items.add(arquivo);
  if (importFile) importFile.files = dt.files;

  aoSelecionarArquivo(arquivo);
});

// Importa ao clicar no botão
btnImport?.addEventListener("click", async () => {
  const arquivo = importFile?.files?.[0];
  if (!arquivo) {
    showToast("Selecione um arquivo antes de importar.", "error");
    return;
  }

  setBtnLoading(btnImport, true);

  const formData = new FormData();
  formData.append("file", arquivo);

  try {
    const res  = await fetch("/api/import", { method: "POST", body: formData });
    const data = await res.json();

    if (res.ok && data?.status === "success") {
      showToast(
        `Importação concluída! ${data.importados} paciente(s) adicionada(s).`,
        "success"
      );
      // Limpa o campo de arquivo
      if (importFile) importFile.value = "";
      if (fileLabel)  fileLabel.textContent = "Arraste ou clique para selecionar";
      if (fileDrop)   fileDrop.classList.remove("file-drop--active");
      if (btnImport)  btnImport.disabled = true;

      // Recarrega a página após 1,5s para atualizar os cards de métricas
      setTimeout(() => location.reload(), 1500);
    } else {
      showToast(data?.detail || data?.message || "Falha na importação.", "error");
    }
  } catch {
    showToast("Erro de rede ao importar. Verifique a conexão.", "error");
  } finally {
    setBtnLoading(btnImport, false);
  }
});


/* ==================================================================
   DISPARO DE CONVITES
   ================================================================== */

const btnInvite      = document.getElementById("btnInvite");
const inviteTemplate = document.getElementById("inviteTemplate");
const inviteLimit    = document.getElementById("inviteLimit");

btnInvite?.addEventListener("click", async () => {
  const template = inviteTemplate?.value?.trim();
  const limite   = parseInt(inviteLimit?.value || "50", 10);

  if (!template) {
    showToast("O campo de mensagem não pode estar vazio.", "error");
    return;
  }

  if (isNaN(limite) || limite < 1) {
    showToast("Informe um limite de envios válido.", "error");
    return;
  }

  setBtnLoading(btnInvite, true);

  const formData = new FormData();
  formData.append("template", template);
  formData.append("limite",   String(limite));

  try {
    const res  = await fetch("/api/invite", { method: "POST", body: formData });
    const data = await res.json();

    if (res.ok && data?.status === "success") {
      const { enviados, erros, ignorados } = data;
      showToast(
        `Convites: ${enviados} enviado(s), ${erros} erro(s), ${ignorados} ignorado(s).`,
        enviados > 0 ? "success" : "info"
      );
      // Atualiza os cards após 2s
      setTimeout(() => location.reload(), 2000);
    } else {
      showToast(data?.detail || "Falha ao enviar convites.", "error");
    }
  } catch {
    showToast("Erro de rede ao enviar convites.", "error");
  } finally {
    setBtnLoading(btnInvite, false);
  }
});


/* ==================================================================
   AGENDAMENTO MANUAL
   ================================================================== */

const btnSchedule = document.getElementById("btnSchedule");
const schedPhone  = document.getElementById("schedPhone");
const schedWhen   = document.getElementById("schedWhen");
const schedPlace  = document.getElementById("schedPlace");

btnSchedule?.addEventListener("click", async () => {
  const telefone = schedPhone?.value?.trim();
  const quando   = schedWhen?.value;
  const local    = schedPlace?.value?.trim() || "UBS";

  // Validações básicas no frontend
  if (!telefone) {
    showToast("Informe o telefone da paciente.", "error");
    schedPhone?.focus();
    return;
  }

  if (!quando) {
    showToast("Informe a data e hora do agendamento.", "error");
    schedWhen?.focus();
    return;
  }

  setBtnLoading(btnSchedule, true);

  const formData = new FormData();
  formData.append("person_phone", telefone);
  formData.append("when",         formatarDatetime(quando));
  formData.append("place",        local);

  try {
    const res  = await fetch("/api/schedule", { method: "POST", body: formData });
    const data = await res.json();

    if (res.ok && data?.status === "success") {
      showToast(
        `Agendamento criado para ${data.paciente}. Confirmação enviada!`,
        "success"
      );
      // Limpa os campos
      if (schedPhone) schedPhone.value = "";
      if (schedWhen)  schedWhen.value  = "";
      if (schedPlace) schedPlace.value = "";

      setTimeout(() => location.reload(), 2000);
    } else {
      showToast(data?.detail || "Paciente não encontrada ou erro ao agendar.", "error");
    }
  } catch {
    showToast("Erro de rede ao criar agendamento.", "error");
  } finally {
    setBtnLoading(btnSchedule, false);
  }
});


/* ==================================================================
   OPT-OUT DE PACIENTES (tabela de pacientes)
   ================================================================== */

/**
 * Delegação de eventos: um único listener na tabela cuida de todos
 * os botões de opt-out, mesmo os adicionados dinamicamente.
 */
document.addEventListener("click", async (e) => {
  const btn = e.target.closest(".btn-optout");
  if (!btn) return;

  const id     = btn.dataset.id;
  const optout = btn.dataset.optout === "true";

  if (!id) return;

  // Confirmação apenas para ativar opt-out (ação mais crítica)
  if (!optout) {
    const confirmado = confirm(
      "Deseja desativar os envios para esta paciente?\n" +
      "Ela não receberá mais mensagens automáticas."
    );
    if (!confirmado) return;
  }

  btn.disabled = true;

  try {
    const res  = await fetch(`/api/patients/${id}/optout`, { method: "PUT" });
    const data = await res.json();

    if (res.ok && data?.status === "success") {
      showToast(data.mensagem, "success");

      // Atualiza o botão visualmente sem recarregar a página
      const novoOptout = data.optout;
      btn.dataset.optout = String(novoOptout);
      btn.classList.toggle("btn-optout--active", novoOptout);
      btn.title = novoOptout ? "Reativar paciente" : "Desativar envios";

      // Troca o ícone Lucide
      btn.innerHTML = novoOptout
        ? '<i data-lucide="bell-off"></i>'
        : '<i data-lucide="bell"></i>';
      if (window.lucide) lucide.createIcons({ nodes: [btn] });

      // Atualiza o badge de status na mesma linha
      const linha = btn.closest("tr");
      if (linha && novoOptout) {
        const statusBadge = $(".status-badge", linha);
        if (statusBadge) {
          statusBadge.textContent = "skipped";
          statusBadge.className   = "status-badge status-badge--skipped";
        }
      }
    } else {
      showToast(data?.detail || "Erro ao alterar opt-out.", "error");
    }
  } catch {
    showToast("Erro de rede ao alterar opt-out.", "error");
  } finally {
    btn.disabled = false;
  }
});


/* ==================================================================
   ATUALIZAÇÃO DE STATUS DE AGENDAMENTOS (tabela de agendamentos)
   ================================================================== */

/**
 * Delegação de eventos para os botões "concluído" e "cancelar"
 * na tabela de agendamentos.
 */
document.addEventListener("click", async (e) => {
  const btn = e.target.closest(".btn-appt");
  if (!btn) return;

  const id         = btn.dataset.id;
  const novoStatus = btn.dataset.status;

  if (!id || !novoStatus) return;

  const labels = { done: "realizado", cancelled: "cancelado" };
  const confirmado = confirm(
    `Confirmar agendamento #${id} como ${labels[novoStatus] ?? novoStatus}?`
  );
  if (!confirmado) return;

  btn.disabled = true;

  const formData = new FormData();
  formData.append("novo_status", novoStatus);

  try {
    const res  = await fetch(`/api/appointments/${id}/status`, {
      method: "PUT",
      body:   formData,
    });
    const data = await res.json();

    if (res.ok && data?.status === "success") {
      showToast(`Agendamento #${id} marcado como ${labels[novoStatus]}.`, "success");

      // Atualiza o badge de status na linha sem recarregar
      const linha = btn.closest("tr");
      if (linha) {
        const badge = $(".status-badge", linha);
        if (badge) {
          badge.textContent = novoStatus;
          badge.className   = `status-badge status-badge--${novoStatus}`;
        }

        // Desabilita os dois botões da linha (ação já realizada)
        $$(".btn-appt", linha).forEach((b) => { b.disabled = true; });
      }
    } else {
      showToast(data?.detail || "Erro ao atualizar agendamento.", "error");
      btn.disabled = false;
    }
  } catch {
    showToast("Erro de rede ao atualizar agendamento.", "error");
    btn.disabled = false;
  }
});


/* ==================================================================
   INICIALIZAÇÃO
   ================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  // Reinicializa ícones após o DOM estar completo
  if (window.lucide) lucide.createIcons();
});