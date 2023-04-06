

arr = range(10, 70)
idx = len(arr) // 2
mov = len(arr) // 2
target = 50

for _ in range(0, 6):  # only try 6 times

    print('index', idx, 'movement', mov, 'val', arr[idx])

    if target == arr[idx]:
        print('Done')
        break

    mov -= (mov//2)

    if target < arr[idx]:
        idx -= mov
    else:
        idx += mov


