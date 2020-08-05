import sys

if __name__ == '__main__':

    file_name = sys.argv[1]
    up_name = sys.argv[2]
    down_name = sys.argv[3]
    uplink_list = []
    downlink_list = []
    Flag = False 
    with open(file_name, 'r') as f:
        for cnt, line in enumerate(f):
            if 'Connection to 192.168.1.102 closed.' in line and Flag:
                uplink_list.append(uplink_list[-1])
                downlink_list.append(downlink_list[-1]) 
            elif 'time' in line and Flag:
                Flag = False 
            elif 'Kbps' in line:
                Flag = True
            elif Flag:
                line = " ".join(line.rstrip().split())
                uplink_list.append(round(float(line.split(' ')[2]), 2))
                downlink_list.append(round(float(line.split(' ')[1]), 2))

    #print('len(uplink_list): ' + str(len(uplink_list)))
    #print('len(downlink_list): ' + str(len(downlink_list)))

    with open(up_name, 'w') as wf:
        for v in uplink_list[:-1]:
            wf.write(str(v)+',')
            #print(v, end = ' ')
        wf.write(str(uplink_list[-1]))
        #print('\n')
    with open(down_name, 'w') as wf:
        for v in downlink_list[:-1]:
            wf.write(str(v)+',')
            #print(v, end = ' ')
        wf.write(str(downlink_list[-1]))
        #print('\n')
