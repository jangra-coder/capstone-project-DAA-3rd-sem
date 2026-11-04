# sorting.py
# Merge Sort is used to sort the parcels.
# Parcel with the earliest deadline comes first.
# If two parcels have the same deadline, the one with higher priority comes first.


def comes_first(p1, p2):
    # returns True if parcel p1 should come before parcel p2 (or they are equal)
    if p1["deadline"] != p2["deadline"]:
        return p1["deadline"] < p2["deadline"]

    # same deadline, so check priority (bigger priority = more important)
    return p1["priority"] >= p2["priority"]


def merge(left, right):
    result = []
    i = 0
    j = 0

    # compare first parcel of both lists and take the one which should come first
    while i < len(left) and j < len(right):
        if comes_first(left[i], right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # one list is finished, so add the remaining parcels of the other list
    while i < len(left):
        result.append(left[i])
        i += 1

    while j < len(right):
        result.append(right[j])
        j += 1

    return result


def merge_sort(parcels):
    # list with 0 or 1 parcel is already sorted
    if len(parcels) <= 1:
        return parcels

    # divide the list into two halves and sort both halves
    mid = len(parcels) // 2
    left = merge_sort(parcels[:mid])
    right = merge_sort(parcels[mid:])

    # merge the two sorted halves
    return merge(left, right)
