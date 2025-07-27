import subprocess

subprocess.call(['git', 'init'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.call(['git', 'add', '*'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.call(['git', 'commit', '-m', 'Apply hermesbaby starter kit "log-ledger"'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
