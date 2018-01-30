import numpy
import os.path

def read_tape7(filename='tape7.scn'):

   if os.path.isfile(filename):

      tape7 = {'wavlen mcrn': numpy.array([], dtype=numpy.float),
               'trans':       numpy.array([], dtype=numpy.float),
               'pth thrml':   numpy.array([], dtype=numpy.float),
               'thrml sct':   numpy.array([], dtype=numpy.float),
               'surf emis':   numpy.array([], dtype=numpy.float),
               'sol scat':    numpy.array([], dtype=numpy.float),
               'sing scat':   numpy.array([], dtype=numpy.float),
               'grnd rflt':   numpy.array([], dtype=numpy.float),
               'drct rflt':   numpy.array([], dtype=numpy.float),
               'total rad':   numpy.array([], dtype=numpy.float),
               'ref sol':     numpy.array([], dtype=numpy.float),
               'sol@obs':     numpy.array([], dtype=numpy.float),
               'depth':       numpy.array([], dtype=numpy.float)}

      with open(filename, 'r') as f:
         passedHeader = False
         for line in f:
            if line[0:7] == ' WAVLEN':
               passedHeader = True
               continue
            if passedHeader:
               if line[0:7] == ' -9999.':
                  break

               if line[0:12].strip() == '':
                  tape7['wavlen mcrn'] = \
                     numpy.append(tape7['wavlen mcrn'], None)
               else:
                  tape7['wavlen mcrn'] = \
                     numpy.append(tape7['wavlen mcrn'], 
                                  float(line[0:12].strip())) \

               if line[12:19].strip() == '':
                  tape7['trans'] = \
                     numpy.append(tape7['trans'], None)
               else:
                  tape7['trans'] = \
                     numpy.append(tape7['trans'], 
                                  float(line[12:19].strip())) \

               if line[19:30].strip() == '':
                  tape7['pth thrml'] = \
                     numpy.append(tape7['pth thrml'], None)
               else:
                  tape7['pth thrml'] = \
                     numpy.append(tape7['pth thrml'], 
                                  float(line[19:30].strip())) \

               if line[30:41].strip() == '':
                  tape7['thrml sct'] = \
                     numpy.append(tape7['thrml sct'], None)
               else:
                  tape7['thrml sct'] = \
                     numpy.append(tape7['thrml sct'], 
                                  float(line[30:41].strip())) \

               if line[41:53].strip() == '':
                  tape7['surf emis'] = \
                     numpy.append(tape7['surf emis'], None)
               else:
                  tape7['surf emis'] = \
                     numpy.append(tape7['surf emis'], 
                                  float(line[41:53].strip())) \

               if line[53:64].strip() == '':
                  tape7['sol scat'] = \
                     numpy.append(tape7['sol scat'], None)
               else:
                  tape7['sol scat'] = \
                     numpy.append(tape7['sol scat'], 
                                  float(line[53:64].strip())) \

               if line[64:75].strip() == '':
                  tape7['sing scat'] = \
                     numpy.append(tape7['sing scat'], None)
               else:
                  tape7['sing scat'] = \
                     numpy.append(tape7['sing scat'], 
                                  float(line[64:75].strip())) \

               if line[75:86].strip() == '':
                  tape7['grnd rflt'] = \
                     numpy.append(tape7['grnd rflt'], None)
               else:
                  tape7['grnd rflt'] = \
                     numpy.append(tape7['grnd rflt'], 
                                  float(line[75:86].strip())) \

               if line[86:97].strip() == '':
                  tape7['drct rflt'] = \
                     numpy.append(tape7['drct rflt'], None)
               else:
                  tape7['drct rflt'] = \
                     numpy.append(tape7['drct rflt'], 
                                  float(line[86:97].strip())) \

               if line[97:108].strip() == '':
                  tape7['total rad'] = \
                     numpy.append(tape7['total rad'], None)
               else:
                  tape7['total rad'] = \
                     numpy.append(tape7['total rad'], 
                                  float(line[97:108].strip())) \

               if line[108:117].strip() == '':
                  tape7['ref sol'] = \
                     numpy.append(tape7['ref sol'], None)
               else:
                  tape7['ref sol'] = \
                     numpy.append(tape7['ref sol'], 
                                  float(line[108:117].strip())) \

               if line[117:125].strip() == '':
                  tape7['sol@obs'] = \
                     numpy.append(tape7['sol@obs'], None)
               else:
                  tape7['sol@obs'] = \
                     numpy.append(tape7['sol@obs'], 
                                  float(line[117:125].strip())) \

               if line[125:133].strip() == '':
                  tape7['depth'] = \
                     numpy.append(tape7['depth'], None)
               else:
                  tape7['depth'] = \
                     numpy.append(tape7['depth'], 
                                  float(line[125:133].strip())) \

      f.close()

      return tape7

   else:
      msg = '"tape7" file does not exist at specified locationi: '
      msg +- '{0}'.format(filename)
      raise ValueError(msg)


if __name__ == '__main__':

   import radiometry.modtran

   home = os.path.expanduser('~')
   path = os.path.join(home, 'tmp')
   path = os.path.join(path, 'modtran')
   filename = os.path.join(path, 'tape7.scn')

   tape7 = radiometry.modtran.read_tape7(filename)

   print(tape7)

