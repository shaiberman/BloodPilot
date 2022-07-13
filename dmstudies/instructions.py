from flask import Flask, render_template, request, Blueprint
from flask import redirect, url_for

from dmstudies.tasks import expTaskOrders
from dmstudies.utils import * # this used to be "from utils import *"
from manage_subject_info import *

_thisDir = os.path.dirname(os.path.abspath(__file__)) #.decode(sys.getfilesystemencoding())
_thisDir = os.path.abspath(os.path.join(_thisDir, os.pardir))

instructions = Blueprint('instructions', __name__, url_prefix='/HRV')

expId = 'HRV'

"""
Auction Instructions
"""
@instructions.route("/foodrating_instructions/<order>", methods = ["GET","POST"])
def foodrating_instructions(order):
    name = 'foodrating'
    assignmentId = None
    if 'assignmentId' in request.args:
        assignmentId = request.args.get('assignmentId')
    if contains_necessary_args(request.args) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
        if assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE': # preview -> go to next demo
            nextTask = get_next_task(name, expTaskOrders[expId])
            return redirect(url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live, order=order))
        if workerId_exists(expId, workerId) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
            if request.method == "GET":
                stimuli = get_stimuli(foodStimFolder,'','.bmp')
                nStim = len(stimuli)
                return render_template('dmstudies/foodrating_instructions.html', nStim=nStim)
            else:
                if request.form['submit'] == 'Continue':
                    if assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE': # if in preview
                        nextTask = get_next_task(name, expTaskOrders[expId])
                        return redirect(url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live, order=order))
                    else:
                        return redirect(url_for('tasks.foodrating', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live, order=order))
                else:
                    return redirect(url_for('tasks.foodrating', demo='TRUE', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live, order=order))
        else:
            return redirect(url_for('unauthorized_error'))
    else:
        return redirect(url_for('unauthorized_error'))

"""
Auction Demo Instructions
"""
@instructions.route("/foodrating_demo_instructions/<order>", methods = ["GET","POST"])
def foodrating_demo_instructions(order):
    assignmentId = None

    if 'assignmentId' in request.args:
        assignmentId = request.args.get('assignmentId')

    if contains_necessary_args(request.args) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

        if workerId_exists(expId, workerId) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
            if request.method == "GET":
                stimuli = get_stimuli(foodStimFolder,'','.bmp')
                nStim = len(stimuli)
                return render_template('dmstudies/foodrating_demo_instructions.html', nStim = nStim)
            else:
                return redirect(url_for('tasks.foodrating', demo='TRUE', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live, order=order))
        else:
            return redirect(url_for('unauthorized_error'))
    else:
        return redirect(url_for('unauthorized_error'))

"""
Auction Repeat Instructions
"""
@instructions.route("/foodrating_repeat_instructions/<order>", methods = ["GET","POST"])
def foodrating_repeat_instructions(order):
    assignmentId = None
    if 'assignmentId' in request.args:
        assignmentId = request.args.get('assignmentId')
    if contains_necessary_args(request.args) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

        if workerId_exists(expId, workerId) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
            if request.method == "GET":
                stimuli = get_stimuli(foodStimFolder,'','.bmp')
                nStim = len(stimuli)
                return render_template('dmstudies/foodrating_repeat_instructions.html', nStim=nStim)
            else:
                return redirect(url_for('tasks.foodrating', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live, order=order))
        else:
            return redirect(url_for('unauthorized_error'))
    else:
        return redirect(url_for('unauthorized_error'))

"""
Choice Task Instructions
"""
@instructions.route("/foodchoicetask_instructions/<order>", methods = ["GET","POST"])
def foodchoicetask_instructions(order):
    taskEndpoint = 'tasks.foodchoicetask'
    taskHTML = 'dmstudies/choicetask_instructions.html'
    demo = False
    return route_for_instructions(expId, taskHTML, taskEndpoint, demo, request, order=order)


"""
Choice Task Demo Instructions
"""
@instructions.route("/foodchoicetask_demo_instructions/<order>", methods = ["GET","POST"])
def foodchoicetask_demo_instructions(order):
    taskEndpoint = 'tasks.foodchoicetask'
    taskHTML = 'dmstudies/choicetask_demo_instructions.html'
    demo = True
    return route_for_instructions(expId, taskHTML, taskEndpoint, demo, request, order=order)


"""
WILLINGNESS TO PAY TASK
"""

@instructions.route("/full_instructions_wtp/<order>", methods=["GET", "POST"])
def full_instructions_wtp(order):
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
    if request.method == "GET" and containsAllMTurkArgs:
        subjectId = get_subjectId(expId, workerId)
        temp = 'full_instructions_wtp_frst'
        return render_template('dmstudies/%s.html'%(temp))
    elif containsAllMTurkArgs:
        return redirect(
            url_for('.comprehension_test_wtp', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId,
                    turkSubmitTo=turkSubmitTo, live=live, order=order))
    else:
        return redirect(url_for('unauthorized_error'))


@instructions.route("/comprehension_test_wtp/<order>", methods=["GET", "POST"])
def comprehension_test_wtp(order):
    info = get_comprehensiontestinfo_WTP()
    instructions = 'You will now be asked to answer some questions to ensure that you understood the ' \
                   'instructions.<br>Please answer to the best of your ability. '
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
    if request.method == "GET" and containsAllMTurkArgs:
        options = info[0][list(info[0].keys())[0]]
        widthPercent = 10.0 / len(options)
        return render_template('dmstudies/comprehension_test_wtp.html', info=info, instructions=instructions,
                               widthPercent=widthPercent)
    elif containsAllMTurkArgs:  # in request.method == "POST"
        subjectId = get_subjectId(expId, workerId)
        if request.form['a1'] == 'True' and request.form['a2'] == 'True' and request.form['a3'] == 'True':
            return redirect(
                url_for('tasks.kanga_task_wtp', demo='True', expId=expId, workerId=workerId, assignmentId=assignmentId,
                        hitId=hitId, turkSubmitTo=turkSubmitTo, live=live, order=order))
        else:
            nRetakes = get_subfile_worker_notes(expId, subjectId, 'retookWTPComprehensionTest')
            if nRetakes == None or np.isnan(nRetakes):
                nRetakes = 0
            else:
                nRetakes = int(nRetakes)
            nRetakes += 1
            add_subfile_worker_notes(expId, subjectId, 'retookWTPComprehensionTest', nRetakes)
            return redirect(url_for('.full_instructions_wtp', expId=expId, workerId=workerId, assignmentId=assignmentId,
                                    hitId=hitId, turkSubmitTo=turkSubmitTo, live=live, order=order))
    else:
        return redirect(url_for('unauthorized_error'))


@instructions.route("/main_task_instructions_wtp/<order>", methods=["GET", "POST"])
def main_task_instructions_wtp(order):
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
    if request.method == "GET" and containsAllMTurkArgs:
        return render_template('dmstudies/main_task_instructions_wtp.html')
    elif containsAllMTurkArgs:
        return redirect(
            url_for('tasks.kanga_task_wtp', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId,
                    turkSubmitTo=turkSubmitTo, live=live, order=order))
    else:
        return redirect(url_for('unauthorized_error'))

"""
RATING TASK
"""

@instructions.route("/rating_task_instructions/<order>", methods=["GET", "POST"])
def rating_task_instructions(order):
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
    if request.method == "GET" and containsAllMTurkArgs:
        return render_template('dmstudies/rating_task_instructions.html')
    elif containsAllMTurkArgs:
        return redirect(url_for('tasks.Qrating_task', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId,
                                turkSubmitTo=turkSubmitTo, live=live, order=order))
    else:
        return redirect(url_for('unauthorized_error'))

"""
Renders HTML for instructions page or redirects to task based on arguments in request 
Params:
    expId (string): name of experiment
    taskHTML (string): name of HTML file for instructions page
    taskEndpoint (string): name of task route to redirect to
    demo (boolean): true if this instructions page is for a demo of the task
    request (Flask request object): checked to determine what should be returned

"""
def route_for_instructions(expId, taskHTML, taskEndpoint, demo, request, order):
    assignmentId = None
    if 'assignmentId' in request.args:
        assignmentId = request.args.get('assignmentId')
    if contains_necessary_args(request.args) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
        if workerId_exists(expId, workerId) or assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE':
            if request.method == "GET":
                if assignmentId == 'ASSIGNMENT_ID_NOT_AVAILABLE' and demo == False: # preview -> go to next demo
                    name = taskEndpoint[taskEndpoint.find('.')+1:]
                    nextTask = get_next_task(name, expTaskOrders[expId])
                    return redirect(url_for(nextTask, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live, order=order))
                else:
                    return render_template(taskHTML, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live)
            else:
                if 'submit' in request.form.keys() and request.form['submit'] == 'Continue':
                    return redirect(url_for(taskEndpoint, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live, order=order))
                elif 'submit' in request.form.keys() and request.form['submit'] == 'Repeat Demo':
                    return redirect(url_for(taskEndpoint, demo='TRUE', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live, order=order))
                else:
                    if demo:
                        demoValue = 'TRUE'
                    else:
                        demoValue = 'FALSE'
                    return redirect(url_for(taskEndpoint, demo=demoValue, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live, order=order))
        else:
            return redirect(url_for('unauthorized_error'))
    else:
        return redirect(url_for('unauthorized_error'))

@instructions.route("/rdcolor_instructions/<order>", methods=["GET", "POST"])
def rdcolor_instructions(order):
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
    if request.method == "GET" and containsAllMTurkArgs:
        return render_template('dmstudies/rdcolor_instructions.html')
    elif containsAllMTurkArgs:
        return redirect(
            url_for('tasks.rdcolor_task', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId,
                    turkSubmitTo=turkSubmitTo, live=live, order=order))
    else:
        return redirect(url_for('unauthorized_error'))

@instructions.route("/questionnaire_instructions/<order>", methods=["GET", "POST"])
def questionnaire_instructions(order):
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
    if request.method == "GET" and containsAllMTurkArgs:
        return render_template('dmstudies/questionnaire_instructions.html')
    elif containsAllMTurkArgs:
        return redirect(url_for('tasks.ratehunger', ratingOrder=1, num=2, expId=expId, workerId=workerId, assignmentId=assignmentId,
                hitId=hitId, turkSubmitTo=turkSubmitTo, live=live, order=order))
       # (url_for('tasks.general_questionnaire', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId,
       #                         turkSubmitTo=turkSubmitTo, live=live, order=order))
    else:
        return redirect(url_for('unauthorized_error'))


