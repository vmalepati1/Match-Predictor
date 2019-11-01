from collections import OrderedDict

import tbapy
import operator

tba = tbapy.TBA('1wui0Dih1NifktYrjoXW2hWaMY9XwTfRXaM985Eringd4jeU2raza2nSLXfiALPM')

oprs = tba.event_oprs('2019gacmp')['dprs']
sorted_oprs = sorted(oprs.items(), key=operator.itemgetter(1))
print(sorted_oprs)