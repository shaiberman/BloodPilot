from get_study_info import *
import os
import sys

n1 = 0
n2 = 70

_thisDir = os.path.dirname(os.path.abspath(__file__)) #.decode(sys.getfilesystemencoding())
_parentDir = os.path.abspath(os.path.join(_thisDir, os.pardir))
dataDir = 'C:/Users/shaib/Documents/hunger/Mturk2/data'
sys.path.insert(0, os.path.join(_parentDir))

from manage_subject_info import *
from mturk_utils import *

expId = 'HRV'

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
sandbox=False

if testMode == None:
    print('usage: python pay_wtp_bonuses.py <testMode:True/False> <sandbox/live>')
    sys.exit(-1)

def pay_wtp_bonus(test, sandbox):
    df = show_study_data()
    # NEW IN 2021
    # save bonus payment info in csv
    print(_thisDir)
    df.to_csv(os.path.join(_thisDir,"tmp_bonuses.csv"))
    """
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
    """
pay_wtp_bonus(testMode, sandbox)
