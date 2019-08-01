import requests
import bs4
import re
import os
import urllib
import io
import time
from word2number import w2n
from datetime import datetime
from datetime import date
from collections import defaultdict
import csv
import numpy
import traceback


# def write_cochrane_data(SR_IDs_P3, Total_participants_P3, num_trials_P3, conclusion, pub_date_P3, sr_date_P3):

#
#  with open ("data.csv",'w') as f:
#      columnTitleRow = "SR_IDs_Pub3, Participants_Pub3, Number of trials_Pub3, Conclusions, Publication_Date_Pub3, Search_Date_Pub3\n"
#      f.write(columnTitleRow )
#
#
#      f.write(SR_IDs_P3 + ',')
#      f.write(str(Total_participants) + ',')
#      f.write(str(num_trials_P3)+',')
#      f.write(conclusion + ',')
#      p_date=str(pub_date_P3).strip(' 00:00:00')
#      f.write(pub_date_P3 + ',')
#      f.write(sr_date_P3 + ',')


 # writefile= open("data.csv",'w')
 # writefile.write(str(SR_IDs))
 # writefile.write( str(Total_participants),delimiter='\t')
 # writefile.write(str(conclusion),delimiter='\t')

var='C:/Automatic_DataExtraction_Rules/HTML_SystematicReviews'
def get_pub2_with_pub3(input_file):
    all_dois = []
    pub2_withpub3 = []
    pmids = []
    with open(input_file) as file:
        reader = csv.reader(file)
        for row in reader:
            all_dois.append(row[3])
            pmids.append(row[1])
    for i, doi in enumerate(all_dois):
        # if doi ends with '2' and there exists the same doi ending in a '3'
        if doi[-1] == '2' and doi[:-1] + '3' in all_dois:
            pub2_withpub3.append((doi, pmids[i]))
    return pub2_withpub3


def get_pub3_with_pub2(input_file):
    all_dois = []
    pub2_withpub3 = []
    pmids = []
    with open(input_file) as file:
        reader = csv.reader(file)
        for row in reader:
            all_dois.append(row[3])
            pmids.append(row[1])
    for i, doi in enumerate(all_dois):
        # if doi ends with '2' and there exists the same doi ending in a '3'
        if doi[-1] == '3' and doi[:-1] + '2' in all_dois:
            pub2_withpub3.append((doi, pmids[i]))
        elif doi[-1] == '2' and doi[:-1] + '3' in all_dois:
            pub2_withpub3.append((doi, pmids[i]))
    return pub2_withpub3


# this method extracts data from Information, history, and what's new sections

def get_conclusion(doi, soup):
    split_version = doi.split('.')[3]
    if split_version == "pub3":

        sections_publication = soup.find_all("section", {"id": "information"})
        for i, v in enumerate(
                sections_publication):  # this publication date extracted from top of information section will be used to substract the dates in history and what's new sections
            pub_date = v.find("span", {"class": "publish-date"})
            publication_date = pub_date.text
            extract_date = re.search(r'(\d+.*?\d+)', publication_date,
                                     flags=re.IGNORECASE)
            save_pub_date = extract_date.group()
            print("---Publication Date of Systematic review ---")
            print(save_pub_date)
            date_publication = datetime.strptime(save_pub_date, '%d %B %Y')  # string to date
        # here history table is accessed to extract all of its rows
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
        # here what's new section is accessed to extract all its rows
        sections_whats_new = soup.find_all("section", {"class": "whatsNew"})

        for a, b in enumerate(sections_whats_new):
            tables_whatsnew = b.find("table")
            # print("---What's New Section---")

            for whatsnew_tab_row in tables_whatsnew.find_all("tr")[1:]:
                # print(save_whatsnew)

                # list history contains all rows of history table and now appending the what's new table rows in it to display them together
                list_history.append(whatsnew_tab_row.text)
            # print(list_history)

        list_con = []
        #
        for i in list_history:
            if re.search(r'conclu\w+\s+.*?\s{2}', i, flags=re.IGNORECASE):
                list_con.append(i)
        print(list_con)
        #
        for con in list_con:
            extract_only_conclusion = re.search(r'conclu\w+\s+.*?\s{2}', con,
                                                flags=re.IGNORECASE)  # extract rows discussing about conclusion
            conclusion = extract_only_conclusion.group().rstrip()
            # print(conclusion)
            list_conclusions.append(conclusion)
            extract_only_date = re.search(r'(\d+\s{0,1}\w+\s{0,1}\d+)', con,
                                          flags=re.IGNORECASE)  # extract corresponding dates where something is said about conslusion
            conclusion_date = extract_only_date.group().rstrip()
            list_dates.append(conclusion_date)

        #
        # print(list_conclusions)
        # print(list_dates)
        # Making a dictionary where every date (extracted above) will be key and every conclusion(extracted above) will be value
        dict_conclusions = defaultdict(list)
        for i, d in enumerate(list_dates):
            dict_conclusions[d].append(
                list_conclusions[i])  #
        print(dict_conclusions)
        #

        #
        #
        list_diff = []
        dict_diff = {}

        # for every key in dict_conclusions.keys() now subtract that key(date) from the publication date which we extracted above from information section
        # we are subtractng these dates, because there will be many rows discussing about conslusion, but we want to know which of these is discussing the conlusion of recent review.
        # so where the
        #
        #
        #  difference between two dates will be minimum it means that will be the conclusion of current review
        diffs_by_date = {}
        for k in dict_conclusions.keys():
            date_conclusion = datetime.strptime(k, '%d %B %Y')  # string to date


            date_diff = (date_publication - date_conclusion).days

            # diffs_by_date[date_diff] = date_conclusion
            diffs_by_date[date_diff] = k

        if diffs_by_date:
            min_conclusion_date = diffs_by_date[min(diffs_by_date.keys())]
            # print(min_conclusion_date)
            min_conclusion = dict_conclusions[min_conclusion_date]
            conclusion_text=str(min_conclusion).strip('[]')
            # print(conclusion_text)

            if re.search(r'(not|no)', conclusion_text,
                                                flags=re.IGNORECASE):
                conclusion_text="0"
            else:
                conclusion_text="1"

            if len(conclusion_text)!=0:

                return (conclusion_text,save_pub_date)
            else:
                return (0, save_pub_date)
        # else:
        #
        #     print("Nothing about conclusion")


# def get_publication_info(soup):
#     sections_publication = soup.find_all("section", {"id": "information"})
#     for i, v in enumerate(sections_publication):
#         pub_date= v.find("span",{"class":"publish-date"})
#         publication_date=pub_date.text
#         extract_date = re.search(r'(\d+.*?\d+)', publication_date,
#                                             flags=re.IGNORECASE)
#         save_pub_date= extract_date.group()
#         print("---Publication Date of Systematic review ---")
#         print(save_pub_date)
#


def get_participants_info(soup):
    # print(soup.prettify())

    # it shows the trials included in references (included studies only)
    references_included_trials = soup.find_all("div", {"class": "references_includedStudies"})

    # print("The total number of included trials: {}".format(len(references_included_trials)))

    # Below code is for accessing the participant information from "Characteristics of included studies" table
    sections = soup.find("section", {"class": "characteristicIncludedStudiesContent"})
    list_participants = []
    tables = sections.find_all("table")
    for tab in tables:
        all_second_rows = tab.find_all('tr')[1]
        participant_column = all_second_rows.findAll('td')[1].text.lstrip(
                'Description: ')
        list_trials =[]
        # preprocessed_text_float_values = re.sub(r'[0-9]+\.[0-9]+', 'xx', participant_column)
        # preprocessed_text_step1=re.sub(r'\d+\s+(week|day|month|year)\w{0,1}.[0-9]+','xx',preprocessed_text_float_values)
        ones = {'one': 1, 'eleven': 11,
                'two': 2, 'twelve': 12,
                'three': 3, 'thirteen': 13,
                'four': 4, 'fourteen': 14,
                'five': 5, 'fifteen': 15,
                'six': 6, 'sixteen': 16,
                'seven': 7, 'seventeen': 17,
                'eight': 8, 'eighteen': 18,
                'nine': 9, 'nineteen': 19}

        # a mapping of digits to their names when they appear in the 'tens'
        # place within a number group
        tens = {'ten': 10, 'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
                'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90}

        # an ordered list of the names assigned to number groups
        groups = {'thousand': 1000, 'million': 1000000, 'billion': 1000000000,
                  'trillion': 1000000000000}

        groups_match = re.search(r'(^\s?([\w\s]+?)(?:\s((?:%s?patients))))' %
                                 ('|'.join(groups)), participant_column,
                                 flags=re.IGNORECASE)

        hundreds_match = re.search(r'(^([\w\s]+)\shundred(?:\s(.*?patients)))',
                                   participant_column,
                                   flags=re.IGNORECASE)

        tens_and_ones_match = re.search(
            r'(^((?:%s))(?:\s(.*?patients)))' % ('|'.join(tens.keys())),
            participant_column, flags=re.IGNORECASE)

        if (groups_match):
            replace_symbol = re.sub("‐", '-', participant_column, flags=re.IGNORECASE)
            remove_text = re.split('pati\w+', replace_symbol, flags=re.IGNORECASE)
            number_part = w2n.word_to_num(remove_text[0])
            concatinated_string = str(number_part) + " " + "patients"
            # print(convert)

            list_trials.append(concatinated_string)
            print(list_trials)

        elif (hundreds_match):

            replace_symbol = re.sub("‐", '-', participant_column, flags=re.IGNORECASE)
            remove_text = re.split('pati\w+', replace_symbol, flags=re.IGNORECASE)
            number_part = w2n.word_to_num(remove_text[0])
            concatinated_string = str(number_part) + " " + "patients"
            # print(concat)

            list_trials.append(concatinated_string)
            print(list_trials)

        elif (tens_and_ones_match):

            replace_symbol = re.sub("‐", '-', participant_column, flags=re.IGNORECASE)
            remove_text = re.split('pati\w+', replace_symbol, flags=re.IGNORECASE)
            number_part = w2n.word_to_num(remove_text[0])
            concatinated_string = str(number_part) + " " + "patients"
            # print(concat)

            list_trials.append(concatinated_string)
            print(list_trials)




        else:

            preprocessed_text_step2 = re.sub(
                r'((\w+\s{0,1}(=|:)\s{0,1}\d+\s+)*(exclu\w+|withd\w+|screen\w+|(control|treatment|compar\w+)(\s+group)*)(\s{0,1}(:|=)\s{0,1}\d+)*)|([0-9]+\.[0-9]+)|((age)(\s+|:|=)(\d+|\s+\d+))|\d+\s{0,1}‐\s{0,1}\d+|\d+\s+(week|day|month|year)\w{0,1}|(\d+\s+(to)\s+\d+)|(\d+\s+(and)\s+(\d+|\w+))',
                'xx', participant_column, flags=re.IGNORECASE)
            #
            #
            print(preprocessed_text_step2)
            # preprocessed_text_step2=re.sub(r'([0-9]+\.[0-9]+)|(age|(age\w+)?:\s{0,1}\d+)|\d+\s{0,1}‐\s{0,1}\d+|\d+\s+(week|day|month|year)\w{0,1}|(\d+\s+(to)\s+\d+)|(\d+\s+(and)\s+(\d+|w\+))','xx',participant_column,flags=re.IGNORECASE)
            # print(preprocessed_text_step2)

            # match10 = re.search(r'\d+\s+(men\s+)(and\s+)(wom\w+)', participant_column,
            #                      flags=re.IGNORECASE)

            # match10 = re.search(r'\d+\s+(men\s+)(and\s+)(wom\w+|\d+\s+(\wom\w+))',
            #                     preprocessed_text_step2,
            #                     flags=re.IGNORECASE)

            # match1 = re.search(
            #     r'(sampl\w+\s+(size)(:\s{0,1}|\s{0,1})\d+)|(random\w+:\s{0,1}\d+)($|\s+|\,|\;|\.|[\)])|(total\s+)*(N.|N|No.|numb\w+|parti\w+)\s+(random\w+)\s{0,1}((assign\w+|\w+)\s{0,1})*(=|:)(\s{0,1}total\s{0,1}:)*\s{0,1}\d+($|\s+|\,|\;|\.|[\)])|(numb\w+)(\s+of parti\w+)*((\s+was)*\s+\d+|\s{0,1}(=|:)\s{0,1}\d+)($|\s+|\,|\;|\.|[\)])|((total\s+)*n\s{0,1}(=|:)\s{0,1}\d+($|\s+|\,|\;|\.|[\)]))',
            #     preprocessed_text_step2,
            #     flags=re.IGNORECASE)

            match1 = re.search(
                r'(sampl\w+\s+(size)(:\s{0,1}|\s{0,1})\d+)|(random\w+:\s{0,1}\d+)($|\s+|\,|\;|\.|[\)])|(total\s+){0,1}(N.|N|No.|numb\w+|parti\w+)\s+(random\w+)\s{0,1}((assign\w+|\w+)\s{0,1}){0,1}(=|:)(\s{0,1}total\s{0,1}:){0,1}\s{0,1}\d+($|\s+|\,|\;|\.|[\)])|(numb\w+)(\s+of parti\w+){0,1}((\s+was){0,1}\s+\d+|\s{0,1}(=|:)\s{0,1}\d+)($|\s+|\,|\;|\.|[\)])|((total\s+){0,1}n\s{0,1}(=|:)\s{0,1}\d+($|\s+|\,|\;|\.|[\)]))',
                preprocessed_text_step2,
                flags=re.IGNORECASE)

            # comp = re.compile(
            #     r'(sampl\w+\s+(size)(:\s{0,1}|\s{0,1})\d+)|(random\w+:\s{0,1}\d+)($|\s+|\,|\;|\.|[\)])|(total\s+)*(N.|N|No.|numb\w+|parti\w+)\s+(random\w+)\s{0,1}(((assign\w+|\w+)\s{0,1})*(=|:)(\s{0,1}total\s{0,1}:)*\s{0,1}\d+($|\s+|\,|\;|\.|[\)])|(numb\w+)(\s+of parti\w+)*((\s+was)*\s+\d+|\s{0,1}(=|:)\s{0,1}\d+)($|\s+|\,|\;|\.|[\)])|((total\s+)*n\s{0,1}(=|:)\s{0,1}\d+($|\s+|\,|\;|\.|[\)])))',
            #     flags=re.IGNORECASE)
            #
            # match1 = comp.search(preprocessed_text_step2)



            # match1 = compile_first.search(preprocessed_text_step2)

            # comp = re.compile(r'(sampl\w+\s+(size)(:\s{0,1}|\s{0,1})\d+)|(random\w+:\s{0,1}\d+)($|\s+|\,|\;|\.|[\)])|(total\s+)*(N.|N|No.|numb\w+|parti\w+)\s+(random\w+)\s{0,1}(((assign\w+|\w+)\s{0,1})*(=|:)(\s{0,1}total\s{0,1}:)*\s{0,1}\d+($|\s+|\,|\;|\.|[\)])|(numb\w+)(\s+of parti\w+)*((\s+was)*\s+\d+|\s{0,1}(=|:)\s{0,1}\d+)($|\s+|\,|\;|\.|[\)])|((total\s+)*n\s{0,1}(=|:)\s{0,1}\d+($|\s+|\,|\;|\.|[\)]))',flags=re.IGNORECASE)

            # match1 = comp.search(preprocessed_text_step2)




            # r'(((total\s+)*(N.|N|No.|numb\w+|parti\w+)\s+(random\w+)\s{0,1}((assign\w+|\w+)\s{0,1})*(=|:)(\s{0,1}total\s{0,1}:)*\s{0,1}\d+ |(numb\w+)(\s+of parti\w+)*((\s+was)*\s+\d+|\s{0,1}(=|:)\s{0,1}\d+)|((total\s+)*N\s{0,1}(=|:)\s{0,1}\d+))($|\s+|\,|\;|\.|[\)]))',preprocessed_text_step2, flags=re.IGNORECASE)

            # r'\w+\s*(:|=)\s*[0-9]+(\s+|,|;|.\s+(sex)|[\)])',
            # preprocessed_text_step2,
            # flags=re.IGNORECASE)
            match1a = re.search(
                r'(total)*\s+(n)\s+(random\w+)\s{0,1}(:|=)\s{0,1}\d+($|\s+|\,|\;|\.|[\)])',
                preprocessed_text_step2,
                flags=re.IGNORECASE)

            match2 = re.search(
                r'[0-9]+\s*(part\w+|patie\w+|infan\w+|su\w+|chi\w+|\w+\s*chi|coupl\w+)',
                preprocessed_text_step2, flags=re.IGNORECASE)
            match3 = re.search(
                r'([0-9]+\s*(\w+\s*(peop\w+|pers\w+|patie\w+)|(peop\w+|pers\w+)))',
                preprocessed_text_step2,
                flags=re.IGNORECASE)
            # match4 = re.search(r'(^[0-9]+\s+wom\w+)', participant_column,
            #                    flags=re.IGNORECASE)

            match5 = re.search(r'(^[0-9]+\s+\w+)', preprocessed_text_step2,
                               flags=re.IGNORECASE)
            # match5 = re.search(r'([0-9]+\s+\w+)', participant_column,
            #                    flags=re.IGNORECASE)

            # match6= re.search(r'\w+\s*(:|=)\s*[0-9]+%', participant_column,
            #                  flags=re.IGNORECASE)

            match7 = re.search(r'\w+\s*\:\s*[\(]\d+[\)]', preprocessed_text_step2,
                               flags=re.IGNORECASE)
            # if match6 and match1:
            #     if match6.start()<match1.start():
            #         list_trials.append(match1.group())
            #         print("match1", list_trials)
            match8 = re.search(r'((part\w+\s+|patie\w+\s+)[0-9]+)', preprocessed_text_step2,
                               flags=re.IGNORECASE)

            match9 = re.search(r'[0-9]+\s+(met\s+\w+)', preprocessed_text_step2,
                               flags=re.IGNORECASE)
            # match_wo = re.search(r'\d+\s+(men\s+)(and\s+)(wom\w+|\d+\s+(\wom\w+))', participant_column,
            #                      flags=re.IGNORECASE)
            # match11 = re.search(r'(\d+\s+(men)\,\s+\d+\s+(wom\w+))', preprocessed_text_step2,
            #                     flags=re.IGNORECASE)

            match12 = re.search(r'[0-9]+\s+(wom\w+)', preprocessed_text_step2,
                                flags=re.IGNORECASE)
            # match13 = re.search(r'(Num\w+)\s+(random\w+)\s+\w+(:|=)\s*[0-9]+',
            #                     preprocessed_text_step2,
            #                     flags=re.IGNORECASE)

            match14 = re.search(r'[\(]\w+/\w+[\)]:\s{0,1}\d+/\d+',
                                preprocessed_text_step2,
                                flags=re.IGNORECASE)
            match15 = re.search(
                r'(\d+\s+(men)((,|\s+)(\s+|and)(\s+)*(\d+)*(\s+)*(wom\w+)))',
                preprocessed_text_step2,
                flags=re.IGNORECASE)
            match16 = re.search(r'(partic\w+(:|=)\s{0,1}\d+)', preprocessed_text_step2,
                                flags=re.IGNORECASE)

            # |\w+\s*(=)\s*[0-9]+.
            # if (groups_match):
            #     list_trials.append(groups_match.group())
            #     print("groups_match", list_trials)
            #
            # elif (hundreds_match):
            #
            #     list_trials.append(hundreds_match.group())
            #     print("hundreds_match", list_trials)
            #
            # elif (tens_and_ones_match):
            #
            #     list_trials.append(tens_and_ones_match.group())
            #     print("tens_and_ones_match", list_trials)
            #
            # # if match1 and match13:
            # #     list_trials.append(match13.group())
            #     print("match13", list_trials)

            if match1 and match1a:
                list_trials.append(match1a.group())
                print("match1a", list_trials)



            elif match1 and match2:

                if match2.start() > match1.start():

                    list_trials.append(match1.group())
                    print("match1", list_trials)

                else:
                    list_trials.append(match2.group())
                    print("match2", list_trials)


            elif match1 and match5:
                list_trials.append(match5.group())
                print("match5", list_trials)



            elif match1:
                list_trials.append(match1.group())
                print("Rule 1 ")



            elif match1 and match15:
                if match15.start() > match1.start():
                    list_trials.append(match1.group())
                    print("match1", list_trials)
                else:
                    list_trials.append(match15.group())
                    print("match15", list_trials)


            elif match15 and match2:

                if match15.start() < match2.start():
                    list_trials.append(match15.group())
                    print("match15", list_trials)
                else:
                    list_trials.append(match2.group())
                    print("match2", list_trials)

            elif match9:
                list_trials.append(match9.group())
                print("match9", list_trials)

                # list_trials.append(match2.group())
                # print("Rule 1 and 2nd")
            elif match1 and match3:
                list_trials.append(match3.group())
                print("Rule 1 and 3rd")
            # elif match4 and match1:
            #     list_trials.append(match4.group())
            #     print("Rule 1 and 4th")

            elif match5 and match1:
                list_trials.append(match5.group())
                print("Rule 1 and 5th")

            elif match1 and match8:
                list_trials.append(match8.group())
                print("match8")
            # elif match1 and match11:
            #     list_trials.append(match11.group())
            #     print("match11")

            elif match2 and match5:  # new rule
                list_trials.append(match5.group())
                print("Rule 5th")

            elif match2 and match16:  # new rule
                list_trials.append(match16.group())
                print("match16")

                # print(list_trials)

            elif match2:

                list_trials.append(match2.group())
                print("Rule 2nd")
            elif match3:

                list_trials.append(match3.group())
                print("Rule 3rd")

            # elif match4:
            #     list_trials.append(match4.group())
            #     print("Rule 4th")
            elif match5:

                list_trials.append(match5.group())
                print("Rule 5")

            elif match7:
                list_trials.append(match7.group())
                print("Rule7", list_trials)
            elif match8:
                list_trials.append(match8.group())
                print("match8", list_trials)
            elif match15:
                list_trials.append(match15.group())
                print("match15", list_trials)

            # elif match_wo:
            #     list_trials.append(match_wo.group())
            #     print("match_wo", list_trials)
            elif match12:
                list_trials.append(match12.group())
                print("match12", list_trials)
            elif match14:
                list_trials.append(match14.group())
                print("match12", list_trials)


            else:
                print("Not matched with any rule, apply new rule")

                # list_participants = []
        number = []
        for trial in list_trials:

            # for subitem in trial.split():
            #     if (subitem.isdigit()):
            #         number.append(subitem)

            if re.findall(r'\d+', trial):
                m = re.findall(r'\d+', trial)
                print(m)

                s = 0
                for i in m:
                    s = s + int(i)
                # print(s)
                number.append(s)

                # elif re.search(r'\D+(pati\w+)', trial,flags=re.IGNORECASE):
                #
                #     m = re.split('pati\w+', trial, flags=re.IGNORECASE)
                #     #print(m[0])
                #     replace_symbol = re.sub("‐", '-', m[0], flags=re.IGNORECASE)
                #
                #     # print(m.group())
                #     convert = w2n.word_to_num(replace_symbol)
                #
                #     number.append(convert)

                # print(number)

        for p in number:
            list_participants.append(int(p))
    print(
        "list of all participants in each included trial : {}".format(
            list_participants))
    sum = 0
    for n in list_participants:
        sum = sum + n
    print(str(len(tables)) + ' trials, got participants for ' + str(len(list_participants)))






    return (sum, len(tables), len(list_participants),list_participants)

                        # all_second_rows = all_tables[0].find_all('tr')[1]
                        #
                        # # this will print the information of participants which is the second column of second row in characteristics of included studies
                        # participant_column = all_second_rows.findAll('td')[1].text.lstrip(
                        #     'Description: ')
                        # #print(participant_column)
                        # # preprocessed_text_float_values = re.sub(r'[0-9]+\.[0-9]+', 'xx', participant_column)
                        # # preprocessed_text_step1=re.sub(r'\d+\s+(week|day|month|year)\w{0,1}.[0-9]+','xx',preprocessed_text_float_values)
                        # ones = {'one': 1, 'eleven': 11,
                        #         'two': 2, 'twelve': 12,
                        #         'three': 3, 'thirteen': 13,
                        #         'four': 4, 'fourteen': 14,
                        #         'five': 5, 'fifteen': 15,
                        #         'six': 6, 'sixteen': 16,
                        #         'seven': 7, 'seventeen': 17,
                        #         'eight': 8, 'eighteen': 18,
                        #         'nine': 9, 'nineteen': 19}
                        #
                        # # a mapping of digits to their names when they appear in the 'tens'
                        # # place within a number group
                        # tens = {'ten': 10, 'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
                        #         'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90}
                        #
                        # # an ordered list of the names assigned to number groups
                        # groups = {'thousand': 1000, 'million': 1000000, 'billion': 1000000000,
                        #           'trillion': 1000000000000}
                        #
                        # groups_match = re.search(r'(^\s?([\w\s]+?)(?:\s((?:%s?patients))))' %
                        #                          ('|'.join(groups)), participant_column,
                        #                          flags=re.IGNORECASE)
                        #
                        # hundreds_match = re.search(r'(^([\w\s]+)\shundred(?:\s(.*?patients)))',
                        #                            participant_column,
                        #                            flags=re.IGNORECASE)
                        #
                        # tens_and_ones_match = re.search(r'(^((?:%s))(?:\s(.*?patients)))' % ('|'.join(tens.keys())),
                        #                                 participant_column, flags=re.IGNORECASE)
                        #
                        # if (groups_match):
                        #     replace_symbol = re.sub("‐", '-', participant_column, flags=re.IGNORECASE)
                        #     remove_text = re.split('pati\w+', replace_symbol, flags=re.IGNORECASE)
                        #     number_part = w2n.word_to_num(remove_text[0])
                        #     concatinated_string = str(number_part) + " " + "patients"
                        #     #print(convert)
                        #
                        #     list_trials.append(concatinated_string)
                        #     print( list_trials)
                        #
                        # elif (hundreds_match):
                        #
                        #     replace_symbol = re.sub("‐", '-', participant_column, flags=re.IGNORECASE)
                        #     remove_text = re.split('pati\w+', replace_symbol, flags=re.IGNORECASE)
                        #     number_part = w2n.word_to_num(remove_text[0])
                        #     concatinated_string = str(number_part) + " " + "patients"
                        #     #print(concat)
                        #
                        #     list_trials.append(concatinated_string)
                        #     print( list_trials)
                        #
                        # elif (tens_and_ones_match):
                        #
                        #     replace_symbol = re.sub("‐", '-', participant_column, flags=re.IGNORECASE)
                        #     remove_text = re.split('pati\w+', replace_symbol, flags=re.IGNORECASE)
                        #     number_part = w2n.word_to_num(remove_text[0])
                        #     concatinated_string = str(number_part) + " " + "patients"
                        #     #print(concat)
                        #
                        #     list_trials.append(concatinated_string)
                        #     print( list_trials)
                        #
                        #
                        #
                        #
                        # else:
                        #
                        #     preprocessed_text_step2=re.sub(r'((\w+\s{0,1}(=|:)\s{0,1}\d+\s+)*(exclu\w+|withd\w+|screen\w+|(control|treatment|compar\w+)(\s+group)*)(\s{0,1}(:|=)\s{0,1}\d+)*)|([0-9]+\.[0-9]+)|((age)(\s+|:|=)(\d+|\s+\d+))|\d+\s{0,1}‐\s{0,1}\d+|\d+\s+(week|day|month|year)\w{0,1}|(\d+\s+(to)\s+\d+)|(\d+\s+(and)\s+(\d+|\w+))','xx',participant_column,flags=re.IGNORECASE)
                        #     #
                        #     #
                        #     print(preprocessed_text_step2)
                        #     # preprocessed_text_step2=re.sub(r'([0-9]+\.[0-9]+)|(age|(age\w+)?:\s{0,1}\d+)|\d+\s{0,1}‐\s{0,1}\d+|\d+\s+(week|day|month|year)\w{0,1}|(\d+\s+(to)\s+\d+)|(\d+\s+(and)\s+(\d+|w\+))','xx',participant_column,flags=re.IGNORECASE)
                        #     # print(preprocessed_text_step2)
                        #
                        #
                        #     # match10 = re.search(r'\d+\s+(men\s+)(and\s+)(wom\w+)', participant_column,
                        #     #                      flags=re.IGNORECASE)
                        #
                        #     # match10 = re.search(r'\d+\s+(men\s+)(and\s+)(wom\w+|\d+\s+(\wom\w+))',
                        #     #                     preprocessed_text_step2,
                        #     #                     flags=re.IGNORECASE)
                        #
                        #     match1 = re.search(
                        #         r'(sampl\w+\s+(size)(:\s{0,1}|\s{0,1})\d+)|(random\w+:\s{0,1}\d+)($|\s+|\,|\;|\.|[\)])|(total\s+)*(N.|N|No.|numb\w+|parti\w+)\s+(random\w+)\s{0,1}((assign\w+|\w+)\s{0,1})*(=|:)(\s{0,1}total\s{0,1}:)*\s{0,1}\d+($|\s+|\,|\;|\.|[\)])|(numb\w+)(\s+of parti\w+)*((\s+was)*\s+\d+|\s{0,1}(=|:)\s{0,1}\d+)($|\s+|\,|\;|\.|[\)])|((total\s+)*n\s{0,1}(=|:)\s{0,1}\d+($|\s+|\,|\;|\.|[\)]))',
                        #         preprocessed_text_step2,
                        #         flags=re.IGNORECASE)
                        #         # r'(((total\s+)*(N.|N|No.|numb\w+|parti\w+)\s+(random\w+)\s{0,1}((assign\w+|\w+)\s{0,1})*(=|:)(\s{0,1}total\s{0,1}:)*\s{0,1}\d+ |(numb\w+)(\s+of parti\w+)*((\s+was)*\s+\d+|\s{0,1}(=|:)\s{0,1}\d+)|((total\s+)*N\s{0,1}(=|:)\s{0,1}\d+))($|\s+|\,|\;|\.|[\)]))',preprocessed_text_step2, flags=re.IGNORECASE)
                        #
                        #
                        #                        # r'\w+\s*(:|=)\s*[0-9]+(\s+|,|;|.\s+(sex)|[\)])',
                        #                        # preprocessed_text_step2,
                        #                        # flags=re.IGNORECASE)
                        #     match1a= re.search(r'(total)*\s+(n)\s+(random\w+)\s{0,1}(:|=)\s{0,1}\d+($|\s+|\,|\;|\.|[\)])', preprocessed_text_step2,
                        #         flags=re.IGNORECASE)
                        #
                        #
                        #
                        #
                        #     match2 = re.search(
                        #         r'[0-9]+\s*(part\w+|patie\w+|infan\w+|su\w+|chi\w+|\w+\s*chi|coupl\w+)',
                        #         preprocessed_text_step2, flags=re.IGNORECASE)
                        #     match3 = re.search(
                        #         r'([0-9]+\s*(\w+\s*(peop\w+|pers\w+|patie\w+)|(peop\w+|pers\w+)))',
                        #         preprocessed_text_step2,
                        #         flags=re.IGNORECASE)
                        #     # match4 = re.search(r'(^[0-9]+\s+wom\w+)', participant_column,
                        #     #                    flags=re.IGNORECASE)
                        #
                        #
                        #     match5 = re.search(r'(^[0-9]+\s+\w+)', preprocessed_text_step2,
                        #                        flags=re.IGNORECASE)
                        #     # match5 = re.search(r'([0-9]+\s+\w+)', participant_column,
                        #     #                    flags=re.IGNORECASE)
                        #
                        #     # match6= re.search(r'\w+\s*(:|=)\s*[0-9]+%', participant_column,
                        #     #                  flags=re.IGNORECASE)
                        #
                        #     match7 = re.search(r'\w+\s*\:\s*[\(]\d+[\)]', preprocessed_text_step2,
                        #                        flags=re.IGNORECASE)
                        #     # if match6 and match1:
                        #     #     if match6.start()<match1.start():
                        #     #         list_trials.append(match1.group())
                        #     #         print("match1", list_trials)
                        #     match8 = re.search(r'((part\w+\s+|patie\w+\s+)[0-9]+)', preprocessed_text_step2,
                        #                        flags=re.IGNORECASE)
                        #
                        #     match9 = re.search(r'[0-9]+\s+(met\s+\w+)', preprocessed_text_step2,
                        #                        flags=re.IGNORECASE)
                        #     # match_wo = re.search(r'\d+\s+(men\s+)(and\s+)(wom\w+|\d+\s+(\wom\w+))', participant_column,
                        #     #                      flags=re.IGNORECASE)
                        #     # match11 = re.search(r'(\d+\s+(men)\,\s+\d+\s+(wom\w+))', preprocessed_text_step2,
                        #     #                     flags=re.IGNORECASE)
                        #
                        #     match12 = re.search(r'[0-9]+\s+(wom\w+)', preprocessed_text_step2,
                        #                         flags=re.IGNORECASE)
                        #     # match13 = re.search(r'(Num\w+)\s+(random\w+)\s+\w+(:|=)\s*[0-9]+',
                        #     #                     preprocessed_text_step2,
                        #     #                     flags=re.IGNORECASE)
                        #
                        #     match14 = re.search(r'[\(]\w+/\w+[\)]:\s{0,1}\d+/\d+',
                        #                         preprocessed_text_step2,
                        #                         flags=re.IGNORECASE)
                        #     match15 = re.search(r'(\d+\s+(men)((,|\s+)(\s+|and)(\s+)*(\d+)*(\s+)*(wom\w+)))',
                        #                           preprocessed_text_step2,
                        #                           flags=re.IGNORECASE)
                        #     match16= re.search(r'(partic\w+(:|=)\s{0,1}\d+)',preprocessed_text_step2,
                        #                           flags=re.IGNORECASE)
                        #
                        #
                        #     # |\w+\s*(=)\s*[0-9]+.
                        #     # if (groups_match):
                        #     #     list_trials.append(groups_match.group())
                        #     #     print("groups_match", list_trials)
                        #     #
                        #     # elif (hundreds_match):
                        #     #
                        #     #     list_trials.append(hundreds_match.group())
                        #     #     print("hundreds_match", list_trials)
                        #     #
                        #     # elif (tens_and_ones_match):
                        #     #
                        #     #     list_trials.append(tens_and_ones_match.group())
                        #     #     print("tens_and_ones_match", list_trials)
                        #     #
                        #     # # if match1 and match13:
                        #     # #     list_trials.append(match13.group())
                        #     #     print("match13", list_trials)
                        #
                        #
                        #
                        #     if match1 and match1a:
                        #         list_trials.append(match1a.group())
                        #         print("match1a", list_trials)
                        #
                        #
                        #
                        #     elif match1 and match2:
                        #
                        #         if match2.start() > match1.start():
                        #
                        #             list_trials.append(match1.group())
                        #             print("match1", list_trials)
                        #
                        #         else:
                        #             list_trials.append(match2.group())
                        #             print("match2", list_trials)
                        #
                        #
                        #     elif match1 and match5:
                        #         list_trials.append(match5.group())
                        #         print("match5", list_trials)
                        #
                        #
                        #
                        #     elif match1:
                        #         list_trials.append(match1.group())
                        #         print("Rule 1 ")
                        #
                        #
                        #
                        #     elif  match1 and match15:
                        #         if match15.start() > match1.start():
                        #             list_trials.append(match1.group())
                        #             print("match1", list_trials)
                        #         else:
                        #             list_trials.append(match15.group())
                        #             print("match15", list_trials)
                        #
                        #
                        #     elif match15 and match2:
                        #
                        #         if match15.start() < match2.start():
                        #             list_trials.append(match15.group())
                        #             print("match15", list_trials)
                        #         else:
                        #             list_trials.append(match2.group())
                        #             print("match2", list_trials)
                        #
                        #     elif match9:
                        #         list_trials.append(match9.group())
                        #         print("match9", list_trials)
                        #
                        #
                        #
                        #
                        #             # list_trials.append(match2.group())
                        #             # print("Rule 1 and 2nd")
                        #     elif match1 and match3:
                        #         list_trials.append(match3.group())
                        #         print("Rule 1 and 3rd")
                        #     # elif match4 and match1:
                        #     #     list_trials.append(match4.group())
                        #     #     print("Rule 1 and 4th")
                        #
                        #     elif match5 and match1:
                        #         list_trials.append(match5.group())
                        #         print("Rule 1 and 5th")
                        #
                        #     elif match1 and match8:
                        #         list_trials.append(match8.group())
                        #         print("match8")
                        #     # elif match1 and match11:
                        #     #     list_trials.append(match11.group())
                        #     #     print("match11")
                        #
                        #     elif match2 and match5:  # new rule
                        #         list_trials.append(match5.group())
                        #         print("Rule 5th")
                        #
                        #     elif match2 and match16: # new rule
                        #         list_trials.append(match16.group())
                        #         print("match16")
                        #
                        #
                        #
                        #
                        #
                        #
                        #
                        #         # print(list_trials)
                        #
                        #     elif match2:
                        #
                        #         list_trials.append(match2.group())
                        #         print("Rule 2nd")
                        #     elif match3:
                        #
                        #         list_trials.append(match3.group())
                        #         print("Rule 3rd")
                        #
                        #     # elif match4:
                        #     #     list_trials.append(match4.group())
                        #     #     print("Rule 4th")
                        #     elif match5:
                        #
                        #         list_trials.append(match5.group())
                        #         print("Rule 5")
                        #
                        #     elif match7:
                        #         list_trials.append(match7.group())
                        #         print("Rule7", list_trials)
                        #     elif match8:
                        #         list_trials.append(match8.group())
                        #         print("match8", list_trials)
                        #     elif match15:
                        #         list_trials.append(match15.group())
                        #         print("match15", list_trials)
                        #
                        #     # elif match_wo:
                        #     #     list_trials.append(match_wo.group())
                        #     #     print("match_wo", list_trials)
                        #     elif match12:
                        #         list_trials.append(match12.group())
                        #         print("match12", list_trials)
                        #     elif match14:
                        #         list_trials.append(match14.group())
                        #         print("match12", list_trials)
                        #
                        #
                        #     else:
                        #         print("Not matched with any rule, apply new rule")
                        #
                        #         # list_participants = []
                        # number = []
                        # for trial in list_trials:
                        #
                        #     # for subitem in trial.split():
                        #     #     if (subitem.isdigit()):
                        #     #         number.append(subitem)
                        #
                        #
                        #
                        #
                        #     if re.findall(r'\d+', trial):
                        #         m = re.findall(r'\d+', trial)
                        #         print(m)
                        #
                        #         s = 0
                        #         for i in m:
                        #             s = s + int(i)
                        #         # print(s)
                        #         number.append(s)
                        #
                        #     # elif re.search(r'\D+(pati\w+)', trial,flags=re.IGNORECASE):
                        #     #
                        #     #     m = re.split('pati\w+', trial, flags=re.IGNORECASE)
                        #     #     #print(m[0])
                        #     #     replace_symbol = re.sub("‐", '-', m[0], flags=re.IGNORECASE)
                        #     #
                        #     #     # print(m.group())
                        #     #     convert = w2n.word_to_num(replace_symbol)
                        #     #
                        #     #     number.append(convert)
                        #
                        #     #print(number)
                        #
                        # for p in number:
                        #     list_participants.append(int(p))
                        # print(
                        #     "list of all participants in each included trial : {}".format(
                        #         list_participants))
                        # sum = 0
                        # for n in list_participants:
                        #     sum = sum + n
                        # return sum


# this method fethches the page 1 of SR and then save it in folder
def Save_Html_Contents(doi, SR_IDs):


    path = var
    # all_webpages=[]

    # all_webpages= os.chdir(path)
    # List_page=[]
    #
    # for webpage in all_webpages:
    #  List_page.append(webpage.split('-Part1.html')[0])
    #  if SR_IDs not in List_page:
    print('\n---------------------------')
    print("For systematic review ID: {}".format(SR_IDs))
    print('---------------------------')
    split_version = doi.split('.')[3]
    print("The version is {}".format(split_version))
    if split_version == 'pub3':

        try:
            if SR_IDs + "-Part1.html" not in os.listdir(path):
                base_url = "http://cochranelibrary.com/cdsr/doi/{}/full".format(doi)

                time.sleep(20)
                r = requests.get(base_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
                print(r.status_code)
                # 200 is the HTTP status code for "OK", a successful response.
                if r.status_code == 200:
                    file_contents = r.content
                    # print(file_contents)
                    os.chdir(path)
                    # open('%s.csv' % name, 'wb')
                    write_html_contents = open("%s-Part1"".html" % SR_IDs, 'wb')

                    write_html_contents.write(file_contents)
                    write_html_contents.close()
            else:
                print("{} is already downloaded in folder".format(SR_IDs + "-Part1.html"))
        except FileNotFoundError:
            print("Page is not found")

    elif split_version == 'pub2':
        try:
            if SR_IDs + "-Pub2-Part1.html" not in os.listdir(path):
                base_url = "http://cochranelibrary.com/cdsr/doi/{}/full".format(doi)

                time.sleep(20)
                r = requests.get(base_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
                print(r.status_code)
                # 200 is the HTTP status code for "OK", a successful response.
                if r.status_code == 200:
                    file_contents = r.content
                    # print(file_contents)
                    os.chdir(path)
                    # open('%s.csv' % name, 'wb')
                    write_html_contents = open("%s-Pub2-Part1"".html" % SR_IDs, 'wb')

                    write_html_contents.write(file_contents)
                    write_html_contents.close()
            else:
                print("{} is already downloaded in folder".format(SR_IDs + "-Pub2-Part1.html"))
        except Exception as e:

            print('Error: {0}'.format(e))
            print(traceback.format_exc())


# this method reads the above saved page, checks if 'characteristics of studies' link is present on that page if it is then it sends
# request to server for that page and then store it in the same folder where page 1 was saved.
def Read_Html_Contents(doi, SR_IDs, review_dict):
    split_version = doi.split('.')[3]
    if split_version == 'pub3':


        try:

            path=var
            # path = 'C:/Users/44697147/Desktop/CochraneBot_Programs_updated/HTML_SystematicReviews'
            os.chdir(path)
            # htmlfile_list = []
            # newList = []
            # for file in dirs:
            #     if file.endswith("-Part1.html"):
            #         htmlfile_list.append(file)
            # # print(htmlfile_list)
            # for htmlfile in htmlfile_list:
            #     newList.append(htmlfile.split('-Part1.html')[0])
            # # print(newList)
            #
            # # for s_id in SR_IDs:
            # for HtmlFile_withid in newList:
            #      # if s_id == htmlid:
            #      #    page = urllib.request.urlopen("%s.html" % HtmlFile_withid).read()
            #      #
            #      #
            #      #    print(page)

            contents = open(path + "/%s-Part1.html" % SR_IDs, 'r', encoding="utf8")
            source_code = contents.read()
            # print(source_code)
            # print(contents)

            soup = bs4.BeautifulSoup(source_code, 'html.parser')

            # this is code for extracting the search date

            search_date_section = soup.find("div", {"class": "abstract full_abstract"})
            # print(search_date_section)
            children = search_date_section.findChildren()
            for child in children:
                if child.text == "Search methods" and child.name == "h3":
                    child_id = child.get("id")
                    searchdate_section = soup.find("section", {"id": child_id})
                    Searchdate_text = searchdate_section.getText()
                    # print(Searchdate_text)




                    print("---Search Date of systematic Review---")
                    # print(save_search_date)
                    preprocessed_text_searchdate = re.sub(
                        r'((\d+)*(\s+)*((jan|feb|marc|apr|ma|jun|jul|aug|sep|oct|nov|dec)(\w+)*)\s+\d+\s+(to|and))',
                        'xx', Searchdate_text, flags=re.IGNORECASE)
                    print(preprocessed_text_searchdate)

                    extract_search_date = re.search(
                        r'((\d+)*(\s+)*((jan|feb|marc|apr|ma|jun|jul|aug|sep|oct|nov|dec)(\w+)*)((\s+)*\d+,)*\s+\d+)',
                        preprocessed_text_searchdate, flags=re.IGNORECASE)

                    # print(extract_search_date)
                    save_search_date = extract_search_date.group()

                    if (re.search(r'((\d+)(\s+)*((jan|feb|marc|apr|ma|jun|jul|aug|sep|oct|nov|dec)(\w+)*)(\s+)*\d+)',
                                  save_search_date, flags=re.IGNORECASE)):
                        Sr_Date = re.search(
                            r'((\d+)(\s+)*((jan|feb|marc|apr|ma|jun|jul|aug|sep|oct|nov|dec)(\w+)*)(\s+)*\d+)',
                            save_search_date, flags=re.IGNORECASE)
                        Search_Date = Sr_Date.group()
                        print(Search_Date)
                    elif (re.search(r'(((jan|feb|marc|apr|ma|jun|jul|aug|sep|oct|nov|dec)(\w+)*)(\s+)*(\d+,)(\s+)*\d+)',
                                    save_search_date, flags=re.IGNORECASE)):

                        Sr_Date = re.search(
                            r'(((jan|feb|marc|apr|ma|jun|jul|aug|sep|oct|nov|dec)(\w+)*)(\s+)*(\d+,)(\s+)*\d+)',
                            save_search_date, flags=re.IGNORECASE)
                        Show_Date = Sr_Date.group()
                        # Sear_Date.split(",")
                        print(Show_Date)

                        split_searchdate = re.search(r'(\w+(\s+)*\d+)', Show_Date, flags=re.IGNORECASE)
                        # date= clean_date_part1.group()
                        # print(date)
                        save_day = re.search(r'(\d+)', split_searchdate.group(), flags=re.IGNORECASE)
                        # print(save_day.group())

                        save_month = re.search(r'(\w+)', split_searchdate.group(), flags=re.IGNORECASE)
                        # print(save_month.group())
                        save_year = re.search(r'(,(\s+)*\d+)', Show_Date, flags=re.IGNORECASE)
                        remove_comma_inyear = save_year.group().replace(",", "").strip()
                        # print(remove_comma_inyear)
                        Search_Date = save_day.group() + " " + save_month.group() + " " + remove_comma_inyear
                        print(Search_Date)

                    elif (
                            re.search(r'(((jan|feb|marc|apr|ma|jun|jul|aug|sep|oct|nov|dec)(\w+)*)(\s+)*\d+)',
                                      save_search_date,
                                      flags=re.IGNORECASE)):

                        SDate = re.search(r'(((jan|feb|marc|apr|ma|jun|jul|aug|sep|oct|nov|dec)(\w+)*)(\s+)*\d+)',
                                          save_search_date, flags=re.IGNORECASE)
                        print(SDate.group())
                        if (re.search(r'((jan|marc|ma|jul|aug|oct|dec)(\w+)*)', SDate.group(), flags=re.IGNORECASE)):
                            Search_Date = "31" + " " + SDate.group()
                            print(Search_Date)
                        elif (re.search(r'((apr|jun|sep|nov)(\w+)*)', SDate.group(), flags=re.IGNORECASE)):
                            Search_Date = "30" + " " + SDate.group()
                            print(Search_Date)

                        elif (re.search(r'((feb)(\w+)*)', SDate.group(), flags=re.IGNORECASE)):
                            Search_Date = "28" + " " + SDate.group()
                            print(Search_Date)



































            # print(soup.prettify())

            navigation_characteristics = soup.find_all("li", {"class": "cdsr-nav-link references-link"})
            # print(navigation)

            for i, v in enumerate(navigation_characteristics):
                # print(v.getText())

                # this will check if the characteristics of studies link is present on the main page then will navigate to that page

                if "Characteristics of studies" in v.getText():

                    if SR_IDs + "-Part2.html" not in os.listdir(path):

                        base_url2 = "http://cochranelibrary.com/cdsr/doi/{}/references".format(doi)
                        time.sleep(20)
                        r = requests.get(base_url2, headers={
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
                        print(r.status_code)
                        # 200 is the HTTP status code for "OK", a successful response.
                        if r.status_code == 200:
                            # soup = bs4.BeautifulSoup(r.content, 'html.parser')

                            file_contents = r.content
                            # print(file_contents)
                            os.chdir(path)
                            # open('%s.csv' % name, 'wb')
                            write_html_contents = open("%s-Part2"
                                                       ".html" % SR_IDs, 'wb')

                            write_html_contents.write(file_contents)
                            write_html_contents.close()

                            #
                            # -------------------------------------

                            dirs2 = os.listdir(path)
                            htmlfile_list2 = []
                            newList2 = []
                            # for file2 in dirs2:
                            #     if file2.endswith("-Part2.html"):

                            contents = open(path + "/%s-Part2.html" % SR_IDs, 'r', encoding="utf8")
                            source_code = contents.read()
                            # print(source_code)
                            # print(contents)
                            #
                            #
                            #
                            #
                            #
                            soup = bs4.BeautifulSoup(source_code, 'html.parser')
                            # print("SOUP",soup)

                            Total_participants, total_trials, trials_with_participants,list_participants = get_participants_info(soup)
                            print("The total number of included trials: {}".format(total_trials))
                            print("The total number of participants are {}".format(Total_participants))


                    elif SR_IDs + "-Part2.html" in os.listdir(path):
                        print("{} is already downloaded in folder".format(SR_IDs + "-Part2.html"))
                        contents = open(path + "/%s-Part2.html" % SR_IDs, 'r', encoding="utf8")
                        source_code = contents.read()

                        # print(source_code)
                        # print(contents)
                        #
                        #
                        #
                        #
                        #
                        soup = bs4.BeautifulSoup(source_code, 'html.parser')
                        # print("SOUP",soup)

                        Total_participants, total_trials, trials_with_participants,list_participants = get_participants_info(soup)
                        print("The total number of included trials: {}".format(total_trials))

                        print("The total number of participants are {}".format(Total_participants))

            navigation_history = soup.find_all("li", {"class": "cdsr-nav-link article-section-link"})
            for i, v in enumerate(navigation_history):

                # this will check if the characteristics of studies link is present on the main page then will navigate to that page

                if "History" in v.getText():
                    # History_id = v.get('id')
                    # print(History_id)
                    if SR_IDs + "-Part3.html" not in os.listdir(path):

                        base_url3 = "http://cochranelibrary.com/cdsr/doi/{}/information".format(doi)
                        time.sleep(20)
                        r = requests.get(base_url3, headers={
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
                        print(r.status_code)
                        # 200 is the HTTP status code for "OK", a successful response.
                        if r.status_code == 200:
                            file_contents_history = r.content

                            os.chdir(path)
                            write_html_contents_history = open("%s-Part3"
                                                               ".html" % SR_IDs, 'wb')

                            write_html_contents_history.write(file_contents_history)
                            write_html_contents_history.close()

                            contents_history = open(path + "/%s-Part3.html" % SR_IDs, 'r', encoding="utf8")
                            source_code_history = contents_history.read()
                            # print(source_code)
                            # print(contents)

                            soup = bs4.BeautifulSoup(source_code_history, 'html.parser')

                            # publication_information = get_publication_info(soup)
                            conclusion,publication_date= get_conclusion(doi, soup)
                            # print(conclusion)
#                             # print(publication_date)
                            review_dict[doi]['pmid'] = SR_IDs
                            review_dict[doi]['total_trials'] = total_trials
                            review_dict[doi]['trials_with_participants'] = trials_with_participants
                            review_dict[doi]['list_participants'] = list_participants
                            review_dict[doi]['Total_participants'] = Total_participants
                            review_dict[doi]['conclusion'] = conclusion
                            review_dict[doi]['publication_date'] = publication_date
                            review_dict[doi]['Search_Date'] = Search_Date




                            # write_cochrane_data(SR_IDs, Total_participants, total_trials,conclusion, publication_date, Search_Date)






                    elif SR_IDs + "-Part3.html" in os.listdir(path):

                            print("{} is already downloaded in folder".format(SR_IDs + "-Part3.html"))
                            contents_history = open(path + "/%s-Part3.html" % SR_IDs, 'r', encoding="utf8")
                            source_code_history = contents_history.read()

                            # print(source_code)
                            # print(contents)

                            soup = bs4.BeautifulSoup(source_code_history, 'html.parser')
                            # print(soup.prettify())
                            # print(soup.prettify())
                            # print(soup.prettify())
                            conclusion, publication_date = get_conclusion(doi, soup)
                            print(conclusion)
                            # print(publication_date)
                            # write_cochrane_data(SR_IDs, Total_participants, total_trials, conclusion,publication_date,Search_Date)
                            review_dict[doi]['pmid'] = SR_IDs
                            review_dict[doi]['total_trials'] = total_trials
                            review_dict[doi]['trials_with_participants'] = trials_with_participants
                            review_dict[doi]['list_participants'] = list_participants
                            review_dict[doi]['Total_participants'] = Total_participants
                            review_dict[doi]['conclusion'] = conclusion
                            review_dict[doi]['publication_date'] = publication_date
                            review_dict[doi]['Search_Date'] = Search_Date
                            # print(review_dict[doi])




        except Exception as e:

            print('Error: {0}'.format(e))
            print(traceback.format_exc())

    elif split_version == 'pub2':

        try:

            path = var
            # path = 'C:/Users/44697147/Desktop/CochraneBot_Programs_updated/HTML_SystematicReviews'
            os.chdir(path)

            contents = open(path + "/%s-Pub2-Part1.html" % SR_IDs, 'r', encoding="utf8")
            source_code = contents.read()
            # print(source_code)
            # print(contents)

            soup = bs4.BeautifulSoup(source_code, 'html.parser')

            # this is code for extracting the search dates
            search_date_section = soup.find("div", {"class": "abstract full_abstract"})
            # print(search_date_section)
            children = search_date_section.findChildren()
            for child in children:
                if child.text == "Search methods" and child.name == "h3":
                    child_id = child.get("id")
                    searchdate_section = soup.find("section", {"id": child_id})
                    Searchdate_text = searchdate_section.getText()
                    # print(Searchdate_text)




                    print("---Search Date of systematic Review---")
                    # print(save_search_date)
                    preprocessed_text_searchdate = re.sub(
                        r'((\d+)*(\s+)*((jan|feb|marc|apr|ma|jun|jul|aug|sep|oct|nov|dec)(\w+)*)\s+\d+\s+(to|and))',
                        'xx', Searchdate_text, flags=re.IGNORECASE)
                    print(preprocessed_text_searchdate)

                    extract_search_date = re.search(
                        r'((\d+)*(\s+)*((jan|feb|marc|apr|ma|jun|jul|aug|sep|oct|nov|dec)(\w+)*)((\s+)*\d+,)*\s+\d+)',
                        preprocessed_text_searchdate, flags=re.IGNORECASE)


                    save_search_date = extract_search_date.group()
                    # Check if date is in this format "DD MM YYYY" then save it
                    if (re.search(r'((\d+)(\s+)*((jan|feb|marc|apr|ma|jun|jul|aug|sep|oct|nov|dec)(\w+)*)(\s+)*\d+)',
                                  save_search_date, flags=re.IGNORECASE)):
                        Sr_Date = re.search(
                            r'((\d+)(\s+)*((jan|feb|marc|apr|ma|jun|jul|aug|sep|oct|nov|dec)(\w+)*)(\s+)*\d+)',
                            save_search_date, flags=re.IGNORECASE)
                        Search_Date = Sr_Date.group()
                        print(Search_Date)
                    # Check if date is in this format "MM DD, YYYY" then save it and perform processing to bring it in a format of MM DD YYYY
                    elif (re.search(r'(((jan|feb|marc|apr|ma|jun|jul|aug|sep|oct|nov|dec)(\w+)*)(\s+)*(\d+,)(\s+)*\d+)',
                                    save_search_date, flags=re.IGNORECASE)):

                        Sr_Date = re.search(
                            r'(((jan|feb|marc|apr|ma|jun|jul|aug|sep|oct|nov|dec)(\w+)*)(\s+)*(\d+,)(\s+)*\d+)',
                            save_search_date, flags=re.IGNORECASE)
                        Show_Date = Sr_Date.group()
                        # Sear_Date.split(",")
                        print(Show_Date)

                        split_searchdate = re.search(r'(\w+(\s+)*\d+)', Show_Date, flags=re.IGNORECASE)
                        # date= clean_date_part1.group()
                        # print(date)
                        save_day = re.search(r'(\d+)', split_searchdate.group(), flags=re.IGNORECASE)
                        # print(save_day.group())

                        save_month = re.search(r'(\w+)', split_searchdate.group(), flags=re.IGNORECASE)
                        # print(save_month.group())
                        save_year = re.search(r'(,(\s+)*\d+)', Show_Date, flags=re.IGNORECASE)
                        remove_comma_inyear = save_year.group().replace(",", "").strip()
                        # print(remove_comma_inyear)
                        Search_Date = save_day.group() + " " + save_month.group() + " " + remove_comma_inyear
                        print(Search_Date)
                    # Check if date is in this format "MM YYYY" then save it and perform processing to attach DD with it based on a month
                    elif (
                            re.search(r'(((jan|feb|marc|apr|ma|jun|jul|aug|sep|oct|nov|dec)(\w+)*)(\s+)*\d+)',
                                      save_search_date,
                                      flags=re.IGNORECASE)):

                        SDate = re.search(r'(((jan|feb|marc|apr|ma|jun|jul|aug|sep|oct|nov|dec)(\w+)*)(\s+)*\d+)',
                                          save_search_date, flags=re.IGNORECASE)
                        print(SDate.group())
                        # if month is anyone of these then attach 31 (DD) with month
                        if (re.search(r'((jan|marc|ma|jul|aug|oct|dec)(\w+)*)', SDate.group(), flags=re.IGNORECASE)):
                            Search_Date = "31" + " " + SDate.group()
                            print(Search_Date)
                        # if month is anyone of these then attach 30 (DD) with month
                        elif (re.search(r'((apr|jun|sep|nov)(\w+)*)', SDate.group(), flags=re.IGNORECASE)):
                            Search_Date = "30" + " " + SDate.group()
                            print(Search_Date)
                        # if month is february  then attach 28 (DD) with month
                        elif (re.search(r'((feb)(\w+)*)', SDate.group(), flags=re.IGNORECASE)):
                            Search_Date = "28" + " " + SDate.group()
                            print(Search_Date)


            navigation_characteristics = soup.find_all("li", {"class": "cdsr-nav-link references-link"})
            # print(navigation_characteristics)

            for i, v in enumerate(navigation_characteristics):

                # print(v.getText())

                # this will check if the characteristics of studies link is present on the main page then will navigate to that page

                if "Characteristics of studies" in v.getText():

                    if SR_IDs + "-Pub2-Part2.html" not in os.listdir(path):

                        base_url2 = "http://cochranelibrary.com/cdsr/doi/{}/references".format(doi)
                        time.sleep(20)
                        r = requests.get(base_url2, headers={
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
                        print(r.status_code)
                        # 200 is the HTTP status code for "OK", a successful response.
                        if r.status_code == 200:
                            # soup = bs4.BeautifulSoup(r.content, 'html.parser')

                            file_contents = r.content
                            # print(file_contents)
                            path = var
                            os.chdir(path)
                            # open('%s.csv' % name, 'wb')
                            write_html_contents = open("%s-Pub2-Part2"
                                                       ".html" % SR_IDs, 'wb')

                            write_html_contents.write(file_contents)
                            write_html_contents.close()

                            #
                            # -------------------------------------

                            dirs2 = os.listdir(path)
                            htmlfile_list2 = []
                            newList2 = []
                            # for file2 in dirs2:
                            #     if file2.endswith("-Part2.html"):

                            contents = open(path + "/%s-Pub2-Part2.html" % SR_IDs, 'r', encoding="utf8")
                            source_code = contents.read()
                            # print(source_code)
                            # print(contents)
                            #
                            #
                            #
                            #
                            #
                            soup = bs4.BeautifulSoup(source_code, 'html.parser')
#                             # print("SOUP",soup)

                            Total_participants, total_trials, trials_with_participants,list_participants = get_participants_info(soup)
                            print("The total number of included trials: {}".format(total_trials))
                            print("The total number of participants are {}".format(Total_participants))


                            review_dict[doi]['Total_participants'] = Total_participants
                            review_dict[doi]['total_trials'] = total_trials
                            review_dict[doi]['trials_with_participants'] = trials_with_participants
                            review_dict[doi]['list_participants']=list_participants
                            review_dict[doi]['Total_participants'] = Total_participants
                            review_dict[doi]['Search_Date'] = Search_Date
                            # print(review_dict[doi])


                    elif SR_IDs + "-Pub2-Part2.html" in os.listdir(path):
                        print("{} is already downloaded in folder".format(SR_IDs + "-Pub2-Part2.html"))
                        contents = open(path + "/%s-Pub2-Part2.html" % SR_IDs, 'r', encoding="utf8")
                        source_code = contents.read()

                        # print(source_code)
                        # print(contents)
                        #
                        #
                        #
                        #
                        #
                        soup = bs4.BeautifulSoup(source_code, 'html.parser')
                        # print("SOUP",soup)

                        Total_participants, total_trials, trials_with_participants,list_participants = get_participants_info(soup)
                        print("The total number of included trials: {}".format(total_trials))
                        print("The total number of participants are {}".format(Total_participants))

                        review_dict[doi]['Total_participants'] = Total_participants
                        review_dict[doi]['total_trials'] = total_trials
                        review_dict[doi]['trials_with_participants'] = trials_with_participants
                        review_dict[doi]['list_participants']=list_participants

                        review_dict[doi]['Total_participants'] = Total_participants

                        review_dict[doi]['Search_Date'] = Search_Date
                        # print(review_dict[doi])

        except Exception as e:

            print('Error: {0}'.format(e))
            print(traceback.format_exc())
















if __name__ == "__main__":


    # input_file = 'pubmed_result_formatted_v3.csv'

    input_file = 'C:/Automatic_DataExtraction_Rules/Clean_Data.csv'
    # pub2_withpub3 = get_pub2_with_pub3(input_file)
    # print(len(pub2_withpub3))
    # for review in pub2_withpub3:
    #     # each review looks like  ('10.1002/14651858.CD006131.pub2', '21678352')
    #     # and these methods take the arguments (doi, pmid) so we can use * to pass the review directly to the method
    #     Save_Html_Contents(*review)
    #     Read_Html_Contents(*review)
    from collections import defaultdict
    # info will store every review and the information for the review extracted by Read_Html_Contents
    info = defaultdict()
    pub3_with_pub2 = get_pub3_with_pub2(input_file)
    for review in pub3_with_pub2:
        Save_Html_Contents(*review)
        info[review[0]]={}

        # we pass info to the method so that it can save the extracted information to info
        Read_Html_Contents(*review,info)
    with open('C:/Automatic_DataExtraction_Rules/write_data.csv','w') as outfile:
        writer = csv.DictWriter(outfile,lineterminator='\n' ,fieldnames=['SR_ID_Pub3','No of trials_Pub3','No of participants_Pub3','List of participants_Pub3','PublicationDate_Pub3','SearchDate_Pub3',
                                                     'conclusion','No of trials_Pub2','No of participants_Pub2','List of participants_Pub2','SearchDate_Pub2'])
        writer.writeheader()
        # now info holds all the reviews
        for review in info:
            pub2_id = review[:-1] +'2'
            # if it is a pub3 and the pub2 exists
            if review[-1] =='3' and pub2_id in info:
                # check that pub2 is not empty
                if not info[review[:-1] +'2']:
                    continue
                # check whether number of trials match for pub2 AND pub3
                # if (info[review]['total_trials'] != info[review]['trials_with_participants']) or  (info[pub2_id]['total_trials'] != info[pub2_id]['trials_with_participants']):
                #     continue
                # print('both match')
                print(review,info[review])
                # write the csv
                try:
                    writer.writerow({'SR_ID_Pub3':info[review]['pmid'],'No of trials_Pub3':info[review]['total_trials'],'No of participants_Pub3':info[review]['Total_participants'],'List of participants_Pub3':info[review]['list_participants'],
                                     'PublicationDate_Pub3':info[review]['publication_date'],'SearchDate_Pub3':info[review]['Search_Date'],'conclusion':info[review]['conclusion'],
                                     'No of trials_Pub2':info[pub2_id]['total_trials'],'No of participants_Pub2':info[pub2_id]['Total_participants'],'List of participants_Pub2':info[pub2_id]['list_participants'],'SearchDate_Pub2':info[pub2_id]['Search_Date']})
                except Exception as e:
                    print ('Error: {0}'.format(e))
                    continue