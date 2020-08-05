import sys
import statistics

if __name__ == '__main__':

   file_name = sys.argv[1]
   deploy_num_list = []
   startup_time_list = []
   Flag = False 
   deploy_num = 0
   with open(file_name, 'r') as f:
       for cnt, line in enumerate(f):
           if not Flag:
              Flag = True
              continue
           if 'time' in line:
               deploy_num_list.append(deploy_num)
           elif 'real' in line:
               line = " ".join(line.rstrip().split())
               startup_time = line.split(' ')[1].split('m')
               startup_time = float(startup_time[0])*60+float(startup_time[1][:-1])
               startup_time_list.append(startup_time)
               deploy_num += 1

   print('deploy num:')
   for v in deploy_num_list:
       print(v, end = ' ')
   print('\n')
   for v in startup_time_list:
       print(v, end = ' ')
   print('\n')
   print('average startup time:', statistics.mean(startup_time_list))
