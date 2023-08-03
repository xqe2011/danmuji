import datetime, sys

sys.stdout.reconfigure(line_buffering=True)
def timeLog(string):
    now = datetime.datetime.now()
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S') + ',{:03d}'.format(now.microsecond // 1000)}] {string}")