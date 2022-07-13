from get_study_info import *
import boto3
import os
import sys

n1 = 0
n2 = 100

_thisDir = os.path.dirname(os.path.abspath(__file__)).decode(sys.getfilesystemencoding())
_parentDir = os.path.abspath(os.path.join(_thisDir, os.pardir))
dataDir = _parentDir + '/data/'
sys.path.insert(0, os.path.join(_parentDir))

from manage_subject_info import *
from mturk_utils import *

expId = 'KangaAI'

if (len(sys.argv) < 3):
    print('usage: python pay_wtp_bonuses <testMode:True/False> <sandbox/live>')
    sys.exit(-1)

testMode = None
if sys.argv[1] == 'True':
    testMode = True
if sys.argv[1] == 'False':
    testMode = False
sendMemoryTest = False
sendBonus = False
if sys.argv[2] == 'live':
    client = boto3.client('mturk')
    sandbox = False
elif sys.argv[2] == 'sandbox':
    client = boto3.client('mturk', region_name='us-east-1',
                          endpoint_url='https://mturk-requester-sandbox.us-east-1.amazonaws.com')
    sandbox = True
if testMode == None:
    print('usage: python pay_wtp_bonuses.py <testMode:True/False> <sandbox/live>')
    sys.exit(-1)

def pay_wtp_bonus(test, sandbox):
    df = show_study_data()
    assignmentIds = df['assignmentId']
    df.set_index('assignmentId', inplace=True)
    for assignmentId in assignmentIds:
        response = {'BonusPayments':[]}
        try:
            response = client.list_bonus_payments(
                AssignmentId=assignmentId,
            )
            print(response)
        except:
            print('could not get list of bonus payments from',assignmentId)
        nBonuses = len(response['BonusPayments'])
        if nBonuses == 0:  # haven't paid any bonuses (double check!!)
            subjectId = df.loc[assignmentId, 'subjectId']
            if type(subjectId) != str:
                subjectId = subjectId[-1]
            subnum = int(subjectId[-4:])
            if subnum >= n1 and subnum <= n2:
                workerId = df.loc[assignmentId, 'workerId']
                if type(workerId) != str:
                    workerId = workerId[-1]
                bonusAmount = df.loc[assignmentId, 'bonusAmount']
                if not testMode:
                    if bonusAmount <= 2: # 2 dollars max
                        bonusAmount = str(bonusAmount)
                        try:
                            print "Paying bonus to", subjectId, workerId, assignmentId
                            # pay bonus
                            response = client.send_bonus(
                                WorkerId=workerId,
                                BonusAmount=bonusAmount,
                                AssignmentId=assignmentId,
                                Reason='Bonus payment based on responses in one task. Thank you for participating!',
                                UniqueRequestToken='WTP_'+workerId
                            )
                        except:
                            print "could not pay bonus to", subjectId, workerId
                    else:
                        print "Something funky!", subjectId, workerId
                else:
                    print "Would pay bonus to", subjectId, workerId, bonusAmount


pay_wtp_bonus(testMode, sandbox)
