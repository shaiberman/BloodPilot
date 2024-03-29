
////////////////////////////////////////////////
// 0. Preliminaries
////////////////////////////////////////////////

var expName = 'rdm_color';
var workerId = new URLSearchParams(window.location.search).get('workerId');
var uid;
var signInMetadata;
var confirmationCode;
var exitedFullScreen = false; // we check this on every trial
var blurEvent = false; // event occurs when task window out of focus
var warning = false; // warning if too many miss trials in a row
var pause = false;

// define state names as strings for output (make sure they correspond to states in jspsych-wl-vmr.js!)
var StateNames = ['MAPPING','FIXATE','DELAY','RDM_ON','RESPONSE_WAIT','FEEDBACK','FINISH'];
var FPS = 60; // screen refresh rate, set to 60 by default but will be updated below according to actual frame rate
var PPD = 40; // pixels per degree: set to 40 by default, but will be updated based on virt chin rest plugin
var viewDist = null; // viewing distance in inch, will be updated based on virt chin rest plugin

// Experimental parameters:
// set default task (in case no task decision is made - see below)
var task = '1D_color';
var resp_keys = ['U','I'];

// original-amx: var ColorCoherences = [50.0, 56.4, 62.5, 73.6, 87.9];//[50, 53.2, 56.4, 62.5, 73.6, 87.9];
var ColorCoherences = [50, 53.2, 56.4, 62.5, 73.6, 87.9];

// original-amx: var nReps = 8; // repetition of each color x coherence combination PER BLOCK = 5 (coh) * 2 (col) * 8 (rep) = 80 trials
var nReps = 9;
var nBlocks = 2; // 2 EXPERIMENTAL blocks of 80 trials each
var nBlockTrials = (ColorCoherences.length*2) * nReps; // how manhy trials per block?

// How many trials? This is just used to update progress bar correctly, otherwise doesn't matter much
var trials = {
  preExp: 12, // any 'trials' before actual experiment: FPS check, consent, fullscreen, calibration (2 pages), welcome, 2 x demo, demo-button, post-demo, postPractice, survey
  experiment: (ColorCoherences.length*2) * nReps * nBlocks // total number of experimental trials
}

// compute total number of trials and initialize counter (for progress bar)
var totTrials = Object.values(trials).reduce((a, b) => a + b); // sum over values in an object
//var MaxPractice = 10; // max # of practice trials to reach performance criterion

var BlockCount = 0;
var TrialCount = 0; // counts completed trials (used for progress bar)
var BlockTrialCount = 0;
var checkTrialCount = 0; // check how many misses in last 5 trials, reset counter if warning was shown, so it will wait for the next 5 trials again
var score = 0;

var instructionsMinTime = 5000;


////////////////////////////////////////////////
// 1. Create structure for experiment
////////////////////////////////////////////////

/* ENTER FULL SCREEN */
var screenmode = {
	type: 'fullscreen',
	message: '<h3>This experiment must be run in full-screen.</h3><br>',
	fullscreen_mode: true,
	delay_after: 200, // add little delay to make sure screen size is updated correctly
}


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



//-------------------------------------------//
//--------------- RDM TASK */----------------//
//-------------------------------------------//

/* TASK INSTRUCTIONS */
var trial_Instruction1 = {
	timeline: [{
		type: 'wl-html-keyboard-response',
		stimulus: function() { return '<h3 align=center>Please read the following instructions carefully.</h3><br>' +
			'<p class="instructions-text">'+
			'You will see some dots flickering on the screen. Your task is to judge whether the majority of dots is YELLOW or BLUE.<br><br>' +
			'&ndash; If you think more dots are <b>YELLOW</b>, press the <b>\'' + resp_keys[0] + '\'</b> key with your right index finger.<br>' +
			'&ndash; If you think more dots are <b>BLUE</b>, press the <b>\'' + resp_keys[1] + '\'</b> key with your right middle finger.<br><br>' +
			'Try to be as fast and accurate as possible.<br><br>' +
			'</p><br>'+
			'<p align=center>Press space bar to start with some guided practice.</p><br>';},
		choice_keys: [' '],
		choice_labels: ['Press space bar'],
		requireFullScreen: true,
		hideButtonDuration: instructionsMinTime,
	}],
	on_start: function() { $('body').css('cursor', 'none') }, // show cursor before button click
};

var trial_Instruction2 = {
	timeline: [{
		type: 'wl-html-keyboard-response',
		stimulus: function() { return '<h3 align=center>Remember:</h3><br>' +
			'<p class="instructions-text-block">'+
			'1. Press <b>\'' + resp_keys[0] + '\'</b> for YELLOW and <b>\'' + resp_keys[1] + '\'</b> for BLUE using your right index/middle finger.<br>' +
			'2. Try to be as ACCURATE and as FAST as possible.<br>' +
			'3. Don\'t focus on individual dots, but judge the GLOBAL color tendency.<br>' +
			'4. Always keep your eyes on the red FIXATION CROSS.<br>' +
			'5. Please remain in FULL-SCREEN mode or the game will pause.</p><br>' +
			'<p align=center>&nbsp;&nbsp;&nbsp;Continue with space bar.</p><br><br>'},
		choice_keys: [' '],
		choice_labels: ['Press space bar'],
		requireFullScreen: true,
		hideButtonDuration: instructionsMinTime,
	}],
	on_start: function() {
		$('body').css('cursor', 'none') // show cursor before button click
	},
};

var trial_Instruction3 = {
	timeline: [{
		type: 'wl-html-keyboard-response',
		stimulus: function() { return '<p class="instructions-text">'+
			'The task consists of ' + nBlocks.toString() + ' blocks of ' + nBlockTrials.toString() + ' trials each.<br>' +
			' You can take a break between blocks, but please don\'t pause during an ongoing block.<br><br>'+
			'<b>You may find that the task gets a bit harder from now on. Just try your best to be accurate - never just guess!<br>' +
			'When the decision is difficult, you may need more time to make an accurate choice.</b><br><br>' +
			'If your results indicate that you did not pay attention, your HIT may be rejected and you will not receive any bonus.</p><br><br>' +
			'Press space bar to start the task.</p><br><br>'},
		choice_keys: [' '],
		choice_labels: ['Press space bar'],
		hideButtonDuration: instructionsMinTime,
	}],
	on_start: function() {
		document.exitPointerLock = document.exitPointerLock ||
									 document.mozExitPointerLock;
		// Attempt to unlock
		document.exitPointerLock();
		$('body').css('cursor', 'none');
	} // show cursor before button click
};


/* BREAK BETWEEN BLOCKS */
var trial_break = {
	timeline: [{
		type: 'wl-html-keyboard-response',
		choice_keys: [' '],
		choice_labels: ['Press space bar'],
		hideButtonDuration: instructionsMinTime,
		block_break: true,
		blocks_total: nBlocks,
		final_block: false,
	}],
	on_start: function(trial) {
		document.exitPointerLock = document.exitPointerLock ||
									 document.mozExitPointerLock;
		// Attempt to unlock
		document.exitPointerLock();
		$('body').css('cursor', 'none');

		BlockCount += 1;
		trial.block = BlockCount;
		if (BlockCount === nBlocks+1) {
			trial.final_block = true;
			trial.hideButtonDuration = 1000;
		} else {
			trial.final_block = false;
		}
		trial.score = score;
		BlockTrialCount = 0; // reset block trial count

	}, // show cursor before button click
};


//------------------------//
/* Create BLOCK objects */
/* DEMO BLOCK */
var cond_demo = [{ col: 0, cCoh: ColorCoherences[ColorCoherences.length-1] },
	{ col: 1, cCoh: ColorCoherences[ColorCoherences.length-1] }];

var demo_block = {
	timeline: [{
	// example 1
		type: 'wl-rdm',
		decision_task: task,
		response_keys: resp_keys,
		color: cond_demo[0]['col'],
		color_coherence: cond_demo[0]['cCoh'],
		demo_trial: true,
		onset_delay: [3000],
		feedback_dur: 2000,
		RT_deadline: 15000,
		refresh_rate: function() {return FPS},
		PPD: function() {return PPD},
		requireFullScreen: true,
		pause: function() {return pause},
		data: { TrialType: 'ColorTask_Demo' } // data that is saved for every type of that trial
	},
	{ // example 2
		type: 'wl-rdm',
		decision_task: task,
		response_keys: resp_keys,
		color: cond_demo[1]['col'],
		color_coherence: cond_demo[1]['cCoh'],
		demo_trial: true,
		onset_delay: [2000],
		feedback_dur: 1500,
		RT_deadline: 7000,
		refresh_rate: function() {return FPS},
		PPD: function() {return PPD},
		requireFullScreen: true,
		pause: function() {return pause},
		data: { TrialType: 'ColorTask_Demo' }, // data that is saved for every type of that trial
	},
	{ // repeat demo trial?
	type: 'wl-html-keyboard-response',
	stimulus: function() {return '<h3>Well done! </h3>' +
		'<p class="instructions-text", align=center >'+
		'<p align=center>If you wish to repeat the guided practice, press \'' + resp_keys[0] + '\'.<br>' +
		'Otherwise, press \'' + resp_keys[1] + '\' to move on to the next part.<br><br></p>';},
	choice_keys: function(){ return resp_keys},
	choice_labels: function() {return ['Repeat ['+resp_keys[0] +']','Next ['+resp_keys[1] +']']},
	requireFullScreen: true,
	on_start: function(trial) { // if full-screen exit during demo, it will skip the next trial. To prevent this check here and repeat if necessary
		  if (jsPsych.data.get().last(2).select('missTrialMsg').values[0].includes('exitFullScreen')) {
			trial.stimulus = '<h3>Please remain in full-screen mode and repeat the guided practice.</h3><br><br>';
			trial.choice_keys = ['spacebar'];
			trial.choice_labels = ['Press space bar']
		  }
	  $('body').css('cursor', 'none'); // hide cursor
	}
	}],
    loop_function: function(){ // loop until participant clicks on 'No'
        if(jsPsych.data.get().last(1).select('button_pressed').values[0]===1) { // 'Next' -> Don't repeat
            return false;
        } else {
            // this runs after endTrialRoutine (so we have to undo the increments)
            TrialCount -= 3; // 2 trials + click on button
            jsPsych.setProgressBar(TrialCount/totTrials);
            return true; // Repeat
        }
    }
}


/* EXPERIMENTAL BLOCK */
var cond = []; // create all stimulus condition combinations
    for (c = 0; c < ColorCoherences.length; c++) {
        for (col = 0; col < 2; col++) {
            for (n = 0; n < nReps; n++)
                cond.push({ col: col, cCoh: ColorCoherences[c] })
    }
}

// Create array of trial conditions we want to run (initially: All trial conditions, e.g., [0,1,2,3..n-1])
var runTrialCond = Array.apply(null, {length: cond.length}).map(Number.call, Number);
var randCond = []; // we will fill this array with randomized trial numbers below
// create experimental block
var exp_block = {
    timeline: [{
        type: 'wl-rdm',
        decision_task: task,
        response_keys: resp_keys,
        refresh_rate: function() {return FPS},
        PPD: function() {return PPD},
        score: function() { return score},
        display_score: false,
        requireFullScreen: true,
        pause: function() {return pause},
        data: { TrialType: 'ColorTask' }
    }],
    on_start: function(trial) {
    // randomly draw trial condition
    if (runTrialCond.length>1) {
        var randNew;
        while (randNew === undefined || randNew===randCond[randCond.length - 1]) {  // if you want to avoid immediate repetition of the same trial condition (you may not need this)
            randNew = runTrialCond[Math.round(Math.random() * (runTrialCond.length-1))]
        }
    } else {
        randNew = runTrialCond[0];
    }
    randCond.push(randNew);
    //console.log(randCond)

    // define trial condition based on last randomly drawn trial
    trial.motion_direction = cond[randCond[randCond.length - 1]]['dir'];
    trial.motion_coherence = cond[randCond[randCond.length - 1]]['mCoh'];
    trial.color = cond[randCond[randCond.length - 1]]['col'];
    trial.color_coherence = cond[randCond[randCond.length - 1]]['cCoh'];

    return randCond
    },
    on_finish: function(){
        var LastMissTrial = jsPsych.data.get().last(1).select('missTrial').values[0]; // (false/true)
        if (!LastMissTrial) { // if last trial was NOT a miss trial, remove condition from runTrialCond array
            runTrialCond = runTrialCond.filter((value,index,array) => value !== randCond[randCond.length - 1])
        };
    },
    loop_function: function(){ // loop until trial condition list is empty
        if (runTrialCond.length > 0) {
            return true; // run another trial
        } else { // if no more trials need to be repeated, end current block
            // IMPORTANT: If you want to run multiple blocks, you need to reset runTrialCond and randCond here before the next block!
            runTrialCond =  Array.apply(null, {length: cond.length}).map(Number.call, Number);
            randCond = [];
            return false
        }
    }
}


var exit_screen = {
    timeline: [{
        type: 'wl-html-button-response',
        stimulus: '<h3>End of this session. Thank you!</h3><br>',
        choices: ['Close window']
    }],
    on_start: function() {
        document.exitPointerLock = document.exitPointerLock ||
                                     document.mozExitPointerLock;
        // Attempt to unlock
        document.exitPointerLock();
        $('body').css('cursor', 'auto');
    }, // show cursor
    on_finish: function() {
        closeCheck = false;


        //jsPsych.data.displayData(); //Display the data onto the browser screen

        var form = document.createElement("form");
        form.setAttribute('method',"POST");
        form.setAttribute('id',"exp");

        var input = document.createElement("input");

        input.setAttribute("type", "hidden");
        input.setAttribute("id", "experimentResults");
        input.setAttribute("name", "experimentResults");
        input.setAttribute("value", "[]");
        form.appendChild(input);

        document.body.appendChild(form);

        var strExpResults = jsPsych.data.get().json();
        document.getElementById('experimentResults').value = strExpResults;
        document.getElementById('exp').submit()
	    // amx - window.close();
    }
}


////////////////////////////////////////////////
// 2. Push everything to timeline
////////////////////////////////////////////////

/* Create empty experiment timeline */
var timeline = [];

timeline.push(screenmode);
timeline.push(trial_check_fps);
timeline.push(trial_Instruction1);
timeline.push(demo_block);
timeline.push(trial_Instruction2);
timeline.push(trial_Instruction3);

for (b=0;b<nBlocks;b++) {
    timeline.push(exp_block);
    if (b<nBlocks-1) {
        timeline.push(trial_break);
    }
}

timeline.push(exit_screen);



////////////////////////////////////////////////
// 3. Start the experiment
////////////////////////////////////////////////

// Check for reasons to exclude
var browserInfo = getBrowserInfo();
var browserExclude = !browserInfo.browser.includes('Chrome');

var exclude = browserExclude;
if (exclude){ // {
    var wrong_browser = {
        type: 'wl-html-button-response',
        stimulus: '<p>This experiment is only supported in Google Chrome.<br>' +
                  'Please copy the full URL and reopen it in a Chrome browser window. <br>' +
                  'Leave the MTurk window open in your current browser.<br>' +
                  'Return to the MTurk window to submit after receiving your code in the Chrome browser.</p>',
        choices: ['Close window']}
    jsPsych.init({
        timeline: [wrong_browser],
    });

}else{ // Start the experiment
    jsPsych.init({
    timeline: timeline,
        'show_progress_bar': true,
        'auto_update_progress_bar': false,
        'message_progress_bar': 'Time Elapsed: <label id="minutes">00</label>:<label id="seconds">00</label><br>',
        on_trial_finish: function(trial_data){
            endTrialRoutine(trial_data);
    },
    on_interaction_data_update: function(interaction_data) {
        if (interaction_data.event==='fullscreenexit' && jsPsych.currentTrial().requireFullScreen){
            if (!warning) { // don't run this if warning message is shown on screen (full screen gets activated after warning message anyway)
              exitedFullScreen = true;
              onExitFullscreen();
            }
        }
        if (interaction_data.event==='blur'){
            blurEvent = true;
        }
    },
    on_close: function(e){
        if (closeCheck) {
            e.preventDefault();
            e.returnValue = '';
        }
    },
    default_iti: 0,
    //on_finish: function() {jsPsych.data.displayData();} // uncomment for quick output check
    });

    // start the experiment timer
    var minutesLabel = document.getElementById("minutes");
    var secondsLabel = document.getElementById("seconds");
    var totalSeconds = 0;
    setInterval(setTime, 1000);
}




////////////////////////////////////////////////
// Extra functions
////////////////////////////////////////////////

/* EXIT EXPERIMENT */
function exitExperiment(exclReason) {

    var exitMessage = '<h3>Unfortunately, you do not qualify for this HIT.</h3>';

    if (exclReason === 'FPSexclude') {
        exitMessage +='<h3>Your screen refresh rate needs to be between 55-80 Hz.</h3><br><br>' +
        '<p>You are welcome to change your screen refresh rate (preferably to 60 Hz) and then try again.<p>' +
        '<p>Please also make sure to close all background programs that may slow down your browser.<p>' +
        '<p>If you would like to re-start the experiment, please clear your browser cache first!</p>' +
        '<p>If you do not wish to retry, please return this HIT now.</p>';
    } else if (exclReason === 'ACCexclude') {
        exitMessage += '<h3>For quality purposes, choice performance needs to be sufficiently high to qualify for this task.</h3>' +
        '<p>Please return this HIT now.</p>';
    }
    exitMessage += '<h3><br><br>We are sorry for the inconvenience! You can close this browser window now.</h3>';

    jsPsych.endExperiment(exitMessage);
}


/* Warning message if too many miss trials in a row */
showWarning = function() {
    document.exitFullscreen();
    pause = true;
    warning = true;
    //exitedFullScreen = true; // set this to true, even if no full screen exit, but to prevent next trial from running before 'click'

    var canvasElement = document.getElementById('jspsych-wl-vmr-canvas');
    var buttonResponseStimulusElement = document.getElementById('jspsych-html-button-response-stimulus');
    var buttonResponseButtonsElement = document.getElementById('jspsych-html-button-response-btngroup');
    //console.log(canvasElement)
    if(canvasElement!==null){
        canvasElement.style.display = 'none';
    }
    if (buttonResponseStimulusElement!==null){
        buttonResponseStimulusElement.style.display = 'none';
    }
    if (buttonResponseButtonsElement!==null){
        buttonResponseButtonsElement.style.display = 'none';
    }

    var trial_content_container = document.getElementById("jspsych-content");

    warningScreen = document.createElement('div');
    warningScreen.innerHTML = '<h3>Please pay attention to the task and follow the instructions.</h3><br>' +
    '<h3>Click the button to continue. The task will automatically go back into full-screen mode.</h3><br>' +
    '<button id="jspsych-fullscreen-btn" class="jspsych-btn">Continue task</button>';

    trial_content_container.appendChild(warningScreen);
    //console.log(trial_content_container)

    var continueButton = $('#jspsych-fullscreen-btn')[0];

    document.exitPointerLock = document.exitPointerLock ||
                                 document.mozExitPointerLock;
    // Attempt to unlock
    document.exitPointerLock();
    $('body').css('cursor', 'auto');

    continueButton.addEventListener('click', function(){
    //exitedFullScreen = false;
    warning = false;
    pause = false;
    //console.log('pause exit')

    var element = document.documentElement;
    if (element.requestFullscreen) { element.requestFullscreen(); }
    else if (element.mozRequestFullScreen) { element.mozRequestFullScreen(); }
    else if (element.webkitRequestFullscreen) { element.webkitRequestFullscreen(); }
    else if (element.msRequestFullscreen) { element.msRequestFullscreen(); }

    trial_content_container.removeChild(warningScreen);
    $('body').css('cursor', 'none');

    setTimeout( function(){
        //console.log(pause)
        return pause;
        /*if(canvasElement!==null){
        canvasElement.style.removeProperty('display'); // stop hiding the canvas
        }
        if(buttonResponseStimulusElement!==null){
        buttonResponseStimulusElement.style.removeProperty('display');
        }
        if(buttonResponseButtonsElement!==null){
        buttonResponseButtonsElement.style.removeProperty('display');
        }*/
    }); //,200
    });
}

/* Function to replace current trial with prompt to re-enter full screen */
onExitFullscreen = function() {
    pause = true;

    var canvasElement = document.getElementById('jspsych-wl-vmr-canvas');
    var buttonResponseStimulusElement = document.getElementById('jspsych-html-button-response-stimulus');
    var buttonResponseButtonsElement = document.getElementById('jspsych-html-button-response-btngroup');
    //console.log(canvasElement)
    if(canvasElement!==null){
        canvasElement.style.display = 'none';
    }
    if (buttonResponseStimulusElement!==null){
        buttonResponseStimulusElement.style.display = 'none';
    }
    if (buttonResponseButtonsElement!==null){
        buttonResponseButtonsElement.style.display = 'none';
    }

    var trial_content_container = document.getElementById("jspsych-content");

    fs = document.createElement('div');
    fs.innerHTML = '<h3>This experiment must be run in full-screen.</h3><br>' +
    '<button id="jspsych-fullscreen-btn" class="jspsych-btn">Enter full screen mode</button>';

    trial_content_container.appendChild(fs);
    //console.log(trial_content_container)

    var fullScreenButton = $('#jspsych-fullscreen-btn')[0];

    document.exitPointerLock = document.exitPointerLock ||
                                 document.mozExitPointerLock;
    // Attempt to unlock
    document.exitPointerLock();
    $('body').css('cursor', 'auto');


    fullScreenButton.addEventListener('click', function(){
    exitedFullScreen = false;
    pause = false;
    var element = document.documentElement;
    if (element.requestFullscreen) { element.requestFullscreen(); }
    else if (element.mozRequestFullScreen) { element.mozRequestFullScreen(); }
    else if (element.webkitRequestFullscreen) { element.webkitRequestFullscreen(); }
    else if (element.msRequestFullscreen) { element.msRequestFullscreen(); }

    trial_content_container.removeChild(fs);
    $('body').css('cursor', 'none');

    setTimeout( function(){
        if(canvasElement!==null){
            canvasElement.style.removeProperty('display'); // stop hiding the canvas
        }
        if(buttonResponseStimulusElement!==null){
            buttonResponseStimulusElement.style.removeProperty('display');
        }
        if(buttonResponseButtonsElement!==null){
            buttonResponseButtonsElement.style.removeProperty('display');
        }
        //fullScreenButton.removeEventListener('click', RequestFullScreen);
    }, 200);
    });
}


/* Function checking browser */
function getBrowserInfo() {
    var ua = navigator.userAgent, tem,
    M = ua.match(/(opera|chrome|safari|firefox|msie|trident(?=\/))\/?\s*(\d+)/i) || [];
    if(/trident/i.test(M[1])) {
        tem=  /\brv[ :]+(\d+)/g.exec(ua) || [];
        return 'IE '+(tem[1] || '');
    }
    if(M[1]=== 'Chrome') {
        tem= ua.match(/\b(OPR|Edge)\/(\d+)/);
        if(tem!= null)
        return tem.slice(1).join(' ').replace('OPR', 'Opera');
    }
    M = M[2]? [M[1], M[2]]: [navigator.appName, navigator.appVersion, '-?'];
    if((tem= ua.match(/version\/(\d+)/i))!= null)
    M.splice(1, 1, tem[1]);
    return { 'browser': M[0], 'version': M[1] };
}

/* Function getting OS information */
function getOSInfo() {
    var OSName = "Unknown";
    if (window.navigator.userAgent.indexOf("Windows NT 10.0")!= -1) OSName="Windows 10";
    if (window.navigator.userAgent.indexOf("Windows NT 6.2") != -1) OSName="Windows 8";
    if (window.navigator.userAgent.indexOf("Windows NT 6.1") != -1) OSName="Windows 7";
    if (window.navigator.userAgent.indexOf("Windows NT 6.0") != -1) OSName="Windows Vista";
    if (window.navigator.userAgent.indexOf("Windows NT 5.1") != -1) OSName="Windows XP";
    if (window.navigator.userAgent.indexOf("Windows NT 5.0") != -1) OSName="Windows 2000";
    if (window.navigator.userAgent.indexOf("Mac")            != -1) OSName="Mac/iOS";
    if (window.navigator.userAgent.indexOf("X11")            != -1) OSName="UNIX";
    if (window.navigator.userAgent.indexOf("Linux")          != -1) OSName="Linux";
    return OSName;
}

// Generate completion code: Create five-character random string
function makeid(){
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for( var i=0; i < 5; i++ )
      text += possible.charAt(Math.floor(Math.random() * possible.length));
    return text;
}

/* Function to remember some data from this trial for next trial */
function endTrialRoutine(data) {

    // check if ful-screen exit
    if (exitedFullScreen){
        data.missTrial = true;
        data.missTrialMsg += 'exitFullScreen ';
    }

    // check if blur event
    if (blurEvent){
        data.missTrial = true;
        data.missTrialMsg += 'blurEvent ';
        blurEvent = false;
    }

    if (!data.missTrial){
        TrialCount += 1;
    }
    data.Block = BlockCount;
    data.TrialNumber = TrialCount; // add trial number to output
    //console.log(data.TrialNumber)

    if (data.TrialType === 'ColorTask') {
        if (data.Accuracy) {
            score += 1;
        } else if (!data.Accuracy || (data.missTrial && !data.missTrialMsg.includes('blurEvent'))) {
            score -= 1; // lose point for errors/misses/full screen exits etc.
        }
        data.Score = score;

        BlockTrialCount += 1;
        data.BlockTrial = BlockTrialCount;

        // Show warning if >= 8 miss trials in last 10 trials
        checkTrialCount += 1;
        //console.log(checkTrialCount)
        if (checkTrialCount >= 10) {
            var RecentMissTrials = jsPsych.data.get().last(10).select('missTrial').values; // (false/true)
            //console.log(RecentMissTrials.filter(x => x).length)
            if (RecentMissTrials.filter(x => x).length >= 8) {
                //console.log('show warning')
                data.missTrialMsg = data.missTrialMsg + 'warning ';
                checkTrialCount = 0; // reset so warning doesn't get shown again immediately on the next trial
                showWarning();
            }
        }

    }

    jsPsych.setProgressBar(TrialCount/totTrials);

}


function setTime() {
    ++totalSeconds;
    secondsLabel.innerHTML = pad(totalSeconds % 60);
    minutesLabel.innerHTML = pad(parseInt(totalSeconds / 60));
}

function pad(val) {
    var valString = val + "";
    if (valString.length < 2) {
        return "0" + valString;
    } else {
        return valString;
    }
}
