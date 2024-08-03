f = open("check.txt", "w")
for i in range(1, 9999999999):
    f.write(str(i) + "\n")
f.close()