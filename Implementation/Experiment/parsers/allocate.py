import sys

class analytic():
 def __init__(self, name):
  self.name = name
  if name == 'yolo1':
     self.scale = 1
     self.weight = 1
  elif name =='yolo2':
     self.scale = 1.15
     self.weight = 0.8
  elif name =='yolo3':
     self.scale = 0.85 
     self.weight = 0.6
  elif name =='yolo4':
     self.scale = 1.3
     self.weight = 0.4
  elif name =='yolo5':
     self.scale = 0.7
     self.weight = 0.2
  elif name =='audio1':
     self.scale = 1
     self.weight = 0.9
  elif name =='audio2':
     self.scale = 1.15
     self.weight = 0.7
  elif name =='audio3':
     self.scale = 0.85
     self.weight = 0.5
  elif name =='audio4':
     self.scale = 1.3
     self.weight = 0.3
  elif name =='audio5':
     self.scale = 0.7
     self.weight = 0.1

if __name__ == '__main__':

   file_name = sys.argv[1]
   QoS_list = []
   Flag = False 
   with open(file_name, 'r') as f:
       avg_QoS = 0
       weights = 1
       for cnt, line in enumerate(f):
           if cnt == 0:
              continue
           if '**time' in line and Flag:
               QoS_list.append(avg_QoS/weights)
           elif 'Done' in line:
               avg_QoS = 0
               weights = 0
           elif 'audio' in line or 'yolo' in line:
               app_name = analytic(line.split(' ')[0])
               QoS = float(line.split(' ')[3])
              
               avg_QoS += min(QoS*app_name.scale, 1.0)*app_name.weight
               weights += app_name.weight
           Flag = True

   for v in QoS_list:
       print(v, end = ' ')
   print('\n')
