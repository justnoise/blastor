from aiohttp import web
import asyncio
import time
import subprocess
import sys
import os


PRIVOXY_LOGFILE = '/var/log/privoxy/logfile'
MAX_IDLE_TIME = 30 * 60  # 30 minutes
LIFETIME = 12 * 60 * 60  # 12 hours
kill_at = time.time() + LIFETIME


async def handle_deathclock(request):
    data = await request.post()
    new_time = data.get('time')
    set_deathclock(new_time)
    return web.Response(text='OK')


async def handle_delete(request):
    set_deathclock(5)
    return web.Response(text='OK')


async def handle_newnym(request):
    # throw it to the wind.  It'll work!  If it don't, I'll rewrite this
    cmd = """echo -e 'authenticate ""\nsignal newnym\nquit\n' | nc localhost 9051"""
    subprocess.run(cmd, shell=True)
    return web.Response(text='OK')


def set_deathclock(seconds_from_now):
    global kill_at
    print("Setting deathclock to {}s".format(seconds_from_now)
    seconds_from_now = float(seconds_from_now)
    kill_at = time.time() + seconds_from_now


async def deathclock_loop():
    while True:
        if time.time() > kill_at:
            print("killing process due deathclock expiration")
            sys.stdout.flush()
            sys.exit(0)
        await asyncio.sleep(1)


async def log_loop(logfile):
    last_filesize = -1
    last_change_time = time.time()
    while True:
        try:
            filesize = os.stat(logfile).st_size
            if filesize != last_filesize:
                last_filesize = filesize
                last_change_time = time.time()
        except OSError:
            pass
        if last_change_time + MAX_IDLE_TIME < time.time():
            print("killing process due to unchanging log filesize")
            sys.stdout.flush()
            sys.exit(0)
        await asyncio.sleep(10)


def run_services():
    subprocess.run('service tor start', shell=True)
    subprocess.run('service privoxy start', shell=True)


def main():
    loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    app.router.add_post('/deathclock', handle_deathclock)
    app.router.add_delete('/', handle_delete)
    app.router.add_get('/newnym', handle_newnym)
    run_services()
    loop.create_task(deathclock_loop())
    loop.create_task(log_loop(PRIVOXY_LOGFILE))
    web.run_app(app)


if __name__ == '__main__':
    main()
