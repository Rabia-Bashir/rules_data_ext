
from __future__ import division
# from __future__ import print_function
import numpy as np
# from sklearn import tree
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
import pydotplus
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import KFold
import datetime
from datetime import date
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt

from sklearn import metrics
from sklearn.metrics import roc_curve, auc
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.tree import export_graphviz
import traceback
from sklearn.externals.six import StringIO

from IPython.display import Image


def calc_num_days(date1, date2):

        num_days = (date2 - date1).days
        return num_days
#
def convert_todate(datest):


        return datetime.datetime.strptime(datest, '%d-%b-%y')


def draw_randomforesttree(rf,f_names,l_names):
  # try:
  # for i in range(60):
    dot_data = StringIO()



    export_graphviz(rf.estimators_[5], out_file=dot_data, label='all', node_ids=False,
                    feature_names=f_names,
                    class_names=l_names,
                    filled=True, rounded=True,
                    special_characters=True, impurity=True, proportion=True)




    graph = pydotplus.graph_from_dot_data(dot_data.getvalue())

    
    # graph.write_png(str(i)+'forest.png')


    graph.write_png('forest.png')

    Image(graph.create_png())

    # output_dt_drawing =  "Rforest" +'.pdf'
    # graphToDraw.write_pdf(output_dt_drawing)


  # except Exception as e:
  #     print('Error: {0}'.format(e))

def Forest_Training(d_training, l_training, fnames_training, lnames_training):

 # try:

        d_train, d_test, l_train, l_test = train_test_split(d_training, l_training, test_size=0.2, random_state=30)



        # randomforest = RandomForestClassifier()
        # parameters={'n_estimators': [60,70,100,120,140,180,200,250,400], 'min_samples_leaf':[30], 'max_depth':[2, 3], 'criterion':['entropy','gini'],
        #                                       'class_weight':['balanced','balanced_subsample'], 'max_features':['auto', 'sqrt', 'log2'],'min_samples_split':[4,5],
        #                                      'random_state':[40,30,50]}
        #
        #
        #
        # CV_rfc = GridSearchCV(estimator=randomforest,param_grid=parameters,cv=5)
        # CV_rfc.fit(d_training, l_training)
        # best_parameters =CV_rfc.best_params_
        # print(best_parameters) # after finding best_parameters, use them in RandomForestClassifier()



        random_best= RandomForestClassifier(n_estimators=120, min_samples_leaf=30, max_depth=2, criterion='entropy',
                                              class_weight='balanced_subsample', max_features='auto', min_samples_split=4,
                                             random_state=40)



        random_best.fit(d_training, l_training)
        l_pred = random_best.predict(d_test)


        importances = list(random_best.feature_importances_)

        feature_importances = [(feature, round(importance, 2)) for feature, importance in zip(fnames_training, importances)]
        # Sort the feature importances by most important first
        feature_importances = sorted(feature_importances, key=lambda x: x[1], reverse=True)


        [print('Variable: {:20} Importance: {}'.format(*pair)) for pair in feature_importances];



















        roc_value=roc_auc_score(l_test,l_pred)
        print("----------------------------")
        print("ROC Value: ",roc_value)

        #print(confusion_matrix(l_test, l_pred))
        print(classification_report(l_test, l_pred))
        print("Accuracy: ", accuracy_score(l_test, l_pred))


        print("----------------------------")
        print("Draw Random Forest")

        draw_randomforesttree(random_best, fnames_training, lnames_training)

        #
        # fpr, tpr, threshold = metrics.roc_curve(t_values, l_pred)
        #
        #
        # roc_auc = metrics.auc(fpr, tpr)
        #
        #
        # plt.title('Receiver Operating Characteristic')
        # plt.plot(fpr, tpr, 'b', label='AUC = %0.2f' % roc_auc)
        # plt.legend(loc='lower right')
        # plt.plot([0, 1], [0, 1], 'r--')
        # plt.xlim([0, 1])
        # plt.ylim([0, 1])
        # plt.ylabel('True Positive Rate')
        # plt.xlabel('False Positive Rate')
        # plt.show()



def  read_input_file(input_file):
            y_true = []
            label_names=[]
            data=[]
            label=[]
            feature_names = []


            label_names = ['Not changed', 'Changed']


            # label_names = np.asarray(label_names, dtype='|S10') # converts input to an array
            label_names = np.asarray(label_names)


            feature_names.append('Number of Trials in SR')
            feature_names.append('Number of participants in SR')
            feature_names.append('Coverage score')
            feature_names.append('Update time using search dates')


            # input_file = "C:/Users/44697147/Desktop/CochraneBot_Programs_updated/Automatic_Data_Extraction_Final_Data.csv"
            infile = open(input_file, 'r')
            cntLine = 0
            data= []
            labels = []
            for line in infile:
                    if cntLine == 0:
                        cntLine += 1
                        continue
                    else:
                        cntLine += 1

                    line = line.strip()
                    sPart = line.split(',')

                    SR1_ID = sPart[0]
                    Numb_of_trials_SR1 = float(sPart[6])
                    Numb_of_participants_SR1 = float(sPart[7])
                    Numb_of_participants_SR2 = float(sPart[2])
                    SR1_searchDate=sPart[5]
                    SR2_searchDate=sPart[4]

                    SR1_searchDate = convert_todate(sPart[5])

                    SR2_searchDate = convert_todate(sPart[4])
                    # print(SR1_searchDate)
                    # print(SR2_searchDate)

                    Conclusion = int(sPart[8])
                    Update_time_using_search_dates = int(calc_num_days(SR1_searchDate, SR2_searchDate))
                    # print(Update_time_using_search_dates)

                    Completeness_score = float(Numb_of_participants_SR1 / Numb_of_participants_SR2)
                    # print(Completeness_score)
                    data.append([Numb_of_trials_SR1, Numb_of_participants_SR1, Completeness_score,
                              Update_time_using_search_dates])

                    labels.append(Conclusion)

                    # if Conclusion==0:
                    #     y_true.append(0)
                    #
                    # else:
                    #     y_true.append(1)



            data=np.asarray(data)

            labels=np.asarray(labels)






            Forest_Training(data, labels,feature_names,label_names)
            # except Exception as e:
            #     print('Error: {0}'.format(e))
            #     print('On the line {0}: {1}'.format(cntLine, line))



if __name__ == '__main__':
    # read_input_file("C:/Users/44697147/Desktop/CochraneBot_Programs_updated/Automatic_Data_Extraction_Final_Data.csv")
    read_input_file("C:/Users/44697147/Desktop/CochraneBot_Programs_updated/Automatic_Data_Extraction_updated_624Records.csv")
    # read_input_file("C:/Users/44697147/Desktop/CochraneBot_Programs_updated/Automatic_Data_Extraction_Final_Data_excludeRevieswith_notrials_inupdate.csv")























