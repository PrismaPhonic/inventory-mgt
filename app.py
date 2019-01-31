from csv import DictReader, DictWriter
import sys

VEN_CODE = 'VenCode'
PART_NUMBER = 'PartNumber'
SKU = 'SKU'
QUANTITY = 'TotalQty'


FIELDNAMES = [VEN_CODE, PART_NUMBER, SKU, QUANTITY]

if len(sys.argv) > 2:
    filename_master = sys.argv[1]
    filename_supply = sys.argv[2]
else:
    filename_master = 'MasterInventory.csv'
    filename_supply = 'SupplyInventory.csv'

print("Master filename:", filename_master)
print("Supply filename:", filename_supply)


def create_master_cache():
    index = {}
    with open(filename_master) as csv_file:
        master = DictReader(csv_file)
        for part in master:
            code = part[VEN_CODE]
            num = part[PART_NUMBER]
            qty = part[QUANTITY]

            if index.get(code):
                index[code][num] = qty if qty else 0
            else:
                index[code] = {num: qty if qty else 0}
    return index

def create_row(code, num, qty):
    return {
        VEN_CODE: code, 
        PART_NUMBER: num,
        SKU: f'{code}_{num}',
        QUANTITY: qty,
    }
    

def write_to_master(cache):
    fieldnames = FIELDNAMES
    with open("newmaster.csv", 'w', newline='') as out_file:
        writer = DictWriter(out_file, fieldnames=fieldnames)
        print(dict((field, field) for field in fieldnames))
        writer.writerow(dict((field, field) for field in fieldnames))
        for code in cache:
            for num in cache[code]:
                qty = cache[code][num]
                row = create_row(code, num, qty)
                writer.writerow(row)

def search_cache(idx, keys, level=0):
    if level >= len(keys):
        return False
    key = keys[level]
    val = idx.get(key)
    if level == len(keys)-1:
        return val if val != '' else 0  
    if not val:
        return False   
    return search_cache(val, keys, level+1)


def update_master():
    """Create a new csv file called 'newmaster.csv' that will contain 
    the rows from the master inventory file with quantities updated from 
    the supply inventory."""
    
    try:
        # cache data in memory from the master inventory file
        master_cache = create_master_cache()

        with open(filename_supply) as csv_file:
            supply = DictReader(csv_file)

            # loop through each row in the supply inventory,
            # and update the qty in the master cache
            for part in supply:
                supply_code = part[VEN_CODE]
                supply_num = part[PART_NUMBER]
                supply_qty = part[QUANTITY]
                
                # search the master inventory cache
                # for the supply 
                master_qty = search_cache(
                    master_cache,
                    [supply_code, supply_num]
                )

                if master_qty:
                    master_cache[supply_code][supply_num] = supply_qty

        # write the cache to the master csv file
        write_to_master(master_cache)

    except KeyError as e:
        print('There was an error', e)

if __name__ == "__main__":
    update_master()
