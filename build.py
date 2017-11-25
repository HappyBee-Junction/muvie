import senticnet4
import collections

def builddictionary():
    dic = dict()
    data = senticnet4.senticnet
    for line in data:
        for item in data[line]:
            if "#" in  item and item not in dic:
                dic[item.replace("#","")] = None
    return sorted(collections.OrderedDict(dic.items()))