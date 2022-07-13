console.log("loaded run_foodratingtask.js ");

// var expVariables set in HTML

var recordAllKeyPresses = true;
var allKeyPresses = [];

var currTrialN = 0;

var stimuli = []; 
var specialKeys = [];

var expResults = [];
var allTrials = [];

default_font = "Optima,Segoe,'Segoe UI',Candara,Calibri,Arial,sans-serif;"

// canvas is the drawing platform on which stimuli are draw
var canvas = document.getElementById("myCanvas");
// set canvas width and height to that of browser window (inner excludes bookmarks bar, etc.)
var winWidth = window.innerWidth;
var winHeight = window.innerHeight;
canvas.width = winWidth;
canvas.height = winHeight;
var ctx = canvas.getContext('2d');

var svg = document.getElementById("mySVG");
svg.setAttribute("width", winWidth.toString());
svg.setAttribute("height", winHeight.toString());

var t1, t2; 
// t1: start time of trial
// t2: end time of trial
var t1_UNIX, t2_UNIX;

var scale;

var origImgWidth = 576; // necessary for rescaling images and positioning scale
var origImgHeight = 432; // necessary for rescaling images

var widthPercent = .80;
var rescaleHeight = true;
var stimNames = ["stimulus"];

/*
 * Called in the HTML
*/
var nStimuli;
var nImagesLoaded = 0;
var startExperiment = function() {
	nStimuli = expVariables.length;
	// drawLoadingText(WHITE);
	generateOffScreenCanvases(drawStimuliToCanvas,'');
}

var drawStimuliToCanvas = function(trialVariables, trialN, canvasCtx) {
	var position = "CENTER";
	var stimulus = trialVariables['stimulus'];
	var fullStimName = trialVariables['fullStimName']
	var img1 = new imageStimulus(stimulus, stimFolder + fullStimName, 'NaN', widthPercent, rescaleHeight);
	img1.drawImage(position, trialN, canvasCtx);
	trialStimuli = [img1];
	stimuli[trialN] = trialStimuli;
}


var startFirstTrial = function() {
	removeLoadingText();
	drawTrialDisplay(expVariables[currTrialN]); 
}

/*
  * Draws individual trial display
  * Updates trial information
  * Draws images for trial
  * Adds rating scale to display
  * @param {python dictionary/js object} trialVariables: has keys and values for trial parameters
*/
var instructions;
var leftRating;
var middleRating;
var rightRating;
var drawTrialDisplay = function(trialVariables) {
	// condition is a dictionary - each key can be used to set trial conditions
	ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
	var stimulus = trialVariables['stimulus'];

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

	var scaledImgDimensions = rescaleImgSize([origImgWidth,origImgHeight], widthPercent, rescaleHeight);
	var scaledHeight = scaledImgDimensions[1];

	instructionsText=trialVariables['question']
	if (instructions == null) {
		instructions = new textBox(instructions, instructionsText, 20, WHITE);
	} else {
		instructions.removeText();
	}
	instructions.setText(instructionsText);
	instructions.showText(0, canvas.height/2 - scaledHeight/2 - 30);
	// instructions.setFont("Optima,Segoe,'Segoe UI',Candara,Calibri,Arial,sans-serif;");

	if (scale == null) { // set up scale for first trial
		scale = new ratingScale(trialVariables['rs_min'],trialVariables['rs_max'],trialVariables['rs_tickIncrement'],trialVariables['rs_increment'],canvas.width/2,canvas.height/2 + scaledHeight/2 + 10, trialVariables['rs_labelNames'],WHITE);
	} else {
		scale.removeScale(); // removes current scale
	}
	scale.setRatingScaleParams(trialVariables['rs_min'],trialVariables['rs_max'],trialVariables['rs_tickIncrement'],trialVariables['rs_increment'],canvas.width/2,canvas.height/2 + scaledHeight/2 + 10, trialVariables['rs_labelNames'],WHITE);
	scale.drawRatingScale(canvas.width/2,canvas.height/2 + scaledHeight/2 + 10, false, null, null, WHITE); // draws/redraws scale
	
	leftRatingText=trialVariables['leftRatingText']
	if (leftRating == null) {
		leftRating = new textBox(leftRating, leftRatingText, 20, WHITE);
	} else {
		leftRating.removeText();
	}
	leftRating.setText(leftRatingText);
	leftRating.showText(0 - scale.ratingBarWidth/2, canvas.height/2 + scaledHeight/2 + 85);

	middleRatingText=trialVariables['middleRatingText']
	if (middleRating == null) {
		middleRating = new textBox(middleRating, middleRatingText, 20, WHITE);
	} else {
		middleRating.removeText();
	}
	middleRating.setText(middleRatingText);
	middleRating.showText(0, canvas.height/2 + scaledHeight/2 + 85);

	rightRatingText=trialVariables['rightRatingText']
	if (rightRating == null) {
		rightRating = new textBox(rightRating, rightRatingText, 20, WHITE);
	} else {
		rightRating.removeText();
	}
	rightRating.setText(rightRatingText);
	rightRating.showText(0 + scale.ratingBarWidth/2, canvas.height/2 + scaledHeight/2 + 85);
}


/*
 * Initializes set of trial information and adds to allTrials
 * Checks for any special key presses (associated with stimuli) and adds to specialKeys
 * Sets start time for trial
*/
var pushTrialInfo = function() {
	var currTrial = new trial({'trialN':currTrialN, 'stimuli':stimuli[currTrialN], 'question':expVariables[currTrialN]['question']});
	allTrials.push(currTrial);

	// send stimuli here to trialInfo, set special keys inside trialInfo
	var i;
	for (i=0;i<stimuli[currTrialN].length;i++) {
		if (stimuli[currTrialN][i].key != 'NaN') {
			specialKeys.push(stimuli[currTrialN][i].key);
		}
	}

	t1 = performance.now(); // start timer for this trial
	t1_UNIX = Date.now();

	allTrials[currTrialN].trialStartTime = t1;
	allTrials[currTrialN].trialStartTime_UNIX = t1_UNIX;

	for (i=0;i<stimuli[currTrialN].length;i++) {
		allTrials[currTrialN]['stimulus' + parseInt(i+1,10)] = stimuli[currTrialN][i].id;
	}
}

/*
  * Does all clean up for trial
  * Get trial duration / reaction time
*/
var endTrial = function() {
	t2 = performance.now();
	t2_UNIX = Date.now();
	var i;
	for (i=0;i<stimuli[currTrialN].length;i++) {
		allTrials[currTrialN]['stimulus' + parseInt(i+1,10) + 'Loaded'] = stimuli[currTrialN][i].loaded;
	}
	if (allTrials[currTrialN].rating == null) { // did not respond
		drawNextTrial = true;
		allTrials[currTrialN].rt = t2 - t1; 
		allTrials[currTrialN].receivedResponse = false;
		allTrials[currTrialN].rating = 'NaN';
		allTrials[currTrialN].trialEndTime = t2;
		allTrials[currTrialN].trialDuration = t2 - t1;
		allTrials[currTrialN].trialEndTime_UNIX = t2_UNIX;
		allTrials[currTrialN].rt_UNIX = t2_UNIX - t1_UNIX;
	}
	nextTrial();
}

/*
  * Clears canvas, removes scale
  * Iterates currTrialN by 1, clears current screen and calls drawTrialDisplay for next trial
  * Checks if experiment has ended (there are no more trials), and ends the experiment
*/
var nextTrial = function() {
	ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
	scale.removeScale();
	instructions.removeText();
	leftRating.removeText();
	middleRating.removeText();
	rightRating.removeText();
	currTrialN+=1; // iterate to next trial
	if (currTrialN < expVariables.length) {
		drawTrialDisplay(expVariables[currTrialN]);
	} else {
		var strExpResults = JSON.stringify(allTrials);
		document.getElementById('experimentResults').value = strExpResults;

		drawLoadingText(WHITE);

		document.getElementById('exp').submit()
	}
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
	svg.setAttribute("width", winWidth.toString());
	svg.setAttribute("height", winHeight.toString());

	// remove blanks/alert text if exist
	if (svg.contains(blankScreenCover)) {
		svg.removeChild(blankScreenCover);
	}
	if (svg.contains(alertText)) {
		svg.removeChild(alertText);
	}

	drawTrialDisplay(expVariables[currTrialN]);
}

window.onresize = function() {
    if (document.getElementById('myCanvas').style.visibility == "visible" | document.getElementById('mySVG').style.visibility == "visible") {
	    resizeWindow();
	}
}


/* ENTER FULL SCREEN */
var screenmode = {
    type: 'fullscreen',
    message: '<h3>This experiment must be run in full-screen.</h3><br>',
    fullscreen_mode: true,
    delay_after: 200, // add little delay to make sure screen size is updated correctly
}

var display_element = document.createElement('div');
display_element.innerHTML = screenmode.message + '<button id="jspsych-fullscreen-btn" class="jspsych-btn">Enter full screen mode</button>';

document.getElementById("content").appendChild(display_element);

function enterFullScreen() {
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
    drawLoadingText(WHITE);
    setTimeout(startExperiment,500); // wait before starting experiment, so display isn't redrawn because of window size change
}

document.getElementById("jspsych-fullscreen-btn").addEventListener("click", enterFullScreen);

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