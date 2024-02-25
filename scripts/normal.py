import numpy as np
import sys

with open('/tmp/normal.txt', 'w') as f:
    file = ""
    for i in range(int(sys.argv[1])):
        file += str(round(np.random.normal(1000, 100))) + ","
    f.write(file)

with open('/tmp/config.h', 'w') as f:
    f.write('#define CONFIG_NITERATIONS ' + str(sys.argv[1]))
