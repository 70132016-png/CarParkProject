import pickle

with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)

print("Parking positions:")
for i, pos in enumerate(posList):
    print(f"{i+1}: {pos}")
