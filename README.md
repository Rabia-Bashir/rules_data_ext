# Rules for automatically extracting features
The code uses Cochrane systematic reviews and their updates for automatically extracting the features (number of participants, total number of included trials, search dates and conclusions). For rules (regular expressions) development and web scraping, Pythgon 3.7 and its Beautiful Soup library is used. The figure Steps_AutomaticExtraction.png represents the steps involved in information extraction.


# Method to extract conclusion from systematic review updates


def get_conclusion(doi, soup):
    split_version = doi.split('.')[3]
    if split_version == "pub3":  # .pub3 is update of Cochrane systematic review
    
        # Here Information section is accessed to extract publication date of systematic review update (.pub3)
        sections_publication = soup.find_all("section", {"id": "information"})
        for i, v in enumerate(sections_publication):                          
                                                     
            pub_date = v.find("span", {"class": "publish-date"})
            publication_date = pub_date.text
            extract_date = re.search(r'(\d+.*?\d+)', publication_date,
                                     flags=re.IGNORECASE)
            save_pub_date = extract_date.group()
            print("---Publication Date of Systematic review ---")
            print(save_pub_date)
            #  This publication date extracted from top of information section will be used to substract the dates in history 
            #  and what's new sections
            date_publication = datetime.strptime(save_pub_date, '%d %B %Y')  # string to date
            
            
        # Here History section is accessed to extract all of its rows
        sections_history = soup.find_all("section", {"class": "history"})
        # print(sections_history)
        save_history = []
        list_history = []
        list_dates = []
        list_conclusions = []
        for i, v in enumerate(sections_history):
            tables_history1 = v.find("div", {"class": "table"})
            tables_history = tables_history1.find("table")
            # print("this",tables_history)
            print("---History and What's New Sections---")
            for his_tab_row in tables_history.find_all("tr")[1:]:
                save_history = his_tab_row.text
                # print(save_history)
                list_history.append(save_history)
                
        # Here What's new section is accessed to extract all its rows
        sections_whats_new = soup.find_all("section", {"class": "whatsNew"})
        for a, b in enumerate(sections_whats_new):
            tables_whatsnew = b.find("table")
            # print("---What's New Section---")
            for whatsnew_tab_row in tables_whatsnew.find_all("tr")[1:]:
             

                # list history contains all rows of history table and now appending the what's new table rows in it to display   
                # them together
                list_history.append(whatsnew_tab_row.text)
        list_con = []
    
        for i in list_history:
            if re.search(r'conclu\w+\s+.*?\s{2}', i, flags=re.IGNORECASE):
                list_con.append(i)
        print(list_con)
        #
        for con in list_con:
            # extract only those discussing about conclusion (changed or not)
            extract_only_conclusion = re.search(r'conclu\w+\s+.*?\s{2}', con,
                                                flags=re.IGNORECASE)  
            conclusion = extract_only_conclusion.group().rstrip()
            # print(conclusion)
            list_conclusions.append(conclusion)
            # extract corresponding dates where something is said about conslusion 
            extract_only_date = re.search(r'(\d+\s{0,1}\w+\s{0,1}\d+)', con,
                                          flags=re.IGNORECASE) 
            conclusion_date = extract_only_date.group().rstrip()
            list_dates.append(conclusion_date)

      
        # Make a dictionary where every date (extracted above) will be key and every conclusion(extracted above) will be value
        dict_conclusions = defaultdict(list)
        for i, d in enumerate(list_dates):
            dict_conclusions[d].append(
                list_conclusions[i])  
        print(dict_conclusions)
     
        list_diff = []
        dict_diff = {}
        # for every key in dict_conclusions.keys() now subtract that key(date) from the publication date which we extracted 
        # above from information section
        # we are subtractng these dates, because there will be many rows discussing about conslusion, but we want to know which   
        # of these is discussing the conlusion of recent review.
        # so where the difference between two dates will be minimum it means that will be the conclusion of current review
        diffs_by_date = {}
        for k in dict_conclusions.keys():
            date_conclusion = datetime.strptime(k, '%d %B %Y')  # string to date
            date_diff = (date_publication - date_conclusion).days
            diffs_by_date[date_diff] = k
        if diffs_by_date:
            min_conclusion_date = diffs_by_date[min(diffs_by_date.keys())]
            # print(min_conclusion_date)
            min_conclusion = dict_conclusions[min_conclusion_date]
            conclusion_text=str(min_conclusion).strip('[]')
            # if conclusion is not changed then '0' if changed then '1' and store these values for later use
            if re.search(r'(not|no)', conclusion_text,
                                                flags=re.IGNORECASE):
                conclusion_text="0"
            else:
                conclusion_text="1"

            if len(conclusion_text)!=0:

                return (conclusion_text,save_pub_date)
            else:
                return (0, save_pub_date)
