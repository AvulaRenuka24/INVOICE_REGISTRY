// ============================================
// Invoice Registry Dashboard
// script.js - Part 1
// ============================================


// ============================================
// Helper Functions
// ============================================

function formatDate(dateString) {

    if (!dateString) {

        return "-";

    }

    const date = new Date(dateString);

    return date.toLocaleDateString("en-GB");

}

function formatAmount(amount) {

    if (amount === null || amount === undefined) {

        return "-";

    }

    return amount;

}

function showMessage(message, success = true) {

    const box = document.getElementById("uploadMessage");

    box.innerHTML = message;

    box.style.color = success ? "#d63384" : "#dc3545";

}


// ============================================
// Statistics
// ============================================

async function loadStats() {

    const response = await fetch("/stats");

    const data = await response.json();

    document.getElementById("stats").innerHTML = `

        <div class="stat-card">
            <h3>📄 Documents</h3>
            <p>${data.documents}</p>
        </div>

        <div class="stat-card">
            <h3>🧾 Invoices</h3>
            <p>${data.unique_invoices}</p>
        </div>

        <div class="stat-card">
            <h3>✅ Processed</h3>
            <p>${data.processed_documents}</p>
        </div>

        <div class="stat-card">
            <h3>❌ Failed</h3>
            <p>${data.failed_documents}</p>
        </div>

        <div class="stat-card">
            <h3>📁 Duplicate Files</h3>
            <p>${data.duplicate_files_blocked}</p>
        </div>

        <div class="stat-card">
            <h3>🔁 Duplicate Invoices</h3>
            <p>${data.duplicate_invoices_caught}</p>
        </div>

    `;

}



// ============================================
// Documents Table
// ============================================

async function loadDocuments() {

    const response = await fetch("/documents");

    const documents = await response.json();

    const tbody = document.querySelector("#documentsTable tbody");

    tbody.innerHTML = "";

    documents.forEach(doc => {

        tbody.innerHTML += `

        <tr>

            <td>${doc.id}</td>

            <td>${doc.filename}</td>

            <td>${doc.status}</td>

            <td>${doc.doc_type}</td>

            <td>${formatDate(doc.uploaded_at)}</td>

        </tr>

        `;

    });

}



// ============================================
// Upload PDF
// ============================================

document.getElementById("uploadBtn").onclick = async () => {

    const fileInput = document.getElementById("pdfFile");

    if (fileInput.files.length === 0) {

        alert("Please select a PDF.");

        return;

    }

    const formData = new FormData();

    formData.append(

        "file",

        fileInput.files[0]

    );

    const response = await fetch(

        "/upload",

        {

            method: "POST",

            body: formData

        }

    );

    const result = await response.json();

    if (response.ok) {

        showMessage(

            "✅ Invoice uploaded successfully."

        );

    }

    else {

        if (result.detail.message) {

            showMessage(

                "❌ " + result.detail.message,

                false

            );

        }

        else {

            showMessage(

                "❌ Upload failed.",

                false

            );

        }

    }

    loadStats();

    loadDocuments();

    loadInvoices();

    loadDuplicates();

};

// ============================================
// Load Invoices
// ============================================

async function loadInvoices() {

    let url = "/invoices?limit=100";

    const vendor = document.getElementById("vendorSearch")?.value;

    const invoice = document.getElementById("searchText")?.value;

    const currency = document.getElementById("currency")?.value;

    const dateFrom = document.getElementById("dateFrom")?.value;

    const dateTo = document.getElementById("dateTo")?.value;

    const amountMin = document.getElementById("amountMin")?.value;

    const amountMax = document.getElementById("amountMax")?.value;

    if (vendor)
        url += "&vendor=" + encodeURIComponent(vendor);

    if (invoice)
        url += "&invoice_number=" + encodeURIComponent(invoice);

    if (currency)
        url += "&currency=" + currency;

    if (dateFrom)
        url += "&start_date=" + dateFrom;

    if (dateTo)
        url += "&end_date=" + dateTo;

    if (amountMin)
        url += "&min_amount=" + amountMin;

    if (amountMax)
        url += "&max_amount=" + amountMax;

    const response = await fetch(url);

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

            <td>${inv.currency ?? "-"}</td>

            <td>${inv.review_status}</td>

            <td>

                <button onclick="viewInvoice(${inv.id})">

                    View

                </button>

                <button onclick="deleteInvoice(${inv.id})">

                    Delete

                </button>

            </td>

        </tr>

        `;

    });

}



// ============================================
// View Invoice
// ============================================

async function viewInvoice(id) {

    const response = await fetch("/invoices/" + id);

    const invoice = await response.json();

    alert(

`Invoice ID : ${invoice.id}

Invoice Number : ${invoice.invoice_number}

Vendor : ${invoice.vendor_name}

Date : ${formatDate(invoice.invoice_date)}

Amount : ${formatAmount(invoice.total_amount)}

Currency : ${invoice.currency}

Status : ${invoice.review_status}`

    );

}



// ============================================
// Delete Invoice
// ============================================

async function deleteInvoice(id) {

    if (!confirm("Delete this invoice?")) {

        return;

    }

    await fetch(

        "/invoices/" + id,

        {

            method: "DELETE"

        }

    );

    loadInvoices();

    loadStats();

}



// ============================================
// Search Button
// ============================================

document.getElementById("searchBtn").onclick = () => {

    loadInvoices();

};



// ============================================
// Reset Filters
// ============================================

document.getElementById("resetBtn").onclick = () => {

    document.getElementById("searchText").value = "";

    document.getElementById("vendorSearch").value = "";

    document.getElementById("currency").value = "";

    document.getElementById("dateFrom").value = "";

    document.getElementById("dateTo").value = "";

    document.getElementById("amountMin").value = "";

    document.getElementById("amountMax").value = "";

    loadInvoices();

};
// ============================================
// Duplicate Candidates
// ============================================

async function loadDuplicates() {

    const response = await fetch("/duplicates");

    const duplicates = await response.json();

    const tbody = document.querySelector("#duplicateTable tbody");

    tbody.innerHTML = "";

    if (duplicates.length === 0) {

        tbody.innerHTML = `

        <tr>

            <td colspan="7">

                No duplicate candidates found.

            </td>

        </tr>

        `;

        return;

    }

    duplicates.forEach(candidate => {

        tbody.innerHTML += `

        <tr>

            <td>${candidate.id}</td>

            <td>${candidate.invoice1_id}</td>

            <td>${candidate.invoice2_id}</td>

            <td>${candidate.vendor_score}</td>

            <td>${candidate.invoice_score}</td>

            <td>${candidate.status}</td>

            <td>

                <button onclick="mergeDuplicate(${candidate.id})">

                    Merge

                </button>

                <button onclick="notDuplicate(${candidate.id})">

                    Not Duplicate

                </button>

            </td>

        </tr>

        `;

    });

}



// ============================================
// Merge Duplicate
// ============================================

async function mergeDuplicate(id) {

    if (!confirm("Merge these invoices?")) {

        return;

    }

    const response = await fetch(

        "/duplicates/" + id + "/resolve?action=merge",

        {

            method: "POST"

        }

    );

    const result = await response.json();

    alert(result.message);

    loadDuplicates();

    loadInvoices();

    loadStats();

}



// ============================================
// Mark Not Duplicate
// ============================================

async function notDuplicate(id) {

    const response = await fetch(

        "/duplicates/" + id + "/resolve?action=not_duplicate",

        {

            method: "POST"

        }

    );

    const result = await response.json();

    alert(result.message);

    loadDuplicates();

}



// ============================================
// Auto Refresh Duplicate Table
// ============================================

setInterval(() => {

    loadDuplicates();

}, 10000);

// ============================================
// Export CSV
// ============================================

document.getElementById("exportBtn").onclick = () => {

    let url = "/export?";

    const vendor = document.getElementById("vendorSearch").value;

    const currency = document.getElementById("currency").value;

    const dateFrom = document.getElementById("dateFrom").value;

    const dateTo = document.getElementById("dateTo").value;

    const amountMin = document.getElementById("amountMin").value;

    const amountMax = document.getElementById("amountMax").value;

    if (vendor)
        url += "&vendor=" + encodeURIComponent(vendor);

    if (currency)
        url += "&currency=" + currency;

    if (dateFrom)
        url += "&start_date=" + dateFrom;

    if (dateTo)
        url += "&end_date=" + dateTo;

    if (amountMin)
        url += "&min_amount=" + amountMin;

    if (amountMax)
        url += "&max_amount=" + amountMax;

    window.location = url;

};



// ============================================
// Refresh Dashboard
// ============================================

async function refreshDashboard() {

    await loadStats();

    await loadDocuments();

    await loadInvoices();

    await loadDuplicates();

}



// ============================================
// Initialize Dashboard
// ============================================

window.onload = async () => {

    await refreshDashboard();

};



// ============================================
// Auto Refresh Dashboard
// ============================================

setInterval(() => {

    refreshDashboard();

}, 30000);



// ============================================
// Console Message
// ============================================

console.log("Invoice Registry Dashboard Loaded Successfully");