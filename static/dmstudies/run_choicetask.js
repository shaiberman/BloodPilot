console.log("loaded run_choicetask.js ");

// var expVariables set in HTML

var allKeyPresses = [];

var currTrialN = 0;

var origImgWidth = 576; // necessary for rescaling images
var origImgHeight = 432; // necessary for rescaling images

var stimuli = []; 
var specialKeys = [];

var expResults = [];
var allTrials = [];

default_font = "Optima,Segoe,'Segoe UI',Candara,Calibri,Arial,sans-serif;"

// canvas is the drawing platform on which stimuli are draw
var canvas = document.getElementById("myCanvas");
// set canvas width and height to that of browser window (inner excludes bookmarks bar, etc.)
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
var ctx = document.getElementById('myCanvas').getContext('2d');

var svg = document.getElementById("mySVG");
svg.setAttribute("width", (window.innerWidth).toString());
svg.setAttribute("height", (window.innerHeight).toString());

var confirmationTime = 500; // in ms
var confirmTimer;
var inConfirmation = false;

var t1, t2;
var t1_UNIX;
var t2_UNIX;
var trialTimer;
var maxTrialDuration = 3500; // in ms


var widthPercent = .45;
var rescaleHeight = false;

/*
 * Called in the HTML
*/
var nStimuli;
var nImagesLoaded = 0;
var startExperiment = function() {
	nStimuli = expVariables.length * 2;
	//drawLoadingText(WHITE);
	generateOffScreenCanvases(drawStimuliToCanvas, '');
}

var drawStimuliToCanvas = function(trialVariables, trialN, canvasCtx) {
	var stimulus1 = trialVariables['stimulus1'];
	var stimulus2 = trialVariables['stimulus2'];
	var stim1Bid = trialVariables['stim1Bid'];
	var stim2Bid = trialVariables['stim2Bid'];
	var fullStim1Name = trialVariables['fullStim1Name']
	var fullStim2Name = trialVariables['fullStim2Name']

	var img1 = new imageStimulus(stimulus1, stimFolder + fullStim1Name, 'u', widthPercent, false);
	img1.drawImage('LEFT', trialN, canvasCtx);
	img1.bid = stim1Bid;

	var img2 = new imageStimulus(stimulus2, stimFolder + fullStim2Name, 'i', widthPercent, false);
	img2.drawImage('RIGHT', trialN, canvasCtx);
	img2.bid = stim2Bid;
	
	stimuli[trialN] = [img1, img2];
}

/*
  * Called in components.js after all images have been loaded
*/
var startFirstTrial = function() {
	startTrial();
}

var startTrial = function() {
	removeLoadingText();
	drawTrialDisplay(expVariables[currTrialN]);
}

/*
  * Draws individual trial display
  * Updates trial information
  * Draws images for trial
  * Adds confirmation box to trial display
  * @param {python dictionary/js object} trialVariables: has keys and values for trial parameters
*/
var instructions;
var confirmationBox;
var drawTrialDisplay = function(trialVariables) {
	// trialVariables is a dictionary - each key can be used to set trial conditions
	var stimulus1 = trialVariables['stimulus1'];
	var stimulus2 = trialVariables['stimulus2'];
	var stim1Bid = trialVariables['stim1Bid'];
	var stim2Bid = trialVariables['stim2Bid'];
	var delta = trialVariables['delta']; // right bid - left bid

	//console.log("Trial " + currTrialN + " " + stimulus1 + " " + stim1Bid.toString() + ", " + stimulus2 + " " + stim2Bid.toString());

	var trialCanvas = document.getElementById("trial"+currTrialN);
	var trialCtx = trialCanvas.getContext('2d');
	if (trialCanvas.width == canvas.width && trialCanvas.height == canvas.height) {
		ctx.drawImage(trialCanvas, 0, 0, canvas.width, canvas.height);
	} else {
		drawStimuliToCanvas(trialVariables, currTrialN, ctx);
	}

	if (allTrials.length == currTrialN) {
		pushTrialInfo();
	}

	allTrials[currTrialN]['stimulus1'] = stimulus1;
	allTrials[currTrialN]['stimulus2'] = stimulus2;
	allTrials[currTrialN]['stimulus1Bid'] = stim1Bid;
	allTrials[currTrialN]['stimulus2Bid'] = stim2Bid;

	allTrials[currTrialN]['delta'] = delta;

	if (confirmationBox == null) {
		confirmationBox = new box(confirmationBox, canvas.width * 0.02);
	} else {
		confirmationBox.removeBox();
	}
	confirmationBox.showBox(canvas.width/2, canvas.height/2, WHITE, canvas.width * 0.02);

	var scaledImgDimensions = rescaleImgSize([origImgWidth,origImgHeight], widthPercent, false);
	var scaledHeight = scaledImgDimensions[1];

	if (instructions == null) {
		instructions = new textBox(instructions, "Which food do you prefer? Press 'u' for the one on the left or 'i' for the one on the right.", 20, WHITE);
	} else {
		instructions.removeText();
	}
	instructions.showText(0, canvas.height/2 - scaledHeight/2 - 10);
}

/*
 * Initializes set of trial information and adds to allTrials
 * Checks for any special key presses (associated with stimuli) and adds to specialKeys
 * Sets start time for trial
 * Sets timer for trial
*/
var pushTrialInfo = function() {
	var currTrial = new trial({'trialN':currTrialN, 'stimuli':stimuli[currTrialN]});
	allTrials.push(currTrial);
	//console.log(currTrial)
	//console.log(allTrials)
	// send stimuli here to trialInfo, set special keys inside trialInfo

	specialKeys = [];
	var i;
	for (i = 0; i < stimuli[currTrialN].length; i++) { 
		if (stimuli[currTrialN][i].key != null) {
			specialKeys.push(stimuli[currTrialN][i].key);

		}
	}
	
	t1 = performance.now(); // start timer for this trial
	t1_UNIX = Date.now();
	trialTimer = setTimeout(endTrial,maxTrialDuration);
	allTrials[currTrialN].trialN = currTrialN;
	allTrials[currTrialN].trialStartTime = t1;
	allTrials[currTrialN].trialStartTime_UNIX = t1_UNIX;
}

/*
  * Checks key presses and moves to next trial
  * Checks array of special keys
  * 	- if current key pressed is in specialKey, moves to next trial
*/
var keyIsDown = false; // keep track if key is still being held down - take one key press at a time
var checkKeyPress = function(e) {
var timePressed_perfnow = performance.now();
	var timePressed = e.timeStamp; // does not seem to be compatible with all browsers - may get UNIX time instead of time relative to trial start
	var timePressed_UNIX = Date.now();

	if (inConfirmation == false && keyIsDown == false && timePressed > t1 && !svg.contains(blankScreenCover)) { 
		keyIsDown = true;
		t2 = timePressed;
		t2_UNIX = timePressed_UNIX;
		// should check if timepressed is after trial starts
		if (specialKeys.indexOf(e.key) > -1 && currTrialN == allTrials.length - 1) { 
			clearTimeout(trialTimer);
			clearTimeout(confirmTimer);
			
			if (currTrialN < expVariables.length) {
				var i;
				for (i=0;i<stimuli[currTrialN].length;i++) {
					if (e.key == stimuli[currTrialN][i].key) {
						allTrials[currTrialN].selected = stimuli[currTrialN][i].id;
					} else {
					}
				}
				allTrials[currTrialN].rt = t2 - t1;
				allTrials[currTrialN].rt_UNIX = t2_UNIX - t1_UNIX;
				allTrials[currTrialN].rt_perfnow = timePressed_perfnow - t1;
				allTrials[currTrialN].receivedResponse = true;
				allTrials[currTrialN].rsp = e.key;
				
				endTrial();
			}
		}
	}
}

var setKeyUp = function(e) {
	keyIsDown = false;
}

/*
  * Called by a timer in endTrial 
  * Clears canvas, removes scale
  * Iterates currTrialN by 1, clears current screen and calls drawTrialDisplay for next trial
  * Checks if experiment has ended (there are no more trials), and ends the experiment
*/
var nextTrial = function() {
	ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
	t2 = performance.now();
	t2_UNIX = Date.now();
	allTrials[currTrialN].trialEndTime = t2;
	allTrials[currTrialN].trialDuration = t2 - t1;
	allTrials[currTrialN].trialEndTime_UNIX = t2_UNIX;
	allTrials[currTrialN].trialDuration_UNIX = t2_UNIX - t1_UNIX;
	confirmationBox.removeBox();
	currTrialN+=1; // iterate to next trial
	inConfirmation = false;
	if (currTrialN < expVariables.length) { // experiment has not ended
	    if (!inDemo && (currTrialN == expVariables.length/2)) {
	        instructions.removeText();
            document.getElementById("myCanvas").style.visibility = "hidden";
            document.getElementById("mySVG").style.visibility = "hidden";
            display_element.innerHTML = '<p>End of 1/2 blocks.</p>' +
                '<p>You can take a short break now.</p><br>' +
                '<button id="jspsych-fullscreen-btn" class="jspsych-btn">Continue</button>';
            document.getElementById("content").appendChild(display_element);
            document.getElementById("jspsych-fullscreen-btn").addEventListener("click", restartExperiment);
	    } else {
		    drawTrialDisplay(expVariables[currTrialN]);
		}
	} else { // experiment has ended
		instructions.removeText();

		var strExpResults = JSON.stringify(allTrials);
		document.getElementById('experimentResults').value = strExpResults;

		drawLoadingText(WHITE);

		document.getElementById('exp').submit()
	}
}

var restartExperiment = function() {
    enterFullScreen(startTrial);
}


/*
  * Does all clean up for trial
  * Clears trialTimer
  * Get trial duration / reaction time
  * Changes color of confirmation box
  * Sets timer for confirmation and iterates to next trial at the end of confirmation
*/
var endTrial = function() {
	t2 = performance.now();
	t2_UNIX = Date.now()
	clearTimeout(trialTimer);
	var color;
	if (allTrials[currTrialN].rsp == null || t2 - t1 > maxTrialDuration) { // did not respond
		color = RED;
		drawNextTrial = true;
		allTrials[currTrialN].selected = 'NaN';
		allTrials[currTrialN].rsp = 'NaN';
		allTrials[currTrialN].rt = 'NaN';
		allTrials[currTrialN].rt_UNIX = 'NaN';
		allTrials[currTrialN].receivedResponse = false;
		allTrials[currTrialN].trialEndTime = t2;
		allTrials[currTrialN].trialDuration = t2 - t1;
		allTrials[currTrialN].trialEndTime_UNIX = t2_UNIX;
		allTrials[currTrialN].trialDuration_UNIX = t2_UNIX - t1_UNIX;
	} else {
		color = GREEN;
	}
	confirmationBox.setColor(color);
	inConfirmation = true;
	confirmTimer = setTimeout(nextTrial,confirmationTime);
}

/*
 * Called when change in window size is detected
 * Changes width and height of canvas and svg to that of window
 * If window was previously too small (has blankScreenCover and alertText)
 * 	 then these are removed
 * Calls on drawTrialDisplay to redraw display according to new window size
*/
var resizeWindow = function() {
	var winWidth = window.innerWidth;
	var winHeight = window.innerHeight;
	canvas.width = winWidth;
	canvas.height = winHeight;
	ctx = document.getElementById('myCanvas').getContext('2d');
	svg.setAttribute("width", (winWidth).toString());
	svg.setAttribute("height", (winHeight).toString());
	if (svg.contains(blankScreenCover)) {
		svg.removeChild(blankScreenCover);
	}
	if (svg.contains(alertText)) {
		svg.removeChild(alertText);
	}
	drawTrialDisplay(expVariables[currTrialN]);
}


window.onresize = function() {
    if (document.getElementById('myCanvas').style.visibility == "visible" || document.getElementById('mySVG').style.visibility == "visible") {
	    resizeWindow();
	}
}
window.addEventListener("keypress", checkKeyPress);
window.addEventListener("keyup", setKeyUp);


/* ENTER FULL SCREEN */
var screenmode = {
    type: 'fullscreen',
    message: '<h3>This experiment must be run in full-screen.</h3><br>',
    fullscreen_mode: true,
    delay_after: 200, // add little delay to make sure screen size is updated correctly
}

function enterFullScreen(nextFunction) {
    document.getElementById("myCanvas").style.visibility = "visible";
    document.getElementById("mySVG").style.visibility = "visible";
    document.getElementById("jspsych-fullscreen-btn").innerHTML = "";
    display_element.innerHTML = "";
    var element = document.documentElement;
    if (element.requestFullscreen) {
        element.requestFullscreen();
    } else if (element.mozRequestFullScreen) {
        element.mozRequestFullScreen();
    } else if (element.webkitRequestFullscreen) {
        element.webkitRequestFullscreen();
    } else if (element.msRequestFullscreen) {
        element.msRequestFullscreen();
    }
    if (currTrialN == 0) {
        drawLoadingText(WHITE);
    }
    setTimeout(nextFunction,500); // wait before starting experiment, so display isn't redrawn because of window size change
}

var display_element = document.createElement('div');
display_element.innerHTML = screenmode.message + '<button id="jspsych-fullscreen-btn" class="jspsych-btn">Enter full screen mode</button>';

document.getElementById("content").appendChild(display_element);
document.getElementById("jspsych-fullscreen-btn").addEventListener("click", function() {
    enterFullScreen(startExperiment);
    });

// fullscreen change capture
function fullscreenchange(){
  var type = (document.isFullScreen || document.webkitIsFullScreen || document.mozIsFullScreen || document.fullscreenElement) ? 'fullscreenenter' : 'fullscreenexit';
  if (typeof(allTrials[currTrialN]['trialEvents']) == 'undefined') {
		allTrials[currTrialN]['trialEvents'] = [];
	}
	allTrials[currTrialN]['trialEvents'].push({'event':'fullscreenchange','details':type,'performance time':performance.now(),'date time':Date.now()});
}

document.addEventListener('fullscreenchange', fullscreenchange);
document.addEventListener('mozfullscreenchange', fullscreenchange);
document.addEventListener('webkitfullscreenchange', fullscreenchange);