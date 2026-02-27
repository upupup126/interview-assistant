/**
 * 面试助手 Web 前端应用 - 完整版
 * 对接 API_DOC.md 中定义的全部后端接口
 */

const API = {
    leetcode:  '/api/v1/leetcode',
    interview: '/api/v1/interview',
    resume:    '/api/v1/resumes',
    analytics: '/api/v1/analytics',
};

const state = {
    currentPage: 'dashboard',
    leetcodeProblems: [],
    interviewQuestions: [],
    resumes: [],
    currentFilter: 'all',
};

// ======================== Init ========================
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    checkBackendStatus();
    loadDashboard();
});

// ======================== Navigation ========================
function initNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => switchPage(item.dataset.page));
    });

    // LeetCode difficulty filter
    document.querySelectorAll('#page-leetcode .filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#page-leetcode .filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterLeetcode(btn.dataset.difficulty);
        });
    });

    // Interview category filter
    document.querySelectorAll('#page-interview .filter-btn').forEach(btn => {
        if (!btn.dataset.category) return;
        btn.addEventListener('click', () => {
            document.querySelectorAll('#page-interview .filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterInterview(btn.dataset.category);
        });
    });

    // LeetCode search
    const searchInput = document.getElementById('leetcode-search');
    if (searchInput) {
        let timer;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(timer);
            timer = setTimeout(() => searchLeetcode(e.target.value), 300);
        });
    }

    // Analytics tabs
    document.querySelectorAll('[data-analytics]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('[data-analytics]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            switchAnalyticsTab(btn.dataset.analytics);
        });
    });

    // Comparison period
    document.querySelectorAll('[data-period]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('[data-period]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            loadComparison(btn.dataset.period);
        });
    });
}

function switchPage(page) {
    state.currentPage = page;
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.page === page);
    });
    document.querySelectorAll('.page').forEach(p => {
        p.classList.toggle('active', p.id === `page-${page}`);
    });
    switch (page) {
        case 'dashboard': loadDashboard(); break;
        case 'leetcode':  loadLeetcode(); break;
        case 'interview': loadInterview(); break;
        case 'resume':    loadResume(); break;
        case 'analytics': loadAnalytics(); break;
    }
}

// ======================== API Helpers ========================
async function apiGet(url) {
    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error(`GET ${url}:`, err);
        return null;
    }
}

async function apiPost(url, body) {
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error(`POST ${url}:`, err);
        return null;
    }
}

async function apiPut(url, body) {
    try {
        const res = await fetch(url, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error(`PUT ${url}:`, err);
        return null;
    }
}

async function apiDelete(url) {
    try {
        const res = await fetch(url, { method: 'DELETE' });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error(`DELETE ${url}:`, err);
        return null;
    }
}

async function apiPostForm(url, formData) {
    try {
        const res = await fetch(url, { method: 'POST', body: formData });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error(`POST(form) ${url}:`, err);
        return null;
    }
}

// ======================== Backend Status ========================
async function checkBackendStatus() {
    const el = document.getElementById('backendStatus');
    try {
        const res = await fetch('/health');
        if (res.ok) {
            el.className = 'status-indicator connected';
            el.querySelector('.text').textContent = '服务已连接';
        } else throw 0;
    } catch {
        el.className = 'status-indicator disconnected';
        el.querySelector('.text').textContent = '连接断开';
        setTimeout(checkBackendStatus, 5000);
    }
}

// ======================== Dashboard ========================
async function loadDashboard() {
    const [overview, daily, insights] = await Promise.all([
        apiGet(`${API.analytics}/overview`),
        apiGet(`${API.leetcode}/daily-challenge`),
        apiGet(`${API.analytics}/learning-insights`),
    ]);

    // Overview stats
    if (overview && overview.overview) {
        const o = overview.overview;
        setText('stat-problems-solved', o.total_problems_solved ?? 0);
        setText('stat-study-time', o.total_study_time ? Math.round(o.total_study_time / 60) : 0);
        setText('stat-avg-score', o.average_score ?? 0);
        setText('stat-streak', o.streak_days ?? 0);
    }

    // Daily challenge
    const dcEl = document.getElementById('daily-challenge');
    if (daily && daily.title) {
        const diffClass = difficultyClass(daily.difficulty);
        dcEl.innerHTML = `
            <div class="daily-item">
                <div class="daily-header">
                    <span class="difficulty-tag ${diffClass}">${daily.difficulty}</span>
                    <span class="daily-date">${daily.date || '今天'}</span>
                </div>
                <div class="daily-title">#${daily.leetcode_id} ${daily.title}</div>
                <div class="tag-list">${(daily.tags||[]).map(t=>`<span class="tag">${t}</span>`).join('')}</div>
            </div>`;
    } else {
        dcEl.innerHTML = '<div class="empty-state">暂无每日挑战数据</div>';
    }

    // Learning insights
    const liEl = document.getElementById('learning-insights');
    if (insights && insights.insights) {
        const ins = insights.insights;
        liEl.innerHTML = `
            <div class="insight-section">
                <h4><i class="ri-medal-line"></i> 优势领域</h4>
                <div class="insight-tags">${(ins.strengths||[]).map(s=>`<span class="tag tag-success">${typeof s === 'object' ? (s.area || s.description || JSON.stringify(s)) : s}</span>`).join('')}</div>
            </div>
            <div class="insight-section">
                <h4><i class="ri-arrow-up-circle-line"></i> 待提升</h4>
                <div class="insight-tags">${(ins.improvement_areas||[]).map(s=>`<span class="tag tag-warning">${typeof s === 'object' ? (s.area || s.description || JSON.stringify(s)) : s}</span>`).join('')}</div>
            </div>
            <div class="insight-section">
                <h4><i class="ri-lightbulb-flash-line"></i> 建议</h4>
                <ul class="insight-list">${(ins.learning_recommendations||[]).map(s=>`<li>${typeof s === 'object' ? (s.title || s.description || JSON.stringify(s)) : s}</li>`).join('')}</ul>
            </div>`;
    } else {
        liEl.innerHTML = '<div class="empty-state">暂无学习洞察数据</div>';
    }
}

// ======================== LeetCode ========================
async function loadLeetcode() {
    const [problems, daily, recommend, submissions] = await Promise.all([
        apiGet(`${API.leetcode}/problems?page=1&page_size=50`),
        apiGet(`${API.leetcode}/daily-challenge`),
        apiGet(`${API.leetcode}/recommendations?count=5`),
        apiGet(`${API.leetcode}/submissions?limit=10`),
    ]);

    // Problems list
    if (problems) {
        state.leetcodeProblems = problems.problems || problems || [];
        renderLeetcodeTable(state.leetcodeProblems);
    }

    // Daily challenge card
    const dcEl = document.getElementById('lc-daily-content');
    if (daily && daily.title) {
        dcEl.innerHTML = `
            <div class="daily-compact">
                <span class="difficulty-tag ${difficultyClass(daily.difficulty)}">${daily.difficulty}</span>
                <strong>#${daily.leetcode_id}</strong> ${daily.title}
            </div>`;
    } else {
        dcEl.innerHTML = '<div class="empty-state">暂无数据</div>';
    }

    // Recommendations
    const rcEl = document.getElementById('lc-recommend-content');
    if (recommend && recommend.problems && recommend.problems.length) {
        rcEl.innerHTML = recommend.problems.map(p => `
            <div class="recommend-item">
                <span class="difficulty-tag ${difficultyClass(p.difficulty)}">${p.difficulty}</span>
                <span>${p.title || p.title_slug || 'Problem #' + p.id}</span>
            </div>`).join('');
    } else {
        rcEl.innerHTML = '<div class="empty-state">暂无推荐</div>';
    }

    // Submissions
    renderSubmissions(submissions);
}

function renderLeetcodeTable(problems) {
    const tbody = document.getElementById('leetcode-table-body');
    if (!problems || problems.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading-placeholder">暂无题目数据</td></tr>';
        return;
    }
    tbody.innerHTML = problems.map(p => {
        const dc = difficultyClass(p.difficulty);
        const tags = (p.tags || []).map(t => `<span class="tag">${t}</span>`).join('');
        const rate = p.acceptance_rate ? p.acceptance_rate.toFixed(1) + '%' : '-';
        return `<tr>
            <td>#${p.leetcode_id || p.id}</td>
            <td><strong class="clickable" onclick="viewProblemDetail(${p.id})">${p.title}</strong></td>
            <td><span class="difficulty-tag ${dc}">${p.difficulty}</span></td>
            <td><div class="tag-list">${tags || '-'}</div></td>
            <td>${rate}</td>
            <td><span class="status-badge ${p.is_premium ? 'premium' : 'free'}">${p.is_premium ? '会员' : '免费'}</span></td>
            <td><button class="btn btn-sm btn-outline" onclick="openSubmitForProblem(${p.id}, '${escape(p.title)}')">
                <i class="ri-send-plane-line"></i> 提交
            </button></td>
        </tr>`;
    }).join('');
}

function renderSubmissions(data) {
    const el = document.getElementById('submissions-list');
    const subs = data ? (data.submissions || data || []) : [];
    if (!subs.length) {
        el.innerHTML = '<div class="empty-state">暂无提交记录</div>';
        return;
    }
    el.innerHTML = `<table class="data-table"><thead><tr>
        <th>题目ID</th><th>语言</th><th>状态</th><th>运行时间</th><th>内存</th>
    </tr></thead><tbody>${subs.map(s => `<tr>
        <td>#${s.problem_id}</td>
        <td>${s.language}</td>
        <td><span class="status-badge ${s.is_accepted ? 'done' : 'wip'}">${s.status}</span></td>
        <td>${s.runtime || '-'}</td>
        <td>${s.memory || '-'}</td>
    </tr>`).join('')}</tbody></table>`;
}

function filterLeetcode(difficulty) {
    if (difficulty === 'all') {
        renderLeetcodeTable(state.leetcodeProblems);
    } else {
        renderLeetcodeTable(state.leetcodeProblems.filter(p => p.difficulty === difficulty));
    }
}

function searchLeetcode(keyword) {
    const kw = keyword.toLowerCase();
    if (!kw) { renderLeetcodeTable(state.leetcodeProblems); return; }
    renderLeetcodeTable(state.leetcodeProblems.filter(p =>
        (p.title || '').toLowerCase().includes(kw) ||
        (p.tags || []).some(t => t.toLowerCase().includes(kw))
    ));
}

async function syncLeetcode() {
    showToast('正在同步题库...', 'info');
    const res = await apiPost(`${API.leetcode}/sync?max_problems=50`, {});
    if (res) {
        showToast(res.message || '同步任务已启动', 'success');
    } else {
        showToast('同步请求失败', 'error');
    }
}

async function viewProblemDetail(id) {
    const data = await apiGet(`${API.leetcode}/problems/${id}`);
    if (!data) { showToast('获取题目详情失败', 'error'); return; }
    openModal(`题目详情 #${data.leetcode_id || data.id}`, `
        <div class="detail-section">
            <div class="detail-header">
                <h2>${data.title}</h2>
                <span class="difficulty-tag ${difficultyClass(data.difficulty)}">${data.difficulty}</span>
            </div>
            <div class="tag-list" style="margin:12px 0;">${(data.tags||[]).map(t=>`<span class="tag">${t}</span>`).join('')}</div>
            <div class="detail-meta">
                <span>通过率: ${data.acceptance_rate ? data.acceptance_rate.toFixed(1)+'%' : '-'}</span>
                <span>会员题: ${data.is_premium ? '是' : '否'}</span>
            </div>
            ${data.content ? `<div class="detail-content">${data.content}</div>` : ''}
            ${data.hints && data.hints.length ? `<div class="detail-hints"><h4>提示</h4><ul>${data.hints.map(h=>`<li>${h}</li>`).join('')}</ul></div>` : ''}
        </div>
    `);
}

function openSubmitForProblem(problemId, title) {
    openModal('提交代码', `
        <form onsubmit="submitCode(event)">
            <input type="hidden" id="submit-problem-id" value="${problemId}">
            <div class="form-group">
                <label>题目</label>
                <input type="text" value="#${problemId} ${unescape(title)}" disabled class="form-input">
            </div>
            <div class="form-group">
                <label>编程语言 *</label>
                <select id="submit-language" class="form-select" required>
                    <option value="python">Python</option>
                    <option value="javascript">JavaScript</option>
                    <option value="java">Java</option>
                    <option value="cpp">C++</option>
                    <option value="go">Go</option>
                </select>
            </div>
            <div class="form-group">
                <label>代码 *</label>
                <textarea id="submit-code" class="form-textarea" rows="8" required placeholder="请输入代码..."></textarea>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>状态</label>
                    <select id="submit-status" class="form-select">
                        <option value="Accepted">Accepted</option>
                        <option value="Wrong Answer">Wrong Answer</option>
                        <option value="Time Limit Exceeded">TLE</option>
                        <option value="Runtime Error">Runtime Error</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>运行时间</label>
                    <input type="text" id="submit-runtime" class="form-input" placeholder="如: 12ms">
                </div>
                <div class="form-group">
                    <label>内存</label>
                    <input type="text" id="submit-memory" class="form-input" placeholder="如: 15.2MB">
                </div>
            </div>
            <div class="form-group">
                <label>解题思路</label>
                <textarea id="submit-approach" class="form-textarea" rows="3" placeholder="描述你的解题思路..."></textarea>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>时间复杂度</label>
                    <input type="text" id="submit-time-complexity" class="form-input" placeholder="O(n)">
                </div>
                <div class="form-group">
                    <label>空间复杂度</label>
                    <input type="text" id="submit-space-complexity" class="form-input" placeholder="O(1)">
                </div>
            </div>
            <div class="form-group">
                <label>备注</label>
                <input type="text" id="submit-notes" class="form-input" placeholder="备注信息...">
            </div>
            <button type="submit" class="btn btn-primary btn-block">
                <i class="ri-send-plane-line"></i> 提交
            </button>
        </form>
    `);
}

function openSubmissionModal() {
    openModal('创建提交记录', `
        <form onsubmit="submitCode(event)">
            <div class="form-group">
                <label>题目ID *</label>
                <input type="number" id="submit-problem-id" class="form-input" required placeholder="输入题目ID">
            </div>
            <div class="form-group">
                <label>编程语言 *</label>
                <select id="submit-language" class="form-select" required>
                    <option value="python">Python</option>
                    <option value="javascript">JavaScript</option>
                    <option value="java">Java</option>
                    <option value="cpp">C++</option>
                    <option value="go">Go</option>
                </select>
            </div>
            <div class="form-group">
                <label>代码 *</label>
                <textarea id="submit-code" class="form-textarea" rows="8" required placeholder="请输入代码..."></textarea>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>状态</label>
                    <select id="submit-status" class="form-select">
                        <option value="Accepted">Accepted</option>
                        <option value="Wrong Answer">Wrong Answer</option>
                        <option value="Time Limit Exceeded">TLE</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>运行时间</label>
                    <input type="text" id="submit-runtime" class="form-input" placeholder="12ms">
                </div>
                <div class="form-group">
                    <label>内存</label>
                    <input type="text" id="submit-memory" class="form-input" placeholder="15.2MB">
                </div>
            </div>
            <div class="form-group">
                <label>解题思路</label>
                <textarea id="submit-approach" class="form-textarea" rows="3" placeholder="描述解题思路..."></textarea>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>时间复杂度</label>
                    <input type="text" id="submit-time-complexity" class="form-input" placeholder="O(n)">
                </div>
                <div class="form-group">
                    <label>空间复杂度</label>
                    <input type="text" id="submit-space-complexity" class="form-input" placeholder="O(1)">
                </div>
            </div>
            <button type="submit" class="btn btn-primary btn-block">
                <i class="ri-send-plane-line"></i> 提交
            </button>
        </form>
    `);
}

async function submitCode(e) {
    e.preventDefault();
    const body = {
        problem_id: parseInt(document.getElementById('submit-problem-id').value),
        language: document.getElementById('submit-language').value,
        code: document.getElementById('submit-code').value,
        status: document.getElementById('submit-status').value,
        runtime: document.getElementById('submit-runtime')?.value || '',
        memory: document.getElementById('submit-memory')?.value || '',
        approach: document.getElementById('submit-approach')?.value || '',
        time_complexity: document.getElementById('submit-time-complexity')?.value || '',
        space_complexity: document.getElementById('submit-space-complexity')?.value || '',
        notes: document.getElementById('submit-notes')?.value || '',
        is_accepted: document.getElementById('submit-status').value === 'Accepted',
    };
    const res = await apiPost(`${API.leetcode}/submissions`, body);
    if (res) {
        showToast('提交记录创建成功！', 'success');
        closeModal();
        // Reload submissions
        const subs = await apiGet(`${API.leetcode}/submissions?limit=10`);
        renderSubmissions(subs);
    } else {
        showToast('提交失败', 'error');
    }
}

// ======================== Interview ========================
async function loadInterview() {
    const data = await apiGet(`${API.interview}/questions`);
    if (!data) {
        document.getElementById('interview-list').innerHTML = '<div class="empty-state">加载失败，请检查后端服务</div>';
        return;
    }
    state.interviewQuestions = data.questions || data || [];
    renderInterviewCards(state.interviewQuestions);
}

function renderInterviewCards(questions) {
    const container = document.getElementById('interview-list');
    if (!questions || questions.length === 0) {
        container.innerHTML = '<div class="empty-state">暂无面试题</div>';
        return;
    }
    container.innerHTML = questions.map(q => {
        const dc = difficultyClass(q.difficulty);
        return `<div class="interview-card">
            <div class="q-header">
                <span class="q-category">${q.category}</span>
                <span class="difficulty-tag ${dc}">${q.difficulty}</span>
            </div>
            <div class="q-text">${q.question}</div>
            <div class="q-tags">${(q.tags||[]).map(t=>`<span class="tag">${t}</span>`).join('')}</div>
            <div class="q-footer">
                <button class="btn btn-sm btn-primary" onclick="showReferenceAnswer(${q.id})">
                    <i class="ri-eye-line"></i> 查看解析
                </button>
                <button class="btn btn-sm btn-outline" onclick="openAnswerModal(${q.id})">
                    <i class="ri-edit-line"></i> 模拟回答
                </button>
            </div>
        </div>`;
    }).join('');
}

function filterInterview(category) {
    if (category === 'all') {
        renderInterviewCards(state.interviewQuestions);
    } else {
        renderInterviewCards(state.interviewQuestions.filter(q => q.category === category));
    }
}

function showReferenceAnswer(id) {
    const q = state.interviewQuestions.find(q => q.id === id);
    if (!q) return;
    openModal(`参考解析 - ${q.category}`, `
        <div class="detail-section">
            <div class="q-text" style="margin-bottom:16px;font-size:16px;font-weight:600;">${q.question}</div>
            <div class="reference-answer">${q.reference_answer || q.answer || '暂无参考答案'}</div>
        </div>
    `);
}

function openAnswerModal(id) {
    const q = state.interviewQuestions.find(q => q.id === id);
    if (!q) return;
    openModal('模拟回答', `
        <form onsubmit="submitAnswer(event, ${id})">
            <div class="form-group">
                <label>题目</label>
                <div class="q-text" style="padding:12px;background:var(--bg-primary);border-radius:8px;margin-bottom:8px;">${q.question}</div>
            </div>
            <div class="form-group">
                <label>你的回答 *</label>
                <textarea id="answer-text" class="form-textarea" rows="8" required placeholder="请输入你的回答..."></textarea>
            </div>
            <button type="submit" class="btn btn-primary btn-block">
                <i class="ri-sparkling-line"></i> 提交并分析
            </button>
        </form>
    `);
}

async function submitAnswer(e, questionId) {
    e.preventDefault();
    const answerText = document.getElementById('answer-text').value;
    const formData = new FormData();
    formData.append('question_id', questionId);
    formData.append('answer_text', answerText);

    showToast('正在分析回答...', 'info');
    const res = await apiPostForm(`${API.interview}/analyze-answer`, formData);
    if (res && res.analysis) {
        const a = res.analysis.analysis || res.analysis;
        closeModal();
        openModal('回答分析结果', `
            <div class="analysis-result" style="display:block;">
                <div class="score">${a.overall_score || '-'}分</div>
                <div class="score-grid">
                    <div class="score-item"><span class="score-label">内容</span><span class="score-val">${a.content_score || '-'}</span></div>
                    <div class="score-item"><span class="score-label">逻辑</span><span class="score-val">${a.logic_score || '-'}</span></div>
                    <div class="score-item"><span class="score-label">准确</span><span class="score-val">${a.accuracy_score || '-'}</span></div>
                </div>
                <div class="section"><h4>优势</h4><ul>${(a.strengths||[]).map(s=>`<li>${s}</li>`).join('')}</ul></div>
                <div class="section"><h4>改进建议</h4><ul>${(a.improvements||[]).map(s=>`<li>${s}</li>`).join('')}</ul></div>
                ${a.detailed_feedback ? `<div class="section"><h4>详细反馈</h4><p>${a.detailed_feedback}</p></div>` : ''}
            </div>
        `);
    } else {
        showToast('分析失败', 'error');
    }
}

async function loadDailyQuestion() {
    const data = await apiGet(`${API.interview}/daily-question`);
    if (data && data.daily_question) {
        const q = data.daily_question;
        openModal('每日一题', `
            <div class="detail-section">
                <div class="detail-meta"><span>日期: ${data.date || '今天'}</span><span>分类: ${q.category}</span></div>
                <div class="q-text" style="font-size:16px;margin:16px 0;">${q.question}</div>
                <span class="difficulty-tag ${q.difficulty==='初级'?'easy':q.difficulty==='高级'?'hard':'medium'}">${q.difficulty}</span>
                <button class="btn btn-primary" style="margin-top:16px;" onclick="closeModal();openAnswerModal(${q.id})">
                    <i class="ri-edit-line"></i> 开始回答
                </button>
            </div>
        `);
    } else {
        showToast('获取每日题目失败', 'error');
    }
}

async function loadInterviewStats() {
    const card = document.getElementById('interview-stats-card');
    card.style.display = 'block';
    const data = await apiGet(`${API.interview}/statistics`);
    const el = document.getElementById('interview-stats-content');
    if (data && data.statistics) {
        const s = data.statistics;
        const cats = s.category_stats || {};
        el.innerHTML = `
            <div class="stats-mini-grid">
                <div class="mini-stat"><span class="mini-val">${s.total_questions_answered || 0}</span><span class="mini-label">已回答</span></div>
                <div class="mini-stat"><span class="mini-val">${s.average_score || 0}</span><span class="mini-label">平均分</span></div>
                <div class="mini-stat"><span class="mini-val">${s.total_practice_time || 0}min</span><span class="mini-label">练习时间</span></div>
            </div>
            <h4 style="margin:16px 0 8px;">分类统计</h4>
            ${Object.entries(cats).map(([k,v]) => `
                <div class="progress-bar-item">
                    <div class="bar-header"><span class="bar-label">${k}</span><span class="bar-value">${v.answered||v.count||0}题 / 均分${v.avg_score||0}</span></div>
                    <div class="progress-bar-track"><div class="progress-bar-fill" style="width:${Math.min((v.avg_score||0),100)}%;background:var(--accent)"></div></div>
                </div>
            `).join('')}
            ${s.improvement_areas ? `<div style="margin-top:12px;"><strong>待提升: </strong>${s.improvement_areas.join(', ')}</div>` : ''}
        `;
    } else {
        el.innerHTML = '<div class="empty-state">暂无统计数据</div>';
    }
}

// ======================== Resume ========================
async function loadResume() {
    const [resumes, templates] = await Promise.all([
        apiGet(`${API.resume}/?skip=0&limit=100`),
        apiGet(`${API.resume}/templates/list`),
    ]);

    // Resume list
    const listEl = document.getElementById('resume-list');
    const items = resumes ? (resumes.resumes || resumes || []) : [];
    state.resumes = items;
    updateResumeSelect(items);

    if (!items.length) {
        listEl.innerHTML = '<div class="empty-state"><i class="ri-file-add-line" style="font-size:48px;color:var(--text-muted);"></i><p>暂无简历，点击「创建简历」开始</p></div>';
    } else {
        listEl.innerHTML = `<div class="resume-grid">${items.map(r => `
            <div class="resume-card">
                <div class="resume-card-header">
                    <h3>${r.title}</h3>
                    <span class="status-badge ${r.is_active ? 'done' : 'pending'}">${r.is_active ? '活跃' : '归档'}</span>
                </div>
                <div class="resume-card-meta">
                    ${r.target_position ? `<span><i class="ri-briefcase-line"></i> ${r.target_position}</span>` : ''}
                    ${r.target_company ? `<span><i class="ri-building-line"></i> ${r.target_company}</span>` : ''}
                </div>
                <div class="resume-card-footer">
                    <span class="resume-date">${formatDate(r.created_at)}</span>
                    <div class="resume-actions">
                        <button class="btn btn-sm btn-outline" onclick="viewResumeDetail(${r.id})"><i class="ri-eye-line"></i></button>
                        <button class="btn btn-sm btn-outline" onclick="openEditResumeModal(${r.id})"><i class="ri-edit-line"></i></button>
                        <button class="btn btn-sm btn-outline btn-danger-outline" onclick="deleteResume(${r.id})"><i class="ri-delete-bin-line"></i></button>
                    </div>
                </div>
            </div>
        `).join('')}</div>`;
    }

    // Templates
    const tplEl = document.getElementById('resume-templates');
    const tpls = templates ? (templates.templates || []) : [];
    if (tpls.length) {
        tplEl.innerHTML = tpls.map(t => `
            <div class="resume-template">
                <i class="ri-file-code-line"></i>
                <div><div class="tpl-name">${t.name}</div><div class="tpl-desc">${t.description}</div></div>
            </div>`).join('');
    } else {
        tplEl.innerHTML = `
            <div class="resume-template"><i class="ri-file-code-line"></i><div><div class="tpl-name">技术型简历</div><div class="tpl-desc">适合软件工程师、算法岗位</div></div></div>
            <div class="resume-template"><i class="ri-projector-line"></i><div><div class="tpl-name">项目导向简历</div><div class="tpl-desc">突出项目经验和技术成果</div></div></div>
            <div class="resume-template"><i class="ri-file-text-line"></i><div><div class="tpl-name">简洁型简历</div><div class="tpl-desc">简洁明了，一页式格式</div></div></div>`;
    }
}

function updateResumeSelect(items) {
    const sel = document.getElementById('optimize-resume-select');
    if (!sel) return;
    sel.innerHTML = '<option value="">-- 选择简历 --</option>' +
        items.map(r => `<option value="${r.id}">${r.title}</option>`).join('');
}

function openCreateResumeModal() {
    openModal('创建简历', `
        <form onsubmit="createResume(event)">
            <div class="form-group">
                <label>简历标题 *</label>
                <input type="text" id="resume-title" class="form-input" required placeholder="如: 后端开发工程师简历">
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>目标岗位</label>
                    <input type="text" id="resume-position" class="form-input" placeholder="如: 后端开发">
                </div>
                <div class="form-group">
                    <label>目标公司</label>
                    <input type="text" id="resume-company" class="form-input" placeholder="如: 字节跳动">
                </div>
            </div>
            <h4 style="margin:16px 0 8px;">个人信息</h4>
            <div class="form-row">
                <div class="form-group"><label>姓名</label><input type="text" id="resume-name" class="form-input" placeholder="姓名"></div>
                <div class="form-group"><label>邮箱</label><input type="email" id="resume-email" class="form-input" placeholder="email@example.com"></div>
            </div>
            <div class="form-row">
                <div class="form-group"><label>电话</label><input type="text" id="resume-phone" class="form-input" placeholder="13800138000"></div>
                <div class="form-group"><label>城市</label><input type="text" id="resume-location" class="form-input" placeholder="北京"></div>
            </div>
            <div class="form-row">
                <div class="form-group"><label>GitHub</label><input type="text" id="resume-github" class="form-input" placeholder="https://github.com/..."></div>
                <div class="form-group"><label>个人网站</label><input type="text" id="resume-website" class="form-input" placeholder="https://..."></div>
            </div>
            <div class="form-group">
                <label>个人简介</label>
                <textarea id="resume-summary" class="form-textarea" rows="3" placeholder="简要描述你的背景和优势..."></textarea>
            </div>
            <button type="submit" class="btn btn-primary btn-block"><i class="ri-add-line"></i> 创建简历</button>
        </form>
    `);
}

async function createResume(e) {
    e.preventDefault();
    const body = {
        title: document.getElementById('resume-title').value,
        target_position: document.getElementById('resume-position').value || undefined,
        target_company: document.getElementById('resume-company').value || undefined,
    };
    const name = document.getElementById('resume-name').value;
    if (name) {
        body.personal_info = {
            name: name,
            email: document.getElementById('resume-email').value || undefined,
            phone: document.getElementById('resume-phone').value || undefined,
            location: document.getElementById('resume-location').value || undefined,
            github: document.getElementById('resume-github').value || undefined,
            website: document.getElementById('resume-website').value || undefined,
            summary: document.getElementById('resume-summary').value || undefined,
        };
    }
    const res = await apiPost(`${API.resume}/`, body);
    if (res) {
        showToast('简历创建成功！', 'success');
        closeModal();
        loadResume();
    } else {
        showToast('创建失败', 'error');
    }
}

async function viewResumeDetail(id) {
    const data = await apiGet(`${API.resume}/${id}`);
    if (!data) { showToast('获取详情失败', 'error'); return; }
    const pi = data.personal_info || {};
    openModal(`简历详情 - ${data.title}`, `
        <div class="detail-section">
            <div class="detail-meta">
                ${data.target_position ? `<span><i class="ri-briefcase-line"></i> ${data.target_position}</span>` : ''}
                ${data.target_company ? `<span><i class="ri-building-line"></i> ${data.target_company}</span>` : ''}
                <span>创建: ${formatDate(data.created_at)}</span>
            </div>
            ${pi.name ? `<h4 style="margin:16px 0 8px;">个人信息</h4>
            <div class="info-grid">
                <div><strong>姓名:</strong> ${pi.name}</div>
                ${pi.email ? `<div><strong>邮箱:</strong> ${pi.email}</div>` : ''}
                ${pi.phone ? `<div><strong>电话:</strong> ${pi.phone}</div>` : ''}
                ${pi.location ? `<div><strong>城市:</strong> ${pi.location}</div>` : ''}
                ${pi.github ? `<div><strong>GitHub:</strong> <a href="${pi.github}" target="_blank">${pi.github}</a></div>` : ''}
                ${pi.summary ? `<div style="grid-column:1/-1;"><strong>简介:</strong> ${pi.summary}</div>` : ''}
            </div>` : ''}
            <div class="detail-actions" style="margin-top:20px;">
                <button class="btn btn-outline" onclick="exportResumePdf(${id})"><i class="ri-file-pdf-line"></i> 导出PDF</button>
                <button class="btn btn-outline" onclick="viewResumeVersions(${id})"><i class="ri-history-line"></i> 版本历史</button>
            </div>
        </div>
    `);
}

function openEditResumeModal(id) {
    const r = state.resumes.find(r => r.id === id);
    if (!r) return;
    openModal('编辑简历', `
        <form onsubmit="updateResume(event, ${id})">
            <div class="form-group">
                <label>简历标题</label>
                <input type="text" id="edit-resume-title" class="form-input" value="${r.title || ''}">
            </div>
            <div class="form-row">
                <div class="form-group"><label>目标岗位</label><input type="text" id="edit-resume-position" class="form-input" value="${r.target_position || ''}"></div>
                <div class="form-group"><label>目标公司</label><input type="text" id="edit-resume-company" class="form-input" value="${r.target_company || ''}"></div>
            </div>
            <div class="form-group">
                <label>状态</label>
                <select id="edit-resume-active" class="form-select">
                    <option value="true" ${r.is_active ? 'selected' : ''}>活跃</option>
                    <option value="false" ${!r.is_active ? 'selected' : ''}>归档</option>
                </select>
            </div>
            <button type="submit" class="btn btn-primary btn-block"><i class="ri-save-line"></i> 保存</button>
        </form>
    `);
}

async function updateResume(e, id) {
    e.preventDefault();
    const body = {
        title: document.getElementById('edit-resume-title').value || undefined,
        target_position: document.getElementById('edit-resume-position').value || undefined,
        target_company: document.getElementById('edit-resume-company').value || undefined,
        is_active: document.getElementById('edit-resume-active').value === 'true',
    };
    const res = await apiPut(`${API.resume}/${id}`, body);
    if (res) {
        showToast('简历更新成功！', 'success');
        closeModal();
        loadResume();
    } else {
        showToast('更新失败', 'error');
    }
}

async function deleteResume(id) {
    if (!confirm('确定删除该简历？')) return;
    const res = await apiDelete(`${API.resume}/${id}`);
    if (res) {
        showToast('简历已删除', 'success');
        loadResume();
    } else {
        showToast('删除失败', 'error');
    }
}

async function exportResumePdf(id) {
    const res = await apiPost(`${API.resume}/${id}/export/pdf`, {});
    if (res && res.success) {
        showToast('PDF 导出成功', 'success');
    } else {
        showToast('导出失败', 'error');
    }
}

async function viewResumeVersions(id) {
    const data = await apiGet(`${API.resume}/${id}/versions`);
    if (data && data.versions) {
        closeModal();
        openModal('版本历史', `
            <div class="versions-list">
                ${data.versions.map(v => `
                    <div class="version-item">
                        <span class="version-num">v${v.version}</span>
                        <span class="version-date">${formatDate(v.created_at)}</span>
                        <span>${v.description || ''}</span>
                    </div>
                `).join('')}
            </div>
        `);
    } else {
        showToast('暂无版本记录', 'info');
    }
}

async function optimizeResume() {
    const resumeId = document.getElementById('optimize-resume-select').value;
    const jobDesc = document.getElementById('job-description-text').value.trim();
    if (!resumeId) { showToast('请先选择一份简历', 'error'); return; }
    if (!jobDesc) { showToast('请输入职位描述', 'error'); return; }

    const btn = document.getElementById('optimize-resume-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="ri-loader-4-line"></i> 优化中...';

    const formData = new FormData();
    formData.append('job_description', jobDesc);
    const res = await apiPostForm(`${API.resume}/${resumeId}/optimize`, formData);

    btn.disabled = false;
    btn.innerHTML = '<i class="ri-sparkling-line"></i> AI 优化';

    const resultEl = document.getElementById('optimize-result');
    if (res && res.success) {
        resultEl.style.display = 'block';
        const opt = res.optimization || {};
        resultEl.innerHTML = `
            <h4>优化建议</h4>
            <ul>${(opt.suggestions || ['暂无具体建议']).map(s => `<li>${s}</li>`).join('')}</ul>
        `;
    } else {
        resultEl.style.display = 'block';
        resultEl.innerHTML = '<p>AI 优化服务暂不可用，请稍后重试</p>';
    }
}

// ======================== Analytics ========================
function switchAnalyticsTab(tab) {
    ['overview', 'comparison', 'goals', 'achievements'].forEach(t => {
        const el = document.getElementById(`analytics-${t}`);
        if (el) el.style.display = t === tab ? 'block' : 'none';
    });
    switch (tab) {
        case 'overview': loadAnalyticsOverview(); break;
        case 'comparison': loadComparison('week'); break;
        case 'goals': loadGoals(); break;
        case 'achievements': loadAchievements(); break;
    }
}

async function loadAnalytics() {
    loadAnalyticsOverview();
}

async function loadAnalyticsOverview() {
    const [dist, score, time, trend] = await Promise.all([
        apiGet(`${API.analytics}/category-distribution`),
        apiGet(`${API.analytics}/score-analysis`),
        apiGet(`${API.analytics}/time-analysis`),
        apiGet(`${API.analytics}/progress-trend?days=30`),
    ]);

    // Category distribution
    const catEl = document.getElementById('category-chart');
    if (dist && dist.distribution) {
        const d = dist.distribution;
        const lcRaw = d.leetcode || {};
        const ivRaw = d.interview || {};
        // 将对象值转为数字（兼容 {total, completed} 格式和纯数字）
        const lcData = {};
        for (const [k, v] of Object.entries(lcRaw)) {
            lcData[k] = typeof v === 'object' ? (v.total || 0) : v;
        }
        const ivData = {};
        for (const [k, v] of Object.entries(ivRaw)) {
            ivData[k] = typeof v === 'object' ? (v.total || 0) : v;
        }
        catEl.innerHTML = `
            <div style="width:100%;">
                <h4 style="margin-bottom:12px;">LeetCode 分类分布</h4>
                ${renderHorizontalBars(lcData, {})}
                <h4 style="margin:20px 0 12px;">面试题分类分布</h4>
                ${renderHorizontalBars(ivData, {})}
            </div>`;
    } else {
        catEl.innerHTML = '<div class="empty-state">暂无分布数据</div>';
    }

    // Score analysis
    const scoreEl = document.getElementById('score-analysis-content');
    if (score && score.analysis) {
        const a = score.analysis;
        scoreEl.innerHTML = `
            <div class="analysis-mini">
                ${a.weak_areas && a.weak_areas.length ? `<div><strong>薄弱领域:</strong> ${a.weak_areas.join(', ')}</div>` : ''}
                ${a.difficulty_performance ? `<div><strong>难度表现:</strong><pre>${JSON.stringify(a.difficulty_performance, null, 2)}</pre></div>` : ''}
            </div>`;
    } else {
        scoreEl.innerHTML = '<div class="empty-state">暂无分数数据</div>';
    }

    // Time analysis
    const timeEl = document.getElementById('time-analysis-content');
    if (time && time.analysis) {
        const a = time.analysis;
        timeEl.innerHTML = `
            <div class="analysis-mini">
                ${a.productivity_metrics ? `<div><strong>效率指标:</strong><pre>${JSON.stringify(a.productivity_metrics, null, 2)}</pre></div>` : ''}
                ${a.daily_pattern ? `<div><strong>每日模式:</strong><pre>${JSON.stringify(a.daily_pattern, null, 2)}</pre></div>` : ''}
            </div>`;
    } else {
        timeEl.innerHTML = '<div class="empty-state">暂无时间数据</div>';
    }

    // Trend
    const trendEl = document.getElementById('trend-content');
    if (trend && trend.trend_data && trend.trend_data.length) {
        // 只显示有数据的最近10天
        const nonEmpty = trend.trend_data.filter(t => t.leetcode_problems > 0 || t.interview_questions > 0 || t.total_time > 0);
        const displayData = (nonEmpty.length ? nonEmpty : trend.trend_data).slice(-10);
        trendEl.innerHTML = `<table class="data-table"><thead><tr>
            <th>日期</th><th>刷题数</th><th>面试题</th><th>学习时间(min)</th>
        </tr></thead><tbody>${displayData.map(t => `<tr>
            <td>${t.date}</td><td>${t.leetcode_problems}</td><td>${t.interview_questions}</td>
            <td>${t.total_time}</td>
        </tr>`).join('')}</tbody></table>
        <div class="trend-info">统计周期: ${trend.period || '30天'}</div>`;
    } else {
        trendEl.innerHTML = '<div class="empty-state">暂无趋势数据</div>';
    }
}

async function loadComparison(period) {
    const data = await apiGet(`${API.analytics}/comparison?period=${period}`);
    const el = document.getElementById('comparison-content');
    if (data && data.comparison) {
        const c = data.comparison;
        const m = c.metrics || {};
        el.innerHTML = `
            <div class="comparison-header">
                <span>${c.current_period || '当前'}</span> vs <span>${c.previous_period || '上期'}</span>
            </div>
            <div class="comparison-grid">
                ${Object.entries(m).map(([key, val]) => `
                    <div class="comparison-card">
                        <div class="comp-label">${formatMetricName(key)}</div>
                        <div class="comp-values">
                            <span class="comp-current">${val.current ?? '-'}</span>
                            <span class="comp-change ${(val.change||'').startsWith('+') ? 'positive' : 'negative'}">${val.change || '-'}</span>
                        </div>
                        <div class="comp-prev">上期: ${val.previous ?? '-'}</div>
                    </div>
                `).join('')}
            </div>`;
    } else {
        el.innerHTML = '<div class="empty-state">暂无对比数据</div>';
    }
}

async function loadGoals() {
    const data = await apiGet(`${API.analytics}/goals`);
    const el = document.getElementById('goals-content');
    if (data && data.goals) {
        const g = data.goals;
        el.innerHTML = `
            <h4 style="margin-bottom:12px;">进行中的目标</h4>
            <div class="goals-list">
                ${(g.active_goals || []).map(goal => `
                    <div class="goal-card">
                        <div class="goal-title">${goal.title}</div>
                        <div class="progress-bar-track"><div class="progress-bar-fill" style="width:${goal.progress||0}%;background:var(--accent)"></div></div>
                        <div class="goal-progress">${goal.progress || 0}%</div>
                    </div>
                `).join('') || '<div class="empty-state">暂无目标</div>'}
            </div>
            ${g.completed_goals && g.completed_goals.length ? `
                <h4 style="margin:20px 0 12px;">已完成的目标</h4>
                <div class="goals-list">${g.completed_goals.map(goal => `
                    <div class="goal-card completed"><div class="goal-title"><i class="ri-check-line"></i> ${goal.title}</div></div>
                `).join('')}</div>
            ` : ''}
            ${g.suggested_goals && g.suggested_goals.length ? `
                <h4 style="margin:20px 0 12px;">建议目标</h4>
                <div class="goals-list">${g.suggested_goals.map(goal => `
                    <div class="goal-card suggested"><div class="goal-title"><i class="ri-lightbulb-line"></i> ${typeof goal === 'string' ? goal : goal.title}</div></div>
                `).join('')}</div>
            ` : ''}
        `;
    } else {
        el.innerHTML = '<div class="empty-state">暂无目标数据</div>';
    }
}

async function loadAchievements() {
    const data = await apiGet(`${API.analytics}/achievements`);
    const el = document.getElementById('achievements-content');
    if (data && data.achievements) {
        const a = data.achievements;
        const stats = a.statistics || {};
        el.innerHTML = `
            <div class="achievement-stats">
                <div class="mini-stat"><span class="mini-val">${stats.unlocked_count || 0}/${stats.total || 0}</span><span class="mini-label">已解锁</span></div>
                <div class="mini-stat"><span class="mini-val">${(stats.completion_rate||0) > 1 ? Math.round(stats.completion_rate) : Math.round((stats.completion_rate||0)*100)}%</span><span class="mini-label">完成率</span></div>
            </div>
            <h4 style="margin:16px 0 12px;">已解锁</h4>
            <div class="achievements-grid">
                ${(a.unlocked || []).map(ach => `
                    <div class="achievement-card unlocked">
                        <i class="ri-trophy-line"></i>
                        <div class="ach-title">${ach.title}</div>
                        <div class="ach-desc">${ach.description}</div>
                        <div class="ach-date">${formatDate(ach.unlocked_at)}</div>
                    </div>
                `).join('') || '<div class="empty-state">暂无成就</div>'}
            </div>
            ${a.locked && a.locked.length ? `
                <h4 style="margin:20px 0 12px;">未解锁</h4>
                <div class="achievements-grid">${a.locked.map(ach => `
                    <div class="achievement-card locked">
                        <i class="ri-lock-line"></i>
                        <div class="ach-title">${ach.title}</div>
                        <div class="ach-desc">${ach.description}</div>
                    </div>
                `).join('')}</div>
            ` : ''}
        `;
    } else {
        el.innerHTML = '<div class="empty-state">暂无成就数据</div>';
    }
}

async function exportReport() {
    showToast('正在生成报告...', 'info');
    const res = await apiPost(`${API.analytics}/export-report?format=json&period=month`, {});
    if (res && res.success) {
        showToast(`报告已生成: ${res.filename || '学习报告'}`, 'success');
    } else {
        showToast('报告生成失败', 'error');
    }
}

// ======================== Modal ========================
function openModal(title, bodyHtml) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-body').innerHTML = bodyHtml;
    document.getElementById('modal-overlay').classList.add('show');
    document.getElementById('modal').classList.add('show');
}

function closeModal() {
    document.getElementById('modal-overlay').classList.remove('show');
    document.getElementById('modal').classList.remove('show');
}

// ======================== Toast ========================
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
}

// ======================== Helpers ========================
function setText(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
}

function difficultyClass(d) {
    if (!d) return 'medium';
    const dl = d.toLowerCase();
    if (dl === 'easy' || d === '简单' || d === '初级') return 'easy';
    if (dl === 'hard' || d === '困难' || d === '高级') return 'hard';
    return 'medium';
}

function formatDate(d) {
    if (!d) return '-';
    return new Date(d).toLocaleDateString('zh-CN');
}

function formatMetricName(key) {
    const map = {
        problems_solved: '解题数',
        study_time: '学习时间',
        average_score: '平均分',
        new_topics: '新主题',
    };
    return map[key] || key;
}

function renderHorizontalBars(data, colorMap) {
    const entries = Object.entries(data);
    if (!entries.length) return '<div class="empty-state">无数据</div>';
    const max = Math.max(...entries.map(([,v]) => v), 1);
    const defaultColors = ['var(--accent)', 'var(--success)', 'var(--warning)', 'var(--danger)', '#9b59b6', '#1abc9c'];
    return entries.map(([k, v], i) => {
        const color = colorMap[k] || defaultColors[i % defaultColors.length];
        const pct = Math.round(v / max * 100);
        return `<div class="progress-bar-item">
            <div class="bar-header"><span class="bar-label">${k}</span><span class="bar-value">${v}</span></div>
            <div class="progress-bar-track"><div class="progress-bar-fill" style="width:${pct}%;background:${color}"></div></div>
        </div>`;
    }).join('');
}
