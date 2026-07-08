/* ============================================
   SUPERMARKET SALES DASHBOARD - CORE APPLICATION
   ============================================ */

(function () {
    'use strict';

    // ======================== STATE ========================
    const state = {
        data: [],
        filteredData: [],
        currentPage: 1,
        rowsPerPage: 20,
        sortColumn: null,
        sortDirection: 'asc',
        activeTab: 'dashboard',
        charts: {},
        uploadedData: null,
        columns: [
            'Invoice ID', 'Branch', 'City', 'Customer type', 'Gender',
            'Product line', 'Unit price', 'Quantity', 'Tax 5%', 'Total',
            'Date', 'Time', 'Payment', 'cogs', 'gross margin percentage',
            'gross income', 'Rating'
        ],
        displayColumns: [
            'Invoice ID', 'Branch', 'City', 'Customer type', 'Gender',
            'Product line', 'Unit price', 'Quantity', 'Total',
            'Date', 'Payment', 'Rating'
        ],
        numericColumns: ['Unit price', 'Quantity', 'Tax 5%', 'Total', 'cogs',
            'gross margin percentage', 'gross income', 'Rating']
    };

    // Chart color palette
    const COLORS = {
        palette: [
            '#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a',
            '#ffecd2', '#a18cd1', '#fbc2eb', '#84fab0', '#8fd3f4'
        ],
        paletteBg: [
            'rgba(102,126,234,0.7)', 'rgba(240,147,251,0.7)', 'rgba(79,172,254,0.7)',
            'rgba(67,233,123,0.7)', 'rgba(250,112,154,0.7)', 'rgba(255,236,210,0.7)',
            'rgba(161,140,209,0.7)', 'rgba(251,194,235,0.7)', 'rgba(132,250,176,0.7)',
            'rgba(143,211,244,0.7)'
        ]
    };

    // ======================== DOM REFERENCES ========================
    const dom = {
        loadingScreen: document.getElementById('loading-screen'),
        pageTitle: document.getElementById('page-title'),
        globalSearch: document.getElementById('global-search'),
        dataCount: document.querySelector('.count-number'),
        menuToggle: document.getElementById('menu-toggle'),
        sidebar: document.getElementById('sidebar'),
        // KPI
        kpiRevenue: document.getElementById('kpi-revenue'),
        kpiOrders: document.getElementById('kpi-orders'),
        kpiRating: document.getElementById('kpi-rating'),
        kpiIncome: document.getElementById('kpi-income'),
        // Table
        tableHeader: document.getElementById('table-header'),
        tableBody: document.getElementById('table-body'),
        tableShowing: document.getElementById('table-showing'),
        pagination: document.getElementById('pagination'),
        // Filters
        filterBranch: document.getElementById('filter-branch'),
        filterProduct: document.getElementById('filter-product'),
        filterGender: document.getElementById('filter-gender'),
        filterCustomer: document.getElementById('filter-customer'),
        filterPayment: document.getElementById('filter-payment'),
        filterSearch: document.getElementById('filter-search'),
        btnResetFilters: document.getElementById('btn-reset-filters'),
        // Upload
        uploadArea: document.getElementById('upload-area'),
        fileInput: document.getElementById('file-input'),
        btnBrowse: document.getElementById('btn-browse'),
        uploadPreview: document.getElementById('upload-preview'),
        previewFilename: document.getElementById('preview-filename'),
        previewFilesize: document.getElementById('preview-filesize'),
        previewCount: document.getElementById('preview-count'),
        previewHeader: document.getElementById('preview-header'),
        previewBody: document.getElementById('preview-body'),
        btnCancelUpload: document.getElementById('btn-cancel-upload'),
        btnMergeData: document.getElementById('btn-merge-data'),
        uploadResult: document.getElementById('upload-result'),
        resultMessage: document.getElementById('result-message'),
        resultDetail: document.getElementById('result-detail'),
        btnUploadMore: document.getElementById('btn-upload-more'),
        // Statistics
        statsGroupBy: document.getElementById('stats-group-by'),
        statsSummary: document.getElementById('stats-summary'),
        statsChartTitle: document.getElementById('stats-chart-title'),
        statsTableHeader: document.getElementById('stats-table-header'),
        statsTableBody: document.getElementById('stats-table-body'),
        // Modal
        detailModal: document.getElementById('detail-modal'),
        modalClose: document.getElementById('modal-close'),
        modalInvoice: document.getElementById('modal-invoice'),
        modalBody: document.getElementById('modal-body'),
        // Toast
        toastContainer: document.getElementById('toast-container')
    };

    // ======================== INITIALIZATION ========================
    async function init() {
        try {
            await loadCSV('data/supermarket_sales.csv');
            setupEventListeners();
            populateProductFilter();
            updateDashboard();
            renderTable();
            updateStatistics();
            dom.loadingScreen.classList.add('hidden');
        } catch (err) {
            console.error('Init error:', err);
            dom.loadingScreen.innerHTML = `
                <div class="loader">
                    <p style="color:#fa709a">Lỗi tải dữ liệu: ${err.message}</p>
                    <p style="color:#9999b3;margin-top:8px">Vui lòng đảm bảo file data/supermarket_sales.csv tồn tại</p>
                </div>`;
        }
    }

    // ======================== DATA LOADING ========================
    function loadCSV(url) {
        return new Promise((resolve, reject) => {
            Papa.parse(url, {
                download: true,
                header: true,
                skipEmptyLines: true,
                dynamicTyping: false,
                complete: function (results) {
                    if (results.errors.length > 0) {
                        console.warn('CSV parse warnings:', results.errors);
                    }
                    state.data = results.data.map(normalizeRow);
                    state.filteredData = [...state.data];
                    dom.dataCount.textContent = state.data.length;
                    resolve();
                },
                error: function (err) {
                    reject(err);
                }
            });
        });
    }

    function normalizeRow(row) {
        const normalized = {};
        for (const key of state.columns) {
            let val = row[key] !== undefined ? String(row[key]).trim() : '';
            if (state.numericColumns.includes(key)) {
                normalized[key] = parseFloat(val) || 0;
            } else {
                normalized[key] = val;
            }
        }
        return normalized;
    }

    // ======================== EVENT LISTENERS ========================
    function setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', () => switchTab(btn.dataset.tab));
        });

        // Mobile menu
        dom.menuToggle.addEventListener('click', () => {
            dom.sidebar.classList.toggle('open');
        });

        // Close sidebar on mobile when clicking outside
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768 &&
                !dom.sidebar.contains(e.target) &&
                !dom.menuToggle.contains(e.target)) {
                dom.sidebar.classList.remove('open');
            }
        });

        // Global search
        dom.globalSearch.addEventListener('input', debounce(() => {
            if (state.activeTab !== 'data') {
                switchTab('data');
            }
            dom.filterSearch.value = dom.globalSearch.value;
            applyFilters();
        }, 300));

        // Filters
        [dom.filterBranch, dom.filterProduct, dom.filterGender,
            dom.filterCustomer, dom.filterPayment].forEach(el => {
                el.addEventListener('change', () => {
                    state.currentPage = 1;
                    applyFilters();
                });
            });

        dom.filterSearch.addEventListener('input', debounce(() => {
            state.currentPage = 1;
            applyFilters();
        }, 300));

        dom.btnResetFilters.addEventListener('click', resetFilters);

        // Upload
        dom.uploadArea.addEventListener('click', () => dom.fileInput.click());
        dom.btnBrowse.addEventListener('click', (e) => {
            e.stopPropagation();
            dom.fileInput.click();
        });
        dom.fileInput.addEventListener('change', handleFileSelect);

        dom.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            dom.uploadArea.classList.add('drag-over');
        });
        dom.uploadArea.addEventListener('dragleave', () => {
            dom.uploadArea.classList.remove('drag-over');
        });
        dom.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            dom.uploadArea.classList.remove('drag-over');
            if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
        });

        dom.btnCancelUpload.addEventListener('click', cancelUpload);
        dom.btnMergeData.addEventListener('click', mergeData);
        dom.btnUploadMore.addEventListener('click', resetUpload);

        // Statistics
        dom.statsGroupBy.addEventListener('change', updateStatistics);

        // Modal
        dom.modalClose.addEventListener('click', closeModal);
        dom.detailModal.addEventListener('click', (e) => {
            if (e.target === dom.detailModal) closeModal();
        });
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeModal();
        });
    }

    // ======================== TAB NAVIGATION ========================
    function switchTab(tab) {
        state.activeTab = tab;

        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelector(`.nav-btn[data-tab="${tab}"]`).classList.add('active');

        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.getElementById(`tab-${tab}`).classList.add('active');

        const titles = {
            dashboard: 'Dashboard',
            data: 'Dữ liệu',
            upload: 'Upload dữ liệu',
            statistics: 'Thống kê'
        };
        dom.pageTitle.textContent = titles[tab] || 'Dashboard';

        // Close mobile sidebar
        dom.sidebar.classList.remove('open');

        // Re-render charts when switching to stats tab to fix canvas sizing
        if (tab === 'statistics') {
            setTimeout(() => updateStatistics(), 100);
        }
    }

    // ======================== DASHBOARD ========================
    function updateDashboard() {
        updateKPIs();
        renderDashboardCharts();
    }

    function updateKPIs() {
        const data = state.data;
        const totalRevenue = data.reduce((sum, r) => sum + r['Total'], 0);
        const totalOrders = data.length;
        const avgRating = data.reduce((sum, r) => sum + r['Rating'], 0) / data.length;
        const totalIncome = data.reduce((sum, r) => sum + r['gross income'], 0);

        animateNumber(dom.kpiRevenue, totalRevenue, '$', true);
        animateNumber(dom.kpiOrders, totalOrders, '', false);
        dom.kpiRating.textContent = avgRating.toFixed(1) + ' ⭐';
        animateNumber(dom.kpiIncome, totalIncome, '$', true);
    }

    function animateNumber(el, target, prefix, isDecimal) {
        const duration = 1200;
        const start = performance.now();
        const startVal = 0;

        function update(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
            const current = startVal + (target - startVal) * eased;

            if (isDecimal) {
                el.textContent = prefix + formatNumber(current);
            } else {
                el.textContent = prefix + Math.round(current).toLocaleString();
            }

            if (progress < 1) requestAnimationFrame(update);
        }
        requestAnimationFrame(update);
    }

    function formatNumber(n) {
        if (n >= 1000000) return (n / 1000000).toFixed(2) + 'M';
        if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
        return n.toFixed(2);
    }

    // ======================== CHARTS ========================
    function renderDashboardCharts() {
        renderRevenueTrendChart();
        renderBranchChart();
        renderProductLineChart();
        renderPaymentChart();
        renderGenderCustomerChart();
    }

    function getChartDefaults() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#9999b3',
                        font: { family: 'Inter', size: 11 },
                        padding: 16,
                        usePointStyle: true,
                        pointStyleWidth: 10
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(26,26,46,0.95)',
                    titleColor: '#e8e8f0',
                    bodyColor: '#9999b3',
                    borderColor: 'rgba(102,126,234,0.3)',
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 8,
                    titleFont: { family: 'Inter', weight: 600 },
                    bodyFont: { family: 'Inter' },
                    displayColors: true,
                    boxPadding: 4
                }
            }
        };
    }

    function createOrUpdateChart(id, config) {
        if (state.charts[id]) {
            state.charts[id].destroy();
        }
        const ctx = document.getElementById(id).getContext('2d');
        state.charts[id] = new Chart(ctx, config);
    }

    function renderRevenueTrendChart() {
        // Group by month
        const monthlyData = {};
        state.data.forEach(row => {
            const parts = row['Date'].split('/');
            const month = parts[0]; // M/D/YYYY
            const year = parts[2];
            const key = `${year}-${month.padStart(2, '0')}`;
            if (!monthlyData[key]) monthlyData[key] = { revenue: 0, count: 0 };
            monthlyData[key].revenue += row['Total'];
            monthlyData[key].count++;
        });

        const sortedKeys = Object.keys(monthlyData).sort();
        const monthNames = { '01': 'Tháng 1', '02': 'Tháng 2', '03': 'Tháng 3', '04': 'Tháng 4', '05': 'Tháng 5', '06': 'Tháng 6', '07': 'Tháng 7', '08': 'Tháng 8', '09': 'Tháng 9', '10': 'Tháng 10', '11': 'Tháng 11', '12': 'Tháng 12' };

        const labels = sortedKeys.map(k => monthNames[k.split('-')[1]] || k);
        const revenues = sortedKeys.map(k => monthlyData[k].revenue);
        const orders = sortedKeys.map(k => monthlyData[k].count);

        const defaults = getChartDefaults();
        createOrUpdateChart('chart-revenue-trend', {
            type: 'line',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Doanh thu ($)',
                        data: revenues,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102,126,234,0.1)',
                        fill: true,
                        tension: 0.4,
                        borderWidth: 3,
                        pointRadius: 6,
                        pointHoverRadius: 9,
                        pointBackgroundColor: '#667eea',
                        pointBorderColor: '#0f0f1a',
                        pointBorderWidth: 2,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Số đơn hàng',
                        data: orders,
                        borderColor: '#f093fb',
                        backgroundColor: 'rgba(240,147,251,0.1)',
                        fill: true,
                        tension: 0.4,
                        borderWidth: 2,
                        borderDash: [5, 5],
                        pointRadius: 4,
                        pointHoverRadius: 7,
                        pointBackgroundColor: '#f093fb',
                        pointBorderColor: '#0f0f1a',
                        pointBorderWidth: 2,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                ...defaults,
                interaction: { intersect: false, mode: 'index' },
                scales: {
                    x: {
                        grid: { color: 'rgba(255,255,255,0.04)' },
                        ticks: { color: '#66668a', font: { family: 'Inter' } }
                    },
                    y: {
                        position: 'left',
                        grid: { color: 'rgba(255,255,255,0.04)' },
                        ticks: {
                            color: '#667eea',
                            font: { family: 'Inter' },
                            callback: v => '$' + (v / 1000).toFixed(0) + 'K'
                        }
                    },
                    y1: {
                        position: 'right',
                        grid: { display: false },
                        ticks: { color: '#f093fb', font: { family: 'Inter' } }
                    }
                }
            }
        });
    }

    function renderBranchChart() {
        const branchData = groupBy(state.data, 'Branch');
        const labels = Object.keys(branchData).sort();
        const revenues = labels.map(b => branchData[b].reduce((s, r) => s + r['Total'], 0));
        const incomes = labels.map(b => branchData[b].reduce((s, r) => s + r['gross income'], 0));
        const cityMap = { 'A': 'Yangon', 'B': 'Mandalay', 'C': 'Naypyitaw' };
        const displayLabels = labels.map(b => `${b} - ${cityMap[b] || b}`);

        const defaults = getChartDefaults();
        createOrUpdateChart('chart-branch', {
            type: 'bar',
            data: {
                labels: displayLabels,
                datasets: [
                    {
                        label: 'Doanh thu',
                        data: revenues,
                        backgroundColor: ['rgba(102,126,234,0.7)', 'rgba(240,147,251,0.7)', 'rgba(79,172,254,0.7)'],
                        borderColor: ['#667eea', '#f093fb', '#4facfe'],
                        borderWidth: 2,
                        borderRadius: 8,
                        borderSkipped: false
                    },
                    {
                        label: 'Lợi nhuận',
                        data: incomes,
                        backgroundColor: ['rgba(102,126,234,0.3)', 'rgba(240,147,251,0.3)', 'rgba(79,172,254,0.3)'],
                        borderColor: ['#667eea', '#f093fb', '#4facfe'],
                        borderWidth: 1,
                        borderRadius: 8,
                        borderSkipped: false
                    }
                ]
            },
            options: {
                ...defaults,
                scales: {
                    x: {
                        grid: { color: 'rgba(255,255,255,0.04)' },
                        ticks: { color: '#66668a', font: { family: 'Inter' } }
                    },
                    y: {
                        grid: { color: 'rgba(255,255,255,0.04)' },
                        ticks: {
                            color: '#66668a',
                            font: { family: 'Inter' },
                            callback: v => '$' + (v / 1000).toFixed(0) + 'K'
                        }
                    }
                }
            }
        });
    }

    function renderProductLineChart() {
        const prodData = groupBy(state.data, 'Product line');
        const labels = Object.keys(prodData).sort();
        const values = labels.map(p => prodData[p].reduce((s, r) => s + r['Total'], 0));

        const defaults = getChartDefaults();
        createOrUpdateChart('chart-product-line', {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data: values,
                    backgroundColor: COLORS.paletteBg.slice(0, labels.length),
                    borderColor: COLORS.palette.slice(0, labels.length),
                    borderWidth: 2,
                    hoverOffset: 8
                }]
            },
            options: {
                ...defaults,
                cutout: '60%',
                plugins: {
                    ...defaults.plugins,
                    legend: {
                        ...defaults.plugins.legend,
                        position: 'bottom'
                    }
                }
            }
        });
    }

    function renderPaymentChart() {
        const payData = groupBy(state.data, 'Payment');
        const labels = Object.keys(payData).sort();
        const values = labels.map(p => payData[p].length);

        const defaults = getChartDefaults();
        createOrUpdateChart('chart-payment', {
            type: 'polarArea',
            data: {
                labels,
                datasets: [{
                    data: values,
                    backgroundColor: ['rgba(102,126,234,0.6)', 'rgba(67,233,123,0.6)', 'rgba(250,112,154,0.6)'],
                    borderColor: ['#667eea', '#43e97b', '#fa709a'],
                    borderWidth: 2
                }]
            },
            options: {
                ...defaults,
                plugins: {
                    ...defaults.plugins,
                    legend: {
                        ...defaults.plugins.legend,
                        position: 'bottom'
                    }
                },
                scales: {
                    r: {
                        grid: { color: 'rgba(255,255,255,0.06)' },
                        ticks: { display: false }
                    }
                }
            }
        });
    }

    function renderGenderCustomerChart() {
        const data = state.data;
        const categories = ['Member-Male', 'Member-Female', 'Normal-Male', 'Normal-Female'];
        const values = categories.map(c => {
            const [ctype, gender] = c.split('-');
            return data.filter(r => r['Customer type'] === ctype && r['Gender'] === gender)
                .reduce((s, r) => s + r['Total'], 0);
        });
        const displayLabels = ['Thành viên - Nam', 'Thành viên - Nữ', 'Thường - Nam', 'Thường - Nữ'];

        const defaults = getChartDefaults();
        createOrUpdateChart('chart-gender-customer', {
            type: 'bar',
            data: {
                labels: displayLabels,
                datasets: [{
                    label: 'Doanh thu',
                    data: values,
                    backgroundColor: [
                        'rgba(79,172,254,0.7)', 'rgba(240,147,251,0.7)',
                        'rgba(79,172,254,0.4)', 'rgba(240,147,251,0.4)'
                    ],
                    borderColor: ['#4facfe', '#f093fb', '#4facfe', '#f093fb'],
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                ...defaults,
                indexAxis: 'y',
                plugins: {
                    ...defaults.plugins,
                    legend: { display: false }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255,255,255,0.04)' },
                        ticks: {
                            color: '#66668a',
                            font: { family: 'Inter', size: 10 },
                            callback: v => '$' + (v / 1000).toFixed(0) + 'K'
                        }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: '#9999b3', font: { family: 'Inter', size: 10 } }
                    }
                }
            }
        });
    }

    // ======================== DATA TABLE ========================
    function renderTable() {
        renderTableHeader();
        renderTableBody();
        renderPagination();
        updateTableInfo();
    }

    function renderTableHeader() {
        dom.tableHeader.innerHTML = state.displayColumns.map(col => {
            let cls = '';
            if (state.sortColumn === col) {
                cls = state.sortDirection === 'asc' ? 'sorted-asc' : 'sorted-desc';
            }
            return `<th class="${cls}" data-col="${col}">${col}</th>`;
        }).join('');

        dom.tableHeader.querySelectorAll('th').forEach(th => {
            th.addEventListener('click', () => {
                const col = th.dataset.col;
                if (state.sortColumn === col) {
                    state.sortDirection = state.sortDirection === 'asc' ? 'desc' : 'asc';
                } else {
                    state.sortColumn = col;
                    state.sortDirection = 'asc';
                }
                sortData();
                renderTable();
            });
        });
    }

    function renderTableBody() {
        const start = (state.currentPage - 1) * state.rowsPerPage;
        const end = start + state.rowsPerPage;
        const pageData = state.filteredData.slice(start, end);

        if (pageData.length === 0) {
            dom.tableBody.innerHTML = `
                <tr><td colspan="${state.displayColumns.length}" style="text-align:center;padding:48px;color:#66668a;">
                    Không tìm thấy dữ liệu phù hợp
                </td></tr>`;
            return;
        }

        dom.tableBody.innerHTML = pageData.map((row, idx) => {
            const cells = state.displayColumns.map(col => {
                const val = row[col];
                return `<td>${formatCell(col, val)}</td>`;
            }).join('');
            return `<tr data-index="${start + idx}">${cells}</tr>`;
        }).join('');

        // Row click for detail
        dom.tableBody.querySelectorAll('tr[data-index]').forEach(tr => {
            tr.addEventListener('click', () => {
                const idx = parseInt(tr.dataset.index);
                showDetailModal(state.filteredData[idx]);
            });
        });
    }

    function formatCell(col, val) {
        switch (col) {
            case 'Branch':
                const branchClass = { A: 'badge-branch-a', B: 'badge-branch-b', C: 'badge-branch-c' };
                return `<span class="badge ${branchClass[val] || ''}">${val}</span>`;
            case 'Customer type':
                return `<span class="badge ${val === 'Member' ? 'badge-member' : 'badge-normal'}">${val === 'Member' ? 'Thành viên' : 'Thường'}</span>`;
            case 'Gender':
                return `<span class="badge ${val === 'Male' ? 'badge-male' : 'badge-female'}">${val === 'Male' ? 'Nam' : 'Nữ'}</span>`;
            case 'Payment':
                const payClass = { Ewallet: 'badge-ewallet', Cash: 'badge-cash', 'Credit card': 'badge-credit' };
                return `<span class="badge ${payClass[val] || ''}">${val}</span>`;
            case 'Unit price':
            case 'Total':
            case 'cogs':
            case 'gross income':
            case 'Tax 5%':
                return '$' + Number(val).toFixed(2);
            case 'Rating':
                return `${val} ⭐`;
            default:
                return val;
        }
    }

    function renderPagination() {
        const totalPages = Math.ceil(state.filteredData.length / state.rowsPerPage) || 1;
        let html = '';

        html += `<button ${state.currentPage === 1 ? 'disabled' : ''} data-page="${state.currentPage - 1}">‹</button>`;

        const maxVisible = 7;
        let startPage = Math.max(1, state.currentPage - Math.floor(maxVisible / 2));
        let endPage = Math.min(totalPages, startPage + maxVisible - 1);
        if (endPage - startPage < maxVisible - 1) {
            startPage = Math.max(1, endPage - maxVisible + 1);
        }

        if (startPage > 1) {
            html += `<button data-page="1">1</button>`;
            if (startPage > 2) html += `<button disabled>…</button>`;
        }

        for (let i = startPage; i <= endPage; i++) {
            html += `<button class="${i === state.currentPage ? 'active' : ''}" data-page="${i}">${i}</button>`;
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) html += `<button disabled>…</button>`;
            html += `<button data-page="${totalPages}">${totalPages}</button>`;
        }

        html += `<button ${state.currentPage === totalPages ? 'disabled' : ''} data-page="${state.currentPage + 1}">›</button>`;

        dom.pagination.innerHTML = html;

        dom.pagination.querySelectorAll('button[data-page]').forEach(btn => {
            btn.addEventListener('click', () => {
                state.currentPage = parseInt(btn.dataset.page);
                renderTableBody();
                renderPagination();
                updateTableInfo();
                // Scroll to top of table
                document.querySelector('.table-wrapper').scrollTop = 0;
            });
        });
    }

    function updateTableInfo() {
        const total = state.filteredData.length;
        const start = total === 0 ? 0 : (state.currentPage - 1) * state.rowsPerPage + 1;
        const end = Math.min(state.currentPage * state.rowsPerPage, total);
        dom.tableShowing.textContent = `Hiển thị ${start}-${end} / ${total} kết quả (tổng: ${state.data.length})`;
    }

    // ======================== FILTERING & SORTING ========================
    function applyFilters() {
        const branch = dom.filterBranch.value;
        const product = dom.filterProduct.value;
        const gender = dom.filterGender.value;
        const customer = dom.filterCustomer.value;
        const payment = dom.filterPayment.value;
        const search = dom.filterSearch.value.toLowerCase().trim();

        state.filteredData = state.data.filter(row => {
            if (branch && row['Branch'] !== branch) return false;
            if (product && row['Product line'] !== product) return false;
            if (gender && row['Gender'] !== gender) return false;
            if (customer && row['Customer type'] !== customer) return false;
            if (payment && row['Payment'] !== payment) return false;
            if (search) {
                const searchable = Object.values(row).join(' ').toLowerCase();
                if (!searchable.includes(search)) return false;
            }
            return true;
        });

        if (state.sortColumn) sortData();
        state.currentPage = 1;
        renderTable();
    }

    function resetFilters() {
        dom.filterBranch.value = '';
        dom.filterProduct.value = '';
        dom.filterGender.value = '';
        dom.filterCustomer.value = '';
        dom.filterPayment.value = '';
        dom.filterSearch.value = '';
        dom.globalSearch.value = '';
        state.filteredData = [...state.data];
        state.sortColumn = null;
        state.sortDirection = 'asc';
        state.currentPage = 1;
        renderTable();
        showToast('Đã reset tất cả bộ lọc', 'info');
    }

    function sortData() {
        const col = state.sortColumn;
        const dir = state.sortDirection === 'asc' ? 1 : -1;
        const isNumeric = state.numericColumns.includes(col);

        state.filteredData.sort((a, b) => {
            let va = a[col];
            let vb = b[col];
            if (isNumeric) {
                return (va - vb) * dir;
            }
            return String(va).localeCompare(String(vb)) * dir;
        });
    }

    function populateProductFilter() {
        const products = [...new Set(state.data.map(r => r['Product line']))].sort();
        products.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p;
            opt.textContent = p;
            dom.filterProduct.appendChild(opt);
        });
    }

    // ======================== FILE UPLOAD ========================
    function handleFileSelect(e) {
        if (e.target.files.length) handleFile(e.target.files[0]);
    }

    function handleFile(file) {
        if (!file.name.endsWith('.csv')) {
            showToast('Vui lòng chọn file CSV', 'info');
            return;
        }

        Papa.parse(file, {
            header: true,
            skipEmptyLines: true,
            complete: function (results) {
                state.uploadedData = results.data.map(normalizeRow);
                showUploadPreview(file, state.uploadedData);
            },
            error: function () {
                showToast('Lỗi đọc file CSV', 'info');
            }
        });
    }

    function showUploadPreview(file, data) {
        dom.uploadArea.style.display = 'none';
        dom.uploadResult.classList.add('hidden');
        dom.uploadPreview.classList.remove('hidden');

        dom.previewFilename.textContent = file.name;
        dom.previewFilesize.textContent = formatFileSize(file.size);
        dom.previewCount.textContent = `${data.length} dòng dữ liệu`;

        // Render preview table (first 10 rows)
        const previewCols = state.displayColumns;
        dom.previewHeader.innerHTML = previewCols.map(c => `<th>${c}</th>`).join('');
        dom.previewBody.innerHTML = data.slice(0, 10).map(row => {
            return '<tr>' + previewCols.map(c => `<td>${formatCell(c, row[c])}</td>`).join('') + '</tr>';
        }).join('');

        if (data.length > 10) {
            dom.previewBody.innerHTML += `<tr><td colspan="${previewCols.length}" style="text-align:center;color:#66668a;padding:12px;">... và ${data.length - 10} dòng nữa</td></tr>`;
        }
    }

    function cancelUpload() {
        state.uploadedData = null;
        dom.uploadPreview.classList.add('hidden');
        dom.uploadArea.style.display = '';
        dom.fileInput.value = '';
    }

    function mergeData() {
        if (!state.uploadedData || state.uploadedData.length === 0) return;

        const count = state.uploadedData.length;
        state.data = [...state.data, ...state.uploadedData];
        state.filteredData = [...state.data];
        dom.dataCount.textContent = state.data.length;

        // Reset sort and filters
        state.sortColumn = null;
        state.sortDirection = 'asc';
        state.currentPage = 1;

        // Update everything
        updateDashboard();
        renderTable();
        populateProductFilterFresh();
        updateStatistics();

        // Show result
        dom.uploadPreview.classList.add('hidden');
        dom.uploadResult.classList.remove('hidden');
        dom.resultMessage.textContent = 'Đã thêm thành công!';
        dom.resultDetail.textContent = `${count} dòng dữ liệu đã được thêm vào. Tổng: ${state.data.length} records.`;

        state.uploadedData = null;
        dom.fileInput.value = '';

        showToast(`Đã thêm ${count} records thành công!`, 'success');
    }

    function resetUpload() {
        dom.uploadResult.classList.add('hidden');
        dom.uploadPreview.classList.add('hidden');
        dom.uploadArea.style.display = '';
        dom.fileInput.value = '';
    }

    function populateProductFilterFresh() {
        // Clear and repopulate
        dom.filterProduct.innerHTML = '<option value="">Tất cả</option>';
        const products = [...new Set(state.data.map(r => r['Product line']))].sort();
        products.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p;
            opt.textContent = p;
            dom.filterProduct.appendChild(opt);
        });
    }

    // ======================== STATISTICS ========================
    function updateStatistics() {
        const groupByField = dom.statsGroupBy.value;
        const groups = groupBy(state.data, groupByField);
        const labels = Object.keys(groups).sort();

        // Summary cards
        const gradients = [
            'var(--gradient-main)', 'var(--gradient-warm)', 'var(--gradient-cool)',
            'var(--gradient-green)', 'linear-gradient(135deg, #a18cd1, #fbc2eb)',
            'linear-gradient(135deg, #ffecd2, #fcb69f)'
        ];

        dom.statsSummary.innerHTML = labels.map((label, i) => {
            const rows = groups[label];
            const revenue = rows.reduce((s, r) => s + r['Total'], 0);
            const count = rows.length;
            return `
                <div class="stat-card" style="--card-accent: ${gradients[i % gradients.length]}">
                    <div class="stat-card-label">${label}</div>
                    <div class="stat-card-value">$${formatNumber(revenue)}</div>
                    <div class="stat-card-sub">${count} đơn hàng</div>
                </div>`;
        }).join('');

        // Stats chart
        dom.statsChartTitle.textContent = `Doanh thu theo ${dom.statsGroupBy.options[dom.statsGroupBy.selectedIndex].text}`;

        const revenues = labels.map(l => groups[l].reduce((s, r) => s + r['Total'], 0));
        const avgRatings = labels.map(l => {
            const rows = groups[l];
            return rows.reduce((s, r) => s + r['Rating'], 0) / rows.length;
        });

        const defaults = getChartDefaults();
        createOrUpdateChart('chart-stats', {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Doanh thu ($)',
                        data: revenues,
                        backgroundColor: labels.map((_, i) => COLORS.paletteBg[i % COLORS.paletteBg.length]),
                        borderColor: labels.map((_, i) => COLORS.palette[i % COLORS.palette.length]),
                        borderWidth: 2,
                        borderRadius: 8,
                        borderSkipped: false,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Rating TB',
                        data: avgRatings,
                        type: 'line',
                        borderColor: '#fa709a',
                        backgroundColor: 'rgba(250,112,154,0.1)',
                        borderWidth: 3,
                        pointRadius: 5,
                        pointHoverRadius: 8,
                        pointBackgroundColor: '#fa709a',
                        pointBorderColor: '#0f0f1a',
                        pointBorderWidth: 2,
                        tension: 0.4,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                ...defaults,
                scales: {
                    x: {
                        grid: { color: 'rgba(255,255,255,0.04)' },
                        ticks: { color: '#9999b3', font: { family: 'Inter', size: 10 }, maxRotation: 45 }
                    },
                    y: {
                        position: 'left',
                        grid: { color: 'rgba(255,255,255,0.04)' },
                        ticks: {
                            color: '#667eea',
                            font: { family: 'Inter' },
                            callback: v => '$' + (v / 1000).toFixed(0) + 'K'
                        }
                    },
                    y1: {
                        position: 'right',
                        min: 0,
                        max: 10,
                        grid: { display: false },
                        ticks: { color: '#fa709a', font: { family: 'Inter' } }
                    }
                }
            }
        });

        // Stats table
        renderStatsTable(groups, labels);
    }

    function renderStatsTable(groups, labels) {
        dom.statsTableHeader.innerHTML = `
            <th>Nhóm</th>
            <th>Số đơn</th>
            <th>Doanh thu</th>
            <th>Lợi nhuận</th>
            <th>TB Đơn giá</th>
            <th>TB Số lượng</th>
            <th>TB Rating</th>
            <th>% Doanh thu</th>
        `;

        const totalRevenue = state.data.reduce((s, r) => s + r['Total'], 0);

        dom.statsTableBody.innerHTML = labels.map(label => {
            const rows = groups[label];
            const revenue = rows.reduce((s, r) => s + r['Total'], 0);
            const income = rows.reduce((s, r) => s + r['gross income'], 0);
            const avgPrice = rows.reduce((s, r) => s + r['Unit price'], 0) / rows.length;
            const avgQty = rows.reduce((s, r) => s + r['Quantity'], 0) / rows.length;
            const avgRating = rows.reduce((s, r) => s + r['Rating'], 0) / rows.length;
            const pct = (revenue / totalRevenue * 100);

            return `<tr>
                <td><strong>${label}</strong></td>
                <td>${rows.length}</td>
                <td>$${revenue.toFixed(2)}</td>
                <td>$${income.toFixed(2)}</td>
                <td>$${avgPrice.toFixed(2)}</td>
                <td>${avgQty.toFixed(1)}</td>
                <td>${avgRating.toFixed(1)} ⭐</td>
                <td>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <div style="flex:1;height:6px;background:rgba(255,255,255,0.06);border-radius:3px;overflow:hidden;">
                            <div style="width:${pct}%;height:100%;background:var(--gradient-main);border-radius:3px;"></div>
                        </div>
                        <span style="font-size:0.8rem;color:#9999b3;">${pct.toFixed(1)}%</span>
                    </div>
                </td>
            </tr>`;
        }).join('');

        // Total row
        const totalIncome = state.data.reduce((s, r) => s + r['gross income'], 0);
        const avgPrice = state.data.reduce((s, r) => s + r['Unit price'], 0) / state.data.length;
        const avgQty = state.data.reduce((s, r) => s + r['Quantity'], 0) / state.data.length;
        const avgRating = state.data.reduce((s, r) => s + r['Rating'], 0) / state.data.length;

        dom.statsTableBody.innerHTML += `<tr style="background:rgba(102,126,234,0.08);font-weight:700;">
            <td>TỔNG</td>
            <td>${state.data.length}</td>
            <td>$${totalRevenue.toFixed(2)}</td>
            <td>$${totalIncome.toFixed(2)}</td>
            <td>$${avgPrice.toFixed(2)}</td>
            <td>${avgQty.toFixed(1)}</td>
            <td>${avgRating.toFixed(1)} ⭐</td>
            <td>100%</td>
        </tr>`;
    }

    // ======================== DETAIL MODAL ========================
    function showDetailModal(row) {
        if (!row) return;

        dom.modalInvoice.textContent = `#${row['Invoice ID']}`;

        const fields = [
            { label: 'Chi nhánh', value: `${row['Branch']} - ${row['City']}` },
            { label: 'Loại khách hàng', value: row['Customer type'] },
            { label: 'Giới tính', value: row['Gender'] === 'Male' ? 'Nam' : 'Nữ' },
            { label: 'Nhóm sản phẩm', value: row['Product line'] },
            { label: 'Đơn giá', value: '$' + row['Unit price'].toFixed(2) },
            { label: 'Số lượng', value: row['Quantity'] },
            { label: 'Giá vốn', value: '$' + row['cogs'].toFixed(2) },
            { label: 'Thuế 5%', value: '$' + row['Tax 5%'].toFixed(2) },
            { label: 'Tổng tiền', value: '$' + row['Total'].toFixed(2), cls: 'total' },
            { label: 'Ngày', value: row['Date'] },
            { label: 'Giờ', value: row['Time'] },
            { label: 'Thanh toán', value: row['Payment'] },
            { label: 'Lợi nhuận gộp', value: '$' + row['gross income'].toFixed(2) },
            { label: 'Đánh giá', value: `<span class="rating-stars">${'★'.repeat(Math.round(row['Rating']))}${'☆'.repeat(10 - Math.round(row['Rating']))}</span> ${row['Rating']}` }
        ];

        dom.modalBody.innerHTML = fields.map(f => `
            <div class="modal-row">
                <span class="modal-row-label">${f.label}</span>
                <span class="modal-row-value ${f.cls || ''}">${f.value}</span>
            </div>
        `).join('');

        dom.detailModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        dom.detailModal.classList.add('hidden');
        document.body.style.overflow = '';
    }

    // ======================== UTILITIES ========================
    function groupBy(arr, key) {
        return arr.reduce((acc, item) => {
            const k = item[key];
            if (!acc[k]) acc[k] = [];
            acc[k].push(item);
            return acc;
        }, {});
    }

    function debounce(fn, delay) {
        let timer;
        return function (...args) {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), delay);
        };
    }

    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / 1048576).toFixed(1) + ' MB';
    }

    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `${type === 'success' ? '✓' : 'ℹ'} ${message}`;
        dom.toastContainer.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    // ======================== START ========================
    document.addEventListener('DOMContentLoaded', init);
})();
