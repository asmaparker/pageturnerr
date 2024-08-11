def search_title(title):
    rs = [int(x) for x in range(1, 10)]
    if len(rs) == 0:
        return False
    else:
        j = 0
        for i in rs:
            j += 1
            print("{}. {}".format(j, i))
        
        while True:
            ch = int(input("Enter the number of the book you would like to select: "))
            if ch <= 9 and ch >= 1:
                return rs[ch-1]
            else:
                print("Error! Choose a number from the list.")

print(search_title("hello"))