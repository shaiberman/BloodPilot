import os
import sys
import random
import pandas as pd
import numpy as np

_thisDir = os.path.dirname(os.path.abspath(__file__))#.decode(sys.getfilesystemencoding())
_parentDir = os.path.abspath(os.path.join(_thisDir, os.pardir))
dataDir = _parentDir + '/data/'

expId = 'HRV'
foodStimFolder = '/static/foodstim60/'


def get_task_results_exists(subjectId, resultsfilename):
    return os.path.exists(os.path.join(dataDir, expId, subjectId, subjectId + '_' + resultsfilename + '.csv'))


"""
Given name of current task and list of tasks, return the task that should be next
If task is final task, return 'thankyou' to route to thank you page

For example:
    x = 'auction'
    y = 'choicetask'
    z = 'hello'
    tasks = ['auction','choicetask'] 
    print(get_next_task('auction', tasks))		# return 'choicetask'
    print(get_next_task('choicetask', tasks)) 	# return 'thankyou'
    print(get_next_task('hello', tasks)) 		# return None

*** For url_for
"""


"""
WILLING TO PAY
"""
"""
There will be around 120 questions. maximum 200. 
so I want there to be around 50 food questions or 40?  
"""

def get_practice_trivia():
    questions = pd.read_csv(_thisDir + "/Kanga_PracticeQs.csv")
    questions.columns = ['QuestionNum', 'Question', 'Answer']
    questions = questions[0:3]
    questions = questions.to_dict('records')
    random.shuffle(questions)
    return questions


def get_jitter():
    jitter = [round(random.uniform(0.5, 2), 3) for i in range(1000)]
    return jitter


def get_wait():
    w = np.array([4, 6, 8, 10, 12, 14, 16])
    wait = np.repeat(w, 500)
    random.shuffle(wait)
    return wait


def get_pay_amounts():
    # w = np.array([4, 6, 8, 10, 12, 14, 16])
    w = np.array([1, 2, 3, 4, 5, 6, 7])
    wait = np.repeat(w, 500)
    random.shuffle(wait)
    return wait

####### for RATING ########
def get_trivia():
    questions = pd.read_csv(_thisDir + "/Kanga_TriviaList_goodQs.csv", usecols=['QuestionNum', 'Question', 'AnswerUse', 'IsFood'], encoding='unicode_escape')
    questions.columns = ['QuestionNum', 'Question', 'Answer','isFood']
    # separate food and non food
    foodsQuestions = questions.loc[questions['isFood'] > 0, ['QuestionNum', 'Question', 'Answer']]
    genQuestions = questions.loc[questions['isFood'] == 0, ['QuestionNum', 'Question', 'Answer']]
    # shuffle the order
    foodsQuestions = foodsQuestions.sample(frac=1).reset_index(drop=True)
    genQuestions = genQuestions.sample(frac=1).reset_index(drop=True)
    # make sure there are enough of the food Qs
    frames = [ foodsQuestions[0:30] , genQuestions[0:200]]
    questions = pd.concat(frames)
    # randomize again
    questions = questions.sample(frac=1).reset_index(drop=True)
    # what is that for?
    # questions = questions.to_dict('records')
    return questions

def get_trivia_as_dicts(questions):
    keys = questions['Question'].values
    values = questions['Answer'].values
    dictionary1 = dict(zip(keys, values))
    keys = questions['Question'].values
    values = questions['QuestionNum'].values
    dictionary2 = dict(zip(keys, values))
    return dictionary1, dictionary2

def get_Qratingtask_expVariables_noanswer(subjectId):
    # overall there are about 460, out of ~70 are food related.
    # this should gets 230 Qs, 30 of which are food Qs.
    # I should put in place something for the second time this is done.
    questions = get_trivia()
    questions = questions.to_dict('records') # vas is das?
    random.shuffle(questions)
    # how many Qs do i want?
    trivia_dict, trivia_qnum_dict = get_trivia_as_dicts(questions)
    qs = questions['Question'].values
    expVariables = []
    rs_min = 0
    rs_max = 100
    rs_tickIncrement = 25
    rs_increment = 1
    rs_labelNames = ["0", "25", "50", "75", "100"]
    for q in qs:
        trial = {}
        trial['TrialType'] = 'RateQuestion'
        trial['Question'] = q
        answer = trivia_dict[q]
        trial['Answer'] = answer
        qnum = trivia_qnum_dict[q]
        trial['QuestionNum'] = int(qnum)
        trial['rs_min'] = int(rs_min)
        trial['rs_max'] = int(rs_max)
        trial['rs_tickIncrement'] = rs_tickIncrement
        trial['rs_increment'] = rs_increment
        trial['rs_labelNames'] = rs_labelNames
        expVariables.append(trial)
    return expVariables


##### WTP#####
# this would be useful for sorting the Qs for the WTP part
def get_questions_used_in_rating_task(subjectId):
    datafile = os.path.join(dataDir, expId, subjectId, subjectId + '_RatingsResults.csv')
    if os.path.exists(datafile):
        df = pd.read_csv(datafile)
        questions = df['Question'].values.tolist()
        return questions
    print("File not found")
    return []

def get_wtp_trivia(subjectId):
    questions = get_trivia()
    # remove questions in WTW and rating tasks
    old_questions = get_questions_used_in_rating_task(subjectId)
    questions = questions.loc[~questions['Question'].isin(old_questions)]

    questions = questions.to_dict('records')
    random.shuffle(questions)
    return questions


def get_questions_used_in_wtp_task(subjectId):
    datafile = os.path.join(dataDir, expId, subjectId, subjectId + '_WillingnessToPayResults.csv')
    if os.path.exists(datafile):
        df = pd.read_csv(datafile)
        questions = df['Question'].values.tolist()
        return questions
    print("File not found")
    return []


# # # # for second time around # # # #
def get_trivia_all():
    questions = pd.read_csv(_thisDir + "/Kanga_TriviaList_goodQs.csv", usecols=['QuestionNum', 'Question', 'AnswerUse', 'IsFood'], encoding='unicode_escape')
    questions.columns = ['QuestionNum', 'Question', 'Answer','isFood']
    questions = questions.sample(frac=1).reset_index(drop=True) # randomize

    return questions

def get_unused_questions(subjectId):
    questions = get_trivia_all()
    old_questions = get_questions_used_in_wtp_task(subjectId)
    unused_questions = questions.loc[~questions['Question'].isin(old_questions)]
    unused_questions = unused_questions.sample(frac=1).reset_index(drop=True)
    return unused_questions



''' removed functions:

def get_questions_used_in_wtw_task(subjectId):
    datafile = os.path.join(dataDir, expId, subjectId, subjectId + '_CuriosityTaskResults.csv')
    if os.path.exists(datafile):
        df = pd.read_csv(datafile)
        questions = df['Question'].values.tolist()
        return questions
    print("File not found")
    return []

 # this may be unnecessary
 def sample_questions_for_food(questions):

    foodsQuestions = questions.loc[questions['isFood'] > 0, ['QuestionNum', 'Question', 'Answer']]
    genQuestions = questions.loc[questions['isFood'] == 0, ['QuestionNum', 'Question', 'Answer']]
    # shuffle the order
    foodsQuestions = foodsQuestions.sample(frac=1).reset_index(drop=True)
    genQuestions = genQuestions.sample(frac=1).reset_index(drop=True)
    # make sure there are enough of the food Qs
    frames = [foodsQuestions[0:3], genQuestions[0:7]]
    questions = pd.concat(frames)
    # randomize again
    questions = questions.sample(frac=1).reset_index(drop=True)
    return questions

def get_Qratingtask_expVariables(subjectId):
    unused_q_all = get_unused_questions(subjectId) # this returns only the questions
    unused_q_wfood = sample_questions_for_food(unused_q_all) # returns `10 unused qs, 3 of which are food related
    trivia_dict, trivia_qnum_dict = get_trivia_as_dicts(unused_q_wfood)
    unused_q = unused_q_wfood['Question'].values
    expVariables = []
    rs_min = 0
    rs_max = 100
    rs_tickIncrement = 25
    rs_increment = 1
    rs_labelNames = ["0", "25", "50", "75", "100"]
    for q in unused_q:
        trial = {}
        trial['TrialType'] = 'RateQuestion'
        trial['Question'] = q
        answer = trivia_dict[q]
        trial['Answer'] = answer
        qnum = trivia_qnum_dict[q]
        trial['QuestionNum'] = int(qnum)
        trial['rs_min'] = int(rs_min)
        trial['rs_max'] = int(rs_max)
        trial['rs_tickIncrement'] = rs_tickIncrement
        trial['rs_increment'] = rs_increment
        trial['rs_labelNames'] = rs_labelNames
        expVariables.append(trial)

        trial = {}
        trial['TrialType'] = 'RateAnswer'
        trial['Question'] = q
        answer = trivia_dict[q]
        trial['Answer'] = answer
        qnum = trivia_qnum_dict[q]
        trial['QuestionNum'] = int(qnum)
        trial['rs_min'] = int(rs_min)
        trial['rs_max'] = int(rs_max)
        trial['rs_tickIncrement'] = rs_tickIncrement
        trial['rs_increment'] = rs_increment
        trial['rs_labelNames'] = rs_labelNames
        expVariables.append(trial)
    return expVariables
'''