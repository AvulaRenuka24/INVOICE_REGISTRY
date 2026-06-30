// ======================================
// Helper Functions
// ======================================

function formatDate(dateString) {

    if (!dateString) return "-";

    return new Date(dateString).toLocaleDateString("en-GB");

}

function formatAmount(amount) {

    return amount ?? "-";

}

function showMessage(message, success = true) {

    const box = document.getElementById("uploadMessage");

    box.textContent = message;

    box.style.color = success ? "green" : "red";

}

// ======================================
// Statistics
// ======================================

async function loadStats() {

    const response = await fetch("/stats");

    const data = await response.json();

    document.getElementById("stats").innerHTML = `

        <div class="stat-card">
            <h3>Documents</h3>
            <p>${data.documents}</p>
        </div>

        <div class="stat-card">
            <h3>Invoices</h3>
            <p>${data.unique_invoices}</p>
        </div>

        <div class="stat-card">
            <h3>Processed</h3>
            <p>${data.processed_documents}</p>
        </div>

        <div class="stat-card">
            <h3>Failed</h3>
            <p>${data.failed_documents}</p>
        </div>

    `;

}

// ======================================
// Documents
// ======================================

async function loadDocuments() {

    const response = await fetch("/documents");

    const docs = await response.json();

    const tbody = document.querySelector("#documentsTable tbody");

    tbody.innerHTML = "";

    docs.forEach(doc => {

        tbody.innerHTML += `

        <tr>

            <td>${doc.id}</td>

            <td>${doc.filename}</td>

            <td>${doc.status}</td>

            <td>${formatDate(doc.uploaded_at)}</td>

        </tr>

        `;

    });

}

// ======================================
// Invoices
// ======================================

async function loadInvoices() {

    const response = await fetch("/invoices?limit=100");

    const data = await response.json();

    const tbody = document.querySelector("#invoiceTable tbody");

    tbody.innerHTML = "";

    data.results.forEach(inv => {

        tbody.innerHTML += `

        <tr>

            <td>${inv.id}</td>

            <td>${inv.invoice_number ?? "-"}</td>

            <td>${inv.vendor_name ?? "-"}</td>

            <td>${formatDate(inv.invoice_date)}</td>

            <td>${formatAmount(inv.total_amount)}</td>

        </tr>

        `;

    });

}
// ======================================
// Upload Invoice
// ======================================

document.getElementById("uploadBtn").onclick = async () => {

    const fileInput = document.getElementById("pdfFile");

    if (fileInput.files.length === 0) {

        alert("Please select a PDF.");

        return;

    }

    const formData = new FormData();

    formData.append("file", fileInput.files[0]);

    const response = await fetch("/upload", {

        method: "POST",

        body: formData

    });

    const result = await response.json();

    if (response.ok) {

        showMessage("Invoice uploaded successfully.");

    } else {

        if (result.detail && result.detail.message) {

            showMessage(result.detail.message, false);

        } else {

            showMessage("Upload failed.", false);

        }

    }

    await refreshDashboard();

};

// ======================================
// Duplicate Candidates
// ======================================

async function loadDuplicates() {

    const response = await fetch("/duplicates");

    const duplicates = await response.json();

    const tbody = document.querySelector("#duplicateTable tbody");

    tbody.innerHTML = "";

    if (duplicates.length === 0) {

        tbody.innerHTML = `

        <tr>

            <td colspan="5">

                No duplicate candidates found

            </td>

        </tr>

        `;

        return;

    }

    duplicates.slice(0, 20).forEach(item => {

        tbody.innerHTML += `

        <tr>

            <td>${item.id}</td>

            <td>${item.invoice1_id}</td>

            <td>${item.invoice2_id}</td>

            <td>${item.vendor_score}</td>

            <td>${item.status}</td>

        </tr>

        `;

    });

}
// ======================================
// Export CSV
// ======================================

document.getElementById("exportBtn").onclick = () => {

    window.location = "/export";

};

// ======================================
// Refresh Dashboard
// ======================================

async function refreshDashboard() {

    await loadStats();

    await loadDocuments();

    await loadInvoices();

    await loadDuplicates();

}

// ======================================
// Initialize Dashboard
// ======================================

window.onload = async () => {

    await refreshDashboard();

};

// ======================================
// Console
// ======================================

console.log("Invoice Registry Dashboard Loaded");