arr = [1,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0]
i = 0
read = 0
for j in range(15,-1,-1):
    read |= (arr[i] << j)
    i += 1
    
print("***" + str(read))

read >>= 3

print(read)

read *= 0.25

print(read)