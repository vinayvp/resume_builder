/**
 * Resume Builder Frontend Application Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  // Lucide Icons initialization
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // State
  let currentToken = null;
  let currentResolvedFilename = "";
  let currentResolvedCoverLetterFilename = "";
  let isCustomFilenameActive = false;
  let customFilenameOverride = null;
  let isCustomCoverLetterFilenameActive = false;
  let customCoverLetterFilenameOverride = null;

  // DOM Elements
  const companyInput = document.getElementById("companyName");
  const roleInput = document.getElementById("roleName");
  const lblFilenamePreview = document.getElementById("lblFilenamePreview");
  const btnEditFilename = document.getElementById("btnEditFilename");
  const saveDirectoryInput = document.getElementById("saveDirectory");

  const lblCoverLetterFilenamePreview = document.getElementById("lblCoverLetterFilenamePreview");
  const btnEditCoverLetterFilename = document.getElementById("btnEditCoverLetterFilename");
  const coverLetterSaveDirectoryInput = document.getElementById("coverLetterSaveDirectory");

  const selTheme = document.getElementById("selTheme");
  const selFont = document.getElementById("selFont");
  const customFontInput = document.getElementById("customFontInput");
  const selPageSize = document.getElementById("selPageSize");
  const selPhoneFormat = document.getElementById("selPhoneFormat");
  const chkNoFooterNote = document.getElementById("chkNoFooterNote");
  const chkAllowPageBreak = document.getElementById("chkAllowPageBreak");
  const chkAllowSectionPageBreak = document.getElementById("chkAllowSectionPageBreak");

  const yamlEditor = document.getElementById("yamlEditor");
  const yamlLineCount = document.getElementById("yamlLineCount");
  const dropZone = document.getElementById("dropZone");
  const dropOverlay = document.getElementById("dropOverlay");
  const fileUploadInput = document.getElementById("fileUploadInput");
  const btnLoadSample = document.getElementById("btnLoadSample");
  const btnClearYaml = document.getElementById("btnClearYaml");
  const btnRenderResume = document.getElementById("btnRenderResume");
  const lblRenderBtnText = document.getElementById("lblRenderBtnText");

  const pipelineStatusBadge = document.getElementById("pipelineStatusBadge");
  const btnToggleCliLogs = document.getElementById("btnToggleCliLogs");
  const cliLogsPanel = document.getElementById("cliLogsPanel");
  const cliLogsContent = document.getElementById("cliLogsContent");
  const btnCopyLogs = document.getElementById("btnCopyLogs");

  const metricsReviewCard = document.getElementById("metricsReviewCard");
  const metricPageCount = document.getElementById("metricPageCount");
  const metricPageBadge = document.getElementById("metricPageBadge");
  const metricTotalWords = document.getElementById("metricTotalWords");
  const metricWordDensity = document.getElementById("metricWordDensity");
  const metricPageWords = document.getElementById("metricPageWords");
  const metricRenderTime = document.getElementById("metricRenderTime");
  const lblTargetLocation = document.getElementById("lblTargetLocation");
  const btnDownloadPdf = document.getElementById("btnDownloadPdf");
  const btnAcceptSave = document.getElementById("btnAcceptSave");
  const lblSaveBtnText = document.getElementById("lblSaveBtnText");
  const btnSaveBoth = document.getElementById("btnSaveBoth");

  const previewControls = document.getElementById("previewControls");
  const previewPageIndicator = document.getElementById("previewPageIndicator");
  const previewEmptyState = document.getElementById("previewEmptyState");
  const previewPagesContainer = document.getElementById("previewPagesContainer");
  const btnFullscreenPreview = document.getElementById("btnFullscreenPreview");

  // Full Screen Preview Modal DOM elements
  const fullscreenPreviewModal = document.getElementById("fullscreenPreviewModal");
  const fullscreenBackdrop = document.getElementById("fullscreenBackdrop");
  const btnCloseFullscreenModal = document.getElementById("btnCloseFullscreenModal");
  const fullscreenPreviewViewport = document.getElementById("fullscreenPreviewViewport");
  const fullscreenPagesContainer = document.getElementById("fullscreenPagesContainer");
  const fullscreenDocTitle = document.getElementById("fullscreenDocTitle");
  const fullscreenDocPageBadge = document.getElementById("fullscreenDocPageBadge");
  const fullscreenDocIcon = document.getElementById("fullscreenDocIcon");
  const btnFullscreenDocToggle = document.getElementById("btnFullscreenDocToggle");
  const fullscreenDocToggleIcon = document.getElementById("fullscreenDocToggleIcon");
  const fullscreenDocToggleLabel = document.getElementById("fullscreenDocToggleLabel");
  const btnFullscreenDownloadPdf = document.getElementById("btnFullscreenDownloadPdf");
  const btnFullscreenZoomIn = document.getElementById("btnFullscreenZoomIn");
  const btnFullscreenZoomOut = document.getElementById("btnFullscreenZoomOut");
  const btnFullscreenZoomReset = document.getElementById("btnFullscreenZoomReset");
  const fullscreenZoomLevel = document.getElementById("fullscreenZoomLevel");

  const successModal = document.getElementById("successModal");
  const modalResumeGroup = document.getElementById("modalResumeGroup");
  const modalSavedPath = document.getElementById("modalSavedPath");
  const btnCopySavedPath = document.getElementById("btnCopySavedPath");
  const btnCloseModal = document.getElementById("btnCloseModal");
  const btnToggleTheme = document.getElementById("btnToggleTheme");

  // Cover Letter DOM elements & state
  const docTabSelector = document.getElementById("docTabSelector");
  const tabResume = document.getElementById("tabResume");
  const tabCoverLetter = document.getElementById("tabCoverLetter");
  const tabResumeBadge = document.getElementById("tabResumeBadge");
  const tabCoverLetterBadge = document.getElementById("tabCoverLetterBadge");
  const lblDownloadBtn = document.getElementById("lblDownloadBtn");
  const lblReviewTitle = document.getElementById("lblReviewTitle");
  const metricPageWordsLabel = document.getElementById("metricPageWordsLabel");
  const modalTitle = document.getElementById("modalTitle");
  const modalCoverLetterGroup = document.getElementById("modalCoverLetterGroup");
  const modalSavedCoverLetterPath = document.getElementById("modalSavedCoverLetterPath");

  let activeDocTab = "resume";
  let currentRenderData = null;

  // -------------------------------------------------------------
  // Theme Management (Light / Dark)
  // -------------------------------------------------------------
  const updateFavicon = (isDark) => {
    const fav = document.getElementById("faviconLink");
    if (fav) {
      fav.href = isDark ? "/static/img/favicon-dark.png" : "/static/img/favicon-light.png";
    }
  };

  const initTheme = () => {
    const savedTheme = localStorage.getItem("rb-theme");
    const isDark = savedTheme === "dark" || (!savedTheme && window.matchMedia("(prefers-color-scheme: dark)").matches);
    if (isDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
    updateFavicon(isDark);
  };
  initTheme();

  btnToggleTheme.addEventListener("click", () => {
    const isDark = document.documentElement.classList.toggle("dark");
    localStorage.setItem("rb-theme", isDark ? "dark" : "light");
    updateFavicon(isDark);
  });

  // -------------------------------------------------------------
  // Dynamic Filename Calculator
  // -------------------------------------------------------------
  const sanitizeName = (val) => {
    if (!val) return "";
    return val.trim().replace(/[\s\-]+/g, "_").replace(/[^\w]/g, "");
  };

  const updateFilenamePreview = () => {
    const role = sanitizeName(roleInput.value);
    const company = sanitizeName(companyInput.value);

    // Resume Filename
    if (isCustomFilenameActive && customFilenameOverride) {
      currentResolvedFilename = customFilenameOverride;
    } else {
      let name = "VinayakPastey_Resume";
      if (role && company) {
        name += `_${role}_${company}`;
      } else if (role) {
        name += `_${role}`;
      } else if (company) {
        name += `_${company}`;
      }
      name += ".pdf";
      currentResolvedFilename = name;
    }
    if (lblFilenamePreview) {
      lblFilenamePreview.textContent = currentResolvedFilename;
      lblFilenamePreview.title = currentResolvedFilename;
    }

    // Cover Letter Filename
    if (isCustomCoverLetterFilenameActive && customCoverLetterFilenameOverride) {
      currentResolvedCoverLetterFilename = customCoverLetterFilenameOverride;
    } else {
      let clName = "VinayakPastey_Cover_Letter";
      if (role && company) {
        clName += `_${role}_${company}`;
      } else if (role) {
        clName += `_${role}`;
      } else if (company) {
        clName += `_${company}`;
      }
      clName += ".pdf";
      currentResolvedCoverLetterFilename = clName;
    }
    if (lblCoverLetterFilenamePreview) {
      lblCoverLetterFilenamePreview.textContent = currentResolvedCoverLetterFilename;
      lblCoverLetterFilenamePreview.title = currentResolvedCoverLetterFilename;
    }
  };

  companyInput.addEventListener("input", () => {
    isCustomFilenameActive = false;
    isCustomCoverLetterFilenameActive = false;
    updateFilenamePreview();
  });

  roleInput.addEventListener("input", () => {
    isCustomFilenameActive = false;
    isCustomCoverLetterFilenameActive = false;
    updateFilenamePreview();
  });

  btnEditFilename.addEventListener("click", () => {
    const custom = prompt("Enter custom Resume filename:", currentResolvedFilename);
    if (custom !== null && custom.trim() !== "") {
      let trimmed = custom.trim();
      if (!trimmed.toLowerCase().endsWith(".pdf")) trimmed += ".pdf";
      customFilenameOverride = trimmed;
      isCustomFilenameActive = true;
      updateFilenamePreview();
    }
  });

  if (btnEditCoverLetterFilename) {
    btnEditCoverLetterFilename.addEventListener("click", () => {
      const custom = prompt("Enter custom Cover Letter filename:", currentResolvedCoverLetterFilename);
      if (custom !== null && custom.trim() !== "") {
        let trimmed = custom.trim();
        if (!trimmed.toLowerCase().endsWith(".pdf")) trimmed += ".pdf";
        customCoverLetterFilenameOverride = trimmed;
        isCustomCoverLetterFilenameActive = true;
        updateFilenamePreview();
      }
    });
  }

  updateFilenamePreview();

  // -------------------------------------------------------------
  // Font Selector Custom Input Handler
  // -------------------------------------------------------------
  selFont.addEventListener("change", () => {
    if (selFont.value === "__custom__") {
      customFontInput.style.display = "block";
      customFontInput.focus();
    } else {
      customFontInput.style.display = "none";
    }
  });

  const getSelectedFont = () => {
    if (selFont.value === "__custom__") {
      return customFontInput.value.trim() || "Calibri";
    }
    return selFont.value;
  };

  // -------------------------------------------------------------
  // YAML Editor Helper & Line Counter
  // -------------------------------------------------------------
  const updateLineCount = () => {
    const lines = yamlEditor.value.split("\n").length;
    yamlLineCount.textContent = `${lines} lines`;
  };

  yamlEditor.addEventListener("input", updateLineCount);

  // Tab key support in textarea
  yamlEditor.addEventListener("keydown", (e) => {
    if (e.key === "Tab") {
      e.preventDefault();
      const start = yamlEditor.selectionStart;
      const end = yamlEditor.selectionEnd;
      yamlEditor.value = yamlEditor.value.substring(0, start) + "  " + yamlEditor.value.substring(end);
      yamlEditor.selectionStart = yamlEditor.selectionEnd = start + 2;
      updateLineCount();
    } else if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      triggerRender();
    }
  });

  // -------------------------------------------------------------
  // Sample Loader & Clear
  // -------------------------------------------------------------
  const loadSampleYaml = async () => {
    try {
      btnLoadSample.disabled = true;
      btnLoadSample.innerHTML = '<span class="inline-block animate-spin mr-1">↻</span> Loading...';
      const res = await fetch("/api/sample");
      if (!res.ok) throw new Error("Failed to load sample resume");
      const data = await res.json();
      yamlEditor.value = data.yaml;
      updateLineCount();
    } catch (err) {
      alert("Error loading sample YAML: " + err.message);
    } finally {
      btnLoadSample.disabled = false;
      btnLoadSample.innerHTML = '<i data-lucide="file-code-2" class="w-3.5 h-3.5 mr-1"></i><span>Load Sample YAML</span>';
      if (window.lucide) window.lucide.createIcons();
    }
  };

  btnLoadSample.addEventListener("click", loadSampleYaml);

  btnClearYaml.addEventListener("click", () => {
    if (confirm("Reset YAML editor?")) {
      yamlEditor.value = "";
      updateLineCount();
      resetSteps();
    }
  });

  // -------------------------------------------------------------
  // Drag & Drop File Upload
  // -------------------------------------------------------------
  ["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropOverlay.classList.remove("hidden");
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropOverlay.classList.add("hidden");
    });
  });

  dropZone.addEventListener("drop", (e) => {
    const dt = e.dataTransfer;
    const file = dt.files[0];
    if (file) {
      readFile(file);
    }
  });

  fileUploadInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) {
      readFile(file);
    }
  });

  const readFile = (file) => {
    const reader = new FileReader();
    reader.onload = (event) => {
      yamlEditor.value = event.target.result;
      updateLineCount();
    };
    reader.readAsText(file);
  };

  // -------------------------------------------------------------
  // Stepper Visual Management (1-Line Stepper)
  // -------------------------------------------------------------
  const stepTickerDot = document.getElementById("stepTickerDot");
  const stepTickerText = document.getElementById("stepTickerText");

  const resetSteps = () => {
    const stepIds = [
      "validate_input",
      "apply_design",
      "execute_cli",
      "analyze_metrics",
      "prepare_preview",
    ];

    stepIds.forEach((id, idx) => {
      const el = document.getElementById(`step-${id}`);
      if (el) {
        el.className = "step-pill flex items-center space-x-1.5 px-2 py-1 rounded-md bg-slate-200/70 dark:bg-dark-surface/60 text-slate-500 dark:text-[#94A3B8] text-[11px] font-medium transition-all";
        const icon = el.querySelector(".step-icon");
        if (icon) {
          icon.className = "step-icon w-4 h-4 rounded-full bg-slate-300 dark:bg-dark-panel text-slate-600 dark:text-[#EDF2F7] flex items-center justify-center text-[10px]";
          icon.innerHTML = (idx + 1).toString();
        }
      }
      const line = document.getElementById(`step-line-${idx + 1}`);
      if (line) {
        line.className = "flex-1 h-0.5 min-w-[6px] bg-slate-200 dark:bg-dark-plum/30 transition-colors";
      }
    });

    if (stepTickerText) stepTickerText.textContent = "Ready to render";
    if (stepTickerDot) stepTickerDot.className = "w-2 h-2 rounded-full bg-slate-400 dark:bg-dark-plum flex-shrink-0";
    if (pipelineStatusBadge) {
      pipelineStatusBadge.textContent = "Idle";
      pipelineStatusBadge.className = "inline-flex items-center px-2 py-0.2 text-[10px] font-medium rounded-full bg-slate-100 text-slate-600 dark:bg-dark-surface dark:text-[#94A3B8]";
    }
    if (metricsReviewCard) metricsReviewCard.classList.add("hidden");
    if (btnSaveBoth) btnSaveBoth.classList.add("hidden");
    if (lblSaveBtnText) lblSaveBtnText.textContent = "Save Resume";
    if (previewControls) previewControls.classList.add("opacity-40", "pointer-events-none");
    if (previewPagesContainer) previewPagesContainer.classList.add("hidden");
    if (previewEmptyState) previewEmptyState.classList.remove("hidden");
    if (previewPageIndicator) previewPageIndicator.textContent = "No document rendered";
    currentRenderData = null;
    activeDocTab = "resume";
  };

  const updateStepUI = (step, idx) => {
    const el = document.getElementById(`step-${step.id}`);
    if (!el) return;

    const icon = el.querySelector(".step-icon");

    if (step.status === "completed") {
      el.className = "step-pill flex items-center space-x-1.5 px-2 py-1 rounded-md bg-blue-50 dark:bg-dark-accent/15 text-blue-800 dark:text-blue-200 text-[11px] font-semibold border border-blue-200 dark:border-dark-accent/40 transition-all";
      if (icon) {
        icon.className = "step-icon w-4 h-4 rounded-full bg-dark-accent text-white flex items-center justify-center text-[10px]";
        icon.innerHTML = '<i data-lucide="check" class="w-3 h-3"></i>';
      }
      const line = document.getElementById(`step-line-${idx + 1}`);
      if (line) {
        line.className = "flex-1 h-0.5 min-w-[6px] bg-dark-accent transition-colors";
      }
      if (stepTickerText) {
        stepTickerText.textContent = `✓ Step ${idx + 1}: ${step.name} (${step.duration_ms || 0} ms)`;
      }
      if (stepTickerDot) {
        stepTickerDot.className = "w-2 h-2 rounded-full bg-dark-accent flex-shrink-0";
      }
    } else if (step.status === "running") {
      el.className = "step-pill flex items-center space-x-1.5 px-2 py-1 rounded-md bg-dark-accent text-white text-[11px] font-semibold shadow-sm transition-all animate-pulse";
      if (icon) {
        icon.className = "step-icon w-4 h-4 rounded-full bg-white text-dark-accent flex items-center justify-center text-[10px] animate-spin";
        icon.innerHTML = '<i data-lucide="loader-2" class="w-3 h-3"></i>';
      }
      if (stepTickerText) {
        stepTickerText.textContent = `Running ${step.name}...`;
      }
      if (stepTickerDot) {
        stepTickerDot.className = "w-2 h-2 rounded-full bg-dark-accent flex-shrink-0 animate-ping";
      }
    } else if (step.status === "failed") {
      el.className = "step-pill flex items-center space-x-1.5 px-2 py-1 rounded-md bg-red-100 dark:bg-red-950/70 text-red-700 dark:text-red-300 text-[11px] font-semibold border border-red-300 dark:border-red-900 transition-all";
      if (icon) {
        icon.className = "step-icon w-4 h-4 rounded-full bg-red-500 text-white flex items-center justify-center text-[10px]";
        icon.innerHTML = '<i data-lucide="x" class="w-3 h-3"></i>';
      }
      if (stepTickerText) {
        stepTickerText.textContent = `✗ ${step.name} failed: ${step.message || 'Error'}`;
      }
      if (stepTickerDot) {
        stepTickerDot.className = "w-2 h-2 rounded-full bg-red-500 flex-shrink-0";
      }
    }

    if (window.lucide) window.lucide.createIcons();
  };

  // -------------------------------------------------------------
  // CLI Logs Toggle
  // -------------------------------------------------------------
  btnToggleCliLogs.addEventListener("click", () => {
    cliLogsPanel.classList.toggle("hidden");
  });

  btnCopyLogs.addEventListener("click", () => {
    navigator.clipboard.writeText(cliLogsContent.textContent);
    btnCopyLogs.textContent = "Copied!";
    setTimeout(() => {
      btnCopyLogs.textContent = "Copy Logs";
    }, 2000);
  });

  // -------------------------------------------------------------
  // Render Resume Trigger
  // -------------------------------------------------------------
  const triggerRender = async () => {
    const yamlContent = yamlEditor.value.trim();
    if (!yamlContent) {
      alert("Please enter or load a YAML resume first.");
      return;
    }

    resetSteps();
    btnRenderResume.disabled = true;
    lblRenderBtnText.textContent = "Rendering...";
    pipelineStatusBadge.textContent = "Executing...";
    pipelineStatusBadge.className = "inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-blue-100 text-blue-800 dark:bg-dark-accent/20 dark:text-blue-300 animate-pulse";

    const payload = {
      yaml_content: yamlContent,
      company_name: companyInput.value.trim(),
      role_name: roleInput.value.trim(),
      custom_filename: isCustomFilenameActive ? customFilenameOverride : null,
      custom_cover_letter_filename: isCustomCoverLetterFilenameActive ? customCoverLetterFilenameOverride : null,
      save_directory: saveDirectoryInput.value.trim(),
      cover_letter_save_directory: coverLetterSaveDirectoryInput ? coverLetterSaveDirectoryInput.value.trim() : "~/Documents/Globathon/CoverLetters",
      design: {
        theme: selTheme.value,
        font_family: getSelectedFont(),
        page_size: selPageSize.value,
        no_footer_or_top_note: chkNoFooterNote.checked,
        phone_number_format: selPhoneFormat.value,
        allow_page_break_in_entries: chkAllowPageBreak.checked,
        allow_page_break_in_sections: chkAllowSectionPageBreak ? chkAllowSectionPageBreak.checked : true,
      },
    };

    try {
      const res = await fetch("/api/render", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      // Update CLI logs
      if (data.cli_logs) {
        cliLogsContent.textContent = data.cli_logs;
      }

      // Update Steps
      if (data.steps && data.steps.length) {
        data.steps.forEach((step, idx) => {
          updateStepUI(step, idx);
        });
      }

      if (!data.success) {
        pipelineStatusBadge.textContent = "Failed";
        pipelineStatusBadge.className = "inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300";
        cliLogsPanel.classList.remove("hidden");
        alert("Render Error: " + (data.error || "Execution failed. Check CLI logs."));
        return;
      }

      currentToken = data.token;
      currentResolvedFilename = data.resolved_filename || currentResolvedFilename;
      if (lblFilenamePreview) lblFilenamePreview.textContent = currentResolvedFilename;

      currentResolvedCoverLetterFilename = data.cover_letter_resolved_filename || currentResolvedCoverLetterFilename;
      if (lblCoverLetterFilenamePreview) lblCoverLetterFilenamePreview.textContent = currentResolvedCoverLetterFilename;

      pipelineStatusBadge.textContent = "Rendered";
      pipelineStatusBadge.className = "inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-blue-100 text-blue-800 dark:bg-dark-accent/20 dark:text-blue-300";

      currentRenderData = data;

      // Compute total pipeline render time from steps
      const totalTime = data.steps.reduce((acc, s) => acc + (s.duration_ms || 0), 0);
      metricRenderTime.textContent = `${Math.round(totalTime)} ms`;

      if (data.has_cover_letter) {
        if (tabResumeBadge) tabResumeBadge.textContent = `${data.metrics?.page_count || 1} pg`;
        if (tabCoverLetterBadge) {
          tabCoverLetterBadge.textContent = `${data.cover_letter_metrics?.page_count || 1} pg`;
          tabCoverLetterBadge.className = "text-[9px] px-1.5 py-0.2 rounded-full bg-slate-200 text-slate-700 dark:bg-dark-panel dark:text-[#EDF2F7] font-medium";
        }
        if (btnSaveBoth) btnSaveBoth.classList.remove("hidden");
        if (stepTickerText) {
          stepTickerText.textContent = `✓ CV & Cover Letter rendered in ${Math.round(totalTime)} ms`;
        }
      } else {
        if (tabResumeBadge) tabResumeBadge.textContent = `${data.metrics?.page_count || 1} pg`;
        if (tabCoverLetterBadge) {
          tabCoverLetterBadge.textContent = "None";
          tabCoverLetterBadge.className = "text-[9px] px-1.5 py-0.2 rounded-full bg-slate-100 text-slate-400 dark:bg-dark-surface dark:text-[#94A3B8] font-medium";
        }
        if (btnSaveBoth) btnSaveBoth.classList.add("hidden");
        if (stepTickerText) {
          stepTickerText.textContent = `✓ Complete in ${Math.round(totalTime)} ms (${data.metrics?.page_count || 1} pg, ${(data.metrics?.total_words || 0).toLocaleString()} words)`;
        }
      }

      if (stepTickerDot) {
        stepTickerDot.className = "w-2 h-2 rounded-full bg-dark-accent flex-shrink-0";
      }

      metricsReviewCard.classList.remove("hidden");
      if (!activeDocTab) activeDocTab = "resume";
      renderActiveDocumentView();

    } catch (err) {
      pipelineStatusBadge.textContent = "Network Error";
      pipelineStatusBadge.className = "inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-red-100 text-red-800";
      alert("Error invoking render: " + err.message);
    } finally {
      btnRenderResume.disabled = false;
      lblRenderBtnText.textContent = "Render (CV & Cover Letter)";
      if (window.lucide) window.lucide.createIcons();
    }
  };

  const updateTabButtonsUI = () => {
    const isResume = activeDocTab === "resume";
    if (tabResume && tabCoverLetter) {
      if (isResume) {
        tabResume.className = "cursor-pointer inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-md text-xs font-semibold bg-white dark:bg-dark-surface text-slate-900 dark:text-white shadow-sm border border-slate-200/60 dark:border-dark-plum/40 transition-all";
        tabCoverLetter.className = "cursor-pointer inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-md text-xs font-medium text-slate-500 dark:text-[#94A3B8] hover:text-slate-900 dark:hover:text-white transition-all";
      } else {
        tabResume.className = "cursor-pointer inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-md text-xs font-medium text-slate-500 dark:text-[#94A3B8] hover:text-slate-900 dark:hover:text-white transition-all";
        tabCoverLetter.className = "cursor-pointer inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-md text-xs font-semibold bg-white dark:bg-dark-surface text-blue-700 dark:text-white shadow-sm border border-slate-200/60 dark:border-dark-plum/40 transition-all";
      }
    }
  };

  // Expose global tab switcher so it can be invoked via onclick or addEventListener
  window.switchDocTab = (tab) => {
    console.log("[ResumeBuilder] switchDocTab:", tab);
    if (activeDocTab === tab && currentRenderData) {
      if (fullscreenPreviewModal && !fullscreenPreviewModal.classList.contains("hidden")) {
        updateFullscreenModalContent();
      }
      return;
    }
    if (tab === "cover_letter" && currentRenderData && !currentRenderData.has_cover_letter) {
      alert("The rendered YAML does not contain a 'cover_letter:' section. Add a cover_letter block to your YAML to generate and preview a cover letter.");
      return;
    }
    activeDocTab = tab;
    updateTabButtonsUI();
    renderActiveDocumentView();
    if (fullscreenPreviewModal && !fullscreenPreviewModal.classList.contains("hidden")) {
      updateFullscreenModalContent();
    }
  };

  const renderActiveDocumentView = () => {
    updateTabButtonsUI();

    const isResume = activeDocTab === "resume";
    const docTitle = isResume ? "Resume" : "Cover Letter";
    const targetDir = isResume
      ? saveDirectoryInput.value.trim()
      : (coverLetterSaveDirectoryInput ? coverLetterSaveDirectoryInput.value.trim() : "~/Documents/Globathon/CoverLetters");
    const resolvedName = isResume ? currentResolvedFilename : currentResolvedCoverLetterFilename;

    if (lblReviewTitle) {
      lblReviewTitle.textContent = isResume ? "Ready for Review (Resume)" : "Ready for Review (Cover Letter - Omega)";
    }

    if (lblTargetLocation) {
      lblTargetLocation.textContent = `${targetDir}/${resolvedName}`;
    }

    if (lblDownloadBtn) {
      lblDownloadBtn.textContent = isResume ? "Download Resume" : "Download Cover Letter";
    }

    if (lblSaveBtnText) {
      lblSaveBtnText.textContent = isResume ? "Save Resume" : "Save Cover Letter";
    }

    if (!currentRenderData) {
      if (previewEmptyState) {
        const titleEl = previewEmptyState.querySelector("p.font-medium");
        const subTitleEl = previewEmptyState.querySelector("p.text-xs");
        if (titleEl) titleEl.textContent = `No ${docTitle} Rendered Yet`;
        if (subTitleEl) {
          subTitleEl.textContent = isResume
            ? 'Click "Render (CV & Cover Letter)" below to start'
            : 'Click "Render (CV & Cover Letter)" below to compile the Omega cover letter';
        }
      }
      return;
    }

    const urls = isResume ? currentRenderData.preview_urls : currentRenderData.cover_letter_preview_urls;
    const metrics = isResume ? currentRenderData.metrics : currentRenderData.cover_letter_metrics;

    btnDownloadPdf.href = isResume ? currentRenderData.pdf_preview_url : currentRenderData.cover_letter_pdf_url;
    btnDownloadPdf.download = resolvedName;

    // Populate Metrics
    if (metrics) {
      const pages = metrics.page_count;
      const totalWords = metrics.total_words;

      metricPageCount.textContent = pages;
      if (pages === 1) {
        metricPageBadge.textContent = "Single Page";
        metricPageBadge.className = "inline-block mt-1 text-[10px] font-medium px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 dark:bg-dark-accent/20 dark:text-blue-300";
      } else {
        metricPageBadge.textContent = `${pages} Pages`;
        metricPageBadge.className = "inline-block mt-1 text-[10px] font-medium px-2 py-0.5 rounded-full bg-slate-200 text-slate-800 dark:bg-dark-surface dark:text-[#EDF2F7] border border-transparent dark:border-dark-plum/30";
      }

      metricTotalWords.textContent = totalWords.toLocaleString();
      const avgWords = Math.round(totalWords / Math.max(pages, 1));
      metricWordDensity.textContent = `~${avgWords} words/page`;

      if (metrics.page_words && metrics.page_words.length) {
        const breakdown = metrics.page_words.map((w, idx) => `P${idx + 1}: ${w}w`).join(" · ");
        metricPageWords.textContent = breakdown;
        if (metricPageWordsLabel) metricPageWordsLabel.textContent = "Distribution";
      } else {
        metricPageWords.textContent = `${totalWords}w`;
        if (metricPageWordsLabel) metricPageWordsLabel.textContent = "Word count";
      }
    }

    // Populate Preview Pages
    if (urls && urls.length) {
      previewPagesContainer.innerHTML = "";
      urls.forEach((url, idx) => {
        const pageWrapper = document.createElement("div");
        pageWrapper.className = "relative flex flex-col items-center w-full max-w-[800px]";

        const pageHeader = document.createElement("div");
        pageHeader.className = "w-full flex items-center justify-between pb-1.5 px-1 text-[11px] text-slate-400 dark:text-[#94A3B8] font-mono";
        pageHeader.innerHTML = `<span>${docTitle} &middot; Page ${idx + 1} of ${urls.length}</span><span>${metrics?.page_words?.[idx] || metrics?.total_words || 0} words</span>`;

        const img = document.createElement("img");
        img.src = `${url}?t=${Date.now()}`;
        img.alt = `${docTitle} Page ${idx + 1}`;
        img.className = "resume-page-sheet w-full shadow-lg rounded-sm cursor-pointer hover:shadow-xl transition-shadow";
        img.title = "Click to enlarge in full screen preview";
        img.addEventListener("click", () => openFullscreenModal());

        pageWrapper.appendChild(pageHeader);
        pageWrapper.appendChild(img);
        previewPagesContainer.appendChild(pageWrapper);
      });

      previewEmptyState.classList.add("hidden");
      previewPagesContainer.classList.remove("hidden");
      previewControls.classList.remove("opacity-40", "pointer-events-none");
      previewPageIndicator.textContent = `${docTitle}: ${urls.length} page(s) ready`;
    } else {
      previewPagesContainer.innerHTML = "";
      previewPagesContainer.classList.add("hidden");
      previewEmptyState.classList.remove("hidden");
      previewControls.classList.add("opacity-40", "pointer-events-none");
      previewPageIndicator.textContent = `No ${docTitle} rendered`;
    }

    if (fullscreenPreviewModal && !fullscreenPreviewModal.classList.contains("hidden")) {
      updateFullscreenModalContent();
    }

    if (window.lucide) window.lucide.createIcons();
  };

  if (tabResume) {
    tabResume.addEventListener("click", (e) => {
      e.preventDefault();
      window.switchDocTab("resume");
    });
  }

  if (tabCoverLetter) {
    tabCoverLetter.addEventListener("click", (e) => {
      e.preventDefault();
      window.switchDocTab("cover_letter");
    });
  }

  btnRenderResume.addEventListener("click", triggerRender);

  // -------------------------------------------------------------
  // Full Screen Preview Modal Logic
  // -------------------------------------------------------------
  let fullscreenZoom = 100;
  let fullscreenRenderToken = 0;

  // Initialize PDF.js worker
  if (window.pdfjsLib) {
    window.pdfjsLib.GlobalWorkerOptions.workerSrc = "/static/vendor/pdf.worker.min.js";
  }

  const applyFullscreenZoom = () => {
    if (fullscreenPagesContainer) {
      fullscreenPagesContainer.style.transform = `scale(${fullscreenZoom / 100})`;
    }
    if (fullscreenZoomLevel) {
      fullscreenZoomLevel.textContent = `${fullscreenZoom}%`;
    }
  };

  const renderFullscreenWithPdfJs = async (pdfUrl, docTitle, metrics, fallbackUrls) => {
    const renderToken = ++fullscreenRenderToken;
    if (!fullscreenPagesContainer) return;

    fullscreenPagesContainer.innerHTML = `
      <div class="py-16 text-center text-slate-400 text-sm flex flex-col items-center justify-center space-y-2.5">
        <div class="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <span class="font-mono text-xs">Loading document...</span>
      </div>
    `;

    try {
      if (!window.pdfjsLib) {
        throw new Error("pdfjsLib is not available");
      }

      const loadingTask = window.pdfjsLib.getDocument(pdfUrl);
      const pdf = await loadingTask.promise;
      if (renderToken !== fullscreenRenderToken) return;

      fullscreenPagesContainer.innerHTML = "";

      for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
        const page = await pdf.getPage(pageNum);
        if (renderToken !== fullscreenRenderToken) return;

        const pageWrapper = document.createElement("div");
        pageWrapper.className = "relative flex flex-col items-center w-full max-w-4xl select-text";

        const pageHeader = document.createElement("div");
        pageHeader.className = "w-full flex items-center justify-between pb-2 px-1 text-xs text-slate-500 dark:text-[#94A3B8] font-mono select-none";
        const pageWords = metrics?.page_words?.[pageNum - 1] || (pageNum === 1 ? metrics?.total_words : 0) || 0;
        pageHeader.innerHTML = `<span>${docTitle} &middot; Page ${pageNum} of ${pdf.numPages}</span><span>${pageWords} words</span>`;

        // Page container for canvas and transparent text layer
        const pageSheet = document.createElement("div");
        pageSheet.className = "relative pdf-page-sheet resume-page-sheet shadow-2xl rounded-sm overflow-hidden select-text";

        // Scale factor: 1.5 provides high crispness without excessive memory
        const scale = 1.5;
        const viewport = page.getViewport({ scale });

        const canvas = document.createElement("canvas");
        canvas.width = viewport.width;
        canvas.height = viewport.height;
        canvas.className = "block w-full h-auto";
        const canvasContext = canvas.getContext("2d");

        await page.render({ canvasContext, viewport }).promise;
        if (renderToken !== fullscreenRenderToken) return;

        // Overlay text layer for text selection & copying
        const textLayerDiv = document.createElement("div");
        textLayerDiv.className = "textLayer";
        textLayerDiv.style.width = `${viewport.width}px`;
        textLayerDiv.style.height = `${viewport.height}px`;
        textLayerDiv.style.setProperty("--scale-factor", viewport.scale);

        const textContent = await page.getTextContent();
        if (renderToken !== fullscreenRenderToken) return;

        await window.pdfjsLib.renderTextLayer({
          textContentSource: textContent,
          container: textLayerDiv,
          viewport: viewport,
          textDivs: []
        }).promise;

        pageSheet.appendChild(canvas);
        pageSheet.appendChild(textLayerDiv);

        pageWrapper.appendChild(pageHeader);
        pageWrapper.appendChild(pageSheet);
        fullscreenPagesContainer.appendChild(pageWrapper);
      }
    } catch (err) {
      console.warn("[ResumeBuilder] PDF.js rendering error, using fallback images:", err);
      if (renderToken !== fullscreenRenderToken) return;
      renderFullscreenImageFallback(fallbackUrls, docTitle, metrics);
    }
  };

  const renderFullscreenImageFallback = (urls, docTitle, metrics) => {
    if (!fullscreenPagesContainer) return;
    fullscreenPagesContainer.innerHTML = "";
    if (urls && urls.length > 0) {
      urls.forEach((url, idx) => {
        const pageWrapper = document.createElement("div");
        pageWrapper.className = "relative flex flex-col items-center w-full max-w-4xl";

        const pageHeader = document.createElement("div");
        pageHeader.className = "w-full flex items-center justify-between pb-2 px-1 text-xs text-slate-500 dark:text-[#94A3B8] font-mono";
        pageHeader.innerHTML = `<span>${docTitle} &middot; Page ${idx + 1} of ${urls.length}</span><span>${metrics?.page_words?.[idx] || metrics?.total_words || 0} words</span>`;

        const img = document.createElement("img");
        img.src = `${url}?t=${Date.now()}`;
        img.alt = `${docTitle} Page ${idx + 1}`;
        img.className = "resume-page-sheet w-full shadow-2xl rounded-sm";

        pageWrapper.appendChild(pageHeader);
        pageWrapper.appendChild(img);
        fullscreenPagesContainer.appendChild(pageWrapper);
      });
    } else {
      const emptyMsg = document.createElement("div");
      emptyMsg.className = "py-16 text-center text-slate-400 text-sm";
      emptyMsg.textContent = `No ${docTitle} preview available.`;
      fullscreenPagesContainer.appendChild(emptyMsg);
    }
  };

  const updateFullscreenModalContent = () => {
    if (!currentRenderData) return;

    const isResume = activeDocTab === "resume";
    const docTitle = isResume ? "Resume" : "Cover Letter";
    const urls = isResume ? currentRenderData.preview_urls : currentRenderData.cover_letter_preview_urls;
    const metrics = isResume ? currentRenderData.metrics : currentRenderData.cover_letter_metrics;
    const resolvedName = isResume ? currentResolvedFilename : currentResolvedCoverLetterFilename;
    const pdfUrl = isResume ? currentRenderData.pdf_preview_url : currentRenderData.cover_letter_pdf_url;

    // 1. Title, badge, icon
    if (fullscreenDocTitle) {
      fullscreenDocTitle.textContent = `${docTitle} Preview`;
    }
    if (fullscreenDocPageBadge) {
      const pageCount = urls ? urls.length : (metrics?.page_count || 1);
      fullscreenDocPageBadge.textContent = `${pageCount} ${pageCount === 1 ? "page" : "pages"}`;
    }
    if (fullscreenDocIcon) {
      fullscreenDocIcon.className = "p-1.5 rounded-lg bg-blue-50 text-blue-600 dark:bg-dark-surface dark:text-dark-accent flex items-center justify-center flex-shrink-0";
      fullscreenDocIcon.innerHTML = `<i data-lucide="${isResume ? 'file-text' : 'mail'}" class="w-4 h-4"></i>`;
    }

    // 2. Modal PDF Download link
    if (btnFullscreenDownloadPdf) {
      btnFullscreenDownloadPdf.href = pdfUrl || "#";
      btnFullscreenDownloadPdf.download = resolvedName;
    }

    // 3. Document Toggle Button:
    // When in Resume: show "Show Cover Letter" button. Disabled if cover letter doesn't exist.
    // When in Cover Letter: show "Show Resume" button. Disabled if resume doesn't exist.
    const hasCoverLetter = Boolean(
      currentRenderData.has_cover_letter &&
      (currentRenderData.cover_letter_pdf_url || (currentRenderData.cover_letter_preview_urls && currentRenderData.cover_letter_preview_urls.length > 0))
    );
    const hasResume = Boolean(
      currentRenderData.pdf_preview_url || (currentRenderData.preview_urls && currentRenderData.preview_urls.length > 0)
    );

    if (btnFullscreenDocToggle) {
      if (isResume) {
        if (fullscreenDocToggleLabel) fullscreenDocToggleLabel.textContent = "Show Cover Letter";
        if (fullscreenDocToggleIcon) {
          fullscreenDocToggleIcon.setAttribute("data-lucide", "mail");
          fullscreenDocToggleIcon.className = "w-3.5 h-3.5 text-blue-600 dark:text-dark-accent";
        }
        if (!hasCoverLetter) {
          btnFullscreenDocToggle.disabled = true;
          btnFullscreenDocToggle.title = "No cover letter available in current document";
          btnFullscreenDocToggle.classList.add("opacity-40", "cursor-not-allowed");
          btnFullscreenDocToggle.classList.remove("hover:bg-slate-200", "dark:hover:bg-dark-surface/80", "cursor-pointer");
        } else {
          btnFullscreenDocToggle.disabled = false;
          btnFullscreenDocToggle.title = "Switch to Cover Letter preview";
          btnFullscreenDocToggle.classList.remove("opacity-40", "cursor-not-allowed");
          btnFullscreenDocToggle.classList.add("hover:bg-slate-200", "dark:hover:bg-dark-surface/80", "cursor-pointer");
        }
      } else {
        if (fullscreenDocToggleLabel) fullscreenDocToggleLabel.textContent = "Show Resume";
        if (fullscreenDocToggleIcon) {
          fullscreenDocToggleIcon.setAttribute("data-lucide", "file-text");
          fullscreenDocToggleIcon.className = "w-3.5 h-3.5 text-blue-600 dark:text-dark-accent";
        }
        if (!hasResume) {
          btnFullscreenDocToggle.disabled = true;
          btnFullscreenDocToggle.title = "No resume available in current document";
          btnFullscreenDocToggle.classList.add("opacity-40", "cursor-not-allowed");
          btnFullscreenDocToggle.classList.remove("hover:bg-slate-200", "dark:hover:bg-dark-surface/80", "cursor-pointer");
        } else {
          btnFullscreenDocToggle.disabled = false;
          btnFullscreenDocToggle.title = "Switch to Resume preview";
          btnFullscreenDocToggle.classList.remove("opacity-40", "cursor-not-allowed");
          btnFullscreenDocToggle.classList.add("hover:bg-slate-200", "dark:hover:bg-dark-surface/80", "cursor-pointer");
        }
      }
    }

    // 4. Render Pages inside Modal with Selectable Text (via PDF.js)
    if (pdfUrl) {
      renderFullscreenWithPdfJs(pdfUrl, docTitle, metrics, urls);
    } else {
      renderFullscreenImageFallback(urls, docTitle, metrics);
    }

    if (window.lucide) {
      window.lucide.createIcons();
    }
  };

  const openFullscreenModal = () => {
    if (!currentRenderData) {
      alert("No document rendered yet. Please click 'Render (CV & Cover Letter)' first.");
      return;
    }
    fullscreenZoom = 100;
    applyFullscreenZoom();
    updateFullscreenModalContent();
    if (fullscreenPreviewModal) {
      fullscreenPreviewModal.classList.remove("hidden");
    }
    if (fullscreenPreviewViewport) {
      fullscreenPreviewViewport.scrollTop = 0;
    }
    document.body.classList.add("overflow-hidden");
  };

  const closeFullscreenModal = () => {
    fullscreenRenderToken++;
    if (fullscreenPreviewModal) {
      fullscreenPreviewModal.classList.add("hidden");
    }
    document.body.classList.remove("overflow-hidden");
  };

  if (btnFullscreenPreview) {
    btnFullscreenPreview.addEventListener("click", () => {
      openFullscreenModal();
    });
  }

  if (btnCloseFullscreenModal) {
    btnCloseFullscreenModal.addEventListener("click", () => {
      closeFullscreenModal();
    });
  }

  if (fullscreenBackdrop) {
    fullscreenBackdrop.addEventListener("click", () => {
      closeFullscreenModal();
    });
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && fullscreenPreviewModal && !fullscreenPreviewModal.classList.contains("hidden")) {
      closeFullscreenModal();
    }
  });

  if (btnFullscreenDocToggle) {
    btnFullscreenDocToggle.addEventListener("click", () => {
      if (!currentRenderData) return;
      const targetTab = activeDocTab === "resume" ? "cover_letter" : "resume";
      if (targetTab === "cover_letter" && (!currentRenderData.has_cover_letter || !currentRenderData.cover_letter_preview_urls?.length)) {
        return;
      }
      if (targetTab === "resume" && !currentRenderData.preview_urls?.length) {
        return;
      }
      window.switchDocTab(targetTab);
    });
  }

  if (btnFullscreenZoomIn) {
    btnFullscreenZoomIn.addEventListener("click", () => {
      if (fullscreenZoom < 220) {
        fullscreenZoom += 15;
        applyFullscreenZoom();
      }
    });
  }

  if (btnFullscreenZoomOut) {
    btnFullscreenZoomOut.addEventListener("click", () => {
      if (fullscreenZoom > 50) {
        fullscreenZoom -= 15;
        applyFullscreenZoom();
      }
    });
  }

  if (btnFullscreenZoomReset) {
    btnFullscreenZoomReset.addEventListener("click", () => {
      fullscreenZoom = 100;
      applyFullscreenZoom();
    });
  }

  // -------------------------------------------------------------
  // Acceptance & Save Workflow
  // -------------------------------------------------------------
  btnAcceptSave.addEventListener("click", async () => {
    if (!currentToken) {
      alert("No active document rendered. Please click Render Resume first.");
      return;
    }

    const isResume = activeDocTab === "resume";
    btnAcceptSave.disabled = true;
    btnAcceptSave.innerHTML = '<span class="inline-block animate-spin mr-1">↻</span> Saving...';

    const payload = {
      token: currentToken,
      save_resume: isResume,
      save_cover_letter: !isResume,
    };

    if (isResume) {
      payload.custom_filename = currentResolvedFilename;
      payload.save_directory = saveDirectoryInput.value.trim();
    } else {
      payload.custom_cover_letter_filename = currentResolvedCoverLetterFilename;
      payload.cover_letter_save_directory = coverLetterSaveDirectoryInput ? coverLetterSaveDirectoryInput.value.trim() : "";
    }

    try {
      const res = await fetch("/api/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || data.message || "Failed to save file.");
      }

      if (isResume) {
        modalSavedPath.textContent = data.saved_path;
        if (modalResumeGroup) modalResumeGroup.classList.remove("hidden");
        if (modalCoverLetterGroup) modalCoverLetterGroup.classList.add("hidden");
        if (modalTitle) modalTitle.textContent = "Resume Successfully Saved!";
      } else {
        if (modalSavedCoverLetterPath) modalSavedCoverLetterPath.textContent = data.saved_cover_letter_path;
        if (modalResumeGroup) modalResumeGroup.classList.add("hidden");
        if (modalCoverLetterGroup) modalCoverLetterGroup.classList.remove("hidden");
        if (modalTitle) modalTitle.textContent = "Cover Letter Successfully Saved!";
      }
      successModal.classList.remove("hidden");

    } catch (err) {
      alert("Save Failed: " + err.message);
    } finally {
      btnAcceptSave.disabled = false;
      btnAcceptSave.innerHTML = `<i data-lucide="save" class="w-3.5 h-3.5 mr-1.5"></i><span id="lblSaveBtnText">${isResume ? "Save Resume" : "Save Cover Letter"}</span>`;
      if (window.lucide) window.lucide.createIcons();
    }
  });

  // Save Both Workflow
  if (btnSaveBoth) {
    btnSaveBoth.addEventListener("click", async () => {
      if (!currentToken) {
        alert("No active document rendered. Please click Render Resume first.");
        return;
      }

      btnSaveBoth.disabled = true;
      btnSaveBoth.innerHTML = '<span class="inline-block animate-spin mr-1">↻</span> Saving Both...';

      const payload = {
        token: currentToken,
        save_resume: true,
        save_cover_letter: true,
        custom_filename: currentResolvedFilename,
        save_directory: saveDirectoryInput.value.trim(),
        custom_cover_letter_filename: currentResolvedCoverLetterFilename,
        cover_letter_save_directory: coverLetterSaveDirectoryInput ? coverLetterSaveDirectoryInput.value.trim() : "",
      };

      try {
        const res = await fetch("/api/save", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        const data = await res.json();
        if (!res.ok || !data.success) {
          throw new Error(data.error || data.message || "Failed to save files.");
        }

        modalSavedPath.textContent = data.saved_path;
        if (modalSavedCoverLetterPath) modalSavedCoverLetterPath.textContent = data.saved_cover_letter_path;
        if (modalResumeGroup) modalResumeGroup.classList.remove("hidden");
        if (modalCoverLetterGroup) modalCoverLetterGroup.classList.remove("hidden");
        if (modalTitle) modalTitle.textContent = "Resume & Cover Letter Saved!";
        successModal.classList.remove("hidden");

      } catch (err) {
        alert("Save Both Failed: " + err.message);
      } finally {
        btnSaveBoth.disabled = false;
        btnSaveBoth.innerHTML = '<i data-lucide="folder-archive" class="w-3.5 h-3.5 mr-1.5 text-blue-500 dark:text-dark-accent"></i><span>Save Both</span>';
        if (window.lucide) window.lucide.createIcons();
      }
    });
  }

  // Modal actions
  btnCloseModal.addEventListener("click", () => {
    successModal.classList.add("hidden");
  });

  btnCopySavedPath.addEventListener("click", () => {
    const paths = [];
    if (modalResumeGroup && !modalResumeGroup.classList.contains("hidden")) {
      paths.push(`Resume: ${modalSavedPath.textContent.trim()}`);
    }
    if (modalCoverLetterGroup && !modalCoverLetterGroup.classList.contains("hidden")) {
      paths.push(`Cover Letter: ${modalSavedCoverLetterPath.textContent.trim()}`);
    }
    navigator.clipboard.writeText(paths.join("\n"));
    btnCopySavedPath.textContent = "Copied!";
    setTimeout(() => {
      btnCopySavedPath.textContent = "Copy File Path";
    }, 2000);
  });

  // Auto-load sample resume on initial page load for convenience
  loadSampleYaml();
});

