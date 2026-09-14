/* PyStep: offline-first learning workspace, no third-party browser dependencies. */
(() => {
  'use strict';
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const json = value => JSON.stringify(value, null, 2) ?? 'null';
  const KEY = 'pystep.progress.v1';
  const emptyState = () => ({version:1, drafts:{}, accepted:[], attempts:{}, notes:{}, starred:[], theme:'light', lastProblem:null, guideSeen:false});
  let progress = emptyState();
  let storageWarning = false;
  try { const saved = JSON.parse(localStorage.getItem(KEY) || 'null'); if (saved) progress = validateProgress(saved); } catch (_) { storageWarning = true; }
  let problems = [], chapters = [], meta = {}, current = null, routeVersion = 0, busy = false, editorObserver = null;
  let detailTab = 'lesson', hintCount = 0, solutionVisible = false, latestResult = null, resultTab = 'tests', toastTimer;
  const cache = new Map();
  const phases = [
    {title:'Python 基础', from:1, to:9, icon:'{ }', desc:'从变量与循环开始，建立编程直觉。'},
    {title:'常用库与人工智能', from:10, to:18, icon:'◈', desc:'标准库、数据分析、可视化与机器学习。'},
    {title:'复试机考与算法', from:19, to:24, icon:'⌘', desc:'输入输出、数据结构与常见算法。'},
    {title:'全栈与工程实践', from:25, to:30, icon:'▤', desc:'数据库、后端 API 与前端基础。'}
  ];
  const labels = {home:'学习总览', problems:'练习题库', favorites:'我的收藏', review:'错题复习', problem:'开始练习', lab:'API 实验室'};
  function validateProgress(raw) {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw) || raw.version !== 1) throw new Error('备份格式不正确，或版本暂不支持。');
    const state = emptyState();
    const validId = id => /^[1-9]\d{0,5}$/.test(String(id));
    for (const key of ['accepted','starred']) {
      if (!Array.isArray(raw[key]) || raw[key].length > 10000 || raw[key].some(id => !Number.isInteger(id) || !validId(id))) throw new Error(`${key} 列表格式不正确。`);
      state[key] = [...new Set(raw[key])];
    }
    for (const key of ['drafts','notes','attempts']) {
      const data = raw[key];
      if (!data || typeof data !== 'object' || Array.isArray(data) || Object.keys(data).length > 10000) throw new Error(`${key} 数据格式不正确。`);
      for (const [id, value] of Object.entries(data)) {
        if (!validId(id)) throw new Error('备份中包含无效题号。');
        if (key !== 'attempts') {
          if (typeof value !== 'string' || value.length > 150000) throw new Error('代码或笔记过长，或格式不正确。');
          state[key][id] = value;
        } else {
          if (!value || typeof value !== 'object' || !Number.isInteger(value.count) || value.count < 0 || value.count > 10000000 || typeof value.lastStatus !== 'string' || value.lastStatus.length > 50 || !Number.isFinite(value.lastAt) || value.lastAt < 0) throw new Error('练习记录格式不正确。');
          state.attempts[id] = {count:value.count, lastStatus:value.lastStatus, lastAt:value.lastAt};
        }
      }
    }
    state.theme = raw.theme === 'dark' ? 'dark' : 'light';
    state.lastProblem = Number.isInteger(raw.lastProblem) && validId(raw.lastProblem) ? raw.lastProblem : null;
    state.guideSeen = raw.guideSeen === true;
    return state;
  }
  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(progress)); return true; }
    catch (_) { if (!storageWarning) toast('浏览器无法保存进度，请使用「导出进度」备份。'); storageWarning = true; return false; }
  }
  function toast(message) {
    $('#toast').textContent = message; $('#toast').classList.add('visible');
    clearTimeout(toastTimer); toastTimer = setTimeout(() => $('#toast').classList.remove('visible'), 3500);
  }
  function applyTheme() { document.body.classList.toggle('dark', progress.theme === 'dark'); $('#theme-toggle').setAttribute('aria-label', progress.theme === 'dark' ? '切换浅色模式' : '切换深色模式'); }
  const isAccepted = id => progress.accepted.includes(id);
  const isStarred = id => progress.starred.includes(id);
  const isReview = id => !isAccepted(id) && progress.attempts[id] && !['accepted','running'].includes(progress.attempts[id].lastStatus);
  const statusOf = id => isAccepted(id) ? 'accepted' : progress.attempts[id] ? 'attempted' : 'new';
  const language = p => ({sql:'SQL', javascript:'JavaScript', python:'Python'}[p.language || 'python'] || 'Python');
  const pad = id => String(id).padStart(2,'0');
  const percent = (n, total) => total ? Math.round(n / total * 100) : 0;
  function starButton(id, extra = '') { return `<button class="star-button ${isStarred(id) ? 'starred' : ''} ${extra}" data-star="${id}" aria-pressed="${isStarred(id)}" aria-label="${isStarred(id) ? '取消收藏' : '收藏题目'}" title="${isStarred(id) ? '取消收藏' : '收藏题目'}">${isStarred(id) ? '★' : '☆'}</button>`; }
  function difficulty(p) { return `<span class="difficulty ${p.difficulty === '挑战' ? 'hard' : p.difficulty === '进阶' ? 'medium' : ''}">${esc(p.difficulty)}</span>`; }
  function statusIcon(id) { const s = statusOf(id); return `<span class="problem-status ${s}" title="${{accepted:'已完成',attempted:'已尝试',new:'未开始'}[s]}" aria-label="${{accepted:'已完成',attempted:'已尝试',new:'未开始'}[s]}">${{accepted:'✓',attempted:'◔',new:'○'}[s]}</span>`; }
  async function api(path, options = {}) {
    const response = await fetch(path, options);
    let data; try { data = await response.json(); } catch (_) { throw new Error('服务器返回的内容无法读取，请重启本地服务后重试。'); }
    if (!response.ok) throw new Error(data.error?.message || `请求失败（HTTP ${response.status}）`);
    return data;
  }
  function inline(text) { return esc(text).replace(/`([^`]+)`/g, '<code>$1</code>').replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>'); }
  function markdown(text) {
    const blocks = String(text || '').split(/```[^\n]*\n([\s\S]*?)```/g);
    return blocks.map((block, i) => i % 2 ? `<pre><code>${esc(block.trimEnd())}</code></pre>` : block.split(/\n\s*\n/).filter(Boolean).map(paragraph => {
      if (/^#{1,4} /.test(paragraph)) return `<h3>${inline(paragraph.replace(/^#{1,4} /,''))}</h3>`;
      if (paragraph.split('\n').every(line => /^[-*] /.test(line))) return `<ul>${paragraph.split('\n').map(line => `<li>${inline(line.slice(2))}</li>`).join('')}</ul>`;
      return `<p>${paragraph.split('\n').map(inline).join('<br>')}</p>`;
    }).join('')).join('');
  }
  function setPage(kind) {
    document.body.classList.toggle('workbench', kind === 'problem');
    $('.breadcrumb > span').textContent = kind === 'problem' ? 'PyStep 工作台' : '学习空间';
    $('#page-label').textContent = labels[kind] || labels.home;
    $$('[data-nav]').forEach(a => { const active = a.dataset.nav === (kind === 'problem' ? 'problems' : kind); a.classList.toggle('active', active); if (active) a.setAttribute('aria-current','page'); else a.removeAttribute('aria-current'); });
    document.title = `${labels[kind] || 'PyStep'} · PyStep`;
  }
  function recentRow(p) { return `<a class="recent-row" href="#problem/${p.id}"><span class="recent-number">${pad(p.id)}</span><span class="recent-title">${esc(p.title)}<small>第 ${p.chapter} 章 · ${esc(p.chapter_title)}</small></span>${statusIcon(p.id)}<span class="recent-arrow">→</span></a>`; }
  function renderHome() {
    const done = problems.filter(p => isAccepted(p.id)).length;
    const attempted = problems.filter(p => progress.attempts[p.id]).length;
    const completedChapters = chapters.filter(c => problems.filter(p => p.chapter === c.id).every(p => isAccepted(p.id))).length;
    const next = problems.find(p => p.id === progress.lastProblem) || problems.find(p => !isAccepted(p.id)) || problems[0];
    const recent = problems.filter(p => progress.attempts[p.id]).sort((a,b) => progress.attempts[b.id].lastAt - progress.attempts[a.id].lastAt).slice(0,3);
    const totalAttempts = Object.values(progress.attempts).reduce((sum,a) => sum + a.count,0);
    $('#main-content').innerHTML = `<section class="welcome-header"><div><div class="eyebrow">ONE STEP AT A TIME</div><h1>${done ? '欢迎回来，继续向前一步。' : '你好，未来的开发者。'}</h1><p>从第一行代码开始，把「看懂了」变成「我会写」。</p></div><span class="date-label">${esc(new Date().toLocaleDateString('zh-CN',{month:'long',day:'numeric',weekday:'long'}))}</span></section>
      <section class="hero"><div class="hero-copy"><div class="eyebrow">YOUR LEARNING JOURNEY</div><h2>每一个小练习，<br>都是一次新的进步。</h2><p>${problems.length} 道循序渐进的练习，${chapters.length} 个主题章节。<br>读一点语法，写一点代码，让知识真正留下来。</p><div class="hero-actions"><a class="button primary" href="#problem/${next?.id || 1}">${progress.lastProblem ? '继续练习' : '开始第一题'} <span>→</span></a><span class="hero-count">已完成 ${done} / ${problems.length} 题</span></div></div><div class="hero-art" aria-hidden="true"><div class="mini-editor"><div class="mini-editor-top"><i></i><i></i><i></i><span>hello_future.py</span></div><pre><span class="purple">def</span> solve(a, b):
    <span class="purple">return</span> a + b

<span class="green"># 从一个小小的答案开始</span>
solve(2, 3)  <span class="green"># 5</span></pre></div><div class="art-sticker"><span>✓</span>每一次尝试，都算数</div></div></section>
      <section class="stats-grid" aria-label="学习统计">${[
        ['已完成练习',done,`/ ${problems.length}`,`总进度 ${percent(done,problems.length)}%`,'✓'],
        ['已解锁行动',attempted,'题','从尝试开始，慢慢变熟练','⌘'],
        ['完成章节',completedChapters,`/ ${chapters.length}`,'每章 10 题，循序渐进','▤'],
        ['累计提交',totalAttempts,'次','提交全部测试才计入完成','↗']
      ].map(([label,n,unit,sub,icon]) => `<div class="stat-card"><div class="stat-label">${label}<span class="stat-symbol">${icon}</span></div><div class="stat-number">${n}<small>${unit}</small></div><p class="stat-sub">${sub}</p></div>`).join('')}</section>
      <section><div class="section-heading"><div><h2>你的学习路线</h2><p>四个阶段，从 Python 入门走向更多可能。</p></div><a href="#problems">查看全部练习 →</a></div><div class="roadmap-grid">${phases.map((phase,i) => {
        const list = problems.filter(p => p.chapter >= phase.from && p.chapter <= phase.to), n = list.filter(p => isAccepted(p.id)).length;
        return `<a class="roadmap-card" href="#problems?phase=${i}"><span class="phase-icon">${phase.icon}</span><span class="phase-num">PHASE 0${i+1}</span><h3>${phase.title}</h3><p>${phase.desc}</p><div class="roadmap-progress"><i style="width:${percent(n,list.length)}%"></i></div><div class="roadmap-meta"><span>第 ${phase.from}–${phase.to} 章</span><span>${n} / ${list.length} 题</span></div></a>`;
      }).join('')}</div></section>
      <div class="home-bottom"><section class="recent-panel"><div class="section-heading"><h2>${recent.length ? '最近练习' : '从这些小练习开始'}</h2><a href="#review">错题复习 →</a></div>${(recent.length ? recent : problems.slice(0,3)).map(recentRow).join('')}</section><aside class="tip-panel"><div class="tip-kicker">A LITTLE REMINDER</div><h2>不着急看答案，<br>先和问题待一会儿。</h2><p>把输入、输出和每一步变化写下来。卡住时，先展开第一条提示。</p><button data-action="guide">阅读入门指南 →</button></aside></div>
      <section class="workspace-tools"><a class="button" href="#lab">打开 API 实验室 ↗</a><button class="button" data-action="export">导出进度</button><button class="button" data-action="import">导入进度</button><button class="button" data-action="guide">入门指南</button><button class="button text" data-action="reset-progress">清空学习记录</button></section><p class="home-credit">Contributed by <strong>ksy</strong></p>`;
  }
  function renderCatalog(kind, params) {
    const selected = {q:params.get('q') || '',chapter:params.get('chapter') || '',phase:params.get('phase') || '',status:params.get('status') || '',difficulty:params.get('difficulty') || '',language:params.get('language') || ''};
    const heading = {problems:['练习题库','每一题都是一个小台阶。按顺序练习，也可以选择感兴趣的主题。'],favorites:['我的收藏','把值得反复练习的题目，留在这里。'],review:['错题复习','收集尚未通过的提交，重新尝试后会自动移出。']}[kind];
    $('#main-content').innerHTML = `<div class="page-heading"><div><div class="eyebrow">PRACTICE MAKES PROGRESS</div><h1>${heading[0]}</h1><p>${heading[1]}</p></div><a class="button" href="#home">学习路线 ↗</a></div><div class="catalog-layout"><aside class="chapter-list" aria-label="章节筛选"><h3>全部 ${chapters.length} 个章节</h3><button class="chapter-button ${!selected.chapter ? 'active' : ''}" data-chapter=""><span>全部章节</span><small>${problems.length} 题</small></button>${chapters.map(c => `<button class="chapter-button ${Number(selected.chapter) === c.id ? 'active' : ''}" data-chapter="${c.id}"><b>${pad(c.id)}</b><span>${esc(c.title)}</span><small>${problems.filter(p => p.chapter === c.id && isAccepted(p.id)).length}/${c.count}</small></button>`).join('')}</aside><section class="catalog-main"><div class="filters"><label class="search-wrap"><span aria-hidden="true">⌕</span><input id="search" class="field" type="search" placeholder="搜索题号、标题或知识点…" aria-label="搜索题目" value="${esc(selected.q)}"></label><select id="filter-phase" class="field" aria-label="学习阶段"><option value="">全部阶段</option>${phases.map((p,i) => `<option value="${i}">${p.title}</option>`).join('')}</select><select id="filter-chapter" class="field chapter-select" style="display:none" aria-label="章节"><option value="">全部章节</option>${chapters.map(c => `<option value="${c.id}">${pad(c.id)} ${esc(c.title)}</option>`).join('')}</select><select id="filter-status" class="field" aria-label="完成状态"><option value="">全部状态</option><option value="new">未开始</option><option value="attempted">已尝试</option><option value="accepted">已完成</option></select><select id="filter-difficulty" class="field" aria-label="难度"><option value="">全部难度</option>${[...new Set(problems.map(p => p.difficulty))].map(d => `<option>${esc(d)}</option>`).join('')}</select><select id="filter-language" class="field" aria-label="语言"><option value="">全部语言</option><option value="python">Python</option><option value="sql">SQL</option><option value="javascript">JavaScript</option></select><button class="button small" id="clear-filters">重置筛选</button></div><p class="result-count" id="result-count" aria-live="polite"></p><div id="problem-list"></div></section></div>`;
    for (const key of ['phase','chapter','status','difficulty','language']) $(`#filter-${key}`).value = selected[key];
    const updateList = () => {
      selected.q = $('#search').value;
      for (const key of ['phase','chapter','status','difficulty','language']) selected[key] = $(`#filter-${key}`).value;
      const phase = selected.phase === '' ? null : phases[Number(selected.phase)];
      const q = selected.q.toLocaleLowerCase().trim();
      const list = problems.filter(p => (kind !== 'favorites' || isStarred(p.id)) && (kind !== 'review' || isReview(p.id)) && (!selected.chapter || p.chapter === Number(selected.chapter)) && (!phase || p.chapter >= phase.from && p.chapter <= phase.to) && (!selected.status || statusOf(p.id) === selected.status) && (!selected.difficulty || p.difficulty === selected.difficulty) && (!selected.language || (p.language || 'python') === selected.language) && (!q || `${p.id} ${p.title} ${p.chapter_title} ${(p.tags || []).join(' ')} ${p.description}`.toLocaleLowerCase().includes(q)));
      $('#result-count').textContent = `共 ${list.length} 道练习 · ✓ 已完成　◔ 已尝试　○ 未开始`;
      $('#problem-list').innerHTML = list.length ? `<div class="problem-table"><div class="problem-table-head"><span>状态</span><span>题目 / 知识点</span><span>难度</span><span class="language-tag">语言</span><span>收藏</span></div>${list.map(p => `<div class="problem-row" data-problem="${p.id}">${statusIcon(p.id)}<div class="problem-name"><a href="#problem/${p.id}">${pad(p.id)}. ${esc(p.title)}</a><small>第 ${p.chapter} 章 · ${esc(p.chapter_title)}</small></div>${difficulty(p)}<span class="language-tag">${language(p)}</span>${starButton(p.id)}</div>`).join('')}</div>` : `<div class="panel empty-state"><div class="empty-icon">${kind === 'favorites' ? '☆' : '◎'}</div><h3>${kind === 'review' && !q ? '这里暂时没有待复习的错题' : '还没有匹配的练习'}</h3><p>${kind === 'favorites' ? '点击题目旁的星星，即可加入收藏。' : '试着切换章节或清除筛选条件。'}</p><a class="button" href="#problems">浏览全部题库 →</a></div>`;
      const query = new URLSearchParams(Object.entries(selected).filter(([,v]) => v !== '')).toString();
      history.replaceState(null,'',`#${kind}${query ? '?' + query : ''}`);
      $$('.chapter-button').forEach(b => b.classList.toggle('active',b.dataset.chapter === selected.chapter));
    };
    $('#search').addEventListener('input',updateList);
    $$('.filters select').forEach(s => s.addEventListener('change',updateList));
    $$('.chapter-button').forEach(b => b.addEventListener('click',() => { $('#filter-chapter').value = b.dataset.chapter; $('#filter-phase').value = ''; updateList(); }));
    $('#clear-filters').onclick = () => { $('#search').value = ''; $$('.filters select').forEach(s => s.value = ''); updateList(); };
    updateList();
  }
  function dependencyBanner(p) {
    const req = [...(p.requires || [])]; if (p.language === 'javascript' && !req.includes('node')) req.push('node');
    const missing = req.filter(name => meta.dependencies?.[name]?.available !== true);
    if (!missing.length) return '';
    const pip = missing.filter(name => name !== 'node').map(name => name === 'sklearn' ? 'scikit-learn' : name);
    return `<div class="dependency-banner">此题需要 ${missing.map(esc).join('、')}，当前环境尚未就绪。${pip.length ? `<code>python -m pip install ${pip.join(' ')}</code>` : ''}${missing.includes('node') ? '<p>请安装 Node.js，并重启本地平台。</p>' : ''}安装后重启平台并刷新页面，即可运行。</div>`;
  }
  async function renderProblem(id, token) {
    $('#main-content').innerHTML = '<div class="loading-screen"><span class="spinner"></span><p>正在打开练习…</p></div>';
    const p = cache.get(id) || await api(`/api/problems/${id}`); cache.set(id,p);
    if (token !== routeVersion) return;
    current = p; detailTab = 'lesson'; hintCount = 0; solutionVisible = false; latestResult = null;
    progress.lastProblem = p.id; save();
    document.title = `${p.id}. ${p.title} · PyStep`;
    const index = problems.findIndex(item => item.id === p.id), prev = problems[index-1], next = problems[index+1];
    const editorInfo = p.language === 'sql' ? 'SQLite · 编写 SELECT / WITH 查询' : p.language === 'javascript' ? `JavaScript · Node.js ${esc(meta.dependencies?.node?.version || '')}` : `Python ${esc(meta.python || '3')}`;
    $('#main-content').innerHTML = `<div class="practice-top"><a class="practice-back" href="#problems?chapter=${p.chapter}">← 返回题库 <span>/ 第 ${p.chapter} 章</span></a><div class="practice-pager">${prev ? `<a class="icon-button" href="#problem/${prev.id}" aria-label="上一题" title="上一题（Alt + ←）">←</a>` : '<button class="icon-button" disabled aria-label="已是第一题">←</button>'}<span>${index+1} / ${problems.length}</span>${next ? `<a class="icon-button" href="#problem/${next.id}" aria-label="下一题" title="下一题（Alt + →）">→</a>` : '<button class="icon-button" disabled aria-label="已是最后一题">→</button>'}</div></div><div class="practice-grid"><section class="panel problem-panel"><div class="panel-tabs" role="tablist" aria-label="题目内容">${[['lesson','题目与课堂'],['hints','提示'],['solution','参考答案'],['notes','笔记']].map(([tab,label]) => `<button class="panel-tab ${tab === detailTab ? 'active' : ''}" id="tab-${tab}" data-tab="${tab}" role="tab" aria-selected="${tab === detailTab}" aria-controls="problem-body">${label}</button>`).join('')}${starButton(p.id,'panel-star')}</div><div class="problem-body" id="problem-body" role="tabpanel" aria-labelledby="tab-lesson"></div></section><div class="editor-column">${dependencyBanner(p)}<section class="panel editor-panel"><div class="editor-heading"><span class="editor-label"><i class="editor-dot"></i>${editorInfo}</span><div class="editor-tools"><span>自动保存</span><button id="reset-code" aria-label="重置代码" title="重置为初始代码">↺</button></div></div><div class="editor-surface"><div class="line-numbers" id="line-numbers" aria-hidden="true"></div><textarea id="code-editor" class="code-input" aria-label="代码编辑器" spellcheck="false" autocapitalize="off" autocomplete="off" autocorrect="off" wrap="off"></textarea></div><div class="editor-footnote"><span id="save-status">草稿保存在当前浏览器</span><span>Tab 缩进 · Ctrl / ⌘ + Enter 运行</span></div><div class="editor-actions"><label class="custom-toggle"><input type="checkbox" id="custom-enabled">自定义测试</label><div class="actions-right"><button id="run-code" class="button">▷ 运行示例</button><button id="submit-code" class="button primary">提交检查 ↑</button></div></div><div class="custom-input-wrap" id="custom-wrap" hidden><label for="custom-args">输入 JSON 参数数组（按下方参数顺序）</label><textarea id="custom-args" class="field" spellcheck="false">${esc(json(p.examples?.[0]?.args || []))}</textarea><p>${p.language === 'sql' ? 'SQL 参数为 [{"表名": [[行数据], …]}]，每次使用独立数据库。' : '例如两个数字用 [2, 3]；一个列表参数用 [[1, 2, 3]]。'}自定义运行只查看结果，不计入完成。</p></div></section><section class="panel results-panel" id="results-panel" aria-live="polite"><div class="results-heading">运行结果<span>真实执行 · 本地判题</span></div><div id="result-body"><div class="results-empty"><span class="terminal-icon">&gt;_</span><p>写下你的第一行代码，点击「运行示例」。</p><span>先验证示例，再提交全部测试。</span></div></div></section></div></div>`;
    mountWorkbench(p, editorInfo);
    const editor = $('#code-editor'); editor.value = progress.drafts[p.id] ?? p.starter ?? ''; updateLines();
    editor.addEventListener('input',() => { progress.drafts[p.id] = editor.value; const ok = save(); $('#save-status').textContent = ok ? '草稿已保存' : '保存失败，请导出备份'; updateLines(); });
    editor.addEventListener('scroll',() => { $('#line-numbers').scrollTop = editor.scrollTop; syncHighlight(); });
    editor.addEventListener('keydown',editorKeys);
    if (window.ResizeObserver) { editorObserver = new ResizeObserver(() => { const lines = $('#line-numbers'); if (lines && editor.isConnected) lines.style.height = `${editor.clientHeight}px`; syncHighlight(); }); editorObserver.observe(editor); }
    $('#custom-enabled').onchange = e => { $('#custom-wrap').hidden = !e.target.checked; $('#run-code').textContent = e.target.checked ? '▷ 运行自定义' : '▷ 运行示例'; };
    $('#run-code').onclick = () => execute('run'); $('#submit-code').onclick = () => execute('submit');
    $('#reset-code').onclick = () => { if (confirm('将当前代码恢复为题目的初始代码？这会覆盖此题草稿。')) { editor.value = p.starter; editor.dispatchEvent(new Event('input')); toast('已恢复初始代码'); } };
    renderDetail();
  }
  function mountWorkbench(p, editorInfo) {
    const main = $('#main-content');
    const filename = p.language === 'sql' ? 'query.sql' : p.language === 'javascript' ? 'solution.js' : 'solution.py';
    resultTab = 'tests';
    main.insertAdjacentHTML('afterbegin',`<nav class="activity-bar" aria-label="工作台导航"><a href="#home" class="activity-brand" title="返回学习总览" aria-label="返回学习总览">p</a><button class="activity-icon active" data-activity="lesson" title="题目与课堂" aria-label="题目与课堂">▤</button><a class="activity-icon" href="#problems" title="搜索题库" aria-label="搜索题库">⌕</a><button class="activity-icon" data-activity="hints" title="分步提示" aria-label="分步提示">◇</button><button class="activity-icon" data-activity="notes" title="学习笔记" aria-label="学习笔记">✎</button><a class="activity-icon" href="#lab" title="API 实验室" aria-label="API 实验室">⇄</a><button class="activity-icon activity-help" data-action="guide" title="入门指南" aria-label="入门指南">?</button></nav>`);
    $('.practice-top').classList.add('workbench-commandbar');
    $('.practice-top').insertAdjacentHTML('beforeend','<div class="workbench-run-actions"><button class="button" id="toolbar-run" title="运行示例（Ctrl + Enter）">▷ 运行</button><button class="button primary" id="toolbar-submit">✓ 提交检查</button></div>');
    $('.problem-panel').insertAdjacentHTML('afterbegin',`<div class="explorer-heading"><span>资源管理器 · 学习任务</span><span>···</span></div><div class="explorer-folder">⌄ &nbsp;第 ${pad(p.chapter)} 章 · ${esc(p.chapter_title)}</div><div class="explorer-file"><span class="file-icon markdown-icon">M↓</span> README.md <span>题目说明</span></div>`);
    $('.editor-heading').classList.add('editor-filebar');
    $('.editor-label').innerHTML = `<span class="file-icon ${p.language === 'javascript' ? 'js-icon' : p.language === 'sql' ? 'sql-icon' : 'python-icon'}">${p.language === 'javascript' ? 'JS' : p.language === 'sql' ? '▤' : 'Py'}</span><span>${filename}</span><span id="file-dirty" class="file-dirty" title="已保存到本机浏览器">●</span>`;
    $('.editor-label').title = editorInfo.replace(/<[^>]+>/g,'');
    $('.editor-surface').insertAdjacentHTML('beforebegin',`<div class="editor-breadcrumb">练习 &nbsp;›&nbsp; ${pad(p.id)} &nbsp;›&nbsp; ${filename} &nbsp;›&nbsp; <span>${p.language === 'sql' ? '查询' : 'solve'}</span></div>`);
    $('.editor-surface').insertAdjacentHTML('beforeend','<pre class="code-highlight" id="code-highlight" aria-hidden="true"></pre>');
    $('.results-heading').innerHTML = `<div class="workbench-panel-tabs" role="tablist" aria-label="运行面板">${[['problems','问题'],['output','输出'],['terminal','终端'],['tests','测试']].map(([key,label]) => `<button role="tab" class="workbench-panel-tab ${key === 'tests' ? 'active' : ''}" data-result-tab="${key}" aria-selected="${key === 'tests'}">${label}</button>`).join('')}</div><span>本地执行</span>`;
    main.insertAdjacentHTML('beforeend',`<div class="workbench-statusbar"><span class="statusbar-left">⌘ 本地工作区 <span class="statusbar-connection">✓ 已连接</span></span><span class="statusbar-right"><span id="cursor-status">行 1，列 1</span><span>空格: 4</span><span>UTF-8</span><span>${language(p)}</span></span></div>`);
    $('#toolbar-run').onclick = () => execute('run'); $('#toolbar-submit').onclick = () => execute('submit');
    $('#code-editor').addEventListener('click',updateCursor);
    $('#code-editor').addEventListener('keyup',updateCursor);
    $('#code-editor').addEventListener('input',() => { updateCursor(); const dot = $('#file-dirty'); if (dot) { dot.classList.add('saved'); dot.title = '草稿已自动保存'; } });
  }
  function updateCursor() {
    const editor = $('#code-editor'), label = $('#cursor-status'); if (!editor || !label) return;
    const before = editor.value.slice(0,editor.selectionStart), lines = before.split('\n');
    label.textContent = `行 ${lines.length}，列 ${lines[lines.length-1].length+1}`;
  }
  function updateLines() {
    const editor = $('#code-editor'), lines = $('#line-numbers'); if (!editor || !lines) return;
    lines.textContent = Array.from({length:editor.value.split('\n').length},(_,i) => i+1).join('\n'); lines.scrollTop = editor.scrollTop;
    highlightCode();
  }
  function highlightCode() {
    const editor = $('#code-editor'), highlight = $('#code-highlight'); if (!editor || !highlight) return;
    const lang = current?.language || 'python';
    const keywords = new Set((lang === 'sql' ? 'SELECT FROM WHERE AND OR NOT AS JOIN LEFT RIGHT INNER OUTER ON GROUP BY HAVING ORDER ASC DESC LIMIT OFFSET DISTINCT WITH UNION ALL CASE WHEN THEN ELSE END IS NULL IN LIKE BETWEEN EXISTS OVER PARTITION CREATE TABLE INSERT INTO VALUES COUNT SUM AVG MIN MAX' : lang === 'javascript' ? 'async await function return const let var if else for while do break continue switch case default class new this throw try catch finally typeof instanceof in of import from export true false null undefined' : 'def return if else elif for while in not and or is None True False import from as class try except finally raise with pass break continue lambda yield global nonlocal assert del async await').split(' '));
    const builtins = new Set('solve print len range enumerate zip list dict set tuple str int float bool sum min max sorted reversed abs round map filter isinstance any all input open console log JSON Math Array Object Number String Promise'.split(' '));
    const tokenPattern = lang === 'python' ? /("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|#[^\n]*|\b\d+(?:\.\d+)?\b|\b[A-Za-z_]\w*\b)/g : lang === 'sql' ? /('(?:''|[^'])*'|"(?:""|[^"])*"|--[^\n]*|\/\*[\s\S]*?\*\/|\b\d+(?:\.\d+)?\b|\b[A-Za-z_]\w*\b)/g : /("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`|\/\/[^\n]*|\/\*[\s\S]*?\*\/|\b\d+(?:\.\d+)?\b|\b[A-Za-z_$][\w$]*\b)/g;
    let offset = 0, html = '';
    for (const match of editor.value.matchAll(tokenPattern)) {
      const word = match[0]; html += esc(editor.value.slice(offset,match.index));
      const type = /^(#|\/\/|\/\*|--)/.test(word) ? 'comment' : /^["'`]/.test(word) ? 'string' : /^\d/.test(word) ? 'number' : keywords.has(lang === 'sql' ? word.toUpperCase() : word) ? 'keyword' : builtins.has(word) ? 'function' : '';
      html += type ? `<span class="syntax-${type}">${esc(word)}</span>` : esc(word); offset = match.index + word.length;
    }
    highlight.innerHTML = html + esc(editor.value.slice(offset)) + '\n'; syncHighlight();
  }
  function syncHighlight() {
    const editor = $('#code-editor'), highlight = $('#code-highlight'); if (!editor || !highlight) return;
    highlight.style.width = `${editor.clientWidth}px`; highlight.style.height = `${editor.clientHeight}px`;
    highlight.scrollTop = editor.scrollTop; highlight.scrollLeft = editor.scrollLeft;
  }
  function editorKeys(event) {
    const el = event.currentTarget;
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') { event.preventDefault(); execute(event.shiftKey ? 'submit' : 'run'); return; }
    if (event.key === 'Tab') {
      event.preventDefault(); const start = el.selectionStart, end = el.selectionEnd;
      if (start === end && !event.shiftKey) { el.setRangeText('    ',start,end,'end'); }
      else {
        const lineStart = el.value.lastIndexOf('\n',start-1)+1;
        const block = el.value.slice(lineStart,end);
        const updated = block.split('\n').map(line => event.shiftKey ? line.replace(/^( {1,4}|\t)/,'') : `    ${line}`).join('\n');
        el.setRangeText(updated,lineStart,end,'select');
      }
      el.dispatchEvent(new Event('input'));
    } else if (event.key === 'Enter' && !event.ctrlKey && !event.metaKey) {
      event.preventDefault(); const start = el.selectionStart, lineStart = el.value.lastIndexOf('\n',start-1)+1;
      const line = el.value.slice(lineStart,start), indent = line.match(/^\s*/)[0];
      const extra = /[:{]\s*$/.test(line) ? '    ' : '';
      el.setRangeText(`\n${indent}${extra}`,start,el.selectionEnd,'end'); el.dispatchEvent(new Event('input'));
    }
  }
  function renderDetail() {
    const p = current, body = $('#problem-body'); if (!p || !body) return;
    $$('.panel-tab').forEach(b => { b.classList.toggle('active',b.dataset.tab === detailTab); b.setAttribute('aria-selected',String(b.dataset.tab === detailTab)); });
    body.setAttribute('aria-labelledby',`tab-${detailTab}`);
    const heading = `<div class="problem-heading"><h1><span class="problem-id">${pad(p.id)}.</span>${esc(p.title)}</h1></div><div class="problem-tags">${difficulty(p)}<span class="tag">${language(p)}</span>${(p.requires || []).map(r => `<span class="tag">${esc(r)} ${meta.dependencies?.[r]?.available ? '✓' : '待安装'}</span>`).join('')}<span class="tag">第 ${p.chapter} 章</span>${isAccepted(p.id) ? '<span class="tag accepted-tag">✓ 已完成</span>' : ''}</div>`;
    if (detailTab === 'lesson') body.innerHTML = `${heading}<section class="content-section"><h3><span class="section-mark">01</span> 先学一点：小课堂</h3><div class="prose">${markdown(p.concept)}</div></section><section class="content-section"><h3><span class="section-mark">02</span> 你的任务</h3><div class="prose">${markdown(p.description)}</div></section>${p.parameters?.length ? `<section class="content-section"><h3>参数说明</h3><div class="table-scroll"><table class="parameter-table"><thead><tr><th>参数</th><th>类型</th><th>含义</th></tr></thead><tbody>${p.parameters.map(a => `<tr><td><code>${esc(a.name)}</code></td><td>${esc(a.type)}</td><td>${esc(a.description)}</td></tr>`).join('')}</tbody></table></div></section>` : ''}${p.setup_sql ? `<section class="content-section"><h3>数据表结构</h3><div class="prose"><pre><code>${esc(p.setup_sql)}</code></pre></div><p class="muted">测试会把示例参数中的行插入对应数据表，然后执行你的查询。请按题目要求排序结果。</p></section>` : ''}<section class="content-section"><h3><span class="section-mark">03</span> 看看示例</h3>${(p.examples || []).map((ex,i) => `<div class="example-card"><strong>示例 ${i+1}</strong><div class="example-line"><span>输入</span><code>${esc(json(ex.args))}</code></div><div class="example-line"><span>输出</span><code>${esc(json(ex.expected))}</code></div></div>`).join('')}</section><div class="lesson-callout content-section"><h3>${p.language === 'sql' ? '写出真实 SQL 查询' : p.language === 'javascript' ? '在 Node.js 中运行 solve' : '小提醒：return 和 print 不一样'}</h3><p>${p.language === 'sql' ? '直接编写 SELECT / WITH 查询即可；查询结果按行组成数组返回。' : p.language === 'javascript' ? '返回题目要求的结果。Node.js 没有浏览器 DOM；HTML / CSS 题比较返回的字符串，不验证页面渲染效果。' : '用 return 返回题目要求的结果；print 只会显示在标准输出中。平台会自动调用 solve，无需手动读取 input()。'}</p></div>`;
    if (detailTab === 'hints') body.innerHTML = `${heading}<div class="lesson-callout"><h3>一点一点接近答案</h3><p>先读一条提示，回到编辑器试一试。下一条会给出更具体的方向。</p></div>${(p.hints || []).slice(0,hintCount).map((h,i) => `<div class="hint-card"><h3>提示 ${i+1} / ${(p.hints || []).length}</h3><div class="prose">${markdown(h)}</div></div>`).join('')}${hintCount < (p.hints || []).length ? `<button class="hint-action" data-action="next-hint">${hintCount ? '再给我一点提示' : '展开第一条提示'} ＋</button>` : '<p class="muted">已经展开全部提示。试着把思路变成代码吧。</p>'}`;
    if (detailTab === 'solution') body.innerHTML = `${heading}${solutionVisible ? `<div class="solution-code"><pre><code>${esc(p.solution)}</code></pre></div><div class="code-toolbar"><span>参考实现 · ${language(p)}</span><button class="button small" data-action="use-solution">填入编辑器</button></div><section class="content-section"><h3>为什么这样写</h3><div class="prose">${markdown(p.explanation)}</div></section><p class="muted content-section">看懂以后，试着重置代码，独立再写一次。</p>` : '<div class="solution-cover"><span class="cover-icon">◇</span><h3>先给自己一次尝试的机会</h3><p>参考答案包含完整代码和逐步讲解。<br>如果还没有思路，可以先看看提示。</p><button class="button primary" data-action="reveal-solution">展开参考答案</button></div>'}`;
    if (detailTab === 'notes') { body.innerHTML = `${heading}<div class="lesson-callout"><h3>把自己的理解留下来</h3><p>可以记下犯过的错误、一个新的写法，或下次复习想问自己的问题。</p></div><label for="problem-notes" class="muted">我的学习笔记</label><textarea id="problem-notes" class="field notes-field" maxlength="100000" placeholder="今天我学会了…">${esc(progress.notes[p.id] || '')}</textarea><p class="note-status" id="note-status">笔记自动保存在当前浏览器，并包含在进度备份里。</p>`; $('#problem-notes').oninput = e => { progress.notes[p.id] = e.target.value; $('#note-status').textContent = save() ? '笔记已保存' : '保存失败，请导出备份'; }; }
  }
  async function execute(mode) {
    if (busy || !current || !$('#code-editor')) return;
    const p = current, code = $('#code-editor').value, routeAtStart = routeVersion;
    if (!code.trim()) { toast('先写一点代码，再运行吧。'); return; }
    const body = {problem_id:p.id,code,mode};
    if (mode === 'run' && $('#custom-enabled').checked) {
      try { body.custom_args = JSON.parse($('#custom-args').value); if (!Array.isArray(body.custom_args)) throw new Error(); }
      catch (_) { toast('自定义输入必须是有效的 JSON 参数数组，例如 [2, 3]。'); $('#custom-args').focus(); return; }
      if (p.parameters && body.custom_args.length !== p.parameters.length) { toast(`此题需要 ${p.parameters.length} 个参数，请检查最外层数组的长度。`); $('#custom-args').focus(); return; }
    }
    busy = true; resultTab = 'tests'; $('#run-code').disabled = true; $('#submit-code').disabled = true;
    $$('.workbench-run-actions button').forEach(button => button.disabled = true);
    $('#result-body').innerHTML = `<div class="results-empty"><span class="spinner"></span><p>${mode === 'submit' ? '正在检查全部测试，包括边界情况…' : '正在运行你的代码…'}</p></div>`;
    progress.drafts[p.id] = code; save();
    try {
      const result = await api('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
      if (mode === 'submit') {
        const previous = progress.attempts[p.id];
        progress.attempts[p.id] = {count:(previous?.count || 0)+1,lastStatus:result.status,lastAt:Date.now()};
        if (result.status === 'accepted' && !isAccepted(p.id)) progress.accepted.push(p.id);
        save();
      }
      if (routeAtStart === routeVersion && current?.id === p.id) { latestResult = result; renderResult(); if (mode === 'submit' && result.status === 'accepted') { renderDetail(); toast('提交通过！又向前迈了一步。'); } }
      else toast(`${p.id}. ${p.title}：${result.status === 'accepted' ? mode === 'submit' ? '提交通过' : '运行成功' : '运行结束'}`);
    } catch (error) {
      if (routeAtStart === routeVersion) { latestResult = {status:'error',mode,error:{type:'连接或请求错误',message:error.message,hint:'确认本地服务仍在运行，然后重试。'},cases:[],passed:0,total:0}; renderResult(); }
      else toast(error.message);
    } finally { busy = false; if ($('#run-code')) $('#run-code').disabled = false; if ($('#submit-code')) $('#submit-code').disabled = false; $$('.workbench-run-actions button').forEach(button => button.disabled = false); }
  }
  function renderError(error) {
    if (!error) return '';
    if (typeof error === 'string') return `<div class="error-card"><p>${esc(error)}</p></div>`;
    return `<div class="error-card"><strong>${esc(error.type || '执行错误')}${error.line ? ` · 第 ${Number(error.line)} 行` : ''}</strong><p>${esc(error.message)}</p>${error.hint ? `<p>建议：${esc(error.hint)}</p>` : ''}${error.line ? `<button data-error-line="${Number(error.line)}">定位到编辑器第 ${Number(error.line)} 行 →</button>` : ''}${error.traceback ? `<details><summary>查看详细错误信息</summary><pre class="traceback">${esc(error.traceback)}</pre></details>` : ''}</div>`;
  }
  function renderResult(selectedCase = 0) {
    const result = latestResult; if (!$('#result-body')) return;
    $$('.workbench-panel-tab').forEach(button => { const active = button.dataset.resultTab === resultTab; button.classList.toggle('active',active); button.setAttribute('aria-selected',String(active)); });
    if (!result) { $('#result-body').innerHTML = `<div class="results-empty"><span class="terminal-icon">&gt;_</span><p>${resultTab === 'terminal' ? '执行日志会显示在这里。此面板用于查看代码执行记录，不提供系统命令输入。' : resultTab === 'output' ? 'print / console.log 的真实标准输出会显示在这里。' : resultTab === 'problems' ? '运行后，这里会显示代码错误与失败测试。' : '写下代码，点击「运行」检查公开示例，再提交全部测试。'}</p></div>`; return; }
    if (resultTab === 'output') { $('#result-body').innerHTML = `<div class="result-content"><p class="result-caption">标准输出 · 这是 print / console.log 输出，不是函数返回值。</p><pre class="terminal-output">${esc((result.cases || []).map((item,i) => `用例 ${i+1}\n${item.stdout || '（没有标准输出）'}`).join('\n\n') || '（没有标准输出）')}</pre></div>`; return; }
    if (resultTab === 'terminal') { $('#result-body').innerHTML = `<div class="result-content"><p class="result-caption">本地执行日志 · ${language(current)} · ${result.mode === 'submit' ? '提交全部测试' : '运行测试'}</p><pre class="terminal-output">${esc(`> ${result.mode === 'submit' ? '提交检查' : '运行代码'}\n状态: ${result.status}\n测试: ${result.passed || 0} / ${result.total || 0}\n耗时: ${result.duration_ms == null ? '—' : Math.round(result.duration_ms) + ' ms'}\n${result.error ? '\n' + (result.error.traceback || result.error.message || '') : '\n执行结束。'}`)}</pre></div>`; return; }
    if (resultTab === 'problems') { const failed = (result.cases || []).filter(c => !c.passed); $('#result-body').innerHTML = `<div class="result-content">${renderError(result.error)}${failed.map((c,i) => `<div class="error-card"><strong>失败测试 ${i+1}</strong>${c.error ? renderError(c.error) : `<p>预期：${esc(json(c.expected))}</p><p>实际：${esc(json(c.actual))}</p>`}</div>`).join('')}${!result.error && !failed.length ? '<p class="result-caption">✓ 本次执行没有报告问题。运行示例后仍需提交全部测试，才能完成本题。</p>' : ''}</div>`; return; }
    const ok = result.status === 'accepted', custom = result.cases?.some(c => c.custom);
    const title = ok ? custom ? '自定义运行成功' : result.mode === 'submit' ? '全部通过，做得好！' : '示例通过，试着提交吧' : ({wrong_answer:'结果还差一点',syntax_error:'代码语法需要调整',runtime_error:'运行遇到问题',timeout:'运行超时',missing_dependency:'需要安装依赖',error:'请求未能完成'}[result.status] || '运行未通过');
    const c = result.cases?.[selectedCase];
    const next = problems[problems.findIndex(p => p.id === current.id)+1];
    $('#result-body').innerHTML = `<div class="result-content"><div class="result-summary ${ok ? '' : 'failed'}"><strong>${ok ? '✓' : '↺'} ${title}</strong><small>${result.duration_ms != null ? `${Math.round(result.duration_ms)} ms` : ''}</small></div><p class="result-caption">${custom ? '自定义输入没有预设答案，本次只检查能否正常执行，不计入完成。' : `${result.passed || 0} / ${result.total || 0} 个测试通过。${result.mode === 'run' ? '运行示例不计入完成；点击「提交检查」验证全部测试。' : ok ? '本题已计入学习进度。' : '比较输入、预期输出与实际输出，修正后再试一次。'}`}</p>${renderError(result.error)}${result.cases?.length ? `<div class="case-tabs" aria-label="测试用例">${result.cases.map((item,i) => `<button class="case-tab ${item.passed ? '' : 'failed'} ${i === selectedCase ? 'active' : ''}" data-case="${i}">${item.passed ? '✓' : '×'} ${item.custom ? '自定义' : `用例 ${i+1}`}</button>`).join('')}</div>` : ''}${c ? `<div class="case-details"><div class="case-value"><label>输入参数</label><pre>${esc(json(c.args))}</pre></div>${!c.custom ? `<div class="case-value"><label>预期输出</label><pre>${esc(json(c.expected))}</pre></div>` : ''}<div class="case-value ${!c.passed ? 'wrong' : ''}"><label>实际返回值</label><pre>${esc(json(c.actual))}</pre></div><div class="case-value"><label>标准输出（print / console.log）</label><pre>${esc(c.stdout || '（没有标准输出）')}</pre></div>${c.error && !result.error ? renderError(c.error) : ''}</div>` : ''}${ok && result.mode === 'submit' && next ? `<a class="button primary next-success" href="#problem/${next.id}">继续下一题：${esc(next.title)} →</a>` : ''}</div>`;
  }
  function renderLab() {
    current = null;
    $('#main-content').innerHTML = `<div class="page-heading"><div><div class="eyebrow">FRONTEND MEETS BACKEND</div><h1>API 实验室</h1><p>发送一个真实请求，看看前端和后端如何通过 JSON 交流。</p></div><a class="button" href="#problems?chapter=27">练习 HTTP 与 API →</a></div><div class="lab-grid"><section class="panel lab-request"><h2>1. 配置请求</h2><p class="muted">请求发送到正在运行的本地 Python 服务。</p><label for="lab-endpoint">选择接口</label><select id="lab-endpoint" class="field"><option value="list">GET · 查询商品列表</option><option value="item">GET · 按编号查找商品</option><option value="echo">POST · 回传 JSON</option></select><div id="lab-fields"></div><div class="request-preview" id="request-preview"></div><button id="lab-send" class="button primary">发送请求 →</button></section><section class="panel lab-response"><div class="section-heading"><h2>2. 观察响应</h2><span id="lab-status" class="tag">等待发送</span></div><p class="muted">状态码表示请求结果；响应体是后端返回的数据。</p><pre id="lab-output">点击「发送请求」，查看真实响应。</pre></section></div><section class="panel lab-code"><div class="section-heading"><div><h2>3. 用代码发出同一个请求</h2><p>浏览器使用 fetch，Python 使用标准库 urllib。</p></div></div><div class="lab-code-grid"><div><h3>JavaScript · 浏览器控制台</h3><pre id="lab-js"></pre></div><div><h3>Python · 本地脚本</h3><pre id="lab-python"></pre></div></div><p class="muted">这个网页也在使用 fetch 请求后端。试着查找不存在的商品编号，观察 404；POST 回传接口只回显数据，不保存记录。</p></section>`;
    $('#lab-endpoint').onchange = updateLabFields;
    $('#lab-send').onclick = sendLab;
    updateLabFields();
  }
  function updateLabFields() {
    const kind = $('#lab-endpoint').value;
    $('#lab-fields').innerHTML = kind === 'list' ? '<label for="lab-q">名称关键词 q</label><input class="field" id="lab-q" value="Python"><label for="lab-limit">最多返回数量 limit（1–20）</label><input class="field" id="lab-limit" type="number" min="1" max="20" value="2">' : kind === 'item' ? '<label for="lab-id">商品编号</label><input class="field" id="lab-id" type="number" min="1" value="1">' : '<label for="lab-json">JSON 请求体</label><textarea class="field" id="lab-json" spellcheck="false">{\n  "message": "你好，Python！",\n  "count": 3\n}</textarea>';
    $$('#lab-fields input, #lab-fields textarea').forEach(el => el.addEventListener('input',updateLabCode));
    updateLabCode();
  }
  function labRequest() {
    const kind = $('#lab-endpoint').value;
    if (kind === 'list') return {path:`/api/demo/items?q=${encodeURIComponent($('#lab-q').value)}&limit=${encodeURIComponent($('#lab-limit').value)}`,method:'GET'};
    if (kind === 'item') return {path:`/api/demo/items/${encodeURIComponent($('#lab-id').value)}`,method:'GET'};
    return {path:'/api/demo/echo',method:'POST',body:$('#lab-json').value};
  }
  function updateLabCode() {
    const request = labRequest(), quotedPath = JSON.stringify(request.path);
    $('#request-preview').textContent = `${request.method} ${request.path}`;
    if (request.method === 'GET') {
      $('#lab-js').textContent = `const response = await fetch(${quotedPath});\nconsole.log(response.status);\nconst data = await response.json();\nconsole.log(data);`;
      $('#lab-python').textContent = `import json\nfrom urllib.request import urlopen\nfrom urllib.error import HTTPError\n\nurl = ${JSON.stringify(location.origin + request.path)}\ntry:\n    response = urlopen(url)\nexcept HTTPError as error:\n    response = error\nwith response:\n    print(response.status)\n    print(json.load(response))`;
    } else {
      $('#lab-js').textContent = `const response = await fetch(${quotedPath}, {\n  method: "POST",\n  headers: {"Content-Type": "application/json"},\n  body: ${JSON.stringify(request.body)}\n});\nconsole.log(response.status);\nconsole.log(await response.json());`;
      $('#lab-python').textContent = `import json\nfrom urllib.request import Request, urlopen\n\nbody = ${JSON.stringify(request.body)}\nrequest = Request(\n    ${JSON.stringify(location.origin + request.path)},\n    data=body.encode("utf-8"),\n    headers={"Content-Type": "application/json"},\n    method="POST",\n)\nwith urlopen(request) as response:\n    print(response.status)\n    print(json.load(response))`;
    }
  }
  async function sendLab() {
    const request = labRequest(), token = routeVersion, button = $('#lab-send');
    if (request.method === 'POST') { try { JSON.parse(request.body); } catch (_) { toast('请求体必须是有效 JSON，请检查引号和逗号。'); $('#lab-json').focus(); return; } }
    button.disabled = true; button.textContent = '请求中…';
    try {
      const started = performance.now();
      const response = await fetch(request.path,{method:request.method,...(request.body ? {headers:{'Content-Type':'application/json'},body:request.body} : {})});
      const data = await response.json();
      if (token !== routeVersion) return;
      $('#lab-status').textContent = `HTTP ${response.status} · ${Math.round(performance.now()-started)} ms`;
      $('#lab-status').classList.toggle('accepted-tag',response.ok);
      $('#lab-output').textContent = json(data);
    } catch (error) { if (token === routeVersion) { $('#lab-status').textContent = '连接失败'; $('#lab-output').textContent = error.message; } }
    finally { if (button.isConnected) { button.disabled = false; button.textContent = '发送请求 →'; } }
  }
  function exportProgress() {
    const blob = new Blob([JSON.stringify({app:'PyStep',exportedAt:new Date().toISOString(),...progress},null,2)],{type:'application/json;charset=utf-8'});
    const url = URL.createObjectURL(blob), a = document.createElement('a'); a.href = url; a.download = `pystep-progress-${new Date().toISOString().slice(0,10)}.json`; a.click(); setTimeout(() => URL.revokeObjectURL(url),1000); toast('进度已导出，包含草稿、收藏和笔记。');
  }
  async function importProgress(file) {
    if (!file) return;
    if (file.size > 12*1024*1024) { toast('备份文件超过 12 MB，无法导入。'); return; }
    try {
      const imported = validateProgress(JSON.parse(await file.text()));
      const known = new Set(problems.map(p => p.id));
      const importedIds = [...imported.accepted,...imported.starred,...Object.keys(imported.drafts).map(Number),...Object.keys(imported.notes).map(Number),...Object.keys(imported.attempts).map(Number)];
      if (importedIds.some(id => !known.has(id))) throw new Error('备份含当前题库不存在的题号，请使用对应版本平台。');
      if (!confirm(`将用备份覆盖当前学习记录：${imported.accepted.length} 题已完成，${imported.starred.length} 题已收藏。当前草稿和笔记也会被替换。建议先导出当前进度。继续导入？`)) return;
      progress = imported; save(); applyTheme(); await route(); toast('学习进度已导入。');
    } catch (error) { toast(`导入失败：${error.message}`); }
    finally { $('#import-file').value = ''; }
  }
  function openGuide() { $('#guide-dialog').showModal(); }
  function closeGuide() { $('#guide-dialog').close(); progress.guideSeen = true; save(); }
  async function route() {
    if (editorObserver) { editorObserver.disconnect(); editorObserver = null; }
    const token = ++routeVersion, hash = location.hash.slice(1) || 'home', [path,query = ''] = hash.split('?'), params = new URLSearchParams(query);
    let kind = path.split('/')[0]; if (!(kind in labels)) kind = 'home';
    current = null; setPage(kind); window.scrollTo(0,0);
    try {
      if (kind === 'problem') { const id = Number(path.split('/')[1]); if (!Number.isInteger(id) || !problems.some(p => p.id === id)) throw new Error('没有找到这道练习，请返回题库选择。'); await renderProblem(id,token); }
      else if (['problems','favorites','review'].includes(kind)) renderCatalog(kind,params);
      else if (kind === 'lab') renderLab(); else renderHome();
    } catch (error) { if (token === routeVersion) $('#main-content').innerHTML = `<div class="panel empty-state"><div class="empty-icon">↺</div><h3>暂时无法打开</h3><p>${esc(error.message)}</p><a class="button primary" href="#problems">返回题库</a></div>`; }
  }
  document.addEventListener('click',event => {
    const activity = event.target.closest('[data-activity]'); if (activity) { detailTab = activity.dataset.activity; renderDetail(); $$('.activity-icon[data-activity]').forEach(button => button.classList.toggle('active',button === activity)); $('#problem-body').scrollTop = 0; return; }
    const resultButton = event.target.closest('[data-result-tab]'); if (resultButton) { resultTab = resultButton.dataset.resultTab; renderResult(); return; }
    const star = event.target.closest('[data-star]');
    if (star) { event.preventDefault(); event.stopPropagation(); const id = Number(star.dataset.star); progress.starred = isStarred(id) ? progress.starred.filter(n => n !== id) : [...progress.starred,id]; save(); $$(`[data-star="${id}"]`).forEach(b => { b.classList.toggle('starred',isStarred(id)); b.textContent = isStarred(id) ? '★' : '☆'; b.setAttribute('aria-pressed',String(isStarred(id))); b.setAttribute('aria-label',isStarred(id) ? '取消收藏' : '收藏题目'); b.title = isStarred(id) ? '取消收藏' : '收藏题目'; }); if (location.hash.startsWith('#favorites')) route(); return; }
    const tab = event.target.closest('[data-tab]'); if (tab) { detailTab = tab.dataset.tab; renderDetail(); return; }
    const caseButton = event.target.closest('[data-case]'); if (caseButton) { renderResult(Number(caseButton.dataset.case)); return; }
    const lineButton = event.target.closest('[data-error-line]'); if (lineButton) { const editor = $('#code-editor'); if (editor) { const n = Number(lineButton.dataset.errorLine), lines = editor.value.split('\n'), pos = lines.slice(0,n-1).reduce((sum,line) => sum + line.length + 1,0); editor.focus(); editor.setSelectionRange(pos,pos+(lines[n-1]?.length || 0)); editor.scrollTop = Math.max(0,(n-4)*23); } return; }
    const row = event.target.closest('[data-problem]'); if (row && !event.target.closest('a')) { location.hash = `problem/${row.dataset.problem}`; return; }
    const action = event.target.closest('[data-action]')?.dataset.action;
    if (action === 'guide') openGuide();
    if (action === 'export') exportProgress();
    if (action === 'import') $('#import-file').click();
    if (action === 'next-hint') { hintCount++; renderDetail(); }
    if (action === 'reveal-solution') { solutionVisible = true; renderDetail(); }
    if (action === 'use-solution' && current && confirm('将参考答案填入编辑器？当前草稿会被覆盖。')) { $('#code-editor').value = current.solution; $('#code-editor').dispatchEvent(new Event('input')); toast('已填入参考答案。运行后别忘了理解每一步。'); }
    if (action === 'reset-progress' && confirm('清空全部已完成记录、提交记录、代码草稿、收藏和笔记？此操作无法撤销，请先导出备份。')) { const theme = progress.theme; progress = emptyState(); progress.theme = theme; progress.guideSeen = true; save(); route(); toast('学习记录已清空。'); }
  });
  document.addEventListener('keydown',event => {
    if (event.altKey && ['ArrowLeft','ArrowRight'].includes(event.key) && current && !['TEXTAREA','INPUT','SELECT'].includes(event.target.tagName)) { event.preventDefault(); const index = problems.findIndex(p => p.id === current.id), p = problems[index + (event.key === 'ArrowLeft' ? -1 : 1)]; if (p) location.hash = `problem/${p.id}`; }
    if (event.target.matches('.panel-tab') && ['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) { event.preventDefault(); const tabs = $$('.panel-tab'), index = tabs.indexOf(event.target), next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length-1 : (index+(event.key === 'ArrowRight' ? 1 : -1)+tabs.length)%tabs.length; tabs[next].click(); tabs[next].focus(); }
  });
  $('#theme-toggle').onclick = () => { progress.theme = progress.theme === 'dark' ? 'light' : 'dark'; applyTheme(); save(); };
  $('#export-progress').onclick = exportProgress; $('#import-progress').onclick = () => $('#import-file').click(); $('#import-file').onchange = e => importProgress(e.target.files[0]);
  $('#open-guide').onclick = openGuide; $('#close-guide').onclick = closeGuide; $('#guide-start').onclick = () => { closeGuide(); if (!location.hash || location.hash === '#home') location.hash = `problem/${problems[0]?.id || 1}`; };
  $('#guide-dialog').addEventListener('cancel',() => { progress.guideSeen = true; save(); });
  applyTheme();
  (async () => {
    try {
      const [catalog, environment] = await Promise.all([api('/api/problems'),api('/api/meta').catch(() => null)]);
      problems = catalog.problems; chapters = catalog.chapters; meta = environment || {};
      $('#nav-total').textContent = problems.length;
      $('#runtime-state').innerHTML = environment ? `<i></i>Python ${esc(meta.python)} · 本地已连接` : '<i></i>题库已连接 · 环境信息不可用';
      $('#runtime-state').classList.toggle('offline',!environment);
      $('#runtime-state').title = `SQL: SQLite ${meta.sqlite || '—'}；JavaScript: ${meta.dependencies?.node?.available ? 'Node.js ' + meta.dependencies.node.version : '需要安装 Node.js'}`;
      window.addEventListener('hashchange',route); await route();
      if (!progress.guideSeen) openGuide();
      if (storageWarning) toast('进度读取失败或存储不可用，可导入已有备份恢复。');
    } catch (error) { $('#runtime-state').innerHTML = '<i></i>本地服务未连接'; $('#runtime-state').classList.add('offline'); $('#main-content').innerHTML = `<div class="panel empty-state"><div class="empty-icon">↺</div><h3>还没有连接到学习平台</h3><p>${esc(error.message)}</p><p>请保持启动平台的窗口运行，通过本地地址访问页面。</p><button class="button primary" id="retry-load">重新连接</button></div>`; $('#retry-load').onclick = () => location.reload(); }
  })();
})();
