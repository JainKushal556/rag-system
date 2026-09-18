// ==========================================================================
// NEXUSRAG — FRONTEND CONTROLLER (VANILLA JAVASCRIPT)
// ==========================================================================

const API_BASE_URL = "http://127.0.0.1:8000";

// DOM Elements
const healthStatus = document.getElementById("health-status");
const uploadLoader = document.getElementById("upload-loader");
const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const fileInfo = document.getElementById("file-info");
const fileName = document.getElementById("file-name");
const fileSize = document.getElementById("file-size");
const removeBtn = document.getElementById("remove-btn");
const uploadBtn = document.getElementById("upload-btn");
const cooldownBanner = document.getElementById("cooldown-banner");
const cooldownText = document.getElementById("cooldown-text");

const uploadedFilesList = document.getElementById("uploaded-files-list");
const filesCount = document.getElementById("files-count");

const chatFeed = document.getElementById("chat-feed");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");

let selectedFile = null;
let isUploading = false;
let cooldownInterval = null;

// ==========================================================================
// 1. PERSISTENT RATE-LIMIT COOLDOWN (1 MINUTE LOCK)
// ==========================================================================

function isCooldownActive() {
    const cooldownUntil = parseInt(localStorage.getItem("rag_upload_cooldown_until") || "0", 10);
    return Date.now() < cooldownUntil;
}

function startCooldownTimer(seconds = 60) {
    const expireTime = Date.now() + seconds * 1000;
    localStorage.setItem("rag_upload_cooldown_until", expireTime.toString());
    console.log(`🔒 [Cooldown Started]: Upload locked for ${seconds} seconds until`, new Date(expireTime).toLocaleTimeString());
    applyCooldownUI();
}

function applyCooldownUI() {
    if (cooldownInterval) clearInterval(cooldownInterval);

    const checkAndTick = () => {
        const cooldownUntil = parseInt(localStorage.getItem("rag_upload_cooldown_until") || "0", 10);
        const remainingMs = cooldownUntil - Date.now();

        if (remainingMs > 0) {
            const remainingSec = Math.ceil(remainingMs / 1000);
            
            // 🔒 FULL LOCK ON UPLOAD FACILITIES
            dropZone.classList.add("disabled");
            fileInput.disabled = true;
            uploadBtn.disabled = true;
            uploadBtn.style.opacity = "0.5";
            uploadBtn.style.cursor = "not-allowed";
            uploadBtn.textContent = `🔒 Locked (${remainingSec}s)`;

            if (cooldownBanner) {
                cooldownBanner.style.display = "flex";
                cooldownText.textContent = `Rate limit cooldown: ${remainingSec}s remaining`;
            }
        } else {
            // 🔓 UNLOCK UPLOAD FACILITIES (Only if not currently in-flight uploading)
            clearInterval(cooldownInterval);
            cooldownInterval = null;
            localStorage.removeItem("rag_upload_cooldown_until");

            if (!isUploading) {
                dropZone.classList.remove("disabled");
                fileInput.disabled = false;
                uploadBtn.disabled = false;
                uploadBtn.style.opacity = "1";
                uploadBtn.style.cursor = "pointer";
                uploadBtn.textContent = "Upload & Ingest";

                if (cooldownBanner) {
                    cooldownBanner.style.display = "none";
                }
                console.log("🔓 [Cooldown Expired]: Upload facility is now unlocked.");
            }
        }
    };

    checkAndTick();
    cooldownInterval = setInterval(checkAndTick, 1000);
}

// ==========================================================================
// 2. HEALTH CHECK & BACKEND STATUS INDICATOR
// ==========================================================================

async function checkBackendHealth() {
    if (!healthStatus) return;
    const statusText = healthStatus.querySelector(".status-text");
    try {
        const response = await fetch(`${API_BASE_URL}/health`, { method: "GET" });
        const data = await response.json();
        console.log("🔍 [API /health Response]:", data);

        if (response.ok) {
            healthStatus.className = "status-badge online";
            statusText.textContent = "Backend Live";
        } else {
            healthStatus.className = "status-badge offline";
            statusText.textContent = "Server Error";
        }
    } catch (error) {
        console.error("❌ [API /health Error]:", error);
        healthStatus.className = "status-badge offline";
        statusText.textContent = "Backend Offline";
    }
}

// ==========================================================================
// 3. LOAD & RENDER INDEXED DOCUMENTS (/files)
// ==========================================================================

async function loadUploadedFiles() {
    try {
        const response = await fetch(`${API_BASE_URL}/files`);
        const files = await response.json();
        console.log("📂 [API /files Response]:", files);

        if (!response.ok) return;

        if (filesCount) filesCount.textContent = files.length;
        if (!uploadedFilesList) return;

        if (files.length === 0) {
            uploadedFilesList.innerHTML = `<div class="vault-empty">No documents uploaded yet.</div>`;
            return;
        }

        uploadedFilesList.innerHTML = files.map((file) => `
            <div class="vault-item">
                <div class="vault-item-top">
                    <span class="vault-item-name" title="${file.name}">📄 ${file.name}</span>
                    <span class="vault-item-size">${file.size}</span>
                </div>
                <span class="vault-item-date">Added: ${file.added_date}</span>
            </div>
        `).join("");

    } catch (error) {
        console.error("❌ [API /files Error]:", error);
    }
}

// ==========================================================================
// 4. CHAT MESSAGING & COMPREHENSIVE MARKDOWN RENDERING
// ==========================================================================

function renderMarkdown(raw) {
    if (!raw) return "";

    // 1. Try marked.js if available
    if (typeof marked !== "undefined" && typeof marked.parse === "function") {
        try {
            return marked.parse(raw);
        } catch (e) {
            console.warn("⚠️ marked.js error, falling back to built-in parser:", e);
        }
    }

    // 2. Comprehensive Zero-Dependency Built-in Markdown Parser
    let text = raw.trim();

    // Code Blocks (```lang ... ```)
    text = text.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (match, lang, code) => {
        const cleanCode = code
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
        return `<pre><code class="language-${lang}">${cleanCode}</code></pre>`;
    });

    // Headings (# H1, ## H2, ### H3, #### H4)
    text = text.replace(/^#### (.*$)/gim, '<h4>$1</h4>');
    text = text.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    text = text.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    text = text.replace(/^# (.*$)/gim, '<h1>$1</h1>');

    // Blockquotes (> quote)
    text = text.replace(/^>\s*(.*$)/gim, '<blockquote>$1</blockquote>');

    // Inline formatting: Inline code, Bold, Italic
    text = text.replace(/`([^`\n]+)`/g, '<code>$1</code>');
    text = text.replace(/\*\*\*([^*\n]+)\*\*\*/g, '<strong><em>$1</em></strong>');
    text = text.replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/__([^_]+)__/g, '<strong>$1</strong>');
    text = text.replace(/\*([^*\n]+)\*/g, '<em>$1</em>');
    text = text.replace(/_([^_]+)_/g, '<em>$1</em>');

    // Unordered List Items (- or * or •)
    text = text.replace(/^[\s]*[-*•]\s+(.*)$/gim, '<li>$1</li>');
    text = text.replace(/(<li>[\s\S]*?<\/li>(\s*<li>[\s\S]*?<\/li>)*)/gim, '<ul>$1</ul>');

    // Ordered List Items (1. item)
    text = text.replace(/^[\s]*\d+\.\s+(.*)$/gim, '<oli>$1</oli>');
    text = text.replace(/(<oli>[\s\S]*?<\/oli>(\s*<oli>[\s\S]*?<\/oli>)*)/gim, (m) => {
        return `<ol>${m.replace(/<\/?oli>/g, (t) => t === '<oli>' ? '<li>' : '</li>')}</ol>`;
    });

    // Clean block separation & paragraphs
    const blocks = text.split(/\n\s*\n/);
    const htmlBlocks = blocks.map(block => {
        block = block.trim();
        if (!block) return '';
        if (/^<(h[1-6]|ul|ol|pre|blockquote|table)/i.test(block)) {
            return block;
        }
        return `<p>${block.replace(/\n/g, '<br>')}</p>`;
    });

    return htmlBlocks.filter(Boolean).join('');
}

function appendMessage(sender, content, isMarkdown = false) {
    if (!chatFeed) return;
    const messageEl = document.createElement("div");
    messageEl.className = `message message-${sender}`;

    const contentEl = document.createElement("div");
    contentEl.className = "message-content";
    
    if (isMarkdown) {
        contentEl.innerHTML = renderMarkdown(content);
    } else {
        contentEl.innerHTML = typeof content === "string" ? `<p>${content}</p>` : content;
    }

    messageEl.appendChild(contentEl);
    chatFeed.appendChild(messageEl);
    chatFeed.scrollTop = chatFeed.scrollHeight;
}

// ==========================================================================
// 5. FILE SELECTION & DRAG-AND-DROP
// ==========================================================================

function formatBytes(bytes) {
    if (bytes === 0) return "0 Bytes";
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
}

function handleFileSelection(file) {
    if (!file) return;

    if (isCooldownActive()) {
        const cooldownUntil = parseInt(localStorage.getItem("rag_upload_cooldown_until") || "0", 10);
        const remSec = Math.ceil((cooldownUntil - Date.now()) / 1000);
        alert(`Upload is locked for rate-limit protection. Please wait ${remSec}s before uploading another document.`);
        return;
    }

    if (isUploading) {
        alert("An upload is already in progress. Please wait.");
        return;
    }

    const validExtensions = [".pdf", ".docx", ".txt"];
    const fileExt = "." + file.name.split(".").pop().toLowerCase();
    
    if (!validExtensions.includes(fileExt)) {
        alert("Invalid file type! Please choose a .pdf, .docx, or .txt document.");
        return;
    }

    selectedFile = file;
    console.log("📎 [File Selected]:", {
        name: file.name,
        size: formatBytes(file.size),
        type: file.type
    });

    fileName.textContent = file.name;
    fileSize.textContent = formatBytes(file.size);
    fileInfo.style.display = "flex";

    // Trigger Upload Process automatically upon file selection
    processAndUploadFile();
}

fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
        handleFileSelection(e.target.files[0]);
    }
});

["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        if (isCooldownActive() || isUploading) return;
        dropZone.style.borderColor = "#52525b";
        dropZone.style.backgroundColor = "#1f1f24";
    });
});

["dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropZone.style.borderColor = "";
        dropZone.style.backgroundColor = "";
    });
});

dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    if (isCooldownActive() || isUploading) {
        alert("Upload facility is currently locked.");
        return;
    }
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFileSelection(e.dataTransfer.files[0]);
    }
});

removeBtn.addEventListener("click", () => {
    if (isUploading) return;
    resetFileSelection();
});

function resetFileSelection() {
    selectedFile = null;
    fileInput.value = "";
    fileInfo.style.display = "none";
}

// ==========================================================================
// 6. UPLOAD ACTION & EXECUTION
// ==========================================================================

uploadBtn.addEventListener("click", () => {
    if (isCooldownActive()) {
        const cooldownUntil = parseInt(localStorage.getItem("rag_upload_cooldown_until") || "0", 10);
        const remSec = Math.ceil((cooldownUntil - Date.now()) / 1000);
        alert(`Upload facility is locked for rate limit. Please wait ${remSec}s.`);
        return;
    }

    if (isUploading) return;

    if (!selectedFile) {
        fileInput.click();
    } else {
        processAndUploadFile();
    }
});

async function processAndUploadFile() {
    if (!selectedFile || isCooldownActive() || isUploading) return;

    isUploading = true;
    const fileToUpload = selectedFile;
    const formData = new FormData();
    formData.append("file", fileToUpload);

    console.log(`🚀 [Uploading File]: Starting ingestion for "${fileToUpload.name}"...`);

    // Lock UI immediately during upload
    dropZone.classList.add("disabled");
    fileInput.disabled = true;
    uploadBtn.disabled = true;
    uploadBtn.textContent = "Processing & Ingesting...";
    uploadLoader.style.display = "flex";

    appendMessage("ai", `⏳ Uploading and indexing <strong>${fileToUpload.name}</strong> (${formatBytes(fileToUpload.size)})... Extracting text, chunking, and generating Gemini 1536d embeddings.`);

    try {
        const response = await fetch(`${API_BASE_URL}/uploadfile`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        console.log("📥 [API /uploadfile Response]:", data);

        uploadLoader.style.display = "none";
        isUploading = false;

        if (response.ok && data.status === "Success") {
            const timeInfo = data.time_taken ? ` in ${data.time_taken.toFixed(1)}s` : "";
            appendMessage("ai", `✅ <strong>${fileToUpload.name}</strong> has been successfully processed, chunked, and stored in PostgreSQL pgvector${timeInfo}! You can now ask questions about it in the chat.`);
            
            resetFileSelection();
            await loadUploadedFiles();

            // 🔒 LOCK UPLOAD FACILITY FOR 60 SECONDS
            startCooldownTimer(60);

        } else {
            const errorMsg = data.detail || (data.status === "UnSuccessful" ? "Document parsing failed." : "Upload failed on the server.");
            appendMessage("ai", `<span style="color: #ef4444;">❌ Upload failed: ${errorMsg}</span>`);
            resetFileSelection();
            
            // Apply 60-second cooldown even on error
            startCooldownTimer(60);
        }
    } catch (error) {
        uploadLoader.style.display = "none";
        isUploading = false;
        resetFileSelection();
        console.error("❌ [API /uploadfile Error]:", error);
        appendMessage("ai", `<span style="color: #ef4444;">❌ Connection error: Could not reach the backend server.</span>`);
        startCooldownTimer(30);
    }
}

// ==========================================================================
// 7. CHAT MESSAGING & RETRIEVAL (/query)
// ==========================================================================

chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;

    console.log(`💬 [User Query]: "${query}"`);

    appendMessage("user", query);
    chatInput.value = "";
    sendBtn.disabled = true;

    const typingId = "typing-" + Date.now();
    const typingEl = document.createElement("div");
    typingEl.className = "message message-ai";
    typingEl.id = typingId;
    typingEl.innerHTML = `<div class="message-content"><p style="color: #a1a1aa;"><em>Thinking & retrieving relevant context...</em></p></div>`;
    chatFeed.appendChild(typingEl);
    chatFeed.scrollTop = chatFeed.scrollHeight;

    try {
        const response = await fetch(`${API_BASE_URL}/query?query=${encodeURIComponent(query)}`, {
            method: "POST"
        });

        const data = await response.json();
        console.log("🤖 [API /query Response]:", data);

        document.getElementById(typingId)?.remove();

        if (response.ok && data.answer) {
            appendMessage("ai", data.answer, true);
        } else {
            const errorMsg = data.detail || "Unable to get an answer from the server.";
            appendMessage("ai", `<span style="color: #ef4444;">❌ Error: ${errorMsg}</span>`);
        }
    } catch (error) {
        console.error("❌ [API /query Error]:", error);
        document.getElementById(typingId)?.remove();
        appendMessage("ai", `<span style="color: #ef4444;">❌ Connection error: Could not reach the backend API server.</span>`);
    } finally {
        sendBtn.disabled = false;
        chatInput.focus();
    }
});

// ==========================================================================
// 8. INITIALIZATION ON PAGE LOAD
// ==========================================================================

document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 [App Initialized]: Ready.");
    
    // Initial checks
    checkBackendHealth();
    loadUploadedFiles();

    // 🔄 Periodic Backend Health Check every 10 seconds
    setInterval(checkBackendHealth, 10000);

    // 🔒 RESTORE ACTIVE COOLDOWN IF PAGE WAS REFRESHED
    if (isCooldownActive()) {
        applyCooldownUI();
    }
});
