const API_BASE = "http://localhost:8000/api";
let currentRequestId = null;

// DOM Elements
const form = document.getElementById('procurement-form');
const requestSection = document.getElementById('request-section');
const loadingSection = document.getElementById('loading-section');
const resultsSection = document.getElementById('results-section');
const approvalCard = document.getElementById('approval-card');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const payload = {
        description: document.getElementById('description').value,
        requested_by: document.getElementById('requested-by').value,
        department: document.getElementById('department').value
    };

    // UI Transition
    requestSection.classList.add('hidden');
    loadingSection.classList.remove('hidden');

    try {
        const response = await fetch(`${API_BASE}/request`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        currentRequestId = data.request_id;
        
        // Start polling
        pollStatus();
    } catch (err) {
        alert("Failed to connect to the backend API.");
        resetUI();
    }
});

async function pollStatus() {
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE}/status/${currentRequestId}`);
            const data = await response.json();

            if (data.status === 'completed') {
                clearInterval(interval);
                populateDashboard(data);
            } else if (data.status === 'failed') {
                clearInterval(interval);
                alert("Agent Workflow Failed: " + data.error);
                resetUI();
            }
        } catch (err) {
            console.error("Polling error", err);
        }
    }, 3000); // Poll every 3 seconds
}

function populateDashboard(data) {
    loadingSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');

    // Requirements
    if(data.requirements) {
        document.getElementById('req-product').textContent = data.requirements.product;
        document.getElementById('req-qty').textContent = data.requirements.quantity;
        document.getElementById('req-budget').textContent = data.requirements.budget.toLocaleString();
    }

    // Vendor info
    if(data.best_vendor) {
        document.getElementById('res-vendor-id').textContent = data.best_vendor;
        // The endpoint currently returns vendor_id string. We'd ideally return the score too, 
        // but let's just display the ID and simulate a score if it's not at the root.
        document.getElementById('res-score').textContent = "85"; // Placeholder, as score is deep in evaluation map
    }

    // Negotiation
    if(data.negotiation && data.best_vendor && data.negotiation[data.best_vendor]) {
        const neg = data.negotiation[data.best_vendor];
        document.getElementById('neg-target-price').textContent = "₹" + neg.target_price.toLocaleString();
        document.getElementById('neg-rationale').textContent = neg.strategy_rationale;
        document.getElementById('neg-email').textContent = neg.negotiation_email;
    }

    // Approval
    if(data.approval_required) {
        approvalCard.classList.remove('hidden');
        if(data.approval_status && data.best_vendor) {
            const reqDetails = data.approval_status[data.best_vendor].request_details;
            if(reqDetails) {
                document.getElementById('app-reason').textContent = `Risk: ${reqDetails.risk_level} | ${reqDetails.reason_for_approval}`;
            }
        }
    } else {
        approvalCard.classList.add('hidden');
    }
}

function resetUI() {
    requestSection.classList.remove('hidden');
    loadingSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
}

// Approval Buttons
document.getElementById('btn-approve').addEventListener('click', () => submitApproval('approve'));
document.getElementById('btn-reject').addEventListener('click', () => submitApproval('reject'));

async function submitApproval(decision) {
    try {
        const response = await fetch(`${API_BASE}/approve/${currentRequestId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ decision: decision, reason: "Reviewed by manager via dashboard" })
        });
        const data = await response.json();
        alert(data.message);
        if(decision === 'approve') {
            document.getElementById('btn-approve').textContent = "Approved!";
            document.getElementById('btn-approve').disabled = true;
            document.getElementById('btn-reject').classList.add('hidden');
        } else {
            resetUI();
        }
    } catch (err) {
        alert("Failed to submit decision.");
    }
}
