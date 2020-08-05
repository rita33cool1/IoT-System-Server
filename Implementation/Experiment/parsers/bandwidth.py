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
                continue
            elif 'time' in line and Flag:
               uplink_list.append(round(avg_uplink/cnts, 2))
               downlink_list.append(round(avg_downlink/cnts, 2))
               Flag = False 
            elif 'Kbps' in line:
               avg_uplink = 0
               avg_downlink = 0
               cnts = 0
               Flag = True
            elif Flag:
               line = " ".join(line.rstrip().split())
               avg_downlink += float(line.split(' ')[1])
               avg_uplink += float(line.split(' ')[2])
               cnts +=1 

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
