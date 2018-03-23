# -*- coding: utf-8 -*-
import psycopg2 as pg


def Header():
    print('Export metrics to csv v0.8')
    print()


if __name__ == '__main__':
    Header()
    conn = conn = pg.connect(host='127.0.0.1', user='eba', password='ebaeba18', database='eba')

    sql = 'select distinct filename from metrics'
    curr = conn.cursor()
    curr.execute(sql)
    rows = curr.fetchall()
    cols = ['id', 'transect_id', 'filename', 'index_', 'x', 'y', 'all_', 'min', 'max', 'avg', 'qav', 'std', 'ske',
            'kur', 'p01', 'p05', 'p10', 'p20', 'p25', 'p30', 'p40', 'p50', 'p60', 'p70', 'p75', 'p80', 'p90', 'p95',
            'p99', 'b05', 'b10', 'b20', 'b30', 'b40', 'b50', 'b60', 'b70', 'b80', 'b90', 'c00', 'c01', 'c02', 'c03',
            'c04', 'c05', 'c06', 'c07', 'c08', 'd00', 'd01', 'd02', 'd03', 'd04', 'd05', 'd06', 'd07', 'd08', 'cov_gap',
            'dns_gap']
    colsstr = ','.join(map(str, cols))
    for row in rows:
        transect = row[0]
        f = open(r'e:\metrics\{0}.csv'.format(transect), 'w')
        f.write(colsstr + '\n')
        sql = "SELECT {0} FROM metrics where filename  = '{1}'".format(colsstr, transect)
        curr2 = conn.cursor()
        curr2.execute(sql)
        metrics = curr2.fetchall()
        for row in metrics:
            line = ''
            for j in range(len(cols)):
                line += '{0},'.format(row[j])
            f.write(line[:-1] + '\n')
        f.close()
        print(transect)
    print('Done.')
