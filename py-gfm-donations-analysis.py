'''performs basic metrics analysis on GFM donations'''
#!/usr/bin/env python

import  sys, statistics, json, requests

def create_gfm_gateway_call(gfmcn, limit, offset):
    '''
    creates a json response call to the GoFundMe gateway (GFMGW)
    <type gfmcn> str
    <desc gfmcn> url campaign designation
        ex URL = "habitat-for-the-pathak-family"
    <type limit> int
    <desc limit> maximum number of donations to return in single call
        *** hard set at 100 by GFM Gateway***
    <type offset> int
    <desc offset> used to retrieve the next set of donations, if >100 total

    <<type gwurl>> str
    <<desc gwurl>> url used to parse info from the GFM gateway api
        ex URL = "https://gateway.gofundme.com/web-gateway/v1/feed/habitat-for-the-pathak-family/
        donations?limit=100&sort=recent"
    '''
    SORT_DIRECTION = 'recent'   # most recent donations listed first

    gwurl = f"https://gateway.gofundme.com/web-gateway/v1/feed/{gfmcn}/donations?limit={limit}&offset={offset}&sort={SORT_DIRECTION}"
    print(f'calling <{gwurl}')

    return gwurl

def get_donations_list(gfmcn):
    '''
    gets the list of donations from GFMGW call
    <type gfmcn> str
    <desc gfmcn> url campaign designation

    <<type full_list>> list
    <<desc full_list>> detailed dicts of individual donation information
    '''
    DONATIONS_LIMIT = 100     # maximum returned donations in a single call (GFM limit)
    full_list = []
    offset_value = 0
    finished_flag = False
    while not finished_flag:
        gwurl = create_gfm_gateway_call(gfmcn, DONATIONS_LIMIT, offset_value)
        offset_value += DONATIONS_LIMIT
        u_response = requests.get(gwurl).content.decode('utf-8')
        json_response = json.loads(u_response)
        full_list.extend(json_response['references']['donations'])
        if not json_response['meta']['has_next']:
            finished_flag = True

    return full_list

def check_gfm_url(url):
    '''
    validates the url input string
    <type url> str
    <desc url> url of gofundme campaign

    <<type gfm_campaign_name>> str
    <<desc gfm_campaign_name>> url campaign designation
    '''
    if 'gofundme.com' in url: # validates url input
        url_elements = url.split('/')
        if 'https' in url:
            gfm_campaign_name = url_elements[4]
        else:
            gfm_campaign_name = url_elements[2]
        return gfm_campaign_name
    else:
        print("not a valid gofundme.com URL")
        print("  :ex: gofundme.com/f/[campaign-name-url]")
        url_input = input("  :try again: ")
        return check_gfm_url(url_input) # recursive url check

def get_consolidated_list(ip):
    '''
    get consolidated list of donors, except Anonymous
    <type ip> list
    <desc ip> cleaned dononations

    <<type op>> list
    <<desc op>> consolidated list of donors
    '''
    names = [x['name'] for x in ip if x['name'] != 'Anonymous']
    duplicates = []
    op = []
    for each in ip:
        if each['name'] in duplicates:
            pass
        elif names.count(each['name']) > 1: # if name appears more than once
            # sum the donation amounts based on the name
            summed_amt = sum([float(y['amount']) for y in ip if y['name'] == each['name']])
            new_dict = {
                'amount':summed_amt, 
                'name': each['name'], 
                'is_anonymous':each['is_anonymous'], 
                'created_at':each['created_at']}
            op.append(new_dict) # add the amount to the consolidated list
            duplicates.append(each['name'])
        else:
            op.append(each)
    return op

def main(url):
    print(f"Called script using <{url}> as input...")

    #get the GoFundMe Campaign name designation
    gfm_name = check_gfm_url(url)

    # get clean list of donations from the GFM Gateway
    donations_list = get_donations_list(gfm_name)
    cleaned_list = [{'amount':x['amount'], 
                        'name':x['name'].strip(), 
                        'is_anonymous':x['is_anonymous'], 
                        'created_at':x['created_at']} for x in donations_list]

    # consolidate donors
    consolidated_list = get_consolidated_list(cleaned_list)
    
    # setup output information
    donations = [x["amount"] for x in cleaned_list]
    anondonations = [x["amount"] for x in cleaned_list\
         if x['is_anonymous']]
    nonanondonations = [x["amount"] for x in cleaned_list\
         if not x['is_anonymous']]

    # relevant donation metrics
    print(f"    Number of donations: {len(donations)}\n\
    Total Amount Donated: ${sum(donations)}\n\
    Median Amount: ${int(statistics.median(donations))}\n\
    Average Amount: ${int(statistics.mean(donations))}\n\
    Largest Donation: ${int(max(donations))}\n\n\
    Number of Donations (Anonymous): {len(anondonations)}\n\
    Total Amount Anonymous Donations: ${sum(anondonations)}\n\
    Median Anonymous Donation Amount: ${int(statistics.median(anondonations))}\n\
    Average Anonymous Donation Amount: ${int(statistics.mean(anondonations))}\n\
    Largest Anonymous Donation Amount: ${int(max(anondonations))}\n\n\
    Number of Donations (Non-Anonymous): {len(nonanondonations)}\n\
    Total Amount Anonymous Donations: ${sum(nonanondonations)}\n\
    Median Anonymous Donation Amount: ${int(statistics.median(nonanondonations))}\n\
    Average Anonymous Donation Amount: ${int(statistics.mean(nonanondonations))}\n\
    Largest Anonymous Donation Amount: ${int(max(nonanondonations))}")

    # relevant donor metrics
    print(f"\n\nBig Donors: (Top 10 of {len(donations)} donations)")
    big_donor_list = sorted([(x['amount'],i) for (i,x) in enumerate(consolidated_list)], reverse=True )[:10]
    idxd_list = [x[1] for x in big_donor_list]
    for x in idxd_list:
        print (f"{str(consolidated_list[x]['name']).rjust(25)} : ${str(int(consolidated_list[x]['amount'])).rjust(5)}")

if __name__ == "__main__": 
    if len(sys.argv) == 2:
        # If there are keyword arguments
        main(sys.argv[1])
    elif len(sys.argv) == 1:
        # If no keyword arguments
        url_input = input("Please enter a valid gofundme.com URL:\n::  ")
        main(url_input)
