current_team_data = []
# print(current_team_data)

previous_team_data = []
previous_team_data.append([1, 2, 3, 4])
previous_team_data.append([2, 3, 4, 5])
# print(previous_team_data[-3:])

for i, x in enumerate(previous_team_data, 1):
    print(i)
    print(x)

# print(np.average(current_team_data + previous_team_data, axis=0))
