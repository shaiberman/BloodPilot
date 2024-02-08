import pandas as pd
import csv
import os
import sys
import datetime

# Methods to manage EXPID_subject_assignment_info.csv and EXPID_subject_worker_ids.csv inside experiment folder

_thisDir = os.path.dirname(os.path.abspath(__file__))# .decode(sys.getfilesystemencoding())
os.chdir(_thisDir)

def store_subject_info(expId, workerId, tasksToComplete, assignmentId, hitId, turkSubmitTo):
    if not os.path.exists(_thisDir + '/data/' + expId):
        os.makedirs(_thisDir + '/data/' + expId)
    # store subjectId and other relevant subject info, except workerId
    csvLocation = _thisDir + '/data/' + expId +'/' + expId + '_subject_assignment_info.csv'
    workerIDfile =  _thisDir + '/data/' + expId +'/' + expId + '_subject_worker_ids.csv'

    # first subject
    if not os.path.exists(csvLocation):
        if not os.path.exists(workerIDfile):
            newSubjectId = expId + "_%04d" % (1,)

        currentTime = datetime.datetime.now()
        currentTime = currentTime.strftime("%Y-%m-%d %H:%M:%S")
        newSubject = {'subjectId':newSubjectId, 'assignmentId':assignmentId, 'hitId':hitId, 'turkSubmitTo':turkSubmitTo, 'timestamp':currentTime}
        newSubject.update(tasksToComplete)
        new_df = pd.DataFrame(data=newSubject, index=[0])
    else:
        day = is_oldsubjectID(workerIDfile, workerId)
        df = pd.read_csv(csvLocation)
        df2 = pd.read_csv(workerIDfile)
        nSubjects = len(df2.index)
        if day == 1:
            newSubjectId = expId + "_%04d" % (nSubjects+1,)
        else:
            newSubjectId = workerId
        currentTime = datetime.datetime.now()
        currentTime = currentTime.strftime("%Y-%m-%d %H:%M:%S")
        newSubject = {'subjectId':newSubjectId, 'assignmentId':assignmentId, 'hitId':hitId, 'turkSubmitTo':turkSubmitTo, 'timestamp':currentTime}
        newSubject.update(tasksToComplete)
        df2 = pd.DataFrame(data=newSubject, index=[0])
        new_df = pd.concat([df,df2], axis=0)
    new_df.to_csv(csvLocation,index=False)

    # store subjectId and workerId
    csvLocation = _thisDir + '/data/' + expId +'/' + expId + '_subject_worker_ids.csv'
    newSubject = {'expId':expId,'subID':newSubjectId, 'workerId':workerId, 'timestamp':currentTime}
    if not os.path.exists(csvLocation):
        new_df = pd.DataFrame(data=newSubject, index=[0])
    else:
        df = pd.read_csv(csvLocation)
        df2 = pd.DataFrame(data=newSubject, index=[0])
        new_df = pd.concat([df,df2], axis=0)
    new_df.to_csv(csvLocation,index=False)

    return day

def is_oldsubjectID(workerIDdayfile, workerId):
    df = pd.read_csv(workerIDdayfile)
    isitthere = (df['workerId']==workerId).any()
    print(isitthere)
    if isitthere:
        day = 2
    else:
        day =1
    return day


def get_timestamp(expId, workerId):
    csvLocation = _thisDir + '/data/' + expId +'/' + expId + '_subject_worker_ids.csv'
    if os.path.exists(csvLocation):
        df = pd.read_csv(csvLocation)
        timestamps = df.loc[df['workerId'] == workerId]['timestamp'].values
        if len(timestamps) > 0:
            return timestamps[0]
        else:
            return False

# should assume subject did not participate before
def get_subjectId(expId, workerId):
    csvLocation = _thisDir + '/data/' + expId +'/' + expId + '_subject_assignment_info.csv'
    csvWorkerIds = _thisDir + '/data/' + expId +'/' + expId + '_subject_worker_ids.csv'
    if os.path.exists(csvLocation):
        df = pd.read_csv(csvLocation)
        timestamp = get_timestamp(expId, workerId)
        if timestamp != False:
            subjectIds = df.loc[df['timestamp'] == timestamp]['subjectId'].values
            if len(subjectIds) > 0:
                if len(subjectIds) > 1: # same timestamp
                    df2 = pd.read_csv(csvWorkerIds)
                    workerIds = df2.loc[df2['timestamp'] == timestamp]['workerId'].values
                    i = workerIds.tolist().index(workerId)
                    return subjectIds[i]
                return subjectIds[0]
            else:
                return False
        else:
            return False
    else:
        return False

def get_workerId(expId, subjectId):
    csvWorkerIds = _thisDir + '/data/' + expId +'/' + expId + '_subject_worker_ids.csv'
    csvSubjectIds = _thisDir + '/data/' + expId +'/' + expId + '_subject_assignment_info.csv'
    if os.path.exists(csvSubjectIds):
        df = pd.read_csv(csvSubjectIds)
        timestamps = df.loc[df['subjectId'] == subjectId]['timestamp'].values
        if len(timestamps) > 0:
            timestamp = timestamps[0]
            if os.path.exists(csvWorkerIds):
                df2 = pd.read_csv(csvWorkerIds)
                workerIds = df2.loc[df2['timestamp'] == timestamp]['workerId'].values
                if len(workerIds) > 0:
                    if len(workerIds) > 1: # same timestamp
                        df2 = pd.read_csv(csvSubjectIds)
                        subjectIds = df2.loc[df2['timestamp'] == timestamp]['subjectId'].values
                        i = subjectIds.tolist().index(subjectId)
                        return workerIds[i]
                    return workerIds[0]
                else:
                    return False
        else:
            return False


def get_assignmentId(expId, subjectId):
    csvLocation = _thisDir + '/data/' + expId +'/' + expId + '_subject_assignment_info.csv'
    if os.path.exists(csvLocation):
        df = pd.read_csv(csvLocation)
        assignmentIds = df.loc[df['subjectId'] == subjectId]['assignmentId'].values
        if len(assignmentIds) > 0:
            assignmentId = assignmentIds[0]
            return assignmentId
        else:
            return False # assignmentId doesn't exist
    else:
        return False

def get_turkSubmitTo(expId, subjectId):
    csvLocation = _thisDir + '/data/' + expId +'/' + expId + '_subject_assignment_info.csv'
    if os.path.exists(csvLocation):
        df = pd.read_csv(csvLocation)
        turkSubmitTo = df.loc[df['subjectId'] == subjectId]['turkSubmitTo'].values
        if len(turkSubmitTo) > 0:
            return turkSubmitTo[0]
        else:
            return False # turkSubmitTo doesn't exist
    else:
        return False

def get_hitId(expId, subjectId):
    csvLocation = _thisDir + '/data/' + expId +'/' + expId + '_subject_assignment_info.csv'
    if os.path.exists(csvLocation):
        df = pd.read_csv(csvLocation)
        turkSubmitTo = df.loc[df['subjectId'] == subjectId]['hitId'].values
        if len(turkSubmitTo) > 0:
            return turkSubmitTo[0]
        else:
            return False # turkSubmitTo doesn't exist
    else:
        return False

def workerId_exists(expId, workerId):
    csvWorkerIds = _thisDir + '/data/' + expId +'/' + expId + '_subject_worker_ids.csv'
    if os.path.exists(csvWorkerIds):
        df = pd.read_csv(csvWorkerIds)
        if workerId in df['workerId'].values:
            return True
    return False

def completed_task(expId, workerId, task):
    csvLocation = _thisDir + '/data/' + expId +'/' + expId + '_subject_assignment_info.csv'
    if os.path.exists(csvLocation):
        df = pd.read_csv(csvLocation)
        if workerId_exists(expId, workerId) and task in df.columns:
            subjectId = get_subjectId(expId, workerId)
            completed = df.loc[df['subjectId'] == subjectId][task].values[0]
            if completed == True:
                return True
            else:
                return False
        else:
            return False
    else:
        return False

def completed_task_subject(expId, subjectId, task):
    csvLocation = _thisDir + '/data/' + expId +'/' + expId + '_subject_assignment_info.csv'
    if os.path.exists(csvLocation):
        df = pd.read_csv(csvLocation)
        if task in df.columns:
            completed = df.loc[df['subjectId'] == subjectId][task].values[0]
            if completed == True:
                return True
            else:
                return False
        else:
            return False
    else:
        return False

def set_completed_task(expId, workerId, task, boole):
    csvLocation = _thisDir + '/data/' + expId +'/' + expId + '_subject_assignment_info.csv'
    if os.path.exists(csvLocation):
        df = pd.read_csv(csvLocation)
        if workerId_exists(expId, workerId):
            subjectId = get_subjectId(expId, workerId)
            idx = df[df['subjectId'] == subjectId].index[0]
            df.loc[idx, task] = boole
            df.to_csv(csvLocation,index=False)

"""
name: name of note
"""
def get_worker_notes(expId, subjectId, name):
    csvLocation = _thisDir + '/data/' + expId +'/' + expId + '_subject_assignment_info.csv'
    if os.path.exists(csvLocation):
        df = pd.read_csv(csvLocation)
        if name in df.columns:
            #print df.loc[df[subjectId] == subjectId][name].values
            values = df.loc[df['subjectId'] == subjectId][name].values
            if len(values) > 0:
                return values[0]
    return None

"""
name: name of note
value: value of note with the given name
"""
def add_worker_notes(expId, workerId, name, value):
    csvLocation = _thisDir + '/data/' + expId +'/' + expId + '_subject_assignment_info.csv'
    if os.path.exists(csvLocation):
        df = pd.read_csv(csvLocation)
        if workerId_exists(expId, workerId):
            subjectId = get_subjectId(expId, workerId)
            idx = df[df['subjectId'] == subjectId].index[0]
            df.loc[idx, name] = value
            df.to_csv(csvLocation,index=False)

def store_feedback(expId, workerId, feedback):
    csvLocation = _thisDir + '/data/' + expId +'/' + expId + '_subject_feedback.csv'
    if workerId_exists(expId, workerId):
        subjectId = get_subjectId(expId, workerId)
        newData = {'expId':expId, 'subjectId':subjectId, 'feedback':feedback}
        if not os.path.exists(csvLocation):
            new_df = pd.DataFrame(data=newData, index=[0])
        else:
            df = pd.read_csv(csvLocation)
            df2 = pd.DataFrame(data=newData, index=[0])
            new_df = pd.concat([df,df2], axis=0)
        new_df.to_csv(csvLocation,index=False)

"""
Get information from csv in individual subject folders
name: name of note
"""
def get_subfile_worker_notes(expId, subjectId, name):
    subDir = os.path.join(_thisDir, 'data', expId, subjectId)
    csvLocation = os.path.join(subDir, subjectId+'_SubjectNotes.csv')
    if os.path.exists(csvLocation):
        df = pd.read_csv(csvLocation)
        if name in df.columns:
            #print df.loc[df[subjectId] == subjectId][name].values
            values = df.loc[df['subjectId'] == subjectId][name].values
            if len(values) > 0:
                return values[0]
    return False


"""
Add information to csv in individual subject folders
name: name of note
value: value of note with the given name
"""
def add_subfile_worker_notes(expId, subjectId, name, value):
    subDir = os.path.join(_thisDir, 'data', expId, subjectId)
    if not os.path.exists(subDir):
        os.mkdir(subDir)
    csvLocation = os.path.join(subDir, subjectId+'_SubjectNotes.csv')
    df = pd.DataFrame()
    if os.path.exists(csvLocation):
        df = pd.read_csv(csvLocation)

    df = df.to_dict('list')
    df['subjectId'] = [subjectId]
    df[name] = [str(value)]
    df = pd.DataFrame.from_dict(df)
    df.to_csv(csvLocation,index=False)