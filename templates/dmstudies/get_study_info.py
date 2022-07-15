import pandas as pd
import numpy as np
import os
import sys

_thisDir = os.path.dirname(os.path.abspath(__file__)) #.decode(sys.getfilesystemencoding())
_parentDir = os.path.abspath(os.path.join(_thisDir, os.pardir))
dataDir = _parentDir + '/data/'
sys.path.insert(0, os.path.join(_parentDir))

from manage_subject_info import *

"""
Get total about subject indicated they were willing to pay for questions
Returns amount in cents
"""
def get_wtp_pay_amount(expId, subjectId):
    subDir = os.path.join(dataDir, expId, subjectId)
    totalAmount = 0
    if os.path.exists(os.path.join(subDir, subjectId+'_WillingnessToPayResults.csv')):
        df = pd.read_csv(os.path.join(subDir, subjectId+'_WillingnessToPayResults.csv'))
        payTrialAmounts = df.loc[df['C_SWK'] == 'W','C_Pay'].values
        totalAmount = np.sum(payTrialAmounts)
    return totalAmount

expId = 'KangaAI'
subdirs = os.listdir(os.path.join(dataDir,expId))
subdirs.sort()

def show_study_data():
    df = pd.DataFrame()
    for sub in subdirs:
        subinfopath = os.path.join(dataDir,expId,sub,sub+'_SubjectNotes.csv')
        if os.path.exists(subinfopath):
            subdf = pd.read_csv(subinfopath)
            payAmount = get_wtp_pay_amount(expId, sub)
            subdf['WTP_pay_amount_in_cents'] = payAmount
            bonusAmount = 200 - payAmount # in cents
            bonusAmount = bonusAmount / 100.0
            bonusAmount = round(bonusAmount, 2) # converted to dollars
            subdf['bonusAmount'] = bonusAmount
            workerId = get_workerId(expId, sub)
            assignmentId = get_assignmentId(expId, sub)
            subdf['workerId'] = workerId
            subdf['assignmentId'] = assignmentId
            df = pd.concat([df, subdf])

    print(df.columns)
    print(df.describe())
    columns = ['completedAddQ', 'completedDemoQ', 'completedQuestionnaire1',
           'completedQuestionnaire2', 'completedQuestionnaire3',
           'completedQuestionnaire4', 'completedQuestionnaire5',
           'completedQuestionnaire6', 'completedRatingsTask',
           'retookComprehensionTest', 'retookWTPComprehensionTest',
           'retookWTWComprehensionTest', 'subjectId', 'workerId','assignmentId']

    """
    columns = ['completedAddQ', 'completedRatingsTask',
           'completedWTWTask', 'completedWTPTask', 'payAmount', 'bonusAmount', 'subjectId']
    """

    columns = ['completedAddQ', 'completedRatingsTask',
           'WTP_pay_amount_in_cents', 'bonusAmount','subjectId', 'workerId','assignmentId']

    df = df[columns]
    print(df.tail(50))
    return df

show_study_data()
