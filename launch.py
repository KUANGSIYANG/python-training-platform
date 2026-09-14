"""Convenient launch with delayed browser open after the HTTP listener exists."""
import threading
import webbrowser

from server import LearningServer


def main():
    server = None
    for port in range(8765, 8786):
        try:
            server = LearningServer(('127.0.0.1', port))
            break
        except OSError as exc:
            if getattr(exc, 'winerror', None) != 10048 and getattr(exc, 'errno', None) != 98:
                raise
    if server is None:
        print('端口 8765–8785 都被占用，请关闭旧的平台窗口后再试。')
        return 1
    url = f'http://127.0.0.1:{server.server_port}'
    print(f'PyStep 学习平台已启动：{url}', flush=True)
    print('保持此窗口运行，关闭窗口或按 Ctrl+C 停止。', flush=True)
    print('只运行你信任的本地代码。学习进度保存在当前浏览器。', flush=True)
    if server.server_port != 8765:
        print('默认端口被占用，已换用空闲端口。不同端口的浏览器进度独立，可导入备份。', flush=True)
    timer = threading.Timer(0.4, lambda: webbrowser.open(url))
    timer.daemon = True
    timer.start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n学习平台已停止。')
    finally:
        server.server_close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
