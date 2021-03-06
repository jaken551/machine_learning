# coding: utf-8

# # Enron Fraud Exploration with Machine Learning
#
# Jake Neyer, Feb 2018
#
# ## Abstract
#
# The goal of this project is to use machine learning tactics to indentify persons-of-interest in a currated dataset of emails which were released after the Enron Scandal. Developing patterns of fraud and malicious intent in a dataset this large is nearly impossible by simple obervation and human intuition which is why machine learning tactics are essential.
#
#
# ## Background
#
# The Enron scandal that was publicized in October 2001 was perhaps one of the greatest examples of corporate fraud in American history. Through several means of hiding billions of dollars in debt, Enron executives were able to artificially increase and maintain stock value of the compaby. Disgruntled shareholders filed a lawsuit against the company and in December 2, 2001 which led to Enron filing for bankruptcy. Several Enron executives were indicted and sentenced. Addionally, Authur Andersen(a large audit and accounting partnership) was found guilty of illegally destroying documents related to the investigation and ultimately closed its doors because of it.
#
# Read more here: https://en.wikipedia.org/wiki/Enron_scandal

# ## Loading Dataset

# In[107]:


# !/usr/bin/python
import sys
import pickle

sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data
from sklearn import tree
import pandas
import numpy
import matplotlib.pyplot as plt

# In[108]:


### Loading the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

# Translating the dictionary into a pandas dataframe will make exploratory data analysis easier.

# In[109]:


# Translating Data in pandas data frame
df = pandas.DataFrame.from_records(list(data_dict.values()))
employees = pandas.Series(list(data_dict.keys()))
# set the index of df to be the employees series:
df.set_index(employees, inplace=True)

# ## Data Exploration
#
# Taking a look at what makes up the dataset:

# In[110]:


# Dataframe of POIs
poi = df[df['poi'] == 1]
poi

# And now taking a look at the Non-POI attributes.

# In[111]:


# Dataframe of Non-POIs
not_poi = df[df['poi'] == 0]
not_poi

# In[112]:


# Financial Averages
#
# Average POI Salary
print "Average POI Salary: ", poi["salary"].astype(float).mean()
# Average Non-POI Salary
print "Average Non-POI Salary: ", not_poi["salary"].astype(float).mean(), "\n"

# Average POI Deffered Income
print "Average POI Deffered Income: ", poi["deferred_income"].astype(float).mean()
# Average Non-POI Salary
print "Average Non-POI Deffered Income: ", not_poi["deferred_income"].astype(float).mean(), "\n"

# Average POI Deffered Income
print "Average POI Total Payments: ", poi["total_payments"].astype(float).mean()
# Average Non-POI Salary
print "Average Non-POI Total Payments: ", not_poi["total_payments"].astype(float).mean(), "\n"

# Average POI Bonus
print "Average POI Bonus: ", poi["bonus"].astype(float).mean()
# Average Non-POI Bonus
print "Average Non-POI Bonus: ", not_poi["bonus"].astype(float).mean(), "\n"

# Average POI Bonus
print "Average POI total payments: ", poi["total_payments"].astype(float).mean()
# Average Non-POI Bonus
print "Average Non-POI total payments: ", not_poi["total_payments"].astype(float).mean(), "\n"

# Average POI Total Stock Value
print "Average POI Total Stock Value: ", poi["total_stock_value"].astype(float).mean()
# Average Non-POI Total Stock Value
print "Average Non-POI Total Stock Value: ", not_poi["total_stock_value"].astype(float).mean(), "\n"

# Email Averages
#
# Average Emails From POI
print "Average Emails From POI to POI: ", poi["from_poi_to_this_person"].astype(float).mean()
# Average Emails From POI (Non-POIs)
print "Average Emails From POI to Non-POI: ", not_poi["from_poi_to_this_person"].astype(float).mean(), "\n"

# Average Emails to POI
print "Average Emails to POI from POI: ", poi["from_this_person_to_poi"].astype(float).mean()
# Average Emails to POI(Non-POIs)
print "Average Emails to POI from Non-POI: ", not_poi["from_this_person_to_poi"].astype(float).mean(), "\n"

# Average Shared Receipt with POI
print "Average Shared Receipt with POI (POI): ", poi["shared_receipt_with_poi"].astype(float).mean()
# Average Shared Receipt with POI (Non-POIs)
print "Average Shared Receipt with POI (Non-POIs): ", not_poi["shared_receipt_with_poi"].astype(float).mean()

# There are some significant differences between POIs and Non-POIs, specificallly in attributes such as salary, bonus, total payments, stock value, email from POI, emails to POI, and emails shared with POIs.

# In[113]:


# Number of total data points
len(df)

# In[114]:


# Number of POI data points
len(poi)

# In[115]:


# Number of Non-POI data points
len(not_poi)

# In[116]:


# Number of Features
len(df.columns)

# There are 146 total data points in this dataset. Of those 146 data points, there are 18 POIs and 128 Non-POI entries. Each entry has 24 different features.

# ## Indentifying Outliers

# In[117]:


# Determining 99th quantile of salaries
q = df["salary"].astype(float).quantile(0.99)
salary_outliers = df[df["salary"] > q]
salary_outliers = salary_outliers[salary_outliers['salary'] != 'NaN']
salary_outliers

# Clearly this entry is an anomaly in our dataset and an outlier. This is most likely just a issue with the formatting on the dataset we loaded.

# In[118]:


# Removing TOTAL entry from data frame
salary_outliers = salary_outliers.drop(['TOTAL'])
salary_outliers

# In[119]:


df.drop(['TOTAL'], inplace=True)

# In[120]:


# Looking at List of Employees
df.index.tolist()

# Notice the entry:`THE TRAVEL AGENCY IN THE PARK',` this is clearly not an employee.

# In[121]:


# Removing Bad Entry
df.drop(['THE TRAVEL AGENCY IN THE PARK'], inplace=True)

# In[122]:


# Looking at EUGENE LOCKHART
df.loc['LOCKHART EUGENE E']

# The TOTAL entry in the dataset was most certainly an outlier. It was actually an accumulation of multiple different entries in the same dataset, as opposed to a single unique entry. Because of this, I drop it from the dataset in the line above `df.drop(['TOTAL'],inplace=True)`. This will keep it from futher intruding in the data exploration process and moreover, will keep it from ruining the results of the classifiers. Similarly, I remove the Travel Agency in the park entry: `df.drop(['THE TRAVEL AGENCY IN THE PARK'],inplace=True)` because it is not a valid employee of the company. And finally, I will remove the `EUGENE LOCKHART` because it had no information. It was a completely empty entry.

# ## Additional Features
#
# There may be some ambiguity in the email features. For example, the total number of emails to, from, and shared with POIs might not be the best indicator for those particular metrics, but rather a more descriptive metric may be a ratio of the total emails sent, recieved, and shared to the total emails sent to POIs, recieved from POIs, and shared with POIs.

# In[123]:


# Ratio of Emails from POI
df['from_poi_ratio'] = df['from_poi_to_this_person'].astype(float) / (
df['from_poi_to_this_person'].astype(float) + df['from_messages'].astype(float))

# Ratio of Emails to POI
df['to_poi_ratio'] = df['from_this_person_to_poi'].astype(float) / (
df['from_this_person_to_poi'].astype(float) + df['to_messages'].astype(float))

# Ratio of Shared Emails with POI
df['shared_poi_ratio'] = df['shared_receipt_with_poi'].astype(float) / (
df['shared_receipt_with_poi'].astype(float) + df['from_messages'].astype(float) + df['from_poi_to_this_person'].astype(
    float))

# ## Building Dataset and Feature List

# In[124]:


# Creating a dictionary from the dataframe
df = df.replace(numpy.nan, 'NaN', regex=True)
df.drop('email_address', axis=1, inplace=True)
my_dataset = df.to_dict('index')

# In[125]:


# Making list of all features in dataframe
total_features_list = df.columns.values

# Printing List
print total_features_list

# I am going to be using the email ratios and total stock value in my feature list for building my machine learning model.

# In[126]:


# Creating my feature list

my_feature_list = ['poi', 'bonus', 'deferral_payments', 'deferred_income', 'director_fees',
                   'exercised_stock_options', 'expenses', 'from_messages',
                   'from_poi_to_this_person', 'from_this_person_to_poi', 'loan_advances',
                   'long_term_incentive', 'other', 'restricted_stock',
                   'restricted_stock_deferred', 'salary', 'shared_receipt_with_poi',
                   'to_messages', 'total_payments', 'total_stock_value', 'from_poi_ratio',
                   'to_poi_ratio', 'shared_poi_ratio']

# The from_poi_ratio, to_poi_ratio, and shard_poi_ratio were features I created to get a more granular number of how much communcitaion was made between each individual and individuals labled as POIs. For instance, if someone who sends a massive amounts of emails has 10 emails sent to a POI, it is less important than someone who sends few emails that sends 10 emails to a POI. So what I did was calculate separate ratios for all emails sent, recieved and shared with all emails sent, recieved and shared with POIs; the resulting features are from_poi_ratio, to_poi_ratio, and shard_poi_ratio.

# ## Creating Lables and Features for Models

# In[127]:


# my_feature_list features/lables

# Extracting features and labels from dataset for local testing
from sklearn.cross_validation import StratifiedShuffleSplit

data = featureFormat(my_dataset, my_feature_list, remove_NaN=True, sort_keys=True)

labels, features = targetFeatureSplit(data)
cv = StratifiedShuffleSplit(labels, 1000)
for train_idx, test_idx in cv:
    features_train = []
    features_test = []
    labels_train = []
    labels_test = []
    for ii in train_idx:
        features_train.append(features[ii])
        labels_train.append(labels[ii])
    for jj in test_idx:
        features_test.append(features[jj])
        labels_test.append(labels[jj])

# One thing to note here is the effort put into validation. A classic mistake with missing validation is overfitted the data. So here, the labels and features are both split into training and testing sets using the `StratifiedShuffleSplit` algorithm provided in the sklearn library. This algorithm merges StratifiedKFold and ShuffleSplit algorithms and returns randomized folds in the dataset. This will ensure that the data will be split for training and testing so that either set will not have an overwhelming percentage of POI or Non-POI entries.

# ## Feature Selection

# In[128]:


from sklearn.feature_selection import SelectKBest, f_classif

k_best = SelectKBest(f_classif, k=7)
k_best.fit_transform(features_train, labels_train)

mask = k_best.get_support()
new_features_list = []

for bool, feature in zip(mask, my_feature_list):
    if bool:
        new_features_list.append(feature)

print new_features_list

# In[129]:


# Building Final Feature List
for i in range(len(new_features_list) - 1):
    if new_features_list[i] == 'poi':
        new_features_list.pop(i)

new_features_list.insert(0, "poi")
my_feature_list = new_features_list

print my_feature_list

# I used the `SelectKBest` algorithm to select my features.

# ## New Feature Justification
#
# The `from_poi_ratio` here is a great example of why the creation of this feature was justified. It has a consistently high feature importance, as determined by `SelectKbest`.

# In[130]:


# Using New Features
# Extracting features and labels from dataset for local testing
from sklearn.cross_validation import StratifiedShuffleSplit

data = featureFormat(my_dataset, my_feature_list, remove_NaN=True, sort_keys=True)

labels, features = targetFeatureSplit(data)
cv = StratifiedShuffleSplit(labels, 1000)
for train_idx, test_idx in cv:
    features_train = []
    features_test = []
    labels_train = []
    labels_test = []
    for ii in train_idx:
        features_train.append(features[ii])
        labels_train.append(labels[ii])
    for jj in test_idx:
        features_test.append(features[jj])
        labels_test.append(labels[jj])

# ## Building and Testing Classifiers

# In order to get some sort of baseline, I will start with a simple Naive Bayes classifer.

# In[131]:


from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score

# Constructing Naive Bayes Classifier
clf = GaussianNB()
# Ffitting classifier
clf.fit(features_train, labels_train)
# Storing predicted values in a list
nb_pred = clf.predict(features_test)

print accuracy_score(labels_test, nb_pred)
print "Precision: ", precision_score(labels_test, nb_pred, average='micro')
print "Recall: ", recall_score(labels_test, nb_pred, average='micro')

# The NB classifier scored an accuracy of about 90%. I will continue to try other classifiers to see if anything is better.

# Next I wil try a Support Vector Machine to see what kind of results I can yeild.

# In[132]:


from sklearn.svm import SVC

# Creating a SVM
clf = SVC()
# Fitting the SVM
clf.fit(features_train, labels_train)
# Making a list of predicitions
svm_pred = clf.predict(features_test)

print accuracy_score(labels_test, svm_pred)
print "Precision: ", precision_score(labels_test, svm_pred, average='micro')
print "Recall: ", recall_score(labels_test, svm_pred, average='micro')

# Wow! This is a pretty good accuracy score. I will try a random forest classifier to see if it is any better.

# In[133]:


from sklearn.ensemble import RandomForestClassifier

# Constructing Random Forest
clf = RandomForestClassifier()
# Fitting classifier
clf.fit(features_train, labels_train)
# Making list of predictions
rf_pred = clf.predict(features_test)

print accuracy_score(labels_test, rf_pred)
print "Precision: ", precision_score(labels_test, rf_pred, average='micro')
print "Recall: ", recall_score(labels_test, rf_pred, average='micro')

# The random forest classifier is not bad with over 90% accuracy right out of the box.

# The classifier I ultimately chose to go with was the Random Forest Classifier. It did not have the best accuracy right out of the box, but due to its plethora of tunable parameters, I think it will improve significantly after the tuning process of this project. Random Forest Classifiers(RFCs) are great for supervised classifiation problem sets such as the one we are working with. Essentially, RFCs are a culmination of simpler decision trees. In this case, I think it will be a great fit for our problem set.
#

# ## Scaling
#
# I did not scale any of the features in this particular instance. As I am using a Random Forest Classifier, scaling is not necessarily an important step. Unlike SVMs, K-nearest neighbors, and logistic regression where normalization is essential, RFCs do not particularly need scaled features to perform.

# ## Tuning Classifier

# In[134]:


from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from scipy.stats import randint as sp_randint

# Constructing Random Forest
rfc = RandomForestClassifier()

param_dist = {'n_estimators': [5,10],
              'max_depth': [None, 2, 4, 10],
              'min_samples_split': [2, 4, 6],
              'min_samples_leaf': [1,3],
              'max_leaf_nodes': [None, 2, 10],
              'criterion': ["gini"]}

# run randomized search
n_iter_search = 50
gs = GridSearchCV(rfc, param_dist)

gs.fit(features_train, labels_train)

clf = gs.best_estimator_
rs_pred = clf.predict(features_test)

print accuracy_score(labels_test, rs_pred)
print "Precision: ", precision_score(labels_test, rs_pred, average='micro')
print "Recall: ", recall_score(labels_test, rs_pred, average='micro')

# Tuning parameters in machine learning models is sometimes refered to as tuning the hyperparameters as the parameters are often noted as the coefficients of the algorithm. In this case, tuning the hyperparamters means adjusted the way the classifier is constructed by changing items such as the max depth, max features, minimum samples required to split, et cetera. Changing these hyperparameters can significantly affect the way the classifier performs. I used the `GridSearchCV` algorithm to determine hyperparamters due to its reliable results and perfomance. `GridSearchCV` runs a search to determine which paramters are most effective.

# ## Evaluation Metrics

# In[135]:


from sklearn.metrics import precision_score
from sklearn.metrics import recall_score

print "Precision: ", precision_score(labels_test, rf_pred, average='micro')
print "Recall: ", recall_score(labels_test, rf_pred, average='micro')

# The two evaluation metrics I chose to use were recall and precision. The recall measures the number of items that can be correctly identified. For example, if there are 10 POIs in this dataset(there are more than that) and this classifier can only say that 9 people are POIs then the recall if 0.90. The precisions measures the accuracy of the indetification. For example, if there are once again 10 POIs in this dataset, if the classifier determines 10 people are POIs, but of those 10 people only 9 ARE actually POIs, then the precision is 0.90.
#

# ## Dumping Classifier for Reuse

# In[136]:


#hard coded features and classifier after trial and error
my_feature_list = ['poi', 'deferral_payments', 'director_fees', 'exercised_stock_options',
                   'restricted_stock_deferred', 'total_payments', 'total_stock_value', 'loan_advances']

clf = RandomForestClassifier(bootstrap=False, class_weight=None, criterion='gini',
            max_depth=None, max_features=3, max_leaf_nodes=None,
            min_impurity_decrease=0.0, min_impurity_split=None,
            min_samples_leaf=3, min_samples_split=2,
            min_weight_fraction_leaf=0.0, n_estimators=10, n_jobs=1,
            oob_score=False, random_state=None, verbose=0,
            warm_start=False)



# Dumping Classifier
dump_classifier_and_data(clf, my_dataset, my_feature_list)


# ## Sources
#
# https://machinelearningmastery.com/how-to-tune-algorithm-parameters-with-scikit-learn/
#
# https://en.wikipedia.org/wiki/Random_forest
#
# http://scikit-learn.org/stable/documentation.html
#
# https://discussions.udacity.com/t/project-fear-strugging-with-machine-learning-project/198529/2
#
# https://discussions.udacity.com/t/featureformat-function-not-doing-its-job/192923/2
#
# http://scikit-learn.org/stable/auto_examples/preprocessing/plot_scaling_importance.html
#
