from flask import Flask, render_template, request
from flask import redirect, url_for
from manage_subject_info import *
from mturk_utils import *
import urllib

"""
Import blueprints
"""
from dmstudies.tasks import tasks
from dmstudies.instructions import instructions

_thisDir = os.path.dirname(os.path.abspath(__file__))#.decode(sys.getfilesystemencoding())

app = Flask(__name__)

"""
Register blueprints
"""
# Learning under threat
app.register_blueprint(instructions)
app.register_blueprint(tasks)

@app.route("/thankyou", methods = ["GET"])
def thankyou():
    if 'assignmentId' in request.args:
        assignmentId = request.args.get('assignmentId')
        live = request.args.get('live')
        live = live == "True"
        return render_template('thankyou.html', assignmentId=assignmentId, live=live)
    else:
        return redirect(url_for('unauthorized_error'))

@app.route("/feedback/<expId>", methods=["GET","POST"])
def feedback(expId):
    if 'taskToComplete' in request.args:
        taskToComplete = request.args.get('taskToComplete')
    else:
        taskToComplete = None
    if contains_necessary_args(request.args):
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
        if request.method == "GET":
            return render_template('feedback.html')
        else:
            feedback = request.form["feedback"]
            store_feedback(expId, workerId, feedback)
            return redirect(url_for('show_completion_code', taskToComplete=taskToComplete, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
    else:
        return redirect(url_for('unauthorized_error'))

@app.route("/route_to_site/<expId>/<newRoute>", methods = ["GET", "POST"])
def route_to_site(expId,newRoute):
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)

        '''##################################'''
        # we will let the subject input their name for worker ID
        info = {}  # a dictionary with subject info
        info['Subject ID'] = 'P02'
        info['Fasting'] = 'sb'
        dlg = gui.DlgFromDict(info, sortKeys=False)  # (and from psychopy import gui at top of script)
        if not dlg.OK:
            print('something not ok')
            core.quit()
        workerId =  info['Subject ID']
        '''######################################'''

        subjectId = get_subjectId(expId, workerId)
    if 'error_message' in request.args:
        error_message = request.args.get('error_message')
    else:
        error_message = ''
    if 'url_prefix' in request.args:
        url_prefix = request.args.get('url_prefix')
    else:
        url_prefix = None
    if 'url_suffix' in request.args:
        url_suffix = request.args.get('url_suffix')
    else:
        url_suffix = None
    if 'taskToComplete' in request.args:
        taskToComplete = request.args.get('taskToComplete')
    else:
        taskToComplete = None
    argsd={}
    argsd['workerId']=workerId
    argsd['assignmentId']=assignmentId
    argsd['hitId']=hitId
    argsd['turkSubmitTo']=turkSubmitTo
    argsd['live']=live
    args='?'+urllib.urlencode(argsd)

    if url_prefix == None:
        HIT_description_path=_thisDir+"/HIT_descriptions/"+expId+"_HIT_description.txt"
    else:
        HIT_description_path=_thisDir+"/HIT_descriptions/"+url_prefix+"_HIT_description.txt"
    if os.path.exists(HIT_description_path):
        f = open(HIT_description_path,"r")
        HIT_description = f.read()
    else:
        HIT_description=''

    if url_prefix == None:
        link=os.path.join(request.url_root,expId)
    else:
        link=os.path.join(request.url_root,url_prefix,expId)

    if url_suffix != None:
        link=os.path.join(link,url_suffix)

    link=os.path.join(link,newRoute+args)

    if request.method == "GET" and containsAllMTurkArgs:
        completion_code = get_worker_notes(expId, subjectId, 'completionCode')
        if type(completion_code) != str:
            completion_code = get_completion_code()
            add_worker_notes(expId, workerId, 'completionCode', completion_code)
        return render_template('route_to_site.html',HIT_description=HIT_description, link=link, error_message=error_message)
    elif containsAllMTurkArgs:
        error_message='Incorrect completion code'
        completion_code = request.form['completion_code']
        subjectId = get_subjectId(expId, workerId)
        completedTask1 = completed_task(expId, workerId, taskToComplete)
        completedTask2 = get_subfile_worker_notes(expId, subjectId, taskToComplete)
        if taskToComplete==None or (taskToComplete!=None and (completedTask1 or completedTask2)):
            completion_code=completion_code.strip()
            if completion_code == get_worker_notes(expId, subjectId, 'completionCode'): # check if matches
                set_completed_task(expId,workerId,'submittedCode',True)
                return redirect(url_for('thankyou', expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
            return redirect(url_for('route_to_site', error_message=error_message, newRoute=newRoute, url_prefix=url_prefix, url_suffix=url_suffix, taskToComplete=taskToComplete, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
        error_message='Please complete the study before submitting the completion code.'
        return redirect(url_for('route_to_site', error_message=error_message, newRoute=newRoute, url_prefix=url_prefix, url_suffix=url_suffix, taskToComplete=taskToComplete, expId=expId, workerId=workerId, assignmentId=assignmentId, hitId=hitId, turkSubmitTo=turkSubmitTo, live=live))
    else:
        return redirect(url_for('unauthorized_error'))

@app.route("/show_completion_code/<expId>", methods = ["GET"])
def show_completion_code(expId):
    if 'taskToComplete' in request.args:
        taskToComplete = request.args.get('taskToComplete')
    else:
        taskToComplete = None
    containsAllMTurkArgs = contains_necessary_args(request.args)
    if containsAllMTurkArgs:
        [workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
    if containsAllMTurkArgs:
        if taskToComplete==None or (taskToComplete!=None and completed_task(expId, workerId, taskToComplete) == True):
            subjectId = get_subjectId(expId, workerId)
            completion_code = get_worker_notes(expId, subjectId, 'completionCode')
            return render_template('show_completion_code.html',code=completion_code)
        else:
            return render_template('completion_error.html')
    else:
        return redirect(url_for('unauthorized_error'))

@app.route("/unauthorized_error", methods = ["GET"])
def unauthorized_error():
    return render_template('unauthorized_error.html')

@app.route("/accept_hit", methods = ["GET"])
def accept_hit():
    return render_template('accept_hit.html')

@app.route("/page_not_found", methods = ["GET"])
def page_not_found():
    return render_template('404.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.debug = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    #app.run(host = '0.0.0.0', port = 8000)#app.run(host ='127.0.0.1', port = 5000) ## app.run(host = '0.0.0.0', port = 8000)#
    app.run(host = 'http://foodchoiceexp.pythonanywhere.com/')
