/* PyStep: offline-first learning workspace, no third-party browser dependencies. */
(() => {
  'use strict';
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const json = value => JSON.stringify(value, null, 2) ?? 'null';
  const KEY = 'pystep.progress.v1';
  const emptyState = () => ({version:1, drafts:{}, accepted:[], attempts:{}, notes:{}, starred:[], theme:'light', lastProblem:null, guideSeen:false, submissions:[], activity:{}, assistance:{}, checkpoints:{}, settings:{fontSize:14,focus:false,split:43}, training:null, trainingArchive:[]});
  let progress = emptyState();
  let storageWarning = false, stateRevision = 0;
  try { const saved = JSON.parse(localStorage.getItem(KEY) || 'null'); if (saved) progress = validateProgress(saved); } catch (_) { storageWarning = true; }
  let problems = [], chapters = [], meta = {}, current = null, routeVersion = 0, busy = false, editorObserver = null;
  let detailTab = 'lesson', hintCount = 0, solutionVisible = false, latestResult = null, resultTab = 'tests', traceIndex = 0, toastTimer;
  const cache = new Map();
  const phases = [
    {title:'Python 基础', from:1, to:9, icon:'{ }', desc:'从变量与循环开始，建立编程直觉。'},
    {title:'常用库与人工智能', from:10, to:18, icon:'◈', desc:'标准库、数据分析、可视化与机器学习。'},
    {title:'复试机考与算法', from:19, to:24, icon:'⌘', desc:'输入输出、数据结构与常见算法。'},
    {title:'全栈与工程实践', from:25, to:30, icon:'▤', desc:'数据库、后端 API 与前端基础。'},
    {title:'秋招算法与面试', from:31, to:36, icon:'↗', desc:'从高频题型到复杂度分析，练习完整表达解题过程。'},
    {title:'ACM 竞赛进阶', from:37, to:42, icon:'◆', desc:'标准输入输出、进阶图论与动态规划，走向综合训练。'}
  ];
  const labels = {home:'学习总览', roadmap:'学习路线', training:'限时训练', history:'提交记录', problems:'练习题库', favorites:'我的收藏', review:'错题复习', problem:'开始练习', lab:'API 实验室'};
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
    if (raw.settings && typeof raw.settings === 'object') state.settings = {fontSize:Math.max(12,Math.min(22,Number(raw.settings.fontSize)||14)),focus:raw.settings.focus === true,split:Math.max(28,Math.min(65,Number(raw.settings.split)||43))};
    for (const key of ['assistance','checkpoints']) {
      if (raw[key] && typeof raw[key] === 'object' && !Array.isArray(raw[key])) for (const [id,value] of Object.entries(raw[key]).slice(0,10000)) if (validId(id)) state[key][id] = key === 'assistance' ? value === true : Math.max(0,Math.min(3,Number(value)||0));
    }
    if (raw.activity && typeof raw.activity === 'object') for (const [day,count] of Object.entries(raw.activity).slice(-730)) if (/^\d{4}-\d{2}-\d{2}$/.test(day) && Number.isInteger(count) && count > 0) state.activity[day] = Math.min(count,1000000);
    if (Array.isArray(raw.submissions)) state.submissions = raw.submissions.filter(s => s && validId(s.problemId) && Number.isFinite(s.at) && typeof s.code === 'string' && s.code.length <= 150000 && typeof s.status === 'string').slice(0,80).map(s => ({id:String(s.id).slice(0,80),problemId:Number(s.problemId),at:s.at,code:s.code,status:s.status.slice(0,50),passed:Math.max(0,Number(s.passed)||0),total:Math.max(0,Number(s.total)||0),duration:Math.max(0,Number(s.duration)||0),feedback:String(s.feedback||'').slice(0,4000),assisted:s.assisted===true,trainingId:typeof s.trainingId==='string'?s.trainingId.slice(0,80):null}));
    state.training = validateTraining(raw.training);
    if (Array.isArray(raw.trainingArchive)) state.trainingArchive = raw.trainingArchive.map(validateTraining).filter(s => s && s.status === 'finished').slice(0,12);
    let budget = 0; state.submissions = state.submissions.filter(s => (budget += s.code.length) <= 600000);
    return state;
  }
  function validateTraining(raw) {
    if (!raw || typeof raw !== 'object' || !Number.isFinite(raw.startedAt) || !Number.isFinite(raw.deadline) || raw.deadline <= raw.startedAt || raw.deadline-raw.startedAt > 4*60*60*1000 || !Array.isArray(raw.problemIds) || !raw.problemIds.length || raw.problemIds.length > 12 || raw.problemIds.some(id => !Number.isInteger(id) || id < 1)) return null;
    const session = {id:String(raw.id||raw.startedAt).slice(0,80),preset:String(raw.preset||'autumn').slice(0,20),title:String(raw.title||'限时训练').slice(0,80),startedAt:raw.startedAt,deadline:raw.deadline,status:raw.status==='finished'?'finished':'active',endedAt:Number.isFinite(raw.endedAt)?Math.max(raw.startedAt,Math.min(raw.endedAt,raw.deadline)):null,problemIds:[...new Set(raw.problemIds)],assisted:{},records:[],totals:{}};
    for (const id of session.problemIds) if (raw.assisted?.[id] === true) session.assisted[id] = true;
    if (Array.isArray(raw.records)) session.records = raw.records.filter(r => r && session.problemIds.includes(r.problemId) && Number.isFinite(r.at) && r.at >= session.startedAt && r.at <= Math.min(session.deadline,session.endedAt||session.deadline) && typeof r.status==='string').map(r => ({problemId:r.problemId,at:r.at,status:r.status.slice(0,50),assisted:r.assisted===true,passed:Math.max(0,Number(r.passed)||0),total:Math.max(0,Number(r.total)||0)}));
    for (const id of session.problemIds) {
      const total=raw.totals?.[id];
      if(total && Number.isInteger(total.attempts) && total.attempts>=0 && total.attempts<=10000000) session.totals[id]={attempts:total.attempts,accepted:total.accepted===true,independent:total.accepted===true&&total.independent===true};
    }
    session.totals = sessionStats(session).perProblem;
    session.records = session.records.slice(-500);
    return session;
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
  const isReview = id => progress.assistance[id] === true || progress.attempts[id]?.lastStatus === 'revisiting' || !isAccepted(id) && progress.attempts[id] && !['accepted','running'].includes(progress.attempts[id].lastStatus);
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
        ['尝试过的题目',attempted,'题','从尝试开始，慢慢变熟练','⌘'],
        ['完成章节',completedChapters,`/ ${chapters.length}`,'每章 10 题，循序渐进','▤'],
        ['累计提交',totalAttempts,'次','提交全部测试才计入完成','↗']
      ].map(([label,n,unit,sub,icon]) => `<div class="stat-card"><div class="stat-label">${label}<span class="stat-symbol">${icon}</span></div><div class="stat-number">${n}<small>${unit}</small></div><p class="stat-sub">${sub}</p></div>`).join('')}</section>
      <section><div class="section-heading"><div><h2>你的学习路线</h2><p>六个阶段，先学会拆解问题，再独立实现与复盘。</p></div><a href="#roadmap">目标、先修与验收 →</a></div><div class="roadmap-grid">${phases.map((phase,i) => {
        const list = problems.filter(p => p.chapter >= phase.from && p.chapter <= phase.to), n = list.filter(p => isAccepted(p.id)).length;
        return `<a class="roadmap-card" href="#problems?phase=${i}"><span class="phase-icon">${phase.icon}</span><span class="phase-num">PHASE 0${i+1}</span><h3>${phase.title}</h3><p>${phase.desc}</p><div class="roadmap-progress"><i style="width:${percent(n,list.length)}%"></i></div><div class="roadmap-meta"><span>第 ${phase.from}–${phase.to} 章</span><span>${n} / ${list.length} 题</span></div></a>`;
      }).join('')}</div></section>
      <div class="home-bottom"><section class="recent-panel"><div class="section-heading"><h2>${recent.length ? '最近练习' : '从这些小练习开始'}</h2><a href="#review">错题复习 →</a></div>${(recent.length ? recent : problems.slice(0,3)).map(recentRow).join('')}</section><aside class="tip-panel"><div class="tip-kicker">A LITTLE REMINDER</div><h2>不着急看答案，<br>先和问题待一会儿。</h2><p>把输入、输出和每一步变化写下来。卡住时，先展开第一条提示。</p><button data-action="guide">阅读入门指南 →</button></aside></div>
      <section class="workspace-tools"><a class="button" href="#lab">打开 API 实验室 ↗</a><button class="button" data-action="export">导出进度</button><button class="button" data-action="import">导入进度</button><button class="button" data-action="guide">入门指南</button><button class="button text" data-action="reset-progress">清空学习记录</button></section><p class="home-credit">Contributed by <strong>ksy</strong></p>`;
    $('.stats-grid').insertAdjacentHTML('afterend',learningInsights());
  }
  const stageGuides = [
    {prerequisite:'零基础可开始',goal:'独立编写函数，处理分支、循环、字符串、集合与异常。',milestone:'不用参考答案完成一章；用纸笔追踪一次循环；为函数写出空输入与边界示例。',project:'做一个命令行记账工具：录入、分类、查询与保存。'},
    {prerequisite:'建议先完成 Python 基础',goal:'阅读库接口，完成数据清洗、可视化与简单模型流程。',milestone:'解释每个依赖的用途；区分训练与测试数据；说清输出的含义与局限。',project:'分析一份自己的 CSV 数据，展示图表并写出可复现的分析步骤。'},
    {prerequisite:'函数、循环、列表与字典',goal:'建立数据结构与算法模型，掌握常见机考题型。',milestone:'说清暴力做法；比较时间与空间复杂度；用反例验证优化后的算法。',project:'整理个人算法笔记，每个模板配一个适用条件和一个反例。'},
    {prerequisite:'Python 基础；按章节补足 SQL / JavaScript',goal:'理解数据存储、HTTP 请求与前后端之间的约定。',milestone:'独立写出查询；观察真实 API 响应；解释验证、错误处理与数据流。',project:'做一个带持久化的小型待办应用，记录接口与测试步骤。'},
    {prerequisite:'建议先完成第 19–24 章算法基础',goal:'识别秋招常见题型，并能解释正确性、复杂度与边界。',milestone:'不看答案完成 90 分钟训练；复盘每个失败用例；口述一种替代解法。',project:'建立错题清单，间隔几天重写；用不同约束尝试变式题。'},
    {prerequisite:'算法基础、复杂度分析与标准输入输出',goal:'练习竞赛中的建模、模板选择与完整程序实现。',milestone:'完成 120 / 180 分钟训练；记录卡题原因；比较瓶颈与优化效果。',project:'参与公开竞赛或补题，持续学习更深入的图论、数论与动态规划。'}
  ];
  function chapterDone(id) { const list = problems.filter(p => p.chapter === id); return list.length > 0 && list.every(p => isAccepted(p.id)); }
  function recommendedProblem() {
    const review = problems.filter(p => isReview(p.id)).sort((a,b) => (progress.attempts[b.id]?.lastAt||0)-(progress.attempts[a.id]?.lastAt||0));
    const last = problems.find(p => p.id === progress.lastProblem && !isAccepted(p.id));
    return {problem:review[0]||last||problems.find(p => !isAccepted(p.id))||problems[0],reason:review.length?'先复习最近的错题或辅助通过题，尝试独立重写。':last?'上次的草稿仍在，先把这道题独立完成。':'沿路线推进下一道练习：先学概念，再验证自己的理解。'};
  }
  function dayKey(date=new Date()) { return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`; }
  function learningInsights() {
    const recommended = recommendedProblem(), weak = chapters.map(c => ({...c,failed:problems.filter(p => p.chapter===c.id && isReview(p.id)).length})).filter(c => c.failed).sort((a,b)=>b.failed-a.failed).slice(0,3);
    const days = Array.from({length:14},(_,i) => { const d = new Date(); d.setDate(d.getDate()-13+i); return {key:dayKey(d),label:`${d.getMonth()+1}/${d.getDate()}`}; });
    const total = days.reduce((n,d)=>n+(progress.activity[d.key]||0),0), active = days.filter(d => progress.activity[d.key]).length;
    return `<section class="insights-grid"><article class="recommend-card"><div class="eyebrow">YOUR NEXT STEP</div><h2>${recommended.problem ? esc(recommended.problem.title) : '准备开始'}</h2><p>${recommended.reason}</p><a class="button primary" href="#problem/${recommended.problem?.id||1}">开始这一步 →</a></article><article class="activity-card panel"><div class="section-heading"><h2>最近 14 天</h2><span>${active} 天有提交 · ${total} 次</span></div><div class="activity-chart" aria-label="最近十四天真实提交次数">${days.map(d => `<div title="${d.key}：${progress.activity[d.key]||0} 次提交"><span style="height:${Math.max(4,Math.min(56,(progress.activity[d.key]||0)*8))}px" class="${progress.activity[d.key]?'has-activity':''}"></span><small>${d.label}</small></div>`).join('')}</div><p class="muted">自此版本起逐日记录。旧版累计记录保留，不推算历史天数。</p></article></section><section class="weak-chapters panel"><div><h2>把薄弱点练扎实</h2><p>${weak.length?'按待复习题数推荐章节，包含辅助通过的题。':'暂无待复习错题。提交失败后，会在这里推荐对应章节。'}</p></div><div>${weak.map(c=>`<a class="button" href="#review?chapter=${c.id}">${esc(c.title)} <span>${c.failed} 题待复习 →</span></a>`).join('')||'<a class="button" href="#roadmap">查看学习路线 →</a>'}</div></section>`;
  }
  function renderRoadmap() {
    $('#main-content').innerHTML = `<div class="page-heading"><div><div class="eyebrow">LEARN · APPLY · REFLECT</div><h1>一条能学，也能练的路线。</h1><p>从第一行代码到秋招与竞赛进阶。按先修知识选择起点，以独立实现和复盘检验理解。</p></div><a class="button primary" href="#problem/${recommendedProblem().problem?.id||1}">继续学习 →</a></div><section class="learning-loop panel"><span><b>01</b> 学概念<small>目标与先修知识</small></span><i>→</i><span><b>02</b> 拆示例<small>追踪输入到输出</small></span><i>→</i><span><b>03</b> 引导练习<small>分步提示与反馈</small></span><i>→</i><span><b>04</b> 独立实践<small>重写、提交、复盘</small></span></section><div class="stage-list">${phases.map((phase,i)=>{
      const guide=stageGuides[i], list=problems.filter(p=>p.chapter>=phase.from&&p.chapter<=phase.to), done=list.filter(p=>isAccepted(p.id)).length, next=list.find(p=>!isAccepted(p.id))||list[0];
      return `<article class="stage-card panel" id="stage-${i}"><div class="stage-index">0${i+1}</div><div class="stage-content"><div class="section-heading"><div><span class="eyebrow">第 ${phase.from}–${phase.to} 章 · ${done}/${list.length} 已通过</span><h2>${phase.title}</h2></div><a class="button" href="#problem/${next?.id||1}">${done===list.length?'重新练习':'进入阶段'} →</a></div><p class="stage-goal">${guide.goal}</p><div class="stage-prerequisite">先修建议 · ${guide.prerequisite}</div><div class="stage-milestones"><div><h3>阶段自检</h3><p>${guide.milestone}</p></div><div><h3>迁移实践</h3><p>${guide.project}</p></div></div><details><summary>查看本阶段 ${chapters.filter(c=>c.id>=phase.from&&c.id<=phase.to).length} 个章节</summary><div class="chapter-path">${chapters.filter(c=>c.id>=phase.from&&c.id<=phase.to).map(c=>`<a href="#problems?chapter=${c.id}"><span>${chapterDone(c.id)?'✓':pad(c.id)}</span><b>${esc(c.title)}</b><small>${problems.filter(p=>p.chapter===c.id&&isAccepted(p.id)).length}/${c.count} →</small></a>`).join('')}</div></details></div></article>`;
    }).join('')}</div><p class="roadmap-note">通过测试表示当前题目的实现满足测试要求。进阶能力还需要新题迁移、项目实践和持续复盘。</p>`;
  }
  const trainingPresets = {
    autumn:{title:'秋招模拟',minutes:90,from:31,to:36,offsets:[2,25,48],desc:'3 道算法题 · 读题、实现、边界检查'},
    acm120:{title:'ACM 专项',minutes:120,from:37,to:42,offsets:[3,24,45],desc:'3 道标准输入题 · 完整程序与算法迁移'},
    acm180:{title:'ACM 综合',minutes:180,from:37,to:42,offsets:[3,17,31,45,58],desc:'5 道标准输入题 · 时间分配与综合复盘'}
  };
  function sessionActive() { return progress.training?.status === 'active' && Date.now() < progress.training.deadline; }
  function trainingLocked(id) { return sessionActive() && progress.training.problemIds.includes(id); }
  function durationLabel(milliseconds) { const seconds = Math.max(0,Math.ceil(milliseconds/1000)); return `${String(Math.floor(seconds/3600)).padStart(2,'0')}:${String(Math.floor(seconds/60)%60).padStart(2,'0')}:${String(seconds%60).padStart(2,'0')}`; }
  function sessionStats(session) {
    const perProblem = {};
    for (const id of session.problemIds) {
      const records = session.records.filter(r=>r.problemId===id), total = session.totals?.[id];
      perProblem[id] = {attempts:Math.max(total?.attempts||0,records.length),accepted:total?.accepted===true||records.some(r=>r.status==='accepted'),independent:total?.independent===true||records.some(r=>r.status==='accepted'&&!r.assisted)};
    }
    const accepted=session.problemIds.filter(id=>perProblem[id].accepted), independent=accepted.filter(id=>!session.assisted[id]&&perProblem[id].independent);
    return {accepted,independent,perProblem,attempted:session.problemIds.filter(id=>perProblem[id].attempts>0).length,submissions:Object.values(perProblem).reduce((n,p)=>n+p.attempts,0)};
  }
  function selectedTrainingProblems(preset) {
    const list = problems.filter(p=>p.chapter>=preset.from&&p.chapter<=preset.to), shift = progress.trainingArchive.length*7;
    return [...new Set(preset.offsets.map(offset=>list[(offset+shift)%list.length]?.id).filter(Boolean))];
  }
  function startTraining() {
    if (sessionActive()) { toast('当前训练仍在进行，可以继续作答或提前结束。'); return; }
    const presetId = $('#training-preset')?.value || 'autumn', preset=trainingPresets[presetId]; if (!preset) return;
    const ids=selectedTrainingProblems(preset); if (!ids.length) { toast('当前题库尚未包含此训练阶段。'); return; }
    if (progress.training) progress.trainingArchive.unshift(progress.training);
    progress.trainingArchive=progress.trainingArchive.slice(0,12);
    const startedAt=Date.now(), assisted={}; for (const id of ids) if (progress.assistance[id]) assisted[id]=true;
    progress.training={id:`training-${startedAt}`,preset:presetId,title:preset.title,startedAt,deadline:startedAt+preset.minutes*60000,endedAt:null,status:'active',problemIds:ids,records:[],assisted};
    save(); renderTraining(); tickTraining(); toast('训练开始。刷新与离开页面不会暂停倒计时。');
  }
  function finishTraining(automatic=false) {
    const session=progress.training; if (!session||session.status!=='active') return;
    session.status='finished'; session.endedAt=automatic?session.deadline:Math.min(Date.now(),session.deadline); save();
    if (location.hash.startsWith('#training')) renderTraining(); else if (current) { renderDetail(); renderTrainingBanner(); }
    tickTraining(); toast(automatic?'训练时间已到，成绩已保存。':'本场训练已结束，可以查看复盘。');
  }
  function tickTraining() {
    const session=progress.training;
    if (session?.status==='active' && Date.now()>=session.deadline) { finishTraining(true); return; }
    const indicator=$('#session-indicator'); indicator.hidden=!session;
    if (session) indicator.textContent=session.status==='active'?`◷ ${durationLabel(session.deadline-Date.now())}`:'查看训练结果';
    $$('[data-countdown]').forEach(el=>el.textContent=session?.status==='active'?durationLabel(session.deadline-Date.now()):'已结束');
  }
  function renderTrainingBanner() {
    $('#practice-session')?.remove(); if (!current||!progress.training?.problemIds.includes(current.id)) return;
    const active=sessionActive(); $('.practice-top')?.insertAdjacentHTML('afterend',`<div id="practice-session" class="practice-session"><a href="#training">${esc(progress.training.title)} · ${active?'进行中':'已结束'} →</a><span>${active?'本场隐藏提示、答案与历史代码；仅记录开始后的提交。':'本场结果已保存，后续提交计入日常练习。'}</span>${active?'<b data-countdown></b>':''}</div>`); tickTraining();
  }
  function renderTraining() {
    const session=progress.training;
    if (!session) {
      $('#main-content').innerHTML=`<div class="page-heading"><div><div class="eyebrow">MAKE TIME FOR DEEP PRACTICE</div><h1>给自己一场完整的练习。</h1><p>把所学放进真实的时间限制里。开始后，刷新、切换题目或关闭页面都不会重置倒计时。</p></div></div><div class="training-setup"><section class="training-intro panel"><span class="training-clock">◷</span><h2>从容读题，独立完成。</h2><p>本场成绩只计算开始后、截止前发起的提交。以前通过的题也需要重新提交；运行示例不算完成。</p><ul><li>题目与代码草稿自动保存，随时返回继续。</li><li>本场题目的提示、参考答案和历史代码暂时隐藏。</li><li>若草稿已标记使用辅助，本场通过会单独标注。</li><li>结束后查看每题提交、通过情况与复盘建议。</li></ul><p class="muted">这是本地自我训练，计时依赖设备时钟。它不作为认证或正式竞赛成绩。</p></section><section class="training-config panel"><label for="training-preset">选择训练方案</label><select id="training-preset" class="field">${Object.entries(trainingPresets).map(([id,p])=>`<option value="${id}">${p.title} · ${p.minutes} 分钟</option>`).join('')}</select><div id="training-preview"></div><button id="start-training" class="button primary" data-action="start-training">开始计时训练 →</button></section></div>${renderTrainingArchive()}`;
      $('#training-preset').onchange=updateTrainingPreview; updateTrainingPreview(); return;
    }
    const stats=sessionStats(session), active=sessionActive(), elapsed=(active?Date.now():session.endedAt||session.deadline)-session.startedAt;
    $('#main-content').innerHTML=`<div class="page-heading"><div><div class="eyebrow">${active?'TRAINING IN PROGRESS':'SESSION REVIEW'}</div><h1>${esc(session.title)}${active?'，专注当下。':'，把经验留下。'}</h1><p>${new Date(session.startedAt).toLocaleString('zh-CN')} 开始 · ${session.problemIds.length} 题 · ${Math.round((session.deadline-session.startedAt)/60000)} 分钟</p></div><div class="training-timer"><span>${active?'剩余时间':'实际用时'}</span><strong ${active?'data-countdown':''}>${durationLabel(active?session.deadline-Date.now():elapsed)}</strong></div></div><section class="stats-grid session-stats">${[['本场独立通过',stats.independent.length,session.problemIds.length],['辅助通过',stats.accepted.length-stats.independent.length,'题'],['已尝试',stats.attempted,'题'],['本场提交',stats.submissions,'次']].map(([label,n,total])=>`<div class="stat-card"><div class="stat-label">${label}</div><div class="stat-number">${n}<small>${typeof total==='number'?'/ ':''}${total}</small></div></div>`).join('')}</section><div class="session-layout"><section class="panel session-problems"><div class="section-heading"><h2>${active?'本场题单':'逐题复盘'}</h2><span>仅统计本场提交</span></div>${session.problemIds.map((id,i)=>{
      const p=problems.find(p=>p.id===id);if(!p)return'';const records=session.records.filter(r=>r.problemId===id),attempts=stats.perProblem[id].attempts,done=stats.accepted.includes(id),independent=stats.independent.includes(id);
      return `<article class="session-problem"><div class="session-letter">${String.fromCharCode(65+i)}</div><div><a href="#problem/${id}">${esc(p.title)}</a><p>${difficulty(p)} <span>${attempts} 次提交 · ${done?independent?'独立通过':'辅助通过':attempts?'尚未通过':'未提交'}${isAccepted(id)&&!done?' · 日常已通过，需本场重交':''}</span></p>${!active?`<small>${done?independent?'复盘建议：解释正确性，再尝试改变输入规模。':'复盘建议：清除草稿中的辅助标记后，独立重写。':attempts?'复盘建议：打开提交记录，定位第一个失败用例。':'复盘建议：先读课堂，再用公开示例手工推演。'}</small>`:''}</div><a class="button small" href="#problem/${id}">${active?'作答':'复习'} →</a></article>`;
    }).join('')}</section><aside class="panel session-rules"><h2>${active?'专注这一场':'下一步怎么练'}</h2><p>${active?'计时持续运行。答案与提示在本场结束后恢复可见；提交截止以点击提交时的时间为准。':'先复盘未通过的题，记录误判条件与边界，再隔一段时间独立重写。正确提交比题数更有意义。'}</p>${active?'<button class="button" data-action="finish-training">提前结束并复盘</button>':'<a class="button" href="#history">查看提交快照 →</a><button class="button primary" data-action="new-training">准备下一场 →</button>'}<p class="muted">${active?'离开页面后，通过右上角倒计时返回。':'历史已通过记录不会自动计入本场成绩。辅助通过与独立通过分开统计。'}</p></aside></div>${renderTrainingArchive()}`;tickTraining();
  }
  function updateTrainingPreview() { const p=trainingPresets[$('#training-preset').value], ids=selectedTrainingProblems(p); $('#training-preview').innerHTML=`<div class="preset-duration">${p.minutes}<small>分钟</small></div><p>${p.desc}</p><div class="preview-topics">${ids.map((id,i)=>`<div><span>${String.fromCharCode(65+i)}</span>${esc(problems.find(p=>p.id===id)?.title||id)}</div>`).join('')}</div><p class="muted">起点：第 ${p.from}–${p.to} 章。建议先完成对应阶段的课堂与基础练习。</p>`; }
  function renderTrainingArchive() { return progress.trainingArchive.length?`<section class="training-archive panel"><h2>过去的训练</h2>${progress.trainingArchive.map(s=>{const stats=sessionStats(s);return `<div><span>${esc(s.title)}<small>${new Date(s.startedAt).toLocaleDateString('zh-CN')}</small></span><span>独立 ${stats.independent.length}/${s.problemIds.length} · 辅助 ${stats.accepted.length-stats.independent.length} · ${stats.submissions} 次提交</span></div>`;}).join('')}</section>`:''; }
  function submissionFeedback(result) { const failed=result.cases?.find(c=>!c.passed); return String(result.error?.message||failed?.error?.message||failed?.hint||(result.status==='accepted'?'全部测试通过。试着解释正确性与复杂度。':`通过 ${result.passed||0}/${result.total||0} 个测试。检查输入边界和返回类型。`)).slice(0,4000); }
  function recordSubmission(p,code,result,at,trainingId,assisted) {
    const record={id:`${at}-${p.id}-${Math.random().toString(36).slice(2,7)}`,problemId:p.id,at,code,status:result.status,passed:result.passed||0,total:result.total||0,duration:result.duration_ms||0,feedback:submissionFeedback(result),assisted,trainingId};
    progress.submissions.unshift(record);let budget=0;progress.submissions=progress.submissions.slice(0,80).filter(s=>(budget+=s.code.length)<=600000);
    const day=dayKey(new Date(at));progress.activity[day]=(progress.activity[day]||0)+1;
    const session=[progress.training,...progress.trainingArchive].find(s=>s?.id===trainingId);
    if(session&&at>=session.startedAt&&at<=Math.min(session.deadline,session.endedAt||session.deadline)&&session.problemIds.includes(p.id)) {
      session.totals=sessionStats(session).perProblem;
      const total=session.totals[p.id], helped=assisted||session.assisted[p.id]===true;
      total.attempts++;
      if(result.status==='accepted') {total.accepted=true;if(!helped)total.independent=true;}
      session.records.push({problemId:p.id,at,status:result.status,passed:result.passed||0,total:result.total||0,assisted:helped});
      session.records=session.records.slice(-500);
    }
  }
  function renderHistory(params=new URLSearchParams()) {
    const id=Number(params.get('problem'))||0, list=progress.submissions.filter(s=>!id||s.problemId===id);
    $('#main-content').innerHTML=`<div class="page-heading"><div><div class="eyebrow">EVERY ATTEMPT TELLS A STORY</div><h1>提交记录</h1><p>保存近期代码快照与判题反馈。最多保留 80 次、合计 60 万字符的代码；累计提交与通过记录持续保留。</p></div><button class="button" data-action="export">导出完整进度 ↗</button></div><label class="history-filter">筛选题目<select id="history-filter" class="field"><option value="">全部题目</option>${[...new Set(progress.submissions.map(s=>s.problemId))].map(problemId=>`<option value="${problemId}" ${problemId===id?'selected':''}>${problemId}. ${esc(problems.find(p=>p.id===problemId)?.title||'练习')}</option>`).join('')}</select></label><div class="history-list">${list.length?list.map(s=>{
      const p=problems.find(p=>p.id===s.problemId), locked=trainingLocked(s.problemId);return `<article class="panel history-card"><div class="history-card-top"><div><a href="#problem/${s.problemId}">${s.problemId}. ${esc(p?.title||'练习')}</a><p>${new Date(s.at).toLocaleString('zh-CN')} · ${s.assisted?'使用辅助':'未标记辅助'}${s.trainingId?' · 限时训练':''}</p></div><span class="tag ${s.status==='accepted'?'accepted-tag':''}">${esc(s.status)} · ${s.passed}/${s.total}</span></div><p class="history-feedback">${esc(s.feedback)}</p>${locked?'<p class="muted">本场训练进行中，此题历史代码暂时隐藏。</p>':`<details><summary>查看代码快照 · ${Math.round(s.duration)} ms</summary><pre><code>${esc(s.code)}</code></pre><button class="button small" data-restore="${esc(s.id)}">恢复到编辑器</button></details>`}</article>`;
    }).join(''):'<div class="panel empty-state"><h3>从下一次提交开始记录</h3><p>点击「提交检查」后，这里会保存代码与反馈。旧版的累计记录保留，但无法还原过去的代码。</p><a class="button primary" href="#problems">去练习 →</a></div>'}</div>`;$('#history-filter').onchange=e=>location.hash=`history${e.target.value?'?problem='+e.target.value:''}`;
  }
  function renderCatalog(kind, params) {
    const selected = {q:params.get('q') || '',chapter:params.get('chapter') || '',phase:params.get('phase') || '',status:params.get('status') || '',difficulty:params.get('difficulty') || '',language:params.get('language') || ''};
    const heading = {problems:['练习题库','每一题都是一个小台阶。按顺序练习，也可以选择感兴趣的主题。'],favorites:['我的收藏','把值得反复练习的题目，留在这里。'],review:['错题复习','复习未通过题目，以及看过提示或答案后需要独立重写的题目。']}[kind];
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
    $('#main-content').innerHTML = `<div class="practice-top"><a class="practice-back" href="#problems?chapter=${p.chapter}">← 返回题库 <span>/ 第 ${p.chapter} 章</span></a><div class="practice-pager">${prev ? `<a class="icon-button" href="#problem/${prev.id}" aria-label="上一题" title="上一题（Alt + ←）">←</a>` : '<button class="icon-button" disabled aria-label="已是第一题">←</button>'}<span>${index+1} / ${problems.length}</span>${next ? `<a class="icon-button" href="#problem/${next.id}" aria-label="下一题" title="下一题（Alt + →）">→</a>` : '<button class="icon-button" disabled aria-label="已是最后一题">→</button>'}</div></div><div class="practice-grid"><section class="panel problem-panel"><div class="panel-tabs" role="tablist" aria-label="题目内容">${[['lesson','题目与课堂'],['hints','提示'],['solution','参考答案'],['notes','笔记']].map(([tab,label]) => `<button class="panel-tab ${tab === detailTab ? 'active' : ''}" id="tab-${tab}" data-tab="${tab}" role="tab" aria-selected="${tab === detailTab}" aria-controls="problem-body">${label}</button>`).join('')}${starButton(p.id,'panel-star')}</div><div class="problem-body" id="problem-body" role="tabpanel" aria-labelledby="tab-lesson"></div></section><div class="editor-column">${dependencyBanner(p)}<section class="panel editor-panel"><div class="editor-heading"><span class="editor-label"><i class="editor-dot"></i>${editorInfo}</span><div class="editor-tools"><span>自动保存</span><button id="reset-code" aria-label="重置代码" title="重置为初始代码">↺</button></div></div><div class="editor-surface"><div class="line-numbers" id="line-numbers" aria-hidden="true"></div><textarea id="code-editor" class="code-input" aria-label="代码编辑器" spellcheck="false" autocapitalize="off" autocomplete="off" autocorrect="off" wrap="off"></textarea></div><div class="editor-footnote"><span id="save-status">草稿保存在当前浏览器</span><span>Tab 缩进 · Ctrl / ⌘ + Enter 运行</span></div><div class="editor-actions"><label class="custom-toggle"><input type="checkbox" id="custom-enabled">自定义测试</label><div class="actions-right"><button id="run-code" class="button">▷ 运行示例</button><button id="submit-code" class="button primary">提交检查 ↑</button></div></div><div class="custom-input-wrap" id="custom-wrap" hidden><label for="custom-args">${p.execution_mode === 'stdin' ? '标准输入（纯文本，保留换行）' : '输入 JSON 参数数组（按下方参数顺序）'}</label><textarea id="custom-args" class="field" spellcheck="false">${esc(p.execution_mode === 'stdin' ? p.examples?.[0]?.stdin || '' : json(p.examples?.[0]?.args || []))}</textarea><p>${p.execution_mode === 'stdin' ? '像在本地终端一样粘贴完整输入；使用 input() 或 sys.stdin.buffer 读取。' : p.language === 'sql' ? 'SQL 参数为 [{"表名": [[行数据], …]}]，每次使用独立数据库。' : '例如两个数字用 [2, 3]；一个列表参数用 [[1, 2, 3]]。'}自定义运行只查看结果，不计入完成。</p></div></section><section class="panel results-panel" id="results-panel" aria-live="polite"><div class="results-heading">运行结果<span>真实执行 · 本地判题</span></div><div id="result-body"><div class="results-empty"><span class="terminal-icon">&gt;_</span><p>写下你的第一行代码，点击「运行示例」。</p><span>先验证示例，再提交全部测试。</span></div></div></section></div></div>`;
    mountWorkbench(p, editorInfo);
    const editor = $('#code-editor'); editor.value = progress.drafts[p.id] ?? p.starter ?? ''; updateLines();
    editor.addEventListener('input',() => { progress.drafts[p.id] = editor.value; const ok = save(); $('#save-status').textContent = ok ? '草稿已保存' : '保存失败，请导出备份'; updateLines(); });
    editor.addEventListener('scroll',() => { $('#line-numbers').scrollTop = editor.scrollTop; syncHighlight(); });
    editor.addEventListener('keydown',editorKeys);
    if (window.ResizeObserver) { editorObserver = new ResizeObserver(() => { const lines = $('#line-numbers'); if (lines && editor.isConnected) lines.style.height = `${editor.clientHeight}px`; syncHighlight(); }); editorObserver.observe(editor); }
    $('#custom-enabled').onchange = e => { $('#custom-wrap').hidden = !e.target.checked; $('#run-code').textContent = e.target.checked ? '▷ 运行自定义' : '▷ 运行示例'; };
    $('#run-code').onclick = () => execute('run'); $('#submit-code').onclick = () => execute('submit');
    $('#reset-code').onclick = () => { if (confirm('将当前代码恢复为题目的初始代码？这会覆盖此题草稿。')) { independentRewrite(); } };
    renderDetail(); mountEditorSettings(); renderTrainingBanner();
  }
  function mountWorkbench(p, editorInfo) {
    const main = $('#main-content');
    const filename = p.language === 'sql' ? 'query.sql' : p.language === 'javascript' ? 'solution.js' : 'solution.py';
    resultTab = 'tests';
    main.insertAdjacentHTML('afterbegin',`<nav class="activity-bar" aria-label="工作台导航"><a href="#home" class="activity-brand" title="返回学习总览" aria-label="返回学习总览">p</a><button class="activity-icon active" data-activity="lesson" title="题目与课堂" aria-label="题目与课堂">▤</button><a class="activity-icon" href="#problems" title="搜索题库" aria-label="搜索题库">⌕</a><button class="activity-icon" data-activity="hints" title="分步提示" aria-label="分步提示">◇</button><button class="activity-icon" data-activity="notes" title="学习笔记" aria-label="学习笔记">✎</button><a class="activity-icon" href="#lab" title="API 实验室" aria-label="API 实验室">⇄</a><button class="activity-icon activity-help" data-action="guide" title="入门指南" aria-label="入门指南">?</button></nav>`);
    $('.practice-top').classList.add('workbench-commandbar');
    $('.practice-top').insertAdjacentHTML('beforeend','<div class="workbench-run-actions"><button class="button" id="toolbar-run" title="运行示例（Ctrl + Enter）">▷ 运行</button><button class="button primary" id="toolbar-submit">✓ 提交检查</button></div>');
    if ((p.language || 'python') === 'python') $('#toolbar-run').insertAdjacentHTML('beforebegin','<button class="button" id="toolbar-trace" title="运行第一个示例或自定义输入，观察每行执行前的变量">◎ 逐步观察</button>');
    $('.problem-panel').insertAdjacentHTML('afterbegin',`<div class="explorer-heading"><span>资源管理器 · 学习任务</span><span>···</span></div><div class="explorer-folder">⌄ &nbsp;第 ${pad(p.chapter)} 章 · ${esc(p.chapter_title)}</div><div class="explorer-file"><span class="file-icon markdown-icon">M↓</span> README.md <span>题目说明</span></div>`);
    $('.editor-heading').classList.add('editor-filebar');
    $('.editor-label').innerHTML = `<span class="file-icon ${p.language === 'javascript' ? 'js-icon' : p.language === 'sql' ? 'sql-icon' : 'python-icon'}">${p.language === 'javascript' ? 'JS' : p.language === 'sql' ? '▤' : 'Py'}</span><span>${filename}</span><span id="file-dirty" class="file-dirty" title="已保存到本机浏览器">●</span>`;
    $('.editor-label').title = editorInfo.replace(/<[^>]+>/g,'');
    $('.editor-surface').insertAdjacentHTML('beforebegin',`<div class="editor-breadcrumb">练习 &nbsp;›&nbsp; ${pad(p.id)} &nbsp;›&nbsp; ${filename} &nbsp;›&nbsp; <span>${p.language === 'sql' ? '查询' : p.execution_mode === 'stdin' ? '标准输入程序' : 'solve'}</span></div>`);
    $('.editor-surface').insertAdjacentHTML('beforeend','<pre class="code-highlight" id="code-highlight" aria-hidden="true"></pre>');
    $('.results-heading').innerHTML = `<div class="workbench-panel-tabs" role="tablist" aria-label="运行面板">${[['problems','问题'],['output','输出'],['terminal','执行日志'],['tests','测试']].map(([key,label]) => `<button role="tab" class="workbench-panel-tab ${key === 'tests' ? 'active' : ''}" data-result-tab="${key}" aria-selected="${key === 'tests'}">${label}</button>`).join('')}</div><span>本地执行</span>`;
    main.insertAdjacentHTML('beforeend',`<div class="workbench-statusbar"><span class="statusbar-left">⌘ 本地工作区 <span class="statusbar-connection">✓ 已连接</span></span><span class="statusbar-right"><span id="cursor-status">行 1，列 1</span><span>空格: 4</span><span>UTF-8</span><span>${language(p)}</span></span></div>`);
    $('#toolbar-run').onclick = () => execute('run'); $('#toolbar-submit').onclick = () => execute('submit');
    if ($('#toolbar-trace')) {
      $('#toolbar-trace').onclick = () => execute('trace');
      $('.workbench-panel-tabs').insertAdjacentHTML('beforeend','<button role="tab" class="workbench-panel-tab" data-result-tab="trace" aria-selected="false">变量观察</button>');
    }
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
  function teachingIntro(p) {
    const phase=phases.findIndex(s=>p.chapter>=s.from&&p.chapter<=s.to), prerequisite=(p.prerequisites||[]).map(id=>chapters.find(c=>c.id===Number(id))).filter(Boolean), checkpoint=progress.checkpoints[p.id]||0;
    return `<div class="learning-objective"><span class="eyebrow">本题学习目标</span><p>${esc(p.learning_goal||`理解${(p.tags||[]).slice(0,3).join('、')||p.chapter_title}，从示例中找出规律，并独立完成实现。`)}</p><small>先修 · ${prerequisite.length?prerequisite.map(c=>`<a href="#problems?chapter=${c.id}">第 ${c.id} 章 ${esc(c.title)}${chapterDone(c.id)?' ✓':''}</a>`).join(' / '):esc(stageGuides[Math.max(0,phase)].prerequisite)}</small>${p.complexity?`<small>目标复杂度 · 时间 ${esc(p.complexity.time||'见题意')} · 空间 ${esc(p.complexity.space||'见题意')}</small>`:''}</div><nav class="lesson-sequence" aria-label="学习步骤"><button data-learn-step="concept" class="${checkpoint>=1?'done':''}">01 学概念</button><button data-learn-step="examples" class="${checkpoint>=2?'done':''}">02 拆示例</button><button data-learn-step="guided">03 引导练习</button><button data-learn-step="independent" class="${isAccepted(p.id) && !isReview(p.id)?'done':''}">04 独立实践</button></nav>`;
  }
  function mountEditorSettings() {
    $('.editor-tools').insertAdjacentHTML('afterbegin',`<button data-action="font-smaller" aria-label="减小代码字号" title="减小字号">A−</button><span id="font-size-label">${progress.settings.fontSize}</span><button data-action="font-larger" aria-label="增大代码字号" title="增大字号">A+</button><button data-action="focus-editor" aria-label="切换编辑器专注模式" aria-pressed="${progress.settings.focus}" title="专注模式（Esc 退出）">⛶</button>`);
    $('.practice-grid').insertAdjacentHTML('beforebegin',`<label class="split-control">题目栏宽度 <input id="editor-split" type="range" min="28" max="65" value="${progress.settings.split}" aria-label="题目栏宽度百分比"><span>拖动调整</span><a href="#history?problem=${current.id}">此题提交记录 →</a></label>`);
    $('#editor-split').oninput=e=>{progress.settings.split=Number(e.target.value);applyEditorSettings();save();};applyEditorSettings();
  }
  function applyEditorSettings() {
    document.body.style.setProperty('--editor-font',`${progress.settings.fontSize}px`); document.body.style.setProperty('--editor-line',`${Math.round(progress.settings.fontSize*1.7)}px`); document.body.style.setProperty('--problem-share',`${progress.settings.split}%`);
    document.body.classList.toggle('editor-focus',!!current&&progress.settings.focus);if($('#font-size-label'))$('#font-size-label').textContent=progress.settings.fontSize;
    $('[data-action="focus-editor"]')?.setAttribute('aria-pressed',String(progress.settings.focus));syncHighlight();
  }
  function independentRewrite() {
    if(busy){toast('请等待本次运行结束，再开始独立重写。');return;}
    if(!current||!$('#code-editor'))return;progress.assistance[current.id]=false;progress.attempts[current.id]={count:progress.attempts[current.id]?.count||0,lastStatus:'revisiting',lastAt:Date.now()};
    if(trainingLocked(current.id))progress.training.assisted[current.id]=false;
    $('#code-editor').value=current.starter||'';$('#code-editor').dispatchEvent(new Event('input'));solutionVisible=false;hintCount=0;detailTab='lesson';renderDetail();$('#code-editor').focus();toast('已开始独立重写。再次提交通过后，本次记录将标为未使用辅助。');
  }
  function openPalette() { const dialog=$('#command-dialog');if(dialog.open)return;dialog.showModal();$('#command-search').value='';renderPalette();$('#command-search').focus(); }
  function renderPalette() {
    const query=$('#command-search').value.trim().toLocaleLowerCase(),commands=Object.entries(labels).filter(([id])=>id!=='problem').map(([id,label])=>({title:label,subtitle:'页面',href:`#${id}`})),matches=problems.filter(p=>!query||`${p.id} ${p.title} ${p.chapter_title} ${(p.tags||[]).join(' ')}`.toLocaleLowerCase().includes(query)).slice(0,16).map(p=>({title:`${p.id}. ${p.title}`,subtitle:`第 ${p.chapter} 章 · ${language(p)}`,href:`#problem/${p.id}`}));
    const entries=[...commands.filter(c=>!query||c.title.toLocaleLowerCase().includes(query)),...matches].slice(0,20);
    $('#command-results').innerHTML=entries.length?entries.map((entry,i)=>`<a class="command-result ${i===0?'selected':''}" href="${entry.href}" data-command-index="${i}"><span>${esc(entry.title)}<small>${esc(entry.subtitle)}</small></span><span>↵</span></a>`).join(''):'<p class="empty-state">没有匹配项。试试题号或关键词。</p>';
  }
  function renderDetail() {
    const p = current, body = $('#problem-body'); if (!p || !body) return;
    $$('.panel-tab').forEach(b => { b.classList.toggle('active',b.dataset.tab === detailTab); b.setAttribute('aria-selected',String(b.dataset.tab === detailTab)); });
    body.setAttribute('aria-labelledby',`tab-${detailTab}`);
    const heading = `<div class="problem-heading"><h1><span class="problem-id">${pad(p.id)}.</span>${esc(p.title)}</h1></div><div class="problem-tags">${difficulty(p)}<span class="tag">${language(p)}</span>${(p.requires || []).map(r => `<span class="tag">${esc(r)} ${meta.dependencies?.[r]?.available ? '✓' : '待安装'}</span>`).join('')}<span class="tag">第 ${p.chapter} 章</span>${isAccepted(p.id) ? '<span class="tag accepted-tag">✓ 已通过</span>' : ''}${progress.assistance[p.id] ? '<span class="tag assistance-tag">辅助练习 · 待独立重写</span>' : ''}</div>`;
    if (detailTab === 'lesson') body.innerHTML = `${heading}${teachingIntro(p)}<section class="content-section" id="lesson-concept"><h3><span class="section-mark">01</span> 先学一点：小课堂</h3><div class="prose">${markdown(p.concept)}</div></section><section class="content-section"><h3><span class="section-mark">02</span> 你的任务</h3><div class="prose">${markdown(p.description)}</div></section>${p.parameters?.length ? `<section class="content-section"><h3>参数说明</h3><div class="table-scroll"><table class="parameter-table"><thead><tr><th>参数</th><th>类型</th><th>含义</th></tr></thead><tbody>${p.parameters.map(a => `<tr><td><code>${esc(a.name)}</code></td><td>${esc(a.type)}</td><td>${esc(a.description)}</td></tr>`).join('')}</tbody></table></div></section>` : ''}${p.setup_sql ? `<section class="content-section"><h3>数据表结构</h3><div class="prose"><pre><code>${esc(p.setup_sql)}</code></pre></div><p class="muted">测试会把示例参数中的行插入对应数据表，然后执行你的查询。请按题目要求排序结果。</p></section>` : ''}<section class="content-section" id="lesson-examples"><h3><span class="section-mark">03</span> 看看示例</h3>${(p.examples || []).map((ex,i) => `<div class="example-card"><strong>示例 ${i+1}</strong><div class="example-line"><span>输入</span><code>${esc(p.execution_mode === 'stdin' ? ex.stdin : json(ex.args))}</code></div><div class="example-line"><span>输出</span><code>${esc(p.execution_mode === 'stdin' ? ex.expected : json(ex.expected))}</code></div></div>`).join('')}</section><div class="lesson-callout content-section"><h3>${p.execution_mode === 'stdin' ? 'ACM 模式：完整程序，标准输入输出' : p.language === 'sql' ? '写出真实 SQL 查询' : p.language === 'javascript' ? '在 Node.js 中运行 solve' : '小提醒：return 和 print 不一样'}</h3><p>${p.execution_mode === 'stdin' ? '直接编写可执行脚本，用 input() 或 sys.stdin.buffer 读取标准输入，用 print() 输出答案。判题按空白分隔比较输出，忽略多余空格和换行；数值文本严格匹配。调试信息写到 stderr。' : p.language === 'sql' ? '直接编写 SELECT / WITH 查询即可；查询结果按行组成数组返回。' : p.language === 'javascript' ? '返回题目要求的结果。Node.js 没有浏览器 DOM；HTML / CSS 题比较返回的字符串，不验证页面渲染效果。' : '用 return 返回题目要求的结果；print 只会显示在标准输出中。平台会自动调用 solve，无需手动读取 input()。'}</p></div>`;
    if (trainingLocked(p.id) && ['hints','solution'].includes(detailTab)) { body.innerHTML = `${heading}<div class="solution-cover"><span class="cover-icon">◷</span><h3>本场训练，给自己独立思考的空间</h3><p>训练结束后，提示与参考答案会恢复。<br>可以返回课堂查看概念与公开示例。</p><a class="button" href="#training">返回训练 →</a></div>`; return; }
    if (detailTab === 'hints') body.innerHTML = `${heading}<div class="lesson-callout"><h3>一点一点接近答案</h3><p>先读一条提示，回到编辑器试一试。下一条会给出更具体的方向。</p></div>${(p.hints || []).slice(0,hintCount).map((h,i) => `<div class="hint-card"><h3>提示 ${i+1} / ${(p.hints || []).length}</h3><div class="prose">${markdown(h)}</div></div>`).join('')}${hintCount < (p.hints || []).length ? `<button class="hint-action" data-action="next-hint">${hintCount ? '再给我一点提示' : '展开第一条提示'} ＋</button>` : '<p class="muted">已经展开全部提示。试着把思路变成代码吧。</p>'}`;
    if (detailTab === 'solution') body.innerHTML = `${heading}${solutionVisible ? `<div class="solution-code"><pre><code>${esc(p.solution)}</code></pre></div><div class="code-toolbar"><span>参考实现 · ${language(p)}</span><button class="button small" data-action="use-solution">填入编辑器</button></div><section class="content-section"><h3>为什么这样写</h3><div class="prose">${markdown(p.explanation)}</div></section><p class="muted content-section"><button class="button" data-action="independent-rewrite">清空辅助，独立重写 →</button> 看懂以后，建议隔天再独立实现一次。</p>` : '<div class="solution-cover"><span class="cover-icon">◇</span><h3>先给自己一次尝试的机会</h3><p>参考答案包含完整代码和逐步讲解。<br>如果还没有思路，可以先看看提示。</p><button class="button primary" data-action="reveal-solution">展开参考答案</button></div>'}`;
    if (detailTab === 'lesson') body.insertAdjacentHTML('beforeend', `<section class="guided-practice content-section"><h3>从理解走向独立实现</h3><ol><li>先手算一个示例：输入里什么变了，什么没变？</li><li>把实现分为读取 / 处理 / 输出，先写最直接的做法。</li><li>补一个边界：空值、最小规模、重复项或极端数据。</li></ol><div><button class="button small" data-action="understood">${(progress.checkpoints[p.id]||0)>=2?'✓ 已自检理解':'我能解释这个示例'}</button><button class="button small" data-learn-step="guided">需要分步引导</button><button class="button small" data-learn-step="independent">开始独立实现 →</button>${progress.assistance[p.id]?'<button class="button small" data-action="independent-rewrite">独立重写</button>':''}</div><p class="muted">自检只记录学习步骤；提交通过才计入题目完成。</p></section>`);
    if (detailTab === 'notes') { body.innerHTML = `${heading}<div class="lesson-callout"><h3>把自己的理解留下来</h3><p>可以记下犯过的错误、一个新的写法，或下次复习想问自己的问题。</p></div><label for="problem-notes" class="muted">我的学习笔记</label><textarea id="problem-notes" class="field notes-field" maxlength="100000" placeholder="今天我学会了…">${esc(progress.notes[p.id] || '')}</textarea><p class="note-status" id="note-status">笔记自动保存在当前浏览器，并包含在进度备份里。</p>`; $('#problem-notes').oninput = e => { progress.notes[p.id] = e.target.value; $('#note-status').textContent = save() ? '笔记已保存' : '保存失败，请导出备份'; }; }
  }
  async function execute(mode) {
    if (busy || !current || !$('#code-editor')) return;
    const p = current, code = $('#code-editor').value, routeAtStart = routeVersion, submittedAt=Date.now(), trainingId=trainingLocked(current.id)?progress.training.id:null, assisted=progress.assistance[current.id]===true;
    const revisionAtStart = stateRevision;
    if (!code.trim()) { toast('先写一点代码，再运行吧。'); return; }
    const body = {problem_id:p.id,code,mode};
    if (mode !== 'submit' && $('#custom-enabled').checked) {
      if (p.execution_mode === 'stdin') body.custom_stdin = $('#custom-args').value;
      else {
      try { body.custom_args = JSON.parse($('#custom-args').value); if (!Array.isArray(body.custom_args)) throw new Error(); }
      catch (_) { toast('自定义输入必须是有效的 JSON 参数数组，例如 [2, 3]。'); $('#custom-args').focus(); return; }
      if (p.parameters && body.custom_args.length !== p.parameters.length) { toast(`此题需要 ${p.parameters.length} 个参数，请检查最外层数组的长度。`); $('#custom-args').focus(); return; }
      }
    }
    busy = true; resultTab = mode === 'trace' ? 'trace' : 'tests'; traceIndex = 0; $('#run-code').disabled = true; $('#submit-code').disabled = true;
    $$('.workbench-run-actions button').forEach(button => button.disabled = true);
    $('#result-body').innerHTML = `<div class="results-empty"><span class="spinner"></span><p>${mode === 'submit' ? '正在检查全部测试，包括边界情况…' : '正在运行你的代码…'}</p></div>`;
    progress.drafts[p.id] = code; save();
    try {
      const result = await api('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
      if (revisionAtStart !== stateRevision) { toast('运行期间学习记录已替换，本次结果未写入新记录。'); return; }
      result.source_code = code;
      if (mode === 'submit') {
        const previous = progress.attempts[p.id];
        progress.attempts[p.id] = {count:(previous?.count || 0)+1,lastStatus:result.status,lastAt:Date.now()};
        if (result.status === 'accepted' && !isAccepted(p.id)) progress.accepted.push(p.id);
        recordSubmission(p,code,result,submittedAt,trainingId,assisted);
        save();
      }
      if (routeAtStart === routeVersion && current?.id === p.id) { latestResult = result; renderResult(); if (mode === 'submit' && result.status === 'accepted') { renderDetail(); toast('提交通过！又向前迈了一步。'); } }
      else toast(`${p.id}. ${p.title}：${result.status === 'accepted' ? mode === 'submit' ? '提交通过' : '运行成功' : '运行结束'}`);
    } catch (error) {
      if (routeAtStart === routeVersion) { latestResult = {status:'error',mode,error:{type:'连接或请求错误',message:error.message,hint:'确认本地服务仍在运行，然后重试。'},cases:[],passed:0,total:0}; renderResult(); }
      else toast(error.message);
    } finally { busy = false; if ($('#run-code')) $('#run-code').disabled = false; if ($('#submit-code')) $('#submit-code').disabled = false; $$('.workbench-run-actions button').forEach(button => button.disabled = false); if(location.hash.startsWith('#training'))renderTraining(); }
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
    if (resultTab === 'trace') {
      const test = result.cases?.[0], steps = test?.trace || [];
      if (!steps.length) { $('#result-body').innerHTML = `<div class="result-content">${renderError(result.error)}<div class="trace-intro"><h3>把程序的执行过程看清楚</h3><p>点击上方「逐步观察」，执行第一个示例或自定义输入，再用上一步／下一步查看变量变化。仅记录 Python 代码，不进入第三方库。</p><p>观察运行不会计入题目通过或限时训练成绩。</p></div></div>`; return; }
      traceIndex = Math.min(Math.max(0, traceIndex), steps.length - 1);
      const step = steps[traceIndex], previous = traceIndex ? steps[traceIndex-1] : null;
      const codeLine = (result.source_code || '').split('\n')[step.line-1] || '';
      $('#result-body').innerHTML = `<div class="result-content trace-content"><div class="trace-controls"><button class="button small" data-trace-step="${traceIndex-1}" ${traceIndex ? '' : 'disabled'}>← 上一步</button><b>第 ${traceIndex+1} / ${steps.length} 步</b><button class="button small" data-trace-step="${traceIndex+1}" ${traceIndex===steps.length-1?'disabled':''}>下一步 →</button></div><p class="result-caption">${step.event==='line'?'即将执行这一行，下方是执行前的局部变量。':step.event==='return'?`函数返回：${esc(step.value)}`:`此行抛出异常：${esc(step.exception)}`} · ${esc(step.function)}</p><button class="trace-source" data-error-line="${step.line}"><span>第 ${step.line} 行</span><code>${esc(codeLine)}</code></button><table class="trace-variables"><thead><tr><th>变量</th><th>当前值（长内容截取展示）</th></tr></thead><tbody>${Object.entries(step.locals).map(([name,value])=>`<tr class="${previous?.locals?.[name]!==value?'trace-changed':''}"><td>${esc(name)}</td><td><code>${esc(value)}</code></td></tr>`).join('')||'<tr><td colspan="2">此时还没有可显示的局部变量。</td></tr>'}</tbody></table><p class="result-caption">高亮表示相较上一步变量值发生变化。运行已完整结束，这里回放记录；不支持暂停修改变量。${test.trace_truncated?'已达到 160 步或记录大小上限，后续步骤省略；可缩小自定义输入再观察。':''}</p>${renderError(result.error)}<details><summary>本次运行的输出与返回值</summary><pre>${esc(test.stdout || '（没有标准输出）')}\n返回／答案：${esc(json(test.actual))}</pre></details></div>`;
      return;
    }
    if (resultTab === 'output') { $('#result-body').innerHTML = `<div class="result-content"><p class="result-caption">标准输出 · ${current?.execution_mode === 'stdin' ? '这是程序的答案输出；调试信息请写入 stderr。' : '这是 print / console.log 输出，不是函数返回值。'}</p><pre class="terminal-output">${esc((result.cases || []).map((item,i) => `用例 ${i+1}\nstdout:\n${item.stdout || '（没有标准输出）'}${item.stderr ? '\nstderr（调试）:\n' + item.stderr : ''}`).join('\n\n') || '（没有标准输出）')}</pre></div>`; return; }
    if (resultTab === 'terminal') { $('#result-body').innerHTML = `<div class="result-content"><p class="result-caption">本地执行日志 · ${language(current)} · ${result.mode === 'submit' ? '提交全部测试' : '运行测试'}</p><pre class="terminal-output">${esc(`> ${result.mode === 'submit' ? '提交检查' : '运行代码'}\n状态: ${result.status}\n测试: ${result.passed || 0} / ${result.total || 0}\n耗时: ${result.duration_ms == null ? '—' : Math.round(result.duration_ms) + ' ms'}\n${result.error ? '\n' + (result.error.traceback || result.error.message || '') : '\n执行结束。'}`)}</pre></div>`; return; }
    if (resultTab === 'problems') { const failed = (result.cases || []).filter(c => !c.passed); $('#result-body').innerHTML = `<div class="result-content">${renderError(result.error)}${failed.map((c,i) => `<div class="error-card"><strong>失败测试 ${i+1}</strong>${c.error ? renderError(c.error) : `<p>预期：${esc(json(c.expected))}</p><p>实际：${esc(json(c.actual))}</p>`}</div>`).join('')}${!result.error && !failed.length ? '<p class="result-caption">✓ 本次执行没有报告问题。运行示例后仍需提交全部测试，才能完成本题。</p>' : ''}</div>`; return; }
    const ok = result.status === 'accepted', custom = result.cases?.some(c => c.custom);
    const title = ok ? custom ? '自定义运行成功' : result.mode === 'submit' ? '全部通过，做得好！' : '示例通过，试着提交吧' : ({wrong_answer:'结果还差一点',syntax_error:'代码语法需要调整',runtime_error:'运行遇到问题',timeout:'运行超时',missing_dependency:'需要安装依赖',error:'请求未能完成'}[result.status] || '运行未通过');
    const c = result.cases?.[selectedCase];
    const next = problems[problems.findIndex(p => p.id === current.id)+1];
    $('#result-body').innerHTML = `<div class="result-content"><div class="result-summary ${ok ? '' : 'failed'}"><strong>${ok ? '✓' : '↺'} ${title}</strong><small>${result.duration_ms != null ? `${Math.round(result.duration_ms)} ms` : ''}</small></div><p class="result-caption">${custom ? '自定义输入没有预设答案，本次只检查能否正常执行，不计入完成。' : `${result.passed || 0} / ${result.total || 0} 个测试通过。${result.mode !== 'submit' ? '运行示例不计入完成；点击「提交检查」验证全部测试。' : ok ? '本题已计入学习进度。' : '比较输入、预期输出与实际输出，修正后再试一次。'}`}</p>${renderError(result.error)}${result.cases?.length ? `<div class="case-tabs" aria-label="测试用例">${result.cases.map((item,i) => `<button class="case-tab ${item.passed ? '' : 'failed'} ${i === selectedCase ? 'active' : ''}" data-case="${i}">${item.passed ? '✓' : '×'} ${item.custom ? '自定义' : `用例 ${i+1}`}</button>`).join('')}</div>` : ''}${c ? `<div class="case-details"><div class="case-value"><label>${current.execution_mode === 'stdin' ? '标准输入 stdin' : '输入参数'}</label><pre>${esc(current.execution_mode === 'stdin' ? c.stdin : json(c.args))}</pre></div>${!c.custom ? `<div class="case-value"><label>预期输出</label><pre>${esc(current.execution_mode === 'stdin' ? c.expected : json(c.expected))}</pre></div>` : ''}<div class="case-value ${!c.passed ? 'wrong' : ''}"><label>${current.execution_mode === 'stdin' ? '实际标准输出' : '实际返回值'}</label><pre>${esc(current.execution_mode === 'stdin' ? c.actual : json(c.actual))}</pre></div><div class="case-value"><label>标准输出（print / console.log）</label><pre>${esc(c.stdout || '（没有标准输出）')}</pre></div>${c.stderr ? `<div class="case-value"><label>标准错误 stderr · 调试信息</label><pre>${esc(c.stderr)}</pre></div>` : ''}${c.hint ? `<p class="case-hint">${esc(c.hint)}</p>` : ''}${c.error && !result.error ? renderError(c.error) : ''}</div>` : ''}${ok && result.mode === 'submit' && next ? `<a class="button primary next-success" href="#problem/${next.id}">继续下一题：${esc(next.title)} →</a>` : ''}</div>`;
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
    const url = URL.createObjectURL(blob), a = document.createElement('a'); a.href = url; a.download = `pystep-progress-${new Date().toISOString().slice(0,10)}.json`; a.click(); setTimeout(() => URL.revokeObjectURL(url),1000); toast('进度已导出，包含草稿、提交快照、训练、收藏和笔记。');
  }
  async function importProgress(file) {
    if (!file) return;
    if (file.size > 12*1024*1024) { toast('备份文件超过 12 MB，无法导入。'); return; }
    try {
      const imported = validateProgress(JSON.parse(await file.text()));
      const known = new Set(problems.map(p => p.id));
      const importedIds = [...imported.accepted,...imported.starred,...Object.keys(imported.drafts).map(Number),...Object.keys(imported.notes).map(Number),...Object.keys(imported.attempts).map(Number),...Object.keys(imported.assistance).map(Number),...Object.keys(imported.checkpoints).map(Number),...imported.submissions.map(s=>s.problemId),...[imported.training,...imported.trainingArchive].flatMap(s=>s?.problemIds||[])];
      if (importedIds.some(id => !known.has(id))) throw new Error('备份含当前题库不存在的题号，请使用对应版本平台。');
      if (!confirm(`将用备份覆盖当前学习记录：${imported.accepted.length} 题已完成，${imported.starred.length} 题已收藏。当前草稿和笔记也会被替换。建议先导出当前进度。继续导入？`)) return;
      progress = imported; stateRevision++; save(); applyTheme(); await route(); toast('学习进度已导入。');
    } catch (error) { toast(`导入失败：${error.message}`); }
    finally { $('#import-file').value = ''; }
  }
  function openGuide() { $('#guide-dialog').showModal(); }
  function closeGuide() { $('#guide-dialog').close(); progress.guideSeen = true; save(); }
  async function route() {
    if (editorObserver) { editorObserver.disconnect(); editorObserver = null; }
    const token = ++routeVersion, hash = location.hash.slice(1) || 'home', [path,query = ''] = hash.split('?'), params = new URLSearchParams(query);
    let kind = path.split('/')[0]; if (!(kind in labels)) kind = 'home';
    current = null; document.body.classList.remove('editor-focus'); setPage(kind); window.scrollTo(0,0);
    try {
      if (kind === 'problem') { const id = Number(path.split('/')[1]); if (!Number.isInteger(id) || !problems.some(p => p.id === id)) throw new Error('没有找到这道练习，请返回题库选择。'); await renderProblem(id,token); }
      else if (['problems','favorites','review'].includes(kind)) renderCatalog(kind,params);
      else if (kind === 'lab') renderLab(); else if (kind === 'roadmap') renderRoadmap(); else if (kind === 'training') renderTraining(); else if (kind === 'history') renderHistory(params); else renderHome();
    } catch (error) { if (token === routeVersion) $('#main-content').innerHTML = `<div class="panel empty-state"><div class="empty-icon">↺</div><h3>暂时无法打开</h3><p>${esc(error.message)}</p><a class="button primary" href="#problems">返回题库</a></div>`; }
  }
  document.addEventListener('click',event => {
    const traceStep = event.target.closest('[data-trace-step]'); if (traceStep) { traceIndex = Number(traceStep.dataset.traceStep); renderResult(); return; }
    const command=event.target.closest('[data-command-index]');if(command){$('#command-dialog').close();return;}
    const step=event.target.closest('[data-learn-step]');if(step&&current){const value=step.dataset.learnStep;if(value==='guided'){detailTab='hints';renderDetail();}else if(value==='independent'){$('#code-editor').focus();if(progress.assistance[current.id])toast('这份草稿使用过辅助。点击课堂中的「独立重写」重新开始。');}else{detailTab='lesson';renderDetail();$(`#lesson-${value}`)?.scrollIntoView({behavior:'smooth',block:'start'});}return;}
    const restore=event.target.closest('[data-restore]');if(restore){const snapshot=progress.submissions.find(s=>s.id===restore.dataset.restore);if(!snapshot)return;if(trainingLocked(snapshot.problemId)){toast('训练结束后可以恢复此题历史代码。');return;}if(progress.drafts[snapshot.problemId]&&progress.drafts[snapshot.problemId]!==snapshot.code&&!confirm('用此代码快照覆盖当前草稿？提交记录仍然保留。'))return;progress.drafts[snapshot.problemId]=snapshot.code;progress.assistance[snapshot.problemId]=snapshot.assisted;save();location.hash=`problem/${snapshot.problemId}`;toast('已恢复代码快照。可修改后重新运行。');return;}
    const activity = event.target.closest('[data-activity]'); if (activity) { detailTab = activity.dataset.activity; renderDetail(); $$('.activity-icon[data-activity]').forEach(button => button.classList.toggle('active',button === activity)); $('#problem-body').scrollTop = 0; return; }
    const resultButton = event.target.closest('[data-result-tab]'); if (resultButton) { resultTab = resultButton.dataset.resultTab; renderResult(); return; }
    const star = event.target.closest('[data-star]');
    if (star) { event.preventDefault(); event.stopPropagation(); const id = Number(star.dataset.star); progress.starred = isStarred(id) ? progress.starred.filter(n => n !== id) : [...progress.starred,id]; save(); $$(`[data-star="${id}"]`).forEach(b => { b.classList.toggle('starred',isStarred(id)); b.textContent = isStarred(id) ? '★' : '☆'; b.setAttribute('aria-pressed',String(isStarred(id))); b.setAttribute('aria-label',isStarred(id) ? '取消收藏' : '收藏题目'); b.title = isStarred(id) ? '取消收藏' : '收藏题目'; }); if (location.hash.startsWith('#favorites')) route(); return; }
    const tab = event.target.closest('[data-tab]'); if (tab) { detailTab = tab.dataset.tab; renderDetail(); return; }
    const caseButton = event.target.closest('[data-case]'); if (caseButton) { renderResult(Number(caseButton.dataset.case)); return; }
    const lineButton = event.target.closest('[data-error-line]'); if (lineButton) { const editor = $('#code-editor'); if (editor) { const n = Number(lineButton.dataset.errorLine), lines = editor.value.split('\n'), pos = lines.slice(0,n-1).reduce((sum,line) => sum + line.length + 1,0); editor.focus(); editor.setSelectionRange(pos,pos+(lines[n-1]?.length || 0)); editor.scrollTop = Math.max(0,(n-4)*23); } return; }
    const row = event.target.closest('[data-problem]'); if (row && !event.target.closest('a')) { location.hash = `problem/${row.dataset.problem}`; return; }
    const action = event.target.closest('[data-action]')?.dataset.action;
    if (action === 'palette') openPalette();
    if (action === 'close-palette') $('#command-dialog').close();
    if (action === 'start-training') startTraining();
    if (action === 'finish-training' && confirm('提前结束本场计时并保存结果？结束后不能继续累计本场成绩。')) finishTraining();
    if (action === 'new-training') { if (progress.training?.status === 'finished') { progress.trainingArchive.unshift(progress.training);progress.trainingArchive=progress.trainingArchive.slice(0,12);progress.training=null;save();renderTraining();tickTraining(); } }
    if (action === 'font-smaller' || action === 'font-larger') { progress.settings.fontSize=Math.max(12,Math.min(22,progress.settings.fontSize+(action==='font-larger'?1:-1)));applyEditorSettings();save(); }
    if (action === 'focus-editor') {progress.settings.focus=!progress.settings.focus;applyEditorSettings();save();}
    if (action === 'understood' && current) {progress.checkpoints[current.id]=2;save();renderDetail();toast('已记录自检。下一步：独立实现，再提交验证。');}
    if (action === 'independent-rewrite' && current && confirm('恢复初始代码并清除辅助标记，开始独立重写？当前草稿会被覆盖。')) { independentRewrite(); }
    if (action === 'guide') openGuide();
    if (action === 'export') exportProgress();
    if (action === 'import') $('#import-file').click();
    if (action === 'next-hint' && current && !trainingLocked(current.id)) { hintCount++;progress.assistance[current.id]=true;save();renderDetail(); }
    if (action === 'reveal-solution' && current && !trainingLocked(current.id)) { solutionVisible = true;progress.assistance[current.id]=true;save();renderDetail(); }
    if (action === 'use-solution' && current && !trainingLocked(current.id) && confirm('将参考答案填入编辑器？当前草稿会被覆盖。')) { progress.assistance[current.id]=true;$('#code-editor').value = current.solution; $('#code-editor').dispatchEvent(new Event('input')); toast('已填入参考答案，标记为辅助练习。理解后请独立重写。'); }
    if (action === 'reset-progress' && confirm('清空全部已完成记录、提交记录、代码草稿、收藏和笔记？此操作无法撤销，请先导出备份。')) { const theme = progress.theme; progress = emptyState(); stateRevision++; progress.theme = theme; progress.guideSeen = true; save(); route(); toast('学习记录已清空。'); }
  });
  document.addEventListener('keydown',event => {
    if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='k'){event.preventDefault();openPalette();return;}
    if(event.key==='Escape'&&document.body.classList.contains('editor-focus')&&!$('#command-dialog').open){progress.settings.focus=false;applyEditorSettings();save();}
    if($('#command-dialog').open&&['ArrowDown','ArrowUp','Enter'].includes(event.key)){const entries=$$('.command-result'),selected=$('.command-result.selected'),index=entries.indexOf(selected);if(entries.length){event.preventDefault();if(event.key==='Enter'){selected?.click();}else{selected?.classList.remove('selected');const next=entries[(index+(event.key==='ArrowDown'?1:-1)+entries.length)%entries.length];next.classList.add('selected');next.scrollIntoView({block:'nearest'});}}return;}
    if (event.altKey && ['ArrowLeft','ArrowRight'].includes(event.key) && current && !['TEXTAREA','INPUT','SELECT'].includes(event.target.tagName)) { event.preventDefault(); const index = problems.findIndex(p => p.id === current.id), p = problems[index + (event.key === 'ArrowLeft' ? -1 : 1)]; if (p) location.hash = `problem/${p.id}`; }
    if (event.target.matches('.panel-tab') && ['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) { event.preventDefault(); const tabs = $$('.panel-tab'), index = tabs.indexOf(event.target), next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length-1 : (index+(event.key === 'ArrowRight' ? 1 : -1)+tabs.length)%tabs.length; tabs[next].click(); tabs[next].focus(); }
  });
  $('#theme-toggle').onclick = () => { progress.theme = progress.theme === 'dark' ? 'light' : 'dark'; applyTheme(); save(); };
  $('#export-progress').onclick = exportProgress; $('#import-progress').onclick = () => $('#import-file').click(); $('#import-file').onchange = e => importProgress(e.target.files[0]);
  $('#open-guide').onclick = openGuide; $('#close-guide').onclick = closeGuide; $('#guide-start').onclick = () => { closeGuide(); if (!location.hash || location.hash === '#home') location.hash = `problem/${problems[0]?.id || 1}`; };
  $('#guide-dialog').addEventListener('cancel',() => { progress.guideSeen = true; save(); });
  $('#command-search').addEventListener('input',renderPalette);
  applyTheme();
  (async () => {
    try {
      const [catalog, environment] = await Promise.all([api('/api/problems'),api('/api/meta').catch(() => null)]);
      problems = catalog.problems.map(p=>({...p,tags:[...new Set([...(p.tags||[]),...(p.skills||[])])]})); chapters = catalog.chapters; meta = environment || {};
      $('#nav-total').textContent = problems.length;
      $('#runtime-state').innerHTML = environment ? `<i></i>Python ${esc(meta.python)} · 本地已连接` : '<i></i>题库已连接 · 环境信息不可用';
      $('#runtime-state').classList.toggle('offline',!environment);
      $('#runtime-state').title = `SQL: SQLite ${meta.sqlite || '—'}；JavaScript: ${meta.dependencies?.node?.available ? 'Node.js ' + meta.dependencies.node.version : '需要安装 Node.js'}`;
      window.addEventListener('hashchange',route); tickTraining(); setInterval(tickTraining,1000); await route();
      if (!progress.guideSeen) openGuide();
      if (storageWarning) toast('进度读取失败或存储不可用，可导入已有备份恢复。');
    } catch (error) { $('#runtime-state').innerHTML = '<i></i>本地服务未连接'; $('#runtime-state').classList.add('offline'); $('#main-content').innerHTML = `<div class="panel empty-state"><div class="empty-icon">↺</div><h3>还没有连接到学习平台</h3><p>${esc(error.message)}</p><p>请保持启动平台的窗口运行，通过本地地址访问页面。</p><button class="button primary" id="retry-load">重新连接</button></div>`; $('#retry-load').onclick = () => location.reload(); }
  })();
})();
