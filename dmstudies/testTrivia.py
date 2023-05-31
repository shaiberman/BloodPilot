import os
import sys
import random
import pandas as pd
import numpy as np

_thisDir = os.path.dirname(os.path.abspath(__file__))#.decode(sys.getfilesystemencoding())
_parentDir = os.path.abspath(os.path.join(_thisDir, os.pardir))
dataDir = _parentDir + '/data/'

expId = 'HRV'

##### for RATING ########
'''
questions = pd.read_csv(_thisDir + "/Kanga_TriviaList_goodQs.csv", usecols=['QuestionNum', 'Question', 'AnswerUse', 'IsFood'], encoding='unicode_escape')
questions.columns = ['QuestionNum', 'Question', 'Answer','isFood']
# separate food and non food
foodsQuestions = questions.loc[questions['isFood'] > 0, ['QuestionNum', 'Question', 'Answer']]
genQuestions = questions.loc[questions['isFood'] == 0, ['QuestionNum', 'Question', 'Answer']]
# shuffle the order
foodsQuestions = foodsQuestions.sample(frac=1).reset_index(drop=True) # the sample with frac=1 means that i take all drows but in radom order
genQuestions = genQuestions.sample(frac=1).reset_index(drop=True)
# make sure there are enough of the food Qs
frames = [ foodsQuestions[0:30] , genQuestions[0:200]]
questions = pd.concat(frames)
# randomize again
questions = questions.sample(frac=1).reset_index(drop=True)
# what is that for?
# questions = questions.to_dict('records')
print('should be data frame:')
print(type(questions))
questions.to_dict('records')  # vas is das?
print('should be dict:')
print(type(questions))

keys = questions['Question'].values
values = questions['Answer'].values
dictionary1 = dict(zip(keys, values))
keys = questions['Question'].values
values = questions['QuestionNum'].values
dictionary2 = dict(zip(keys, values))

'''
subjectId = 'HRV_0008'
#### done with: stimuli = get_wtp_trivia(subjectId), which is:
### 1. questions = get_trivia() - this gets new questions but i want to pool outof the questions that were used in ratings only
### 2. old_questions = get_questions_used_in_rating_task(subjectId)
### 3. questions = questions.loc[~questions['Question'].isin(old_questions)]
### 4. questions = questions.to_dict('records')

# 1. get all the questions
# get trivie all
questions = pd.read_csv(_thisDir + "/Kanga_TriviaList_goodQs.csv", usecols=['QuestionNum', 'Question', 'AnswerUse', 'IsFood'], encoding='unicode_escape')
questions.columns = ['QuestionNum', 'Question', 'Answer','isFood']
questions = questions.sample(frac=1).reset_index(drop=True) # randomize

# get unknown qs used for ratings
datafile = os.path.join(dataDir, expId, subjectId, subjectId + '_QRatings.csv')
if os.path.exists(datafile):
    df = pd.read_csv(datafile)
    # collect only Qs whose answer they don't know:
    df = df.loc[df['receivedResponse']==True]

    # collect the top 80 questions -
    ratings = df['rating'].to_numpy(dtype=float)
    q = 100*(len(ratings)-80)/len(ratings)
    p = np.percentile(ratings,q)
    df = df.loc[ratings>p]
    q_list = df['Question'].values.tolist()

    print(q_list)

    # q_list = df['Question'].values.tolist()

   # q_list = unknownQs['Question'].values.tolist()
else:
    print("File not found")

questions = questions.loc[questions['Question'].isin(q_list)]
questions = questions.to_dict('records')
