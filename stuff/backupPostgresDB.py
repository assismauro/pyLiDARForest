import os
import time
from subprocess import PIPE, Popen

host = '127.0.0.1'
user = 'eba'
os.environ['PGPASSWORD'] = 'ebaeba18'
db = 'eba'
schema = 'public'
port = 5432
backupdir = r'H:\PostgresBkp'
filename = '{0}_{1}.backup'.format(db, time.strftime('%Y-%m-%d'))
cmd = 'pg_dump.exe -h {0} -p {1} -U {2} -f {3}\{4} -n {5} -Z9 -Fc -b -v {6}'.format(host, port, user, backupdir,
                                                                                    filename, schema, db)
print(cmd)
start_time = time.time()
df = Popen(cmd, stdout=PIPE)
output, err = df.communicate()
print(output)
print(err)
print(time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time)))
