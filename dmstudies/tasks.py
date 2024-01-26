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
dataDir = _parentDir + '/pilotdata/'

expTasksToComplete = {}

order='o1'
# o1: order 1, o2: order 2
# o1 - food rating and choice -> curiosity (wtp) -> perceptual choice
# o2 - curiosity (wtp) -> food rating and choice -> perceptual choice
# for the blood pilot only have a hunger rating.. and then on ssecond day also the eating disorder
expTaskOrders = {
    'HRV': {"o1": ['ratehunger'],
            "o2": ['ratehunger']}
}

day1file = _thisDir + '/data/' + expId + '/' + expId + '_subject_worker_ids_day1.csv'
if not os.path.exists(day1file):  #  day 1  - repeat food rating
    repeatFoodRating = {'HRV': True}
else:                             #  day 2  - repeat food rating
    repeatFoodRating = {'HRV': False}


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
           # workerId = 'A27O7H19C0WQ7T'
            subjectId = get_subjectId(expId, workerId)
            if workerId_exists(expId, workerId) and (get_task_results_exists(subjectId, 'WTWCovidResults')):
                return render_template('return_hit.html')
            elif not workerId_exists(expId, workerId):
                store_subject_info(expId, workerId, expTasksToComplete, assignmentId, hitId, turkSubmitTo)
        elif 'assignmentId' in request.args and request.args.get('assignmentId') == 'ASSIGNMENT_ID_NOT_AVAILABLE':
            # worker previewing HIT
            workerId = 'testWorker' + str(random.randint(1000, 10000))
           # workerId = 'A27O7H19C0WQ7T'
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
#            workerId = 'A27O7H19C0WQ7T'
            assignmentId = 'testAssignment' + str(random.randint(10000, 100000))
            hitId = 'testHIT' + str(random.randint(10000, 100000))
            turkSubmitTo = 'www.calkins.psych.columbia.edu'
            live = False
            store_subject_info(expId, workerId, expTasksToComplete, assignmentId, hitId, turkSubmitTo)
            return redirect(
                url_for('.ratehunger', ratingOrder=1, num=2, expId=expId, workerId=workerId, assignmentId=assignmentId,
                        hitId=hitId,
                        turkSubmitTo=turkSubmitTo, live=live, order=order))


"""
Study information
"""
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
        return redirect(
            url_for('.last_meal', order=order, expId=expId, workerId=workerId, assignmentId=assignmentId,
                    hitId=hitId,
                    turkSubmitTo=turkSubmitTo, live=live))
    else:
        return redirect(url_for('unauthorized_error'))

"""
QUESTIONNAIRES
"""

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

            day1file = _thisDir + '/data/' + expId + '/' + expId + '_subject_worker_ids_day1.csv'
            if not os.path.exists(day1file): # if this the first day - do all te Qs
                return redirect(url_for('.IEQ', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId,
                        turkSubmitTo=turkSubmitTo, live=live, order=order))
            else: # if it's the second day. skip the long questionnaire sand just do the demo as a backup for matching subjet IDs
                return redirect(
                    url_for('.thank_you', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId,
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

            return redirect(url_for('.AEBQ', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId,
                                    turkSubmitTo=turkSubmitTo, live=live, order=order))
    return redirect(url_for('page_not_found'))


"""adult eating behavior"""

@tasks.route("/AEBQ", methods=["GET", "POST"])
def AEBQ():
    name = "AEBQ"
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
        subjectId = get_subjectId(expId, workerId)
        info = get_AEBQ()
        if request.method == "GET":
            options = info[0][list(info[0].keys())[0]]
            widthPercent = 70.0 / len(options)
            return render_template('dmstudies/AEBQ.html', info=info,
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
            add_subfile_worker_notes(expId, subjectId, 'completedAEBQuestionnaire', True)
            results_to_csv(expId, subjectId, filePath, 'AEBQuestionnaireResults.csv', q_and_a, {})

            return redirect(url_for('.IPAQ', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId,
                                    turkSubmitTo=turkSubmitTo, live=live, order=order))
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
                url_for('.thankyou', expId=expId, workerId=workerId, assignmentId=assignmentId,
                        hitId=hitId, turkSubmitTo=turkSubmitTo, live=live, order=order))
    return redirect(url_for('page_not_found'))

@tasks.route("/thankyou/<order>", methods=["GET", "POST"])
def thankyou(order):
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
    if request.method == "GET" and containsAllMTurkArgs:
           return render_template('dmstudies/thankyou.html')
    elif containsAllMTurkArgs:  # in request.method == "POST"
        return render_template('dmstudies/thankyou.html')
    else:
        return redirect(url_for('unauthorized_error'))

