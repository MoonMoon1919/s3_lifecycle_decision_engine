x = 60
n = 30.416666666666668
z = 365

nm = 0
pm = 0


def caller(y):
    """
    Calculates whole months and partial months
    """
    global nm, pm

    if y > n:
        nm += 1
        a = y - n
    else:
        pm = y / n
        return True

    if a > n:
        caller(a)
    else:
        pm = a / n
        return True


caller(x)

# Calculate how many months objects will be in current storage class
sc = nm + pm

# Calculate how many months it will be in new storage class
sm = (1 - pm) + ((z - x) / n)

print(sc, sm)