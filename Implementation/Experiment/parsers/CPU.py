import sys

if __name__ == '__main__':

   file_name = sys.argv[1]
   CPU_list = []
   Flag = False 
   with open(file_name, 'r') as f:
       for cnt, line in enumerate(f):
           if 'time' in line and Flag:
               CPU_list.append(avg_CPU/cnts)
               Flag = False 
           elif 'usr' in line:
               avg_CPU = 0
               cnts = 0
               Flag = True
           elif Flag:
               line = " ".join(line.rstrip().split())
               avg_CPU += round(100 - float(line.split(' ')[-1]), 2)
               cnts +=1 

   for v in CPU_list:
       print(v, end = ' ')
   print('\n')
