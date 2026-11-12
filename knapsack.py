# knapsack.py
# 0/1 Knapsack using DP
# here weight = parcel weight (kg), value = parcel priority, capacity = van capacity


def knapsack(parcels, capacity):
    n = len(parcels)

    # dp[i][w] = best total priority using first i parcels when capacity is w
    dp = []
    for i in range(n + 1):
        dp.append([0] * (capacity + 1))

    for i in range(1, n + 1):
        weight = parcels[i - 1]["weight"]
        value = parcels[i - 1]["priority"]

        for w in range(capacity + 1):
            # case 1 : do not take this parcel
            dp[i][w] = dp[i - 1][w]

            # case 2 : take this parcel (only if it fits)
            if weight <= w:
                if dp[i - 1][w - weight] + value > dp[i][w]:
                    dp[i][w] = dp[i - 1][w - weight] + value

    # go back in the table to find which parcels were taken
    selected = []
    w = capacity
    for i in range(n, 0, -1):
        # if value is different from the row above, parcel i was taken
        if dp[i][w] != dp[i - 1][w]:
            selected.append(parcels[i - 1])
            w = w - parcels[i - 1]["weight"]

    # we went from last parcel to first, so reverse to get the sorted order back
    selected.reverse()

    return dp[n][capacity], selected, dp


def print_dp_table(dp, parcels, capacity):
    # first line shows the capacity 0, 1, 2 ... capacity
    line = f"{'capacity ->':<17}"
    for w in range(capacity + 1):
        line += f"{w:>3}"
    print(line)

    for i in range(len(dp)):
        if i == 0:
            label = "no parcel"
        else:
            p = parcels[i - 1]
            label = f"{p['id']} (w={p['weight']},p={p['priority']})"

        line = f"{label:<17}"
        for value in dp[i]:
            line += f"{value:>3}"
        print(line)
