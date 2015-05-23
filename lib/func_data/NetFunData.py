#!/usr/bin/env python
#-*- coding:utf-8 -*-

""" ��ȡ�������ݣ���/proc/net/dev �ļ� """
""" @Author: baoyiluo@gmail.com
    @Site: www.pythonpie.com
    @Date: 2013-05-23
    @Version: v1.2
    @Note:
        ��Ҫһ�������ļ� /tmp/proc_net_dev ��������һ�ε����ݣ���һ����ʱ��������ݣ�
        ���μ����ʱ���ñ������ݺ���һ��������������ֵ,������ʱ����ļ�����ֵ������������ս��(kb/s)
        /proc/net/dev �����ݵĽ��ͣ�
    [root@hpcstack ~]# cat /proc/net/dev
Inter-|   Receive                                                |  Transmit
 face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
    lo:664087762 3663780    0    0    0     0          0         0 664087762 3663780    0    0    0     0       0          0
  eth0:  651822    6311    0    0    0     0          0         0   553421    6076    0    0    0     0       0          0
  eth1:  663326    6060    0    0    0     0          0         0   962066    4571    0    0    0     0       0          0
interface:������
Receive(����):
    ��һ����(bytes)���ֽ���
    �ڶ�����(packets)������
    ��������(errs)���������
    ���ĸ���(drop)����������
    �������(fifo)��(First in first out)����/FIFO���������
    ��������(frame)��֡��
    ���߸���(compressed)��ѹ��(compressed)����
    �ڰ˸���(multicast)���ಥ��multicast, ����㲥�������鲥��)����
Transmit(����):
    ��һ����(bytes)���ֽ���
    �ڶ�����(packets)������
    ��������(errs)���������
    ���ĸ���(drop)����������
    �������(fifo)��(First in first out)����/FIFO���������
    ��������(colls): �ӿڼ�⵽�ĳ�ͻ��
    ���߸���(carrier): ���ӽ��ʳ��ֹ��ϴ������磺���߽Ӵ�����
    �ڰ˸���(compressed)��ѹ��(compressed)����

"""

import re
import time
import simplejson as json

def get_ProcNetDev(devices):
    """��ȡ����������
        @Params: devices = LIST # �����������豸�������� devices=['eth0', 'eth1', 'eth2', 'eth3']
        @Return: (status, msgs, results) 
            status = INT, Fuction execution status, 0 is normal , other is failure.
            msgs = STRING, If status equal to 0, msgs is '', otherwise will be filled with error message.
            results = DICE {
                    'eth0': { #����eth0�Ĵ�������
                        'transmit': 1024, #��λ������˵������ KB/s
                        'receive': 10240, 
                    },
                    'eth1': { #����eth1�Ĵ�������
                        'transmit': 1024, #��λ������˵������ KB/s
                        'receive': 10240, 
                    }
                }
        @Note:
    """

    status=0; msgs=''; results='';
    if devices == []:
        return (-1, 'Error: Params is None.', '')
    now_data = {} # ��ǰ /proc/net/dev ��ֵ
    last_data = {} # ��һ�� /proc/net/dev ��ֵ�� ʱ�����е��ó������

    # ��ȡ��ǰ����
    try:
        results = file('/proc/net/dev').read()
    except:
        return (-1, 'system file not exist', '')

    now_data['timestamp'] = time.time()
    for device in devices:
        pat = device + ":.*"
        try:
            devicedata = re.search(pat, results).group()
        except:
            return (-2, device+' not exist', '')
        
        tmp_main = devicedata.split(":")
        tmp=tmp_main[1].split()
        now_data[tmp_main[0].strip()] = {
            'receive_bytes': tmp[0],
            'receive_packets': tmp[1],
            'receive_errs': tmp[2],
            'receive_drop': tmp[3],
            'receive_fifo': tmp[4],
            'receive_frame': tmp[5],
            'receive_compressed': tmp[6],
            'receive_multicast': tmp[7],
            'transmit_bytes': tmp[8],
            'transmit_packets': tmp[9],
            'transmit_errs': tmp[10],
            'transmit_drop': tmp[11],
            'transmit_fifo': tmp[12],
            'transmit_colls': tmp[13],
            'transmit_carrier': tmp[14],
            'transmit_compressed': tmp[15]
        }
    # ��ȡ��ʷ����
    try:
        results = file('/tmp/proc_net_dev').read()
        last_data = json.loads("%s" % results.strip())
    except:
        last_data = now_data

    # д��ǰ���ݵ��ļ�
    fp = file('/tmp/proc_net_dev', 'w')
    fp.write(json.dumps(now_data))
    fp.close()

    # �����������ݣ��õ�Ҫ�����ֵ
    results = {}
    timecut = float(now_data['timestamp']) - float(last_data['timestamp'])
    if timecut > 0:
        for key in devices:
            receive = (int(now_data[key]['receive_bytes']) - int(last_data[key]['receive_bytes']))/float(1024)/timecut 
            transmit = (int(now_data[key]['transmit_bytes']) - int(last_data[key]['transmit_bytes']))/float(1024)/timecut 
            results[key] = {'receive':int(receive), 'transmit':int(transmit)}
    else:
        # ��һ�μ��ص�ʱ����ʷ����Ϊ�գ��޷����㣬���Գ�ʼ��Ϊ0
        for key in devices:
            results[key] = {'receive':0, 'transmit':0}
    return (status,msgs,results)

if __name__ == "__main__":
    while True:
        print get_ProcNetDev(devices=['eth0'])
        time.sleep(1)