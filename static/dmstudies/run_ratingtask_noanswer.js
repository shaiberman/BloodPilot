console.log("loaded run_ratingtask.js ");

// var expVariables set in HTML

var recordAllKeyPresses = true;
var allKeyPresses = [];

var currTrialN = 0;

var expResults = [];
var allTrials = [];

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
var t1_UNIX;

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
	document.body.style.backgroundColor = GREY;
	startFirstTrial();
}

var startFirstTrial = function() {
	removeLoadingText();
	drawTrialDisplay(expVariables[currTrialN]); 
}

var inTextDisplay = false;
var inRatingDisplay = false;

var showTextDisplayTimer;
var displayTime=2000;

/*
  * Draws individual trial display
  * Updates trial information
  * Draws images for trial
  * Adds rating scale to display
  * @param {python dictionary/js object} trialVariables: has keys and values for trial parameters
*/
var instructions;
var textToRate;
var skipAnswerDisplay;
var drawTrialDisplay = function(trialVariables) {
	//if (trialVariables['TrialType'] == 'RateQuestion') {
		drawRatingDisplay(trialVariables);
	//} //else {
	//	if (skipAnswerDisplay) {
	//		pushTrialInfo();
	//		endTrial();
	//		skipAnswerDisplay=false;
	//}	// else {
	//		drawTextDisplay(trialVariables);
	//	}
	//}
}

var button, buttonText;
var drawRatingDisplay = function(trialVariables) {
	// condition is a dictionary - each key can be used to set trial conditions
	inTextDisplay=false;
	inRatingDisplay=true;
	ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
	if (allTrials.length == currTrialN) {
		pushTrialInfo();
	}

	var instructionsText='How curious are you about the following question?';

	if (instructions == null) {
		instructions = new textBox(instructions, instructionsText, 22, BLACK);
	} else {
		instructions.removeText();
	}
	instructions.setText(instructionsText);
	instructions.showText(0, canvas.height/2 - 80);
	instructions.textObj.setAttribute("font-family","Gill Sans");

	var text=trialVariables['Question'];
    if (textToRate == null) {
        textToRate = new textBox(textToRate, text, 24, BLACK);
    } else {
        textToRate.removeText();
    }
    textToRate.setText(text);
    textToRate.showText(0, canvas.height/2 - 30);
    textToRate.textObj.setAttribute("font-family","Gill Sans");


	if (scale == null) { // set up scale for first trial
		scale = new ratingScale(trialVariables['rs_min'],trialVariables['rs_max'],trialVariables['rs_tickIncrement'],trialVariables['rs_increment'],canvas.width/2,canvas.height/2 + 20, trialVariables['rs_labelNames']);
	} else {
		scale.removeScale(); // removes current scale
	}
	scale.setRatingScaleParams(trialVariables['rs_min'],trialVariables['rs_max'],trialVariables['rs_tickIncrement'],trialVariables['rs_increment'],canvas.width/2,canvas.height/2 + 20, trialVariables['rs_labelNames']);
	scale.drawRatingScale(canvas.width/2,canvas.height/2 + 20); // draws/redraws scale
	for (i=0;i<scale.tickLabels.length;i++) {
		var label = scale.tickLabels[i];
		label.setAttribute("font-family","Gill Sans");
	}

    if (button == null) {
        button = new rect(button);
    } else {
        button.removeRect();
    }
    button.showRect(canvas.width/2, canvas.height/5 + canvas.height/2, WHITE, 70, 20);
    button.rectObj.setAttribute("rx","7");
    button.rectObj.setAttribute("ry","7");
    button.rectObj.style.stroke="black";
    //button.rectObj.style.strokeWidth=".2";

    if (buttonText == null) {
        buttonText = new textBox(buttonText, 'Know', 18, BLACK);
    } else {
        buttonText.removeText();
    }
    buttonText.setText('Know');
    buttonText.showText(0, canvas.height/5 + canvas.height/2+16);

    button.rectObj.setAttribute("onmouseover", "changeButtonColor('#d9d9d9')");
    button.rectObj.setAttribute("onmouseout","changeButtonColor('#ffffff')")
    button.rectObj.setAttribute("onmousedown", "endTrial()");

}

var removeButton = function() {
	button.removeRect();
	buttonText.removeText();
}

var changeButtonColor = function(color) {
	button.rectObj.style.fill=color;
}

var drawTextDisplay = function(trialVariables) {
	removeButton();
	inRatingDisplay=false;
	inTextDisplay=true;
	ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);

	var text=trialVariables['Question'];

	if (textToRate == null) {
		textToRate = new textBox(textToRate, text, 22, BLACK);
	} else {
		textToRate.removeText();
	}
	textToRate.setText(text);
	textToRate.showText(0, canvas.height/2 - 30);
	textToRate.textObj.setAttribute("font-family","Gill Sans");

	showTextDisplayTimer = setTimeout( function() {
		inTextDisplay = false;
		textToRate.removeText();
		drawRatingDisplay(trialVariables);
	}, displayTime);
}

/*
 * Initializes set of trial information and adds to allTrials
 * Checks for any special key presses (associated with stimuli) and adds to specialKeys
 * Sets start time for trial
*/
var pushTrialInfo = function() {
	var currTrial = new trial({'trialN':currTrialN, 'Question':expVariables[currTrialN]['Question'], 'QuestionNum':expVariables[currTrialN]['QuestionNum'], 'Answer':expVariables[currTrialN]['Answer'], 'TrialType':expVariables[currTrialN]['TrialType']});
	allTrials.push(currTrial);

	t1 = performance.now(); // start timer for this trial
	t1_UNIX = Date.now();

	allTrials[currTrialN].trialStartTime = t1;
	allTrials[currTrialN].trialStartTime_UNIX = t1_UNIX;
}

/*
  * Does all clean up for trial
  * Get trial duration / reaction time
*/
var endTrial = function() {
	t2 = performance.now();
	var i;
	if (!('rating' in allTrials[currTrialN])) { // did not respond
		skipAnswerDisplay = true;
		allTrials[currTrialN].rt = t2 - t1; 
		allTrials[currTrialN].receivedResponse = false;
		if (expVariables[currTrialN]['TrialType'] == 'RateQuestion') {
			allTrials[currTrialN].rating = 'Know';
		} else {
			allTrials[currTrialN].rating = 'NaN';
		}
		allTrials[currTrialN].trialEndTime = t2;
		allTrials[currTrialN].trialDuration = t2 - t1;
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
	textToRate.removeText();
	currTrialN+=1; // iterate to next trial
	if (currTrialN < expVariables.length) {
		drawTrialDisplay(expVariables[currTrialN]);
	} else {
		var strExpResults = JSON.stringify(allTrials);
		document.getElementById('experimentResults').value = strExpResults;

		drawLoadingText();

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
	resizeWindow();
}

// code below from AL and JSPsych

/* ENTER FULL SCREEN */
var screenmode = {
    type: 'fullscreen',
    message: '<h3 style="color:black;">This experiment must be run in full-screen.</h3><br>',
    fullscreen_mode: true,
    delay_after: 200, // add little delay to make sure screen size is updated correctly
}

var display_element = document.createElement('div');

function createFullScreenButtonDisp() {
    display_element.innerHTML = screenmode.message + '<button id="jspsych-fullscreen-btn" class="jspsych-btn">Enter full screen mode</button>';

    document.getElementById("content").appendChild(display_element);
    document.getElementById("jspsych-fullscreen-btn").addEventListener("click", enterFullScreen);
}

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
    setTimeout(startExperiment,500); // wait before starting experiment, so display isn't redrawn because of window size change
}

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


// code below from AL
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

// Check for reasons to exclude
var browserInfo = getBrowserInfo();
var browserExclude = !browserInfo.browser.includes('Chrome');

var exclude = browserExclude;
if (exclude){
    display_element.innerHTML = '<p style="color:black;">This experiment is only supported in Google Chrome.<br>' +
                  'Please copy the full URL and reopen it in a Chrome browser window. <br>' +
                  'Leave the MTurk window open in your current browser.<br>' +
                  'Return to the MTurk window to submit after receiving your code in the Chrome browser.</p>';
    document.getElementById("content").appendChild(display_element);
} else {
    createFullScreenButtonDisp();
}
