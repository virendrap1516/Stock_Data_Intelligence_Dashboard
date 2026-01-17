// Stock Dashboard Frontend Application
const API_BASE = 'http://127.0.0.1:8000';

let chart = null;
let currentSymbol = null;
let companies = [];

// Initialize application
async function init() {
    await loadCompanies();
    setupEventListeners();
}

// Load list of companies from API
async function loadCompanies() {
    try {
        const response = await fetch(`${API_BASE}/companies`);
        if (!response.ok) throw new Error('Failed to fetch companies');
        
        const data = await response.json();
        companies = data.companies;
        
        const ul = document.getElementById('companyList');
        ul.innerHTML = '';
        
        if (companies.length === 0) {
            ul.innerHTML = '<li class="error">No companies found. Run data_prep.py first.</li>';
            return;
        }
        
        companies.forEach(symbol => {
            const li = document.createElement('li');
            li.textContent = symbol;
            li.onclick = () => selectCompany(symbol);
            ul.appendChild(li);
        });
        
        // Populate compare dropdowns
        populateCompareDropdowns();
        
        // Load first company by default
        if (companies.length > 0) {
            selectCompany(companies[0]);
        }
    } catch (error) {
        console.error('Error loading companies:', error);
        document.getElementById('companyList').innerHTML = 
            `<li class="error">Error: ${error.message}</li>`;
    }
}

// Populate compare dropdowns
function populateCompareDropdowns() {
    const select1 = document.getElementById('symbol1');
    const select2 = document.getElementById('symbol2');
    
    select1.innerHTML = '<option value="">Select...</option>';
    select2.innerHTML = '<option value="">Select...</option>';
    
    companies.forEach(symbol => {
        const opt1 = document.createElement('option');
        opt1.value = symbol;
        opt1.textContent = symbol;
        select1.appendChild(opt1);
        
        const opt2 = document.createElement('option');
        opt2.value = symbol;
        opt2.textContent = symbol;
        select2.appendChild(opt2);
    });
}

// Select a company and load its data
async function selectCompany(symbol) {
    currentSymbol = symbol;
    
    // Update active state
    document.querySelectorAll('#companyList li').forEach(li => {
        li.classList.remove('active');
        if (li.textContent === symbol) {
            li.classList.add('active');
        }
    });
    
    await loadStockData(symbol);
    await loadSummary(symbol);
}

// Load stock data for a symbol
async function loadStockData(symbol) {
    try {
        const response = await fetch(`${API_BASE}/data/${symbol}`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to fetch data');
        }
        
        const data = await response.json();
        const daysFilter = parseInt(document.getElementById('daysFilter').value);
        const recentData = data.data.slice(-daysFilter);
        
        renderChart(recentData, symbol);
    } catch (error) {
        console.error('Error loading stock data:', error);
        showError('Failed to load stock data: ' + error.message);
    }
}

// Load 52-week summary
async function loadSummary(symbol) {
    try {
        const response = await fetch(`${API_BASE}/summary/${symbol}`);
        if (!response.ok) throw new Error('Failed to fetch summary');
        
        const summary = await response.json();
        renderSummary(summary);
    } catch (error) {
        console.error('Error loading summary:', error);
        document.getElementById('summary-content').innerHTML = 
            `<p class="error">Failed to load summary: ${error.message}</p>`;
    }
}

// Render chart with Chart.js
function renderChart(data, symbol) {
    const ctx = document.getElementById('chart').getContext('2d');
    
    if (chart) {
        chart.destroy();
    }
    
    const labels = data.map(d => d.date);
    const closes = data.map(d => d.close);
    const ma7 = data.map(d => d.ma_7);
    
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: `${symbol} - Close Price`,
                    data: closes,
                    borderColor: 'rgb(102, 126, 234)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: `${symbol} - 7-Day MA`,
                    data: ma7,
                    borderColor: 'rgb(245, 158, 11)',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    tension: 0.4,
                    borderDash: [5, 5],
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Price (₹)'
                    }
                }
            }
        }
    });
}

// Render summary statistics
function renderSummary(summary) {
    const content = document.getElementById('summary-content');
    content.innerHTML = `
        <div class="stats">
            <div class="stat">
                <div class="stat-label">52-Week High</div>
                <div class="stat-value">₹${summary.high_52w.toFixed(2)}</div>
            </div>
            <div class="stat">
                <div class="stat-label">52-Week Low</div>
                <div class="stat-value">₹${summary.low_52w.toFixed(2)}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Average Close</div>
                <div class="stat-value">₹${summary.avg_close.toFixed(2)}</div>
            </div>
        </div>
    `;
}

// Compare two stocks
async function compareStocks() {
    console.log('Compare button clicked');
    
    const symbol1 = document.getElementById('symbol1').value;
    const symbol2 = document.getElementById('symbol2').value;
    
    console.log('Selected symbols:', { symbol1, symbol2 });
    
    if (!symbol1 || !symbol2) {
        const errorMsg = 'Please select both stocks to compare';
        console.error(errorMsg);
        alert(errorMsg);
        return;
    }
    
    if (symbol1 === symbol2) {
        const errorMsg = 'Please select two different stocks';
        console.error(errorMsg);
        alert(errorMsg);
        return;
    }
    
    try {
        const days = parseInt(document.getElementById('daysFilter').value) || 30;
        const url = `${API_BASE}/compare?symbol1=${symbol1}&symbol2=${symbol2}&days=${days}`;
        console.log('Fetching from:', url);
        
        const response = await fetch(url);
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            let errorDetail;
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail || 'No details provided';
                console.error('API Error:', errorData);
            } catch (e) {
                errorDetail = await response.text();
                console.error('Failed to parse error response:', errorDetail);
            }
            throw new Error(`API Error (${response.status}): ${errorDetail}`);
        }
        
        const data = await response.json();
        console.log('Received comparison data:', data);
        
        if (!data || !data.data || !Array.isArray(data.data)) {
            throw new Error('Invalid data format received from server');
        }
        
        renderCompareChart(data);
    } catch (error) {
        console.error('Error in compareStocks:', error);
        showError('Failed to compare stocks: ' + (error.message || 'Unknown error occurred'));
    }
}

// Render comparison chart
function renderCompareChart(data) {
    const ctx = document.getElementById('chart').getContext('2d');
    
    if (chart) {
        chart.destroy();
    }
    
    const labels = data.data.map(d => d.date);
    const norm1 = data.data.map(d => d[`${data.symbol1}_normalized`]);
    const norm2 = data.data.map(d => d[`${data.symbol2}_normalized`]);
    
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: `${data.symbol1} (Normalized)`,
                    data: norm1,
                    borderColor: 'rgb(34, 197, 94)',
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    tension: 0.4,
                    fill: false
                },
                {
                    label: `${data.symbol2} (Normalized)`,
                    data: norm2,
                    borderColor: 'rgb(239, 68, 68)',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Normalized Price (Base = 100)'
                    }
                }
            }
        }
    });
    
    // Update summary for comparison
    document.getElementById('summary-content').innerHTML = `
        <div class="stats">
            <div class="stat">
                <div class="stat-label">Comparing</div>
                <div class="stat-value">${data.symbol1} vs ${data.symbol2}</div>
            </div>
            <div class="stat">
                <div class="stat-label">Period</div>
                <div class="stat-value">${data.days} days</div>
            </div>
        </div>
    `;
}

// Setup event listeners
function setupEventListeners() {
    // Days filter change handler
    document.getElementById('daysFilter').addEventListener('change', () => {
        if (currentSymbol) {
            loadStockData(currentSymbol);
        }
    });
    
    // Toggle compare section visibility
    const compareBtn = document.getElementById('compareBtn');
    if (compareBtn) {
        compareBtn.addEventListener('click', () => {
            const compareSection = document.getElementById('compare-section');
            if (compareSection) {
                compareSection.style.display = compareSection.style.display === 'flex' ? 'none' : 'flex';
            }
        });
    }
    
    // Add click handler for the compare button
    const doCompareBtn = document.getElementById('doCompare');
    if (doCompareBtn) {
        doCompareBtn.addEventListener('click', compareStocks);
    } else {
        console.error('Compare button not found!');
    }
}

// Show error message
function showError(message) {
    const container = document.getElementById('chart-container');
    container.innerHTML = `<div class="error">${message}</div>`;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);

