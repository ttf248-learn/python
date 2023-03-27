import pymysql


# connect mysql and select data
def connect_mysql(sql):
    conn = pymysql.connect(host='192.168.19.146', user='root', port=5306, passwd='sErjf&eNh9zv4CSV', db='ykcz_trade', charset='utf8')
    cur = conn.cursor()
    cur.execute(sql)
    # 是否为空
    if cur.rowcount == 0:
        print('No data')
        return None

    data = cur.fetchall()
    # 获取字段名
    field = [i[0] for i in cur.description]
    # 将字段名和数据组合成字典
    data_dict = [dict(zip(field, i)) for i in data]

    cur.close()
    conn.close()

    return data_dict

# compare dict
def compare_dict(dict1, dict2):
    for key in dict1:
        if dict1[key] != dict2[key]:
            # 打印 右对齐
            print('{0:20} {1:20} {2:20}'.format(key, dict1[key], dict2[key]))


if __name__ == '__main__':
    # qas 数据
    data_153 = connect_mysql("select * from ykcz_trade.tsecu_product where product_code = '00152'")
    # pubber 数据
    data_152 = connect_mysql("select * from ykcz_trade.tsecu_product where product_code = '00153'")

    # 其中一个为空
    if data_153 is None or data_152 is None:
        print('No data')
        exit()
        
    compare_dict(data_153[0], data_152[0])