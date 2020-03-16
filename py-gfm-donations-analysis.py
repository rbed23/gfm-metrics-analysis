'''performs basic metrics analysis on GFM donations'''
#!/usr/bin/env python

import  sys, statistics, json

def clean_list(rfile):
    '''converts dirty .txt file to clean dict object'''
    #clean list of empty and excessive lines and extra whitespace
    itlist = iter([x.strip() for x in rfile if x.strip() != \
        'Join this list. Donate now.' and not x.strip() == ""])
    
    #break list into individual donations
    tuplist = zip(itlist, itlist, itlist)

    #create dict object of donations
    dictlist = [{'name' : eachtup[0],'amount' : eachtup[1],\
        'days ago' : eachtup[2]} for eachtup in tuplist]
    
    #print (json.dumps(dictlist,indent=2,ensure_ascii=False))
    return dictlist

def main(arg):
    print(f"Called script using <{arg}> as input file...")

    with open(arg, "r+") as rfile:
        readfile = rfile.readlines()

    cleanedlist = clean_list(readfile)

    donations = [int(x["amount"].strip("$")) for x in cleanedlist]
    anondonations = [int(x["amount"].strip("$")) for x in cleanedlist\
         if x["name"] == "Anonymous"]

    print(f"    Number of donations: {len(donations)}\n\
    Total Amount Donated: ${sum(donations)}\n\
    Median Amount: ${int(statistics.median(donations))}\n\
    Average Amount: ${int(statistics.mean(donations))}\n\
    Largest Donation: ${int(max(donations))}\n\n\
    Number of Donations (Anonymous): {len(anondonations)}\n\
    Total Amount Anonymous Donations: ${sum(anondonations)}\n\
    Median Anonymous Donation Amount: ${int(statistics.median(anondonations))}\n\
    Average Anonymous Donation Amount: ${int(statistics.mean(anondonations))}\n\
    Largest Anonymous Donation Amount: ${int(max(anondonations))}")

if __name__ == "__main__":        
    if len(sys.argv) == 2:
        # If there are keyword arguments
        main(sys.argv[1])
    else:
        raise SyntaxError("Insufficient arguments...\n\
    pleae provide JUST the Directory Path of the .txt file as an argument.")

