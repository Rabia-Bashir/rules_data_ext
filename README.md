# Rules for automatically extracting features
The code uses Cochrane systematic reviews and their updates for automatically extracting the features (number of participants, total number of included trials, search dates and conclusions). For rules (regular expressions) development and web scraping, Pythgon 3.7 and its Beautiful Soup library is used. The figure Steps_AutomaticExtraction.png represents the steps involved in information extraction.

## Method to extract number of participants 
def get_participants_info(doi, soup):


    # The get_participants_info () method uses 13 rules (regular expressions) and their combinations to extract the participants  
    # information from all of the included trials from systematic reviews and their updates. Below are the rules for extracting 
    # number of participants. For more detail see code in Cochrane_Bot.py.

    # participant_column contains participants information
    # pre-processing the text in participant_column to remove extra numeric values (replacing with ‘xx’) given along with  
    # participants information

    preprocessed_text_step2 = re.sub(r'((\w+\s{0,1}(=|:)\s{0,1}\d+\s+)*(exclu\w+|withd\w+|screen\w++|(control|treatment|compar    
    \w+)(\s+group)*)(\s{0,1}(:|=)\s{0,1}\d+)*)|([0-9]+\.[0-9]+)|((age)(\s+|:|=)(\d+|\s+\d+))|\d+\s{0,1}‐\s{0,1}\d+|\d+  
    \s+(week|day|month|year)\w{0,1}|(\d+\s+(to)\s+\d+)|(\d+\s+(and)\s+(\d+|\w+))','xx', participant_column, 
    flags=re.IGNORECASE)
  
    # After pre-processing, developed rules and their combinations were applied

    Rule1= re.search(   r'(sampl\w+\s+(size)(:\s{0,1}|\s{0,1})\d+)|(random\w+:\s{0,1}\d+)($|\s+|\,|\;|\.|[\)])|(total\s+){0,1}  
    (N.|N|No.|numb\w+|parti\w+)\s+(random\w+)\s{0,1}((assign\w+|\w+)\s{0,1}){0,1}(=|:)(\s{0,1}total\s{0,1}:){0,1}\s{0,1}\d+($| 
    \s+|\,|\;|\.|[\)])|(numb\w+)(\s+of parti\w+){0,1}((\s+was){0,1}\s+\d+|\s{0,1}(=|:)\s{0,1}\d+)($|\s+|\,|\;|\.|[\)])|((total
    \s+){0,1}n\s{0,1}(=|:)\s{0,1}\d+($|\s+|\,|\;|\.|[\)]))',preprocessed_text,flags=re.IGNORECASE)

    Rule2= re.search(   r'(total)*\s+(n)\s+(random\w+)\s{0,1}(:|=)\s{0,1}\d+($|\s+|\,|\;|\.| 
    [\)])',preprocessed_text,flags=re.IGNORECASE)

    Rule3= re.search(r'[0-9]+\s*(part\w+|patie\w+|infan\w+|su\w+|chi\w+|\w+\s*chi|coupl\w+)',preprocessed_text,  
    flags=re.IGNORECASE)

    Rule4= re.search(r'([0-9]+\s*(\w+\s*(peop\w+|pers\w+|patie\w+)|(peop\w+|pers 
    \w+)))',preprocessed_text,flags=re.IGNORECASE)

    Rule5= re.search(r'(^[0-9]+\s+\w+)', preprocessed_text, flags=re.IGNORECASE)

    Rule6= re.search(r'\w+\s*\:\s*[\(]\d+[\)]', preprocessed_text,flags=re.IGNORECASE)

    Rule7= re.search(r'((part\w+\s+|patie\w+\s+)[0-9]+)', preprocessed_text,flags=re.IGNORECASE)

    Rule8= re.search(r'[0-9]+\s+(met\s+\w+)',preprocessed_text,flags=re.IGNORECASE)

    Rule9= re.search(r'[0-9]+\s+(wom\w+)', preprocessed_text,flags=re.IGNORECASE)

    Rule10= re.search(r'[\(]\w+/\w+[\)]:\s{0,1}\d+/\d+', preprocessed_text,flags=re.IGNORECASE)

    Rule11= re.search(r'(\d+\s+(men)((,|\s+)(\s+|and)(\s+)*(\d+)*(\s+)*(wom\w+)))',preprocessed_text,flags=re.IGNORECASE)

    Rule12= re.search(r'(partic\w+(:|=)\s{0,1}\d+)', preprocessed_text,flags=re.IGNORECASE)

    # Rule13 for extracting participant information provided in number words and converting into numeric digits

    ones = {'one': 1, 'eleven': 11,
        'two': 2, 'twelve': 12,
        'three': 3, 'thirteen': 13,
        'four': 4, 'fourteen': 14,
        'five': 5, 'fifteen': 15,
        'six': 6, 'sixteen': 16,
        'seven': 7, 'seventeen': 17,
        'eight': 8, 'eighteen': 18,
        'nine': 9, 'nineteen': 19}

    tens = {'ten': 10, 'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety':  
    90}

    groups = {'thousand': 1000, 'million': 1000000, 'billion': 1000000000, 'trillion': 1000000000000}

    groups_match = re.search(r'(^\s?([\w\s]+?)(?:\s((?:%s?patients))))' %('|'.join(groups)),  
    preprocessed_text,flags=re.IGNORECASE)
    hundreds_match = re.search(r'(^([\w\s]+)\shundred(?:\s(.*?patients)))',
    preprocessed_text,flags=re.IGNORECASE)

    tens_and_ones_match = re.search(r'(^((?:%s))(?:\s(.*?patients)))' % ('|'.join(tens.keys())),
    preprocessed_text, flags=re.IGNORECASE)

    if (groups_match):
      replace_symbol = re.sub("‐", '-', preprocessed_text, flags=re.IGNORECASE)
      remove_text = re.split('pati\w+', replace_symbol, flags=re.IGNORECASE)
      number_part = w2n.word_to_num(remove_text[0])

    elif (hundreds_match):
      replace_symbol = re.sub("‐", '-', preprocessed_text, flags=re.IGNORECASE)
      remove_text = re.split('pati\w+', replace_symbol, flags=re.IGNORECASE)
      number_part = w2n.word_to_num(remove_text[0])
    
    elif (tens_and_ones_match):
      replace_symbol = re.sub("‐", '-', preprocessed_text, flags=re.IGNORECASE)
      remove_text = re.split('pati\w+', replace_symbol, flags=re.IGNORECASE)
      number_part = w2n.word_to_num(remove_text[0])
      
## To extract total number of included trials
To extarct the total number of included trials from both systematic reviews (.pub2) and updates (.pub3), 'references' section was scraped using soup.find_all() method. For more detail see code in Cochrane_Bot.py.

## Method to extract conclusion 
def get_conclusion(doi, soup):


    # The get_conclusion() method access 'information', 'history' and 'what's new' sections of systematic review update (.pub3) 
    # to finally extract the conclusion
    
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
