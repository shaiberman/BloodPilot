console.log('loaded page_interaction_tracker.js');
/*
This records changes in visibility and focus (whether or not the page is active)
allTrials and currTrialN should be defined in the main task script
visibilitychange event doesn't seem to triggered when task is run in MTurk iframe object
*/

document.addEventListener("visibilitychange", function() {
	if (typeof(allTrials[currTrialN]['trialEvents']) == 'undefined') {
		allTrials[currTrialN]['trialEvents'] = [];
	}
	allTrials[currTrialN]['trialEvents'].push({'event':'visibilitychange','details':document.visibilityState,'performance time':performance.now(),'date time':Date.now()});
});

window.onblur = function() {
	if (typeof(allTrials[currTrialN]['trialEvents']) == 'undefined') {
		allTrials[currTrialN]['trialEvents'] = [];
	}
	allTrials[currTrialN]['trialEvents'].push({'event':'onblur','details':'out of focus','performance time':performance.now(),'date time':Date.now()});
};

window.onfocus = function() {
	if (typeof(allTrials[currTrialN]['trialEvents']) == 'undefined') {
		allTrials[currTrialN]['trialEvents'] = [];
	}
	allTrials[currTrialN]['trialEvents'].push({'event':'onfocus','details':'in focus','performance time':performance.now(),'date time':Date.now()});
};
