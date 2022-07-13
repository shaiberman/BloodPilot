import random
import string
import urllib
import os

def convert_request_to_mturk_args(request):
	[workerId, assignmentId, hitId, turkSubmitTo, live] = get_necessary_args(request.args)
	mturk_args={}
	mturk_args['workerId'] = workerId
	mturk_args['assignmentId'] = assignmentId
	mturk_args['hitId'] = hitId
	mturk_args['turkSubmitTo'] = turkSubmitTo
	mturk_args['live'] = live
	return mturk_args

def get_url(mturk_args,prefix,expId,route):
	arg_keys = ['workerId','assignmentId','hitId','turkSubmitTo','live']
	for key in arg_keys:
		if key not in mturk_args.keys():
			print("Missing key in mturk_args:", key)
			raise KeyError
	args='?'+urllib.urlencode(mturk_args)
	if prefix == None:
		link=os.path.join('https://calkins.psych.columbia.edu',expId,route+args)
	else:
		link=os.path.join('https://calkins.psych.columbia.edu',prefix,expId,route+args)
	return link

"""
Checks request.args has assignmentId, hitId, turkSubmitTo, workerId, live - all but live is passed by MTurk
live refers to whether HIT is live or in sandbox
"""
def contains_necessary_args(args):
	if 'workerId' in args and 'assignmentId' in args and 'hitId' in args and 'turkSubmitTo' in args and 'live' in args:
		return True
	else:
		return False

"""
Retrieve necessary args: assignmentId, hitId, turkSubmitTo, workerId, live
"""
def get_necessary_args(args):
	workerId = args.get('workerId')
	assignmentId = args.get('assignmentId')
	hitId = args.get('hitId')
	turkSubmitTo = args.get('turkSubmitTo')
	live = args.get('live') == "True"
	return [workerId, assignmentId, hitId, turkSubmitTo, live]

def get_completion_code():
	# from https://pythontips.com/2013/07/28/generating-a-random-string/
	return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)])

