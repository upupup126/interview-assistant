/**
 * 面试助手 Web 前端应用
 */

const API_BASE = '/api/v1';

// ===== 全局状态 =====
const state = {
    currentPage: 'dashboard',
    leetcodeProblems: [],
    interviewQuestions: [],
    dashboardData: null,
};

// ===== 初始化 =====
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    checkBackendStatus();
    loadDashboard();
});

// ===== 导航 =====
function initNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => {
            const page = item.dataset.page;
            switchPage(page);
        });
    });

    // 筛选按钮 - LeetCode
    document.querySelectorAll('#page-leetcode .filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#page-leetcode .filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterLeetcode(btn.dataset.difficulty);
        });
    });

    // 筛选按钮 - 面试题
    document.querySelectorAll('#page-interview .filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#page-interview .filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterInterview(btn.dataset.category);
        });
    });

    // 搜索框
    const searchInput = document.getElementById('leetcode-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchLeetcode(e.target.value);
        });
    }

    // 简历分析按钮
    const analyzeBtn = document.getElementById('analyze-resume-btn');
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', analyzeResume);
    }
}

function switchPage(page) {
    state.currentPage = page;

    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.page === page);
    });

    document.querySelectorAll('.page').forEach(p => {
        p.classList.toggle('active', p.id === `page-${page}`);
    });

    // 懒加载页面数据
    switch (page) {
        case 'dashboard': loadDashboard(); break;
        case 'leetcode': loadLeetcode(); break;
        case 'interview': loadInterview(); break;
        case 'resume': loadResume(); break;
        case 'analytics': loadAnalytics(); break;
    }
}

// ===== 后端状态检查 =====
async function checkBackendStatus() {
    const el = document.getElementById('backendStatus');
    try {
        const res = await fetch('/health');
        if (res.ok) {
            el.className = 'status-indicator connected';
            el.querySelector('.text').textContent = '服务已连接';
        } else {
            throw new Error('Not healthy');
        }
    } catch {
        el.className = 'status-indicator disconnected';
        el.querySelector('.text').textContent = '连接断开';
        setTimeout(checkBackendStatus, 5000);
    }
}

// ===== API 请求封装 =====
async function apiGet(path) {
    try {
        const res = await fetch(`${API_BASE}${path}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error(`API GET ${path} failed:`, err);
        return null;
    }
}

async function apiPost(path, body) {
    try {
        const res = await fetch(`${API_BASE}${path}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error(`API POST ${path} failed:`, err);
        return null;
    }
}

// ===== 仪表盘 =====
async function loadDashboard() {
    const data = await apiGet('/analytics/dashboard');
    if (!data) {
        showToast('无法加载仪表盘数据', 'error');
        return;
    }

    state.dashboardData = data;

    const ls = data.leetcode_stats || {};
    document.getElementById('stat-total').textContent = ls.total ?? 0;
    document.getElementById('stat-completed').textContent = ls.completed ?? 0;
    document.getElementById('stat-progress').textContent = ls.in_progress ?? 0;

    const is = data.interview_stats || {};
    document.getElementById('stat-interview').textContent = is.total ?? 0;

    // 最近活动
    const activityEl = document.getElementById('recent-activity');
    const activities = data.recent_activity || [];
    if (activities.length === 0) {
        activityEl.innerHTML = '<div class="loading-placeholder">暂无活动记录</div>';
    } else {
        activityEl.innerHTML = activities.map(a => `
            <div class="activity-item">
                <div class="activity-icon ${a.type}">
                    <i class="ri-${a.type === 'leetcode' ? 'code-box-line' : 'question-answer-line'}"></i>
                </div>
                <div class="activity-text">
                    <strong>${a.action}</strong> ${a.title || ''}
                </div>
                <span class="activity-time">${a.time}</span>
            </div>
        `).join('');
    }
}

// ===== LeetCode =====
async function loadLeetcode() {
    const data = await apiGet('/leetcode/problems');
    if (!data) {
        document.getElementById('leetcode-table-body').innerHTML =
            '<tr><td colspan="6" class="loading-placeholder">加载失败，请检查后端服务</td></tr>';
        return;
    }

    state.leetcodeProblems = data.problems || data;
    renderLeetcodeTable(state.leetcodeProblems);
}

function renderLeetcodeTable(problems) {
    const tbody = document.getElementById('leetcode-table-body');

    if (!problems || problems.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="loading-placeholder">暂无题目数据</td></tr>';
        return;
    }

    tbody.innerHTML = problems.map(p => {
        const diffClass = p.difficulty === '简单' ? 'easy' : p.difficulty === '中等' ? 'medium' : 'hard';
        const statusClass = p.status === '已完成' ? 'done' : p.status === '进行中' ? 'wip' : 'pending';
        const statusText = p.status || '未开始';
        const tags = (p.tags || []).map(t => `<span class="tag">${t}</span>`).join('');

        return `
            <tr>
                <td>#${p.id}</td>
                <td><strong>${p.title}</strong></td>
                <td><span class="difficulty-tag ${diffClass}">${p.difficulty}</span></td>
                <td><div class="tag-list">${tags || '-'}</div></td>
                <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="toggleProblemStatus(${p.id})">
                        ${statusText === '已完成' ? '重置' : '完成'}
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function filterLeetcode(difficulty) {
    if (difficulty === 'all') {
        renderLeetcodeTable(state.leetcodeProblems);
    } else {
        const filtered = state.leetcodeProblems.filter(p => p.difficulty === difficulty);
        renderLeetcodeTable(filtered);
    }
}

function searchLeetcode(keyword) {
    const kw = keyword.toLowerCase();
    const filtered = state.leetcodeProblems.filter(p =>
        p.title.toLowerCase().includes(kw) ||
        (p.tags || []).some(t => t.toLowerCase().includes(kw))
    );
    renderLeetcodeTable(filtered);
}

async function toggleProblemStatus(id) {
    const problem = state.leetcodeProblems.find(p => p.id === id);
    if (!problem) return;

    const newStatus = problem.status === '已完成' ? '未开始' : '已完成';
    problem.status = newStatus;
    renderLeetcodeTable(state.leetcodeProblems);
    showToast(`题目 #${id} 已标记为「${newStatus}」`, 'success');
}

// ===== 面试练习 =====
async function loadInterview() {
    const data = await apiGet('/interview/questions');
    if (!data) {
        document.getElementById('interview-list').innerHTML =
            '<div class="loading-placeholder">加载失败，请检查后端服务</div>';
        return;
    }

    state.interviewQuestions = data.questions || data;
    renderInterviewCards(state.interviewQuestions);
}

function renderInterviewCards(questions) {
    const container = document.getElementById('interview-list');

    if (!questions || questions.length === 0) {
        container.innerHTML = '<div class="loading-placeholder">暂无面试题</div>';
        return;
    }

    container.innerHTML = questions.map(q => {
        const diffClass = q.difficulty === '简单' ? 'easy' : q.difficulty === '中等' ? 'medium' : 'hard';
        return `
            <div class="interview-card">
                <div class="q-header">
                    <span class="q-category">${q.category}</span>
                    <span class="difficulty-tag ${diffClass}">${q.difficulty}</span>
                </div>
                <div class="q-text">${q.question}</div>
                <div class="q-footer">
                    <button class="btn btn-sm btn-primary" onclick="showAnswer(${q.id})">
                        <i class="ri-eye-line"></i> 查看解析
                    </button>
                    <button class="btn btn-sm btn-outline" onclick="practiceQuestion(${q.id})">
                        <i class="ri-mic-line"></i> 模拟回答
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function filterInterview(category) {
    if (category === 'all') {
        renderInterviewCards(state.interviewQuestions);
    } else {
        const filtered = state.interviewQuestions.filter(q => q.category === category);
        renderInterviewCards(filtered);
    }
}

function showAnswer(id) {
    const q = state.interviewQuestions.find(q => q.id === id);
    if (q && q.answer) {
        showToast(`解析: ${q.answer}`, 'info');
    } else {
        showToast('该题暂无参考解析', 'info');
    }
}

function practiceQuestion(id) {
    showToast('语音回答功能正在开发中...', 'info');
}

// ===== 简历管理 =====
async function loadResume() {
    const templatesEl = document.getElementById('resume-templates');
    const templates = [
        { icon: 'ri-file-code-line', name: '技术型简历', desc: '适合软件工程师、算法岗位' },
        { icon: 'ri-projector-line', name: '项目导向简历', desc: '突出项目经验和技术成果' },
        { icon: 'ri-file-text-line', name: '简洁型简历', desc: '简洁明了，一页式格式' },
    ];

    templatesEl.innerHTML = templates.map(t => `
        <div class="resume-template" onclick="showToast('模板功能开发中...', 'info')">
            <i class="${t.icon}"></i>
            <div>
                <div class="tpl-name">${t.name}</div>
                <div class="tpl-desc">${t.desc}</div>
            </div>
        </div>
    `).join('');
}

async function analyzeResume() {
    const text = document.getElementById('resume-text').value.trim();
    if (!text) {
        showToast('请先输入简历内容', 'error');
        return;
    }

    const btn = document.getElementById('analyze-resume-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="ri-loader-4-line"></i> 分析中...';

    const data = await apiPost('/resume/analyze', { resume_text: text });

    btn.disabled = false;
    btn.innerHTML = '<i class="ri-sparkling-line"></i> 开始分析';

    const resultEl = document.getElementById('resume-analysis-result');

    if (!data) {
        // 使用模拟数据
        const mockData = {
            score: 78,
            strengths: ['技术栈描述清晰', '项目经验相关性高'],
            improvements: ['建议增加量化数据', '可补充开源项目经历', '添加技术博客链接'],
        };
        renderAnalysis(resultEl, mockData);
    } else {
        renderAnalysis(resultEl, data);
    }
}

function renderAnalysis(el, data) {
    el.style.display = 'block';
    el.innerHTML = `
        <div class="score">${data.score}分</div>
        <div class="section">
            <h4>✅ 优势</h4>
            <ul>${(data.strengths || []).map(s => `<li>${s}</li>`).join('')}</ul>
        </div>
        <div class="section">
            <h4>🔧 改进建议</h4>
            <ul>${(data.improvements || []).map(s => `<li>${s}</li>`).join('')}</ul>
        </div>
    `;
}

// ===== 数据统计 =====
async function loadAnalytics() {
    const data = await apiGet('/analytics/dashboard');

    const ls = data ? (data.leetcode_stats || {}) : { total: 3, completed: 0, in_progress: 0 };
    const total = ls.total || 3;
    const completed = ls.completed || 0;
    const inProgress = ls.in_progress || 0;
    const pending = total - completed - inProgress;

    renderDonutChart(completed, inProgress, pending, total);
    renderProgressBars(completed, inProgress, pending, total);
}

function renderDonutChart(completed, inProgress, pending, total) {
    const container = document.getElementById('difficulty-chart');
    const r = 70, cx = 90, cy = 90, circumference = 2 * Math.PI * r;

    const pcts = [
        { val: completed, color: 'var(--easy)', label: '已完成' },
        { val: inProgress, color: 'var(--medium)', label: '进行中' },
        { val: pending, color: 'var(--text-muted)', label: '未开始' },
    ];

    let offset = 0;
    const circles = pcts.map(p => {
        const pct = total > 0 ? p.val / total : 0;
        const dashLen = circumference * pct;
        const dashGap = circumference - dashLen;
        const html = `<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${p.color}" stroke-width="14"
            stroke-dasharray="${dashLen} ${dashGap}" stroke-dashoffset="${-offset}" stroke-linecap="round"/>`;
        offset += dashLen;
        return html;
    }).join('');

    const legend = pcts.map(p => `
        <div class="legend-item">
            <span class="legend-dot" style="background:${p.color}"></span>
            ${p.label}: ${p.val}
        </div>
    `).join('');

    container.innerHTML = `
        <div class="donut-chart">
            <svg width="180" height="180">${circles}</svg>
            <div class="center-text">
                <span class="value">${total}</span>
                <span class="label">总题数</span>
            </div>
        </div>
        <div class="chart-legend">${legend}</div>
    `;
}

function renderProgressBars(completed, inProgress, pending, total) {
    const container = document.getElementById('progress-bars');
    const bars = [
        { label: '已完成', value: completed, total, color: 'var(--easy)' },
        { label: '进行中', value: inProgress, total, color: 'var(--medium)' },
        { label: '未开始', value: pending, total, color: 'var(--text-muted)' },
    ];

    container.innerHTML = bars.map(b => {
        const pct = total > 0 ? Math.round(b.value / total * 100) : 0;
        return `
            <div class="progress-bar-item">
                <div class="bar-header">
                    <span class="bar-label">${b.label}</span>
                    <span class="bar-value">${b.value} (${pct}%)</span>
                </div>
                <div class="progress-bar-track">
                    <div class="progress-bar-fill" style="width:${pct}%;background:${b.color}"></div>
                </div>
            </div>
        `;
    }).join('');
}

// ===== Toast =====
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}
