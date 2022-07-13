
////////////////////////////////////////////////
// 0. Preliminaries
////////////////////////////////////////////////

// define state names as strings for output (make sure they correspond to states in jspsych-wl-vmr.js!)
var FPS = 60; // screen refresh rate, set to 60 by default but will be updated below according to actual frame rate


////////////////////////////////////////////////
// 1. Create structure for experiment
////////////////////////////////////////////////

/* MEASURE FRAME RATE */
var trial_check_fps= {
	type: 'wl-check-fps',
	frameN: 300, // check for 300 frames
	on_finish: function(data) {
		FPS = data.FPS_mode;
		if (FPS < 53 || FPS > 82) {
			exitExperiment('FPSexclude');
		} else {
			return FPS
		}
	},
};

////////////////////////////////////////////////
// 2. Push everything to timeline
////////////////////////////////////////////////

/* Create empty experiment timeline */
var timeline = [];
timeline.push(trial_check_fps);


jsPsych.init({timeline:timeline})

////////////////////////////////////////////////
// Extra functions
////////////////////////////////////////////////

/* EXIT EXPERIMENT */
function exitExperiment(exclReason) {
    document.getElementById("message").remove();
    document.getElementById("button").remove();

    var exitMessage = '<h3>Unfortunately, you do not qualify for this HIT.</h3>';

    if (exclReason === 'FPSexclude') {
        exitMessage +='<h3>Your screen refresh rate needs to be between 55-80 Hz.</h3><br><br>' +
        '<p>You are welcome to change your screen refresh rate (preferably to 60 Hz) and then try again.<p>' +
        '<p>Please also make sure to close all background programs that may slow down your browser.<p>' +
        '<p>If you would like to re-start the experiment, please clear your browser cache first!</p>' +
        '<p>If you do not wish to retry, please return this HIT now.</p>';
    }
    exitMessage += '<h3><br><br>We are sorry for the inconvenience! You can close this browser window now.</h3>';
    jsPsych.endExperiment(exitMessage);
}
