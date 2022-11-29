from flask import Flask, render_template, request, Blueprint
from flask import redirect, url_for
import json
from dmstudies.utils import * # this used to be "from utils import *"
from store_data import *
from manage_subject_info import *
import mturk_utils

expId = 'HRV'

tasks = Blueprint('tasks', __name__, url_prefix='/HRV')

_thisDir = os.path.dirname(os.path.abspath(__file__))#.decode(sys.getfilesystemencoding())
_parentDir = os.path.abspath(os.path.join(_thisDir, os.pardir))
dataDir = _parentDir + '/data/'

expTasksToComplete = {}


# o1: order 1, o2: order 2
# o1 - food rating and choice -> curiosity (wtp) -> perceptual choice
# o2 - curiosity (wtp) -> food rating and choice -> perceptual choice
expTaskOrders = {
    'HRV': {"o1": ['foodrating_demo_instructions', 'foodrating',
                   'foodchoicetask_demo_instructions', 'foodchoicetask',
                   'full_instructions_wtp','comprehension_test_wtp', 'main_task_instructions_wtp','task_wtp',
                   'rating_task_instructions','Qrating_task',
                   'rdcolor_instructions', 'rdcolor_task', 'color_questionnaire',
                   'questionnaire_instructions',  'ratehunger'],
            "o2": ['full_instructions_wtp','comprehension_test_wtp', 'main_task_instructions_wtp','task_wtp',
                   'rating_task_instructions','Qrating_task',
                   'foodrating_demo_instructions','foodrating',
                   'foodchoicetask_demo_instructions', 'foodchoicetask',
                   'rdcolor_instructions', 'rdcolor_task', 'color_questionnaire',
                   'questionnaire_instructions',  'ratehunger']}
}
repeatFoodRating = {'HRV': True}


@tasks.route("/", methods=["GET", "POST"])
@tasks.route("/consent_form", methods=["GET", "POST"])
def consent_form():
    if request.method == "GET":
        # if 'preview' in request.args and request.args.get('preview') == 'True':
        return render_template('dmstudies/consent_form.html')
    else:
        if contains_necessary_args(request.args):
            # worker accepted HIT
            [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
            subjectId = get_subjectId(expId, workerId)
            if workerId_exists(expId, workerId) and (get_task_results_exists(subjectId, 'WTWCovidResults')):
                return render_template('return_hit.html')
            elif not workerId_exists(expId, workerId):
                store_subject_info(expId, workerId, expTasksToComplete, assignmentId, hitId, turkSubmitTo)
        elif 'assignmentId' in request.args and request.args.get('assignmentId') == 'ASSIGNMENT_ID_NOT_AVAILABLE':
            # worker previewing HIT
            workerId = 'testWorker' + str(random.randint(1000, 10000))
            assignmentId = request.args.get('assignmentId')
            hitId = 'testHIT' + str(random.randint(10000, 100000))
            turkSubmitTo = 'www.calkins.psych.columbia.edu'
            live = request.args.get('live') == "True"
            return redirect(
                url_for('.foodrating_demo_instructions', expId=expId, workerId=workerId, assignmentId=assignmentId,
                        hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
        else:
            # in testing - accessed site through www.calkins.psych.columbia.edu
            workerId = 'testWorker' + str(random.randint(1000, 10000))
            assignmentId = 'testAssignment' + str(random.randint(10000, 100000))
            hitId = 'testHIT' + str(random.randint(10000, 100000))
            turkSubmitTo = 'www.calkins.psych.columbia.edu'
            live = False
            store_subject_info(expId, workerId, expTasksToComplete, assignmentId, hitId, turkSubmitTo)
        return redirect(
            url_for('.cur_study_info', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId,
                    turkSubmitTo=turkSubmitTo, live=live))


"""
Study information
"""


@tasks.route("/cur_study_info", methods=["GET", "POST"])
def cur_study_info():
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
    if request.method == "GET" and containsAllMTurkArgs:
        subjectId = get_subjectId(expId, workerId)
        completion_code = get_worker_notes(expId, subjectId, 'completionCode')
        if type(completion_code) != str:
            completion_code = mturk_utils.get_completion_code()
            add_worker_notes(expId, workerId, 'completionCode', completion_code)
        return render_template('dmstudies/cur_study_details.html')
    elif containsAllMTurkArgs:

        return redirect(url_for('.checkDiet', expId=expId,
                                workerId=workerId, assignmentId=assignmentId, hitId=hitId,
                                turkSubmitTo=turkSubmitTo, live=live))
    else:
        return redirect(url_for('unauthorized_error'))

"""
check u the subjects are vegan or vegetarian and if so, kick them out
"""

@tasks.route("/checkDiet", methods=["GET", "POST"])
def checkDiet():
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
    if request.method == "GET" and containsAllMTurkArgs:
        return render_template('dmstudies/checkDiet.html')
    elif containsAllMTurkArgs:
        is_veg = request.form["is_vegan"]
        if int(is_veg) == 1:
            return render_template('dmstudies/vegExit.html')
        else:
            subjectId = get_subjectId(expId, workerId)
            if int(subjectId[-4:]) % 2 == 0:
                order = 'o1'
            else:
                order = 'o2'
            nextTask = expTaskOrders[expId][order][0]
            return redirect(url_for('instructions.%s' % nextTask, demo=True, order=order, expId=expId,
                                    workerId=workerId, assignmentId=assignmentId, hitId=hitId,
                                    turkSubmitTo=turkSubmitTo, live=live))
    else:
        return redirect(url_for('unauthorized_error'))



"""
Rate Hunger

ratingOrder: "1" for "Not at all" to "Extremely" hungry scale order, "2" for "Extremely" to "Not at all" hungry scale order
num: "1" for first rating, "2" for second rating
"""


@tasks.route("/<ratingOrder>/ratehunger/<num>/<order>", methods=["GET", "POST"])
def ratehunger(num, ratingOrder, order):
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
    if request.method == "GET" and containsAllMTurkArgs:
        return render_template('dmstudies/ratehunger.html', ratingOrder=ratingOrder)
    elif containsAllMTurkArgs:
        subjectId = get_subjectId(expId, workerId)
        filePath = dataDir + expId + '/' + subjectId + '/'
        hungerRatingResults = json.loads(request.form['hungerRatingResults'])
        results_to_csv(expId, subjectId, filePath, 'HungerRating' + str(num) + '.csv', hungerRatingResults, {})
        if num == str(1):
            nextTask = expTaskOrders[expId][order][0]
            return redirect(url_for('instructions.%s' % nextTask, demo=True, order=order, expId=expId,
                                    workerId=workerId, assignmentId=assignmentId, hitId=hitId,
                                    turkSubmitTo=turkSubmitTo, live=live))
        else:
            return redirect(
                url_for('.last_meal', order=order, expId=expId, workerId=workerId, assignmentId=assignmentId,
                        hitId=hitId,
                        turkSubmitTo=turkSubmitTo, live=live))
    else:
        return redirect(url_for('unauthorized_error'))


""" 
Food Rating Task

Description: 
GET: Passes list of dictionaries with stimulus information to foodrating.html
POST: Saves foodrating data and stimuli to csv files, redirects to choice task

"""


@tasks.route("/foodrating/<order>", methods=["GET", "POST"])
def foodrating(order):
    name = 'foodrating'
    oneLineInstructions = "Rate how much you want to eat this food from 0 (least) to 10 (most)."
    containsAllMTurkArgs = contains_necessary_args(request.args)

    if 'demo' in request.args and containsAllMTurkArgs:
        if request.method == "GET" and request.args.get('demo') == 'TRUE':
            expVariables = get_ratingtask_expVariables(expId, subjectId=None, demo=True, question=oneLineInstructions,
                                                       leftRatingText='', middleRatingText='', rightRatingText='',
                                                       rs_min=0, rs_max=10, rs_tickIncrement=1, rs_increment=0.01,
                                                       rs_labelNames=["0", "", "", "", "", "5", "", "", "", "", "10"])
            return render_template('dmstudies/foodrating.html', expVariables=expVariables,
                                   stimFolder=foodStimFolder + 'demo/')
        else:
            [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

            return redirect(url_for('instructions.foodrating_instructions', expId=expId, workerId=workerId,
                                    assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live,
                                    order=order))
    elif containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

        subjectId = get_subjectId(expId, workerId)
        completedFoodRating = get_subfile_worker_notes(expId, subjectId,
                                                       'completedFoodRating') or get_subfile_worker_notes(expId,
                                                                                                          subjectId,
                                                                                                          'completedFoodRating1')
        if workerId_exists(expId, workerId) and (completedFoodRating == False or repeatFoodRating[expId] == True):
            if request.method == "GET":
                ### set experiment conditions here and pass to experiment.html
                # trialVariables should be an array of dictionaries
                # each element of the array represents the condition for one trial
                # set the variable conditions to the array of conditions
                expVariables = get_ratingtask_expVariables(expId, subjectId=None, demo=False,
                                                           question=oneLineInstructions, leftRatingText='',
                                                           middleRatingText='', rightRatingText='', rs_min=0, rs_max=10,
                                                           rs_tickIncrement=1, rs_increment=0.01,
                                                           rs_labelNames=["0", "", "", "", "", "5", "", "", "", "",
                                                                          "10"])

                return render_template('dmstudies/foodrating.html', expVariables=expVariables,
                                       stimFolder=foodStimFolder)
            else:
                subjectId = get_subjectId(expId, workerId)
                expResults = json.loads(request.form['experimentResults'])
                nextTask = get_next_task(name, expTaskOrders[expId][order])
                filePath = dataDir + expId + '/' + subjectId + '/'

                if not completedFoodRating and repeatFoodRating[expId]:
                    foodratingFileName = 'FoodRatingData1.csv'
                    nextTask = 'instructions.foodrating_repeat_instructions'
                    add_subfile_worker_notes(expId, subjectId, 'completedFoodRating1', True)
                elif completedFoodRating and repeatFoodRating[expId] == True:
                    foodratingFileName = 'FoodRatingData2.csv'
                    add_subfile_worker_notes(expId, subjectId, 'completedFoodRating2', True)
                else:
                    foodratingFileName = 'FoodRatingData.csv'
                    add_subfile_worker_notes(expId, subjectId, 'completedFoodRating', True)
                results_to_csv(expId, subjectId, filePath, foodratingFileName, expResults, {})

                return redirect(
                    url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId,
                            turkSubmitTo=turkSubmitTo, live=live, order=order))
        else:
            return redirect(url_for('unauthorized_error'))
    else:
        return redirect(url_for('unauthorized_error'))


""" 
Choice Task

Description: 
GET: Retrieves stimulus ratings from foodrating data file, sets up stimuli for choice task
POST: Saves choice task data and stimuli to csv files, redirects to thank you page

"""


@tasks.route("/foodchoicetask/<order>", methods=["GET", "POST"])
def foodchoicetask(order):
    name = 'foodchoicetask'
    containsAllMTurkArgs = contains_necessary_args(request.args)

    if 'demo' in request.args and containsAllMTurkArgs:
        if request.method == "GET" and request.args.get('demo') == 'TRUE':
            [stim1Names, stim1Bids, stim2Names, stim2Bids] = get_two_stimuli_lists_without_bids(
                foodStimFolder + 'demo/', '', '.jpg')
            expVariables = []  # array of dictionaries

            deltas = []
            for i in range(0, len(stim1Bids)):
                deltas.append(stim2Bids[i] - stim1Bids[i])

            for i in range(0, len(stim1Bids)):
                expVariables.append({"stimulus1": stim1Names[i], "stimulus2": stim2Names[i], "stim1Bid": stim1Bids[i],
                                     "stim2Bid": stim2Bids[i], "delta": deltas[i],
                                     "fullStim1Name": stim1Names[i] + ".jpg", "fullStim2Name": stim2Names[i] + ".jpg"})
            return render_template('dmstudies/choicetask.html', expId=expId, expVariables=expVariables,
                                   stimFolder=foodStimFolder + 'demo/', demo=True)
        else:
            [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
            if assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
                return redirect(url_for('accept_hit'))
            return redirect(url_for('instructions.foodchoicetask_instructions', expId=expId, workerId=workerId,
                                    assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live,
                                    order=order))
    elif containsAllMTurkArgs:
        # not demo - record responses now
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
        subjectId = get_subjectId(expId, workerId)

        completedFoodRating = get_subfile_worker_notes(expId, subjectId,
                                                       'completedFoodRating') or get_subfile_worker_notes(expId,
                                                                                                          subjectId,
                                                                                                          'completedFoodRating1')
        completedChoiceTask = get_subfile_worker_notes(expId, subjectId, 'completedChoiceTask')

        if workerId_exists(expId, workerId):
            if request.method == "GET":
                ### set experiment conditions here and pass to experiment.html
                # trialVariables should be an array of dictionaries
                # each element of the array represents the condition for one trial
                # set the variable conditions to the array of conditions

                if completedFoodRating:
                    stim1Bids = [];
                    stim2Bids = [];

                    if completedFoodRating == True and repeatFoodRating[expId] == True:
                        foodratingFileName = '_FoodRatingData2.csv'
                    else:
                        foodratingFileName = '_FoodRatingData.csv'
                    stimBidDict = get_bid_responses(
                        dataDir + expId + '/' + subjectId + '/' + subjectId + foodratingFileName)
                    [stim1Names, stim1Bids, stim2Names, stim2Bids] = get_two_stimuli_lists(stimBidDict, foodStimFolder,
                                                                                           '', '.jpg', 280)
                    expVariables = []  # array of dictionaries

                    deltas = []
                    for i in range(0, len(stim1Bids)):
                        deltas.append(stim2Bids[i] - stim1Bids[i])

                    for i in range(0, len(stim1Bids)):
                        expVariables.append(
                            {"stimulus1": stim1Names[i], "stimulus2": stim2Names[i], "stim1Bid": stim1Bids[i],
                             "stim2Bid": stim2Bids[i], "delta": deltas[i], "fullStim1Name": stim1Names[i] + ".jpg",
                             "fullStim2Name": stim2Names[i] + ".jpg"})

                    return render_template('dmstudies/choicetask.html', expId=expId, expVariables=expVariables,
                                           stimFolder=foodStimFolder, demo=False)
                else:
                    return redirect(url_for('unauthorized_error'))
            else:
                expResults = json.loads(request.form['experimentResults'])
                filePath = dataDir + expId + '/' + subjectId + '/'
                results_to_csv(expId, subjectId, filePath, 'ChoiceTaskData.csv', expResults, {})

                add_subfile_worker_notes(expId, subjectId, 'completedFoodChoice', True)

                nextTask = get_next_task(name, expTaskOrders[expId][order])
                return redirect(
                    url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId,
                            turkSubmitTo=turkSubmitTo, live=live, order=order))
    return redirect(url_for('unauthorized_error'))
###############################################################################

"""
CURIOSITY - WILLINGNESS TO PAY
"""


@tasks.route("/task_wtp/<order>", methods=["GET", "POST"])
def kanga_task_wtp(order):
    name = 'task_wtp';
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
    if request.method == "GET" and containsAllMTurkArgs:
        subjectId = get_subjectId(expId, workerId)
        # stimuli = get_trivia()
        stimuli = get_wtp_trivia(subjectId)
        if 'demo' in request.args and request.args.get('demo') == 'True':
            stimuli = get_practice_trivia()
        jitters = get_jitter()
        pay_amounts = get_pay_amounts()
        for i in range(0, len(stimuli)):
            trial = stimuli[i]
            trial['C_Pay'] = int(pay_amounts[i])
            trial['jitter'] = float(jitters[i])
        return render_template('dmstudies/kanga_wtp.html', expVariables=stimuli)
    elif containsAllMTurkArgs:  # request.method == "POST"
        if 'demo' in request.args and request.args.get('demo') == 'True':
            [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
            if assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
                return redirect(url_for('accept_hit'))
            return redirect(
                url_for('instructions.main_task_instructions_wtp', expId=expId, workerId=workerId, assignmentId=assignmentId,
                        hitId=hitId, turkSubmitTo=turkSubmitTo, live=live,order=order))
        else:
            subjectId = get_subjectId(expId, workerId)
            expResults = json.loads(request.form['experimentResults'])
            filePath = dataDir + expId + '/' + subjectId + '/'
            add_subfile_worker_notes(expId, subjectId, 'completedWTPTask', True)
            results_to_csv(expId, subjectId, filePath, 'WillingnessToPayResults.csv', expResults, {})
            nextTask = get_next_task(name, expTaskOrders[expId][order])

            return redirect(
                url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId,
                        hitId=hitId, turkSubmitTo=turkSubmitTo, live=live, order=order))
    else:
        return redirect(url_for('unauthorized_error'))

"""
RATING TASK
"""
@tasks.route("/Qrating_task/<order>", methods=["GET", "POST"])
def Qrating_task(order):
    name = 'Qrating_task'
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

        if workerId_exists(expId, workerId):
            if request.method == "GET":
                subjectId = get_subjectId(expId, workerId)
                expVariables = get_Qratingtask_expVariables(subjectId)

                return render_template('dmstudies/Qrating_task.html', demo='False', expVariables=expVariables)
            else:
                subjectId = get_subjectId(expId, workerId)
                filePath = dataDir + expId + '/' + subjectId + '/'

                add_subfile_worker_notes(expId, subjectId, 'completedRatingsTask', True)

                expResults = json.loads(request.form['experimentResults'])

                correctFormat = True
                condensedExpResults = []
                for i in range(0, len(expResults)):
                    if i % 2 == 0:  # question
                        trial = {}
                        trial['trialN'] = i / 2
                        trial['QuestionNum'] = expResults[i]['QuestionNum']
                        trial['Question'] = expResults[i]['Question']
                        trial['Answer'] = expResults[i]['Answer']
                        trial['QuestionRating'] = expResults[i]['rating']
                    else:  # answer
                        if trial['Answer'] == expResults[i]['Answer']:
                            trial['AnswerRating'] = expResults[i]['rating']
                            condensedExpResults.append(trial)
                        else:
                            correctFormat = False
                if correctFormat:
                    results_to_csv(expId, subjectId, filePath, 'QRatings.csv', condensedExpResults, {})

                else:  # raw results
                    results_to_csv(expId, subjectId, filePath, 'QRawRatings.csv', expResults, {})
                nextTask = get_next_task(name, expTaskOrders[expId][order])
                return redirect(url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId,
                                        hitId=hitId, turkSubmitTo=turkSubmitTo, live=live,order = order))
        else:
            return redirect(url_for('unauthorized_error'))
    else:
        return redirect(url_for('unauthorized_error'))

##################################################################################


"""
Random dot color task
"""


@tasks.route("/rdcolor_task/<order>", methods=["GET", "POST"])
def rdcolor_task(order):
    name = 'rdcolor_task'
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
        subjectId = get_subjectId(expId, workerId)
        if request.method == "GET":
            return render_template('dmstudies/rdm_color.html')
        else:  # in request.method == "POST"
            expResults = json.loads(request.form['experimentResults'])
            filePath = dataDir + expId + '/' + subjectId + '/'
            results_to_csv(expId, subjectId, filePath, 'RDColorData.csv', expResults, {})

            nextTask = get_next_task(name, expTaskOrders[expId][order])
            add_subfile_worker_notes(expId, subjectId, 'completedRDColor', True)
            return redirect(
                url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId,
                        turkSubmitTo=turkSubmitTo, live=live, order=order))
    return redirect(url_for('page_not_found'))


@tasks.route("/color_questionnaire/<order>", methods=["GET", "POST"])
def color_questionnaire(order):
    name = "color_questionnaire"
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
        subjectId = get_subjectId(expId, workerId)
        info = get_color_questionnaire()
        if request.method == "GET":
            options = info[0][list(info[0].keys())[0]]
            widthPercent = 70.0 / len(options)
            return render_template('dmstudies/color_questionnaire.html', info=info,
                                   instructions="Please answer the following questions about the task you just completed.",
                                   category=name,
                                   widthPercent=widthPercent)
        else:  # in request.method == "POST"
            q_and_a = []  # list of dictionaries where questions are keys and answers are values
            nQuestions = len(info)
            for i in range(0, nQuestions):
                tmp = {}
                tmp['QuestionNum'] = i + 1
                tmp['Question'] = request.form['q' + str(i + 1)]
                if 'a' + str(i + 1) in request.form:
                    tmp['Answer'] = request.form['a' + str(i + 1)]  # set keys and values in dictionary
                else:
                    tmp['Answer'] = ''
                q_and_a.append(tmp)

            filePath = dataDir + expId + '/' + subjectId + '/'

            add_subfile_worker_notes(expId, subjectId, 'completedColorQuestionnaire', True)

            results_to_csv(expId, subjectId, filePath, 'ColorQuestionnaireResults.csv', q_and_a, {})

            nextTask = get_next_task(name, expTaskOrders[expId][order])
            add_subfile_worker_notes(expId, subjectId, 'completedRDColor', True)
            return redirect(
                url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId,
                        turkSubmitTo=turkSubmitTo, live=live, order=order))
    return redirect(url_for('page_not_found'))


"""
QUESTIONNAIRES
"""

'''
@tasks.route("/general_questionnaire/<order>", methods=["GET", "POST"])
def general_questionnaire(order):
    name = "General"
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
        subjectId = get_subjectId(expId, workerId)
        info = get_questionnaire('General')
        if request.method == "GET":
            options = info[0][list(info[0].keys())[0]]
            widthPercent = 70.0 / len(options)
            return render_template('dmstudies/generic_anxiety_questionnaire.html', info=info,
                                   instructions="You will now be asked some questions about yourself.",
                                   category=name,
                                   widthPercent=widthPercent)
        else:  # in request.method == "POST"
            q_and_a = []  # list of dictionaries where questions are keys and answers are values
            nQuestions = len(info)
            for i in range(0, nQuestions):
                tmp = {}
                tmp['QuestionNum'] = i + 1
                tmp['Question'] = request.form['q' + str(i + 1)]
                if 'a' + str(i + 1) in request.form:
                    tmp['Answer'] = request.form['a' + str(i + 1)]  # set keys and values in dictionary
                else:
                    tmp['Answer'] = ''
                q_and_a.append(tmp)

            filePath = dataDir + expId + '/' + subjectId + '/'

            add_subfile_worker_notes(expId, subjectId, 'completedGeneralQuestionnaire', True)

            results_to_csv(expId, subjectId, filePath, 'GeneralAnxietyQuestionnaireResults.csv', q_and_a, {})

            return redirect(
                url_for('.ratehunger', ratingOrder=1, num=2, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId,
                        turkSubmitTo=turkSubmitTo, live=live, order=order))
    return redirect(url_for('page_not_found'))
'''

@tasks.route("/last_meal/<order>", methods=["GET", "POST"])
def last_meal(order):
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
        subjectId = get_subjectId(expId, workerId)
        info = get_hungerq()
        if request.method == "GET":
            return render_template('dmstudies/last_meal.html', info=info)
        else:
            q_and_a = []  # list of dictionaries where questions are keys and answers are values
            nQuestions = len(info)
            for i in range(0, nQuestions):
                tmp = {}
                tmp['QuestionNum'] = i + 1
                tmp['Question'] = request.form['q' + str(i + 1)]
                if 'a' + str(i + 1) in request.form:
                    tmp['Answer'] = request.form['a' + str(i + 1)]  # set keys and values in dictionary
                else:
                    tmp['Answer'] = ''
                q_and_a.append(tmp)
            Hours1 = request.form['HoursSinceMeal']
            Hours2 = request.form['HoursToMeal']
            time = request.form['time']
            minute = request.form['minute']
            ampm = request.form['time_of_day']
            results = [{'hours_since_last_meal': Hours1}, {'hours_to_next_meal': Hours2},{'time_of_study':time+minute+ampm}]
            q_and_a = []  # list of dictionaries where questions are keys and answers are values
            nQuestions = len(info)
            for i in range(0, nQuestions):
                tmp = {}
                tmp['QuestionNum'] = i + 1
                tmp['Question'] = request.form['q' + str(i + 1)]
                if 'a' + str(i + 1) in request.form:
                    tmp['Answer'] = request.form['a' + str(i + 1)]  # set keys and values in dictionary
                else:
                    tmp['Answer'] = ''
                q_and_a.append(tmp)

            filePath = dataDir + expId + '/' + subjectId + '/'
            results_to_csv(expId, subjectId, filePath, 'LastMeal.csv', results, {})
            results_to_csv(expId, subjectId, filePath, 'LastMeal2.csv', q_and_a, {})

            return redirect(url_for('.MEQ', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId,
                    turkSubmitTo=turkSubmitTo, live=live, order=order))
    return redirect(url_for('page_not_found'))

@tasks.route("/MEQ/<order>", methods=["GET", "POST"])
def MEQ(order):
    name = "MEQ"
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
        subjectId = get_subjectId(expId, workerId)
        info = get_MEQ()
        if request.method == "GET":
            options = info[0][list(info[0].keys())[0]]
            widthPercent = 70.0 / len(options)
            return render_template('dmstudies/MEQ.html', info=info,
                                   instructions="You will now be asked some questions about your eating habits. For each item, please check the answer that best characterizes your attitudes or behaviors",
                                   category=name,
                                   widthPercent=widthPercent)
        else:  # in request.method == "POST"
            q_and_a = []  # list of dictionaries where questions are keys and answers are values
            nQuestions = len(info)
            for i in range(0, nQuestions):
                tmp = {}
                tmp['QuestionNum'] = i + 1
                tmp['Question'] = request.form['q' + str(i + 1)]
                if 'a' + str(i + 1) in request.form:
                    tmp['Answer'] = request.form['a' + str(i + 1)]  # set keys and values in dictionary
                else:
                    tmp['Answer'] = ''
                q_and_a.append(tmp)

            filePath = dataDir + expId + '/' + subjectId + '/'
            add_subfile_worker_notes(expId, subjectId, 'completedMEQuestionnaire', True)
            results_to_csv(expId, subjectId, filePath, 'MEQuestionnaireResults.csv', q_and_a, {})

            return redirect(url_for('.IEQ', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId,
                                    turkSubmitTo=turkSubmitTo, live=live, order=order))
    return redirect(url_for('page_not_found'))


@tasks.route("/IEQ/<order>", methods=["GET", "POST"])
def IEQ(order):
    name = "IEQ"
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
        subjectId = get_subjectId(expId, workerId)
        info = get_IEQ()
        if request.method == "GET":
            options = info[0][list(info[0].keys())[0]]
            widthPercent = 70.0 / len(options)
            return render_template('dmstudies/IEQ.html', info=info,
                                   instructions="For each item, please check the answer that best characterizes your attitudes or behaviors.",
                                   category=name,
                                   widthPercent=widthPercent)
        else:  # in request.method == "POST"
            q_and_a = []  # list of dictionaries where questions are keys and answers are values
            nQuestions = len(info)
            for i in range(0, nQuestions):
                tmp = {}
                tmp['QuestionNum'] = i + 1
                tmp['Question'] = request.form['q' + str(i + 1)]
                if 'a' + str(i + 1) in request.form:
                    tmp['Answer'] = request.form['a' + str(i + 1)]  # set keys and values in dictionary
                else:
                    tmp['Answer'] = ''
                q_and_a.append(tmp)

            filePath = dataDir + expId + '/' + subjectId + '/'
            add_subfile_worker_notes(expId, subjectId, 'completedIEQuestionnaire', True)
            results_to_csv(expId, subjectId, filePath, 'IEQuestionnaireResults.csv', q_and_a, {})

            return redirect(url_for('.EATq', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId,
                                    turkSubmitTo=turkSubmitTo, live=live, order=order))
    return redirect(url_for('page_not_found'))


@tasks.route("/EATq/<order>", methods=["GET", "POST"])
def EATq(order):
    name = "EATq"
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
        subjectId = get_subjectId(expId, workerId)
        info = get_EATq()
        if request.method == "GET":
            options = info[0][list(info[0].keys())[0]]
            widthPercent = 70.0 / len(options)
            return render_template('dmstudies/EATq.html', info=info,
                                   instructions="For each item, please check the answer that best characterizes your attitudes or behaviors..",
                                   category=name,
                                   widthPercent=widthPercent)
        else:  # in request.method == "POST"
            q_and_a = []  # list of dictionaries where questions are keys and answers are values
            nQuestions = len(info)
            for i in range(0, nQuestions):
                tmp = {}
                tmp['QuestionNum'] = i + 1
                tmp['Question'] = request.form['q' + str(i + 1)]
                if 'a' + str(i + 1) in request.form:
                    tmp['Answer'] = request.form['a' + str(i + 1)]  # set keys and values in dictionary
                else:
                    tmp['Answer'] = ''
                q_and_a.append(tmp)

            filePath = dataDir + expId + '/' + subjectId + '/'
            add_subfile_worker_notes(expId, subjectId, 'completedEATQuestionnaire', True)
            results_to_csv(expId, subjectId, filePath, 'EAT26QuestionnaireResults.csv', q_and_a, {})

            return redirect(
                url_for('.IPAQ', expId=expId, workerId=workerId, assignmentId=assignmentId,
                        hitId=hitId, turkSubmitTo=turkSubmitTo, live=live, order=order))
    return redirect(url_for('page_not_found'))


@tasks.route("/IPAQ/<order>", methods=["GET", "POST"])
def IPAQ(order):
    name = "IPAQ"
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
        subjectId = get_subjectId(expId, workerId)
        if request.method == "GET":
            return render_template('dmstudies/IPAQ.html',
                                   instructions="You will now be asked some questions about your exercise habits.",
                                   category=name,
                                   widthPercent=50)
        else:  # in request.method == "POST"
            VigorousDays =  request.form['VigorousDays']
            VigorousHours =  request.form['VigorousHours']
            VigorousMinutes =  request.form['VigorousMinutes']
            ModerateDays =  request.form['ModerateDays']
            ModerateHours =  request.form['ModerateHours']
            ModerateMinutes =  request.form['ModerateMinutes']
            WalkingDays =  request.form['WalkingDays']
            WalkingHours =  request.form['WalkingHours']
            WalkingMinutes =  request.form['WalkingMinutes']
            SittingHours =  request.form['SittingHours']
            SittingMinutes = request.form['SittingMinutes']
            results = [['VigorousDays', VigorousDays],['VigorousHours', VigorousHours],['VigorousMinutes', VigorousMinutes],
                       ['ModerateDays', ModerateDays],['ModerateHours', ModerateHours],['ModerateMinutes', ModerateMinutes],
                       ['WalkingDays', WalkingDays],['WalkingHours', WalkingHours],['WalkingMinutes', WalkingMinutes],
                       ['SittingHours', SittingHours],['SittingMinutes', SittingMinutes]]


            filePath = dataDir + expId + '/' + subjectId + '/'
            add_subfile_worker_notes(expId, subjectId, 'completedIPAQuestionnaire', True)
            results_to_csv(expId, subjectId, filePath, 'IPAQuestionnaireResults.csv', results, {})

            return redirect(
                url_for('.demographicq', expId=expId, workerId=workerId, assignmentId=assignmentId,
                        hitId=hitId, turkSubmitTo=turkSubmitTo, live=live, order=order))
    return redirect(url_for('page_not_found'))


@tasks.route("/demographicq/<order>", methods=["GET", "POST"])
def demographicq(order):
    info = get_demographicq()
    instructions = 'You will now be asked some questions about yourself. Please answer each question as accurately as possible.'
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
    print(containsAllMTurkArgs)
    if request.method == "GET" and containsAllMTurkArgs:
        options = info[-1][list(info[-1].keys())[0]]
        widthPercent = 10
        return render_template('dmstudies/demographicq.html', info=info, instructions=instructions,
                               widthPercent=widthPercent)
    elif containsAllMTurkArgs:  # in request.method == "POST"
        subjectId = get_subjectId(expId, workerId)
        q_and_a = []  # list of dictionaries where questions are keys and answers are values
        nQuestions = len(info)
        for i in range(0, nQuestions):
            tmp = {}
            tmp['QuestionNum'] = i + 1
            tmp['Question'] = request.form['q' + str(i + 1)]
            if 'a' + str(i + 1) in request.form:
                tmp['Answer'] = request.form['a' + str(i + 1)]  # set keys and values in dictionary
            else:
                tmp['Answer'] = ''
            q_and_a.append(tmp)

        filePath = dataDir + expId + '/' + subjectId + '/'

        add_subfile_worker_notes(expId, subjectId, 'completedDemoQ', True)
        results_to_csv(expId, subjectId, filePath, 'DemographicQuestionnaire.csv', q_and_a, {})

        return redirect(url_for('.wtp_bonus', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId,
                    turkSubmitTo=turkSubmitTo, live=live, order=order))
    else:
        return redirect(url_for('unauthorized_error'))


@tasks.route("/wtp_bonus/<order>", methods=["GET", "POST"])
def wtp_bonus(order):
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
    if request.method == "GET" and containsAllMTurkArgs:
        subjectId = get_subjectId(expId, workerId)
        whichTask = 'trivia'
        pay_amount = get_wtp_pay_amount(expId, subjectId)  # in cents
        # subtract from 2 dollars
        if pay_amount <= 200:
            bonusAmount = 200 - pay_amount
            bonusAmount = bonusAmount / 100.0
            bonusAmount = round(bonusAmount, 2)
            return render_template('dmstudies/wtp_bonus.html', whichTask=whichTask, bonusAmount=bonusAmount)
        else:
            return redirect(url_for('show_completion_code', expId=expId, workerId=workerId, assignmentId=assignmentId,
                        hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
    elif containsAllMTurkArgs:  # in request.method == "POST"
        return redirect(
            url_for('show_completion_code', n=1, expId=expId, workerId=workerId, assignmentId=assignmentId,
                    hitId=hitId, turkSubmitTo=turkSubmitTo, live=live, order=order))
    return redirect(url_for('unauthorized_error'))

