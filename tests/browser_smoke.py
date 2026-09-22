"""Optional real-browser integration checks: python -X utf8 tests/browser_smoke.py.

Requires Playwright and its Chromium browser. Uses a temporary browser profile
and ephemeral localhost port, without touching the learner's saved progress.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import threading
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import LearningServer
from playwright.sync_api import sync_playwright, expect

KEY = 'pystep.progress.v1'
ARTIFACTS = Path(__file__).resolve().parents[1] / 'test-results'


def main():
    ARTIFACTS.mkdir(exist_ok=True)
    server = LearningServer(('127.0.0.1', 0))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f'http://127.0.0.1:{server.server_port}'
    old_progress = {'version': 1, 'drafts': {'1': server.problem_map[1]['solution']},
                    'accepted': [1, 303], 'attempts': {'1': {'count': 2, 'lastStatus': 'accepted', 'lastAt': int(time.time()*1000)}},
                    'notes': {'1': '旧版笔记'}, 'starred': [1], 'theme': 'light',
                    'lastProblem': 1, 'guideSeen': True}
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1440, 'height': 1000})
            context.add_init_script('if (!localStorage.getItem(' + json.dumps(KEY) + ')) localStorage.setItem(' + json.dumps(KEY) + ', ' + json.dumps(json.dumps(old_progress)) + ');')
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('dialog', lambda dialog: dialog.accept())

            def state():
                return page.evaluate('(key) => JSON.parse(localStorage.getItem(key))', KEY)

            def navigate(route, selector):
                page.goto(base + '/#' + route)
                expect(page.locator(selector).first).to_be_visible(timeout=20000)

            def submit(code):
                page.locator('#code-editor').fill(code)
                page.locator('#toolbar-submit').click()
                expect(page.locator('.result-summary')).to_be_visible(timeout=25000)
                expect(page.locator('#toolbar-submit')).to_be_enabled(timeout=25000)

            navigate('home', '.home-credit')
            expect(page.locator('#nav-total')).to_have_text(str(len(server.problems)))
            expect(page.locator('.home-credit')).to_have_text('Contributed by ksy')
            assert state()['notes']['1'] == '旧版笔记'
            page.screenshot(path=str(ARTIFACTS / 'home.png'), full_page=True)
            navigate('roadmap', '.stage-card')
            page.screenshot(path=str(ARTIFACTS / 'roadmap.png'), full_page=True)

            navigate('problem/1', '#code-editor')
            expect(page.locator('#code-editor')).to_have_value(server.problem_map[1]['solution'])
            submit('def solve(:\n    pass')
            expect(page.locator('#result-body')).to_contain_text('第 1 行')
            submit(server.problem_map[1]['solution'])
            expect(page.locator('.result-summary')).to_contain_text('全部通过')
            assert len(state()['submissions']) == 2
            page.locator('#toolbar-trace').click()
            expect(page.locator('.trace-controls')).to_be_visible(timeout=25000)
            assert len(state()['submissions']) == 2
            page.locator('[data-trace-step]').last.click()
            expect(page.locator('.trace-controls b')).to_contain_text('第 2 /')
            page.locator('[data-result-tab="tests"]').click()
            expect(page.locator('#result-body')).to_contain_text('不计入完成')
            page.locator('[data-result-tab="trace"]').click()
            page.locator('[data-action="font-larger"]').click()
            assert state()['settings']['fontSize'] == 15
            page.locator('[data-action="focus-editor"]').click()
            expect(page.locator('body')).to_have_class(__import__('re').compile('.*editor-focus.*'))
            page.keyboard.press('Escape')
            page.locator('#editor-split').fill('50')
            assert state()['settings']['split'] == 50
            page.screenshot(path=str(ARTIFACTS / 'workbench.png'), full_page=True)

            page.locator('#code-editor').fill('# changed draft')
            navigate('history?problem=1', '.history-card')
            page.locator('.history-card').first.locator('summary').click()
            page.locator('[data-restore]').first.click()
            expect(page.locator('#code-editor')).to_have_value(server.problem_map[1]['solution'])

            navigate('problem/361', '#code-editor')
            page.locator('#code-editor').fill(server.problem_map[361]['solution'])
            page.locator('#custom-enabled').check()
            page.locator('#custom-args').fill(server.problem_map[361]['examples'][0]['stdin'])
            page.locator('#toolbar-run').click()
            expect(page.locator('.result-summary')).to_contain_text('自定义运行成功', timeout=25000)
            assert 361 not in state()['accepted']
            submit('import sys\nprint("debug", file=sys.stderr)\n' + server.problem_map[361]['solution'])
            expect(page.locator('.result-summary')).to_contain_text('全部通过')
            expect(page.locator('#result-body')).to_contain_text('debug')
            page.keyboard.press('Control+k')
            page.locator('#command-search').fill('301')
            page.keyboard.press('Enter')
            expect(page).to_have_url(base + '/#problem/301')
            expect(page.locator('#code-editor')).to_be_visible()

            navigate('training', '#training-preset')
            page.locator('#training-preset').select_option('autumn')
            page.locator('#start-training').click()
            expect(page.locator('[data-countdown]').first).to_be_visible()
            session = state()['training']
            assert session['records'] == []
            assert 303 in session['problemIds']
            deadline = session['deadline']
            page.reload()
            expect(page.locator('[data-countdown]').first).to_be_visible()
            assert state()['training']['deadline'] == deadline
            first = session['problemIds'][0]
            navigate(f'problem/{first}', '#code-editor')
            page.locator('[data-tab="solution"]').click()
            assert page.locator('[data-action="reveal-solution"]').count() == 0
            submit(server.problem_map[first]['solution'])
            assert len(state()['training']['records']) == 1
            assert state()['training']['records'][0]['status'] == 'accepted'
            navigate('training', '.session-problems')
            page.locator('[data-action="finish-training"]').click()
            assert state()['training']['status'] == 'finished'
            assert len(state()['training']['records']) == 1
            page.screenshot(path=str(ARTIFACTS / 'training.png'), full_page=True)
            page.evaluate('''key => {
                const s=JSON.parse(localStorage.getItem(key));
                const first=s.training.records[0];
                delete s.training.totals;
                for(let i=0;i<500;i++)s.training.records.push({...first,status:'wrong_answer',passed:0});
                localStorage.setItem(key,JSON.stringify(s));
            }''', KEY)
            page.reload()
            expect(page.locator('.session-stats .stat-number').first).to_have_text(__import__('re').compile(r'^1'))
            expect(page.locator('.session-stats .stat-number').last).to_contain_text('501')
            page.locator('[data-action="new-training"]').click()
            assert state()['training'] is None and len(state()['trainingArchive']) == 1
            summary = state()['trainingArchive'][0]['totals'][str(first)]
            assert summary['accepted'] and summary['independent'] and summary['attempts'] == 501
            assert len(state()['trainingArchive'][0]['records']) == 500
            page.locator('#start-training').click()
            # Simulate returning after a closed-browser session has expired.
            page.evaluate('''key => {
                const s = JSON.parse(localStorage.getItem(key));
                s.training.startedAt = Date.now() - 60000;
                s.training.deadline = Date.now() - 1000;
                localStorage.setItem(key, JSON.stringify(s));
            }''', KEY)
            page.reload()
            expect(page.locator('[data-action="new-training"]')).to_be_visible()
            assert state()['training']['status'] == 'finished'

            # Assistance remains reviewable until the learner starts over.
            navigate('problem/1', '#code-editor')
            page.locator('[data-tab="solution"]').click()
            page.locator('[data-action="reveal-solution"]').click()
            assert state()['assistance']['1'] is True
            page.locator('[data-action="independent-rewrite"]').click()
            expect(page.locator('#code-editor')).to_have_value(server.problem_map[1]['starter'])
            assert state()['assistance']['1'] is False

            # Import a real legacy backup through the file picker flow.
            # A result from the old state must not overwrite the imported state.
            pending = []
            page.route('**/api/run', lambda route: pending.append(route))
            page.locator('#code-editor').fill(server.problem_map[1]['solution'])
            page.locator('#toolbar-submit').click()
            page.wait_for_timeout(50)
            assert len(pending) == 1
            page.locator('#reset-code').click()
            expect(page.locator('#toast')).to_contain_text('请等待本次运行结束')
            expect(page.locator('#code-editor')).to_have_value(server.problem_map[1]['solution'])
            page.locator('#import-file').set_input_files({'name': 'legacy.json', 'mimeType': 'application/json', 'buffer': json.dumps(old_progress).encode()})
            expect(page.locator('#toast')).to_have_text('学习进度已导入。')
            assert state()['notes']['1'] == '旧版笔记'
            assert state()['accepted'] == [1, 303]
            pending[0].fulfill(status=200, content_type='application/json', body=json.dumps({'status': 'accepted', 'passed': 5, 'total': 5, 'cases': [], 'mode': 'submit'}))
            expect(page.locator('#toast')).to_contain_text('本次结果未写入新记录')
            assert state()['attempts']['1']['count'] == 2
            assert state()['submissions'] == []
            page.unroute('**/api/run')

            page.set_viewport_size({'width': 390, 'height': 844})
            for route, selector in [('home', '.home-credit'), ('roadmap', '.stage-card'),
                                    ('problems', '#problem-list'), ('training', '#training-preset'),
                                    ('history', '.history-list'), ('problem/361', '#code-editor')]:
                navigate(route, selector)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), f'Horizontal overflow: {route}'
                if route == 'problem/361':
                    page.screenshot(path=str(ARTIFACTS / 'mobile-workbench.png'), full_page=True)
            assert not errors, '\n'.join(errors)
            context.close()
            browser.close()
            print(f'Browser checks passed: {len(server.problems)} problems, legacy progress, teaching route, judging, snapshots, timer, import and mobile layout.')
    finally:
        server.shutdown()
        server.server_close()
        thread.join(2)


if __name__ == '__main__':
    main()
