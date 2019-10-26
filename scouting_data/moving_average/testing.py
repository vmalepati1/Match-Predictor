import numpy as np

current_team_data = []
# print(current_team_data)

previous_team_data = []
previous_team_data.append([1, 2, 3, 4])
previous_team_data.append([2, 3, 4, 5])
print(np.average([[[1, 2, 3, 4]] + [[2, 3, 4, 5], [2, 3, 4, 5]]], axis=1))

i = 0
for i in range(0, 5):
    print('Yay')

print(i)