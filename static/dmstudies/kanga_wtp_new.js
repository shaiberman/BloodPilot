console.log("loaded kanga.js ");
const LIGHTBLUE = "#99ccff";

// var expVariables set in HTML

var allKeyPresses = [];

var currTrialN = 0;

var specialKeys = [];

var expResults = [];
var allTrials = [];

/* DISPLAY */
// canvas is the drawing platform on which stimuli are draw
var canvas = document.getElementById("myCanvas");
// set canvas width and height to that of browser window (inner excludes bookmarks bar, etc.)
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
var ctx = document.getElementById('myCanvas').getContext('2d');

var svg = document.getElementById("mySVG");
svg.setAttribute("width", (window.innerWidth).toString());
svg.setAttribute("height", (window.innerHeight).toString());

var widthPercent = .45;
var rescaleHeight = false;

/* TIMING */
var maxExperimentDuration = 600000; // 10min in ms
var confirmationTime = 500; // in ms
var tooSlowTime = 1000;
var answerDisplayTime = 4000;
var maxStimDuration = 8500;
var maxWorthDuration = 3500;
var triviaPause = 1500; // wait 1.5s after trivia display before accepting responses
var ratingPause = 500;
var postDecisionDelay = 2000; // after deciding to pay

var confirmTimer;
var inConfirmation = false;
var payPeriodTimer;
var decisionTimer;

var t1, t2;
var trialTimer;

/*
 * Called in the HTML
*/
var experimentTimer;
var endExperiment = false;
var startExperiment = function() {
	document.body.style.backgroundColor = GREY;
	drawTriviaDisplay(expVariables[currTrialN]); 
	experimentTimer = setTimeout(function() {
		endExperiment = true;
		//nextTrial();
	},maxExperimentDuration);
}

/*
  * Draws individual trial display
  * Updates trial information
  * Draws images for trial
  * Adds confirmation box to trial display
  * @param {python dictionary/js object} trialVariables: has keys and values for trial parameters
*/
var inTriviaDisplay = false;
var instructions;
var skipRect;
var payRect;
var skipText;
var payText;
var drawTriviaDisplay = function(trialVariables) {
	inTriviaDisplay = true;
	question = trialVariables['Question']

	if (allTrials.length == currTrialN) {
		pushTrialInfo();
	}
	allTrials[currTrialN]['Question'] = question;

	var fontSize = canvas.width * 0.03;

	var questionText = document.getElementById('html_text'); 
	questionText.innerHTML = question;
	questionText.style.fontFamily = "Gill Sans";
	questionText.style.fontSize = "xx-large";
	questionText.style.paddingTop = (canvas.height/2 - canvas.height/4).toString() + "px";
	questionText.style.lineHeight = "1.2";

	if (instructions == null) {
		instructions = new textBox(instructions, "", fontSize, GREY);
	} else {
		instructions.removeText();
	}
	instructions.showText(0, canvas.height/2 - 10);

	if (skipRect == null) {
		skipRect = new rect(skipRect, canvas.width * 0.02);
	} else {
		skipRect.removeRect();
	}
	skipRect.showRect(canvas.width/2 - canvas.width/4, canvas.height/2 + canvas.height/8, WHITE, canvas.width * 0.2, fontSize);

	if (skipText == null) {
		skipText = new textBox(skipText, "SKIP", canvas.width * 0.04, BLACK);
	} else {
		skipText.removeText();
	}
	skipText.showText(0 - canvas.width/4, canvas.height/2 + canvas.height/8 + fontSize - fontSize*0.1, fontSize);
	skipText.textObj.setAttribute("font-family","Gill Sans");

	if (payRect == null) {
		payRect = new rect(payRect, canvas.width * 0.02);
	} else {
		payRect.removeRect();
	}
	payRect.showRect(canvas.width/2 + canvas.width/4, canvas.height/2 + canvas.height/8, WHITE, canvas.width * 0.2, fontSize);

	payAmount = expVariables[currTrialN]['C_Pay'];
	if (payText == null) {
		payText = new textBox(payText, "PAY " + payAmount.toString() + " cents", fontSize, BLACK);
	} else {
		payText.removeText();
	}
	payText.setText("PAY "+payAmount.toString() + " cents");
	payText.showText(0+ canvas.width/4, canvas.height/2 + canvas.height/8 + fontSize - fontSize*0.1, fontSize);
	payText.textObj.setAttribute("font-family","Gill Sans");

}

/*
  * Remove question from trivia display
*/
var removeQuestionText = function() {
	var questionText = document.getElementById('html_text'); 
	questionText.innerHTML = "";
}

var removeTriviaDisplay = function() {
	if (removeQuestionText!=null) {
		removeQuestionText();
	}
	instructions.removeText();
	skipRect.removeRect();
	payRect.removeRect();
 	skipText.removeText();
	payText.removeText();
 }

/*
 * Initializes set of trial information and adds to allTrials
 * Checks for any special key presses (associated with stimuli) and adds to specialKeys
 * Sets start time for trial
 * Sets timer for trial
*/
var pushTrialInfo = function() {
	trialVariables = expVariables[currTrialN];
	trialVariables['C_Trial'] = currTrialN;
	var currTrial = new trial(trialVariables);
	allTrials.push(currTrial);
	specialKeys = ['q','t','p','1','2','3','4','5'];
	
	t1 = performance.now(); // start timer for this trial
	allTrials[currTrialN].C_QPresent = t1;
	trialTimer = setTimeout(drawConfirmationDisplay,maxStimDuration);
}

/*
  * Checks key presses and moves to next trial
  * Checks array of special keys
  * 	- if current key pressed is in specialKey, moves to next trial
*/
var triviaDisplayResponseKeys = ['q','t','p'];
var rateAnswerResponseKeys = ['1','2','3','4','5'];
var swkKeys = {'q':'S','t':'W','p':'K'};
var keyIsDown = false; // keep track if key is still being held down - take one key press at a time
var checkKeyPress = function(e) {
	var timePressed = e.timeStamp; // does not seem to be compatible with all browsers - may get UNIX time instead of time relative to trial start
	// check that responses should be checked now
	var continueCheck = true;
	if (inTriviaDisplay && (e.timeStamp - allTrials[currTrialN]['C_QPresent'] < triviaPause)) {
		continueCheck = false;
	}
	if (inRateAnswerDisplay && (e.timeStamp - allTrials[currTrialN]['C_WorthPresent'] < ratingPause)) {
		continueCheck = false;
	}
	if (continueCheck && (inTriviaDisplay || inRateAnswerDisplay) && keyIsDown == false && timePressed > t1 && !svg.contains(blankScreenCover)) { 
		keyIsDown = true;
		t2 = timePressed;
		// should check if timepressed is after trial starts
		if (specialKeys.indexOf(e.key) > -1 && currTrialN == allTrials.length - 1) { 
			clearTimeout(trialTimer);
			clearTimeout(confirmTimer);
			clearTimeout(rateAnswerDisplayTimer);
			if (inTriviaDisplay && triviaDisplayResponseKeys.indexOf(e.key) > -1) {
				if (currTrialN < expVariables.length) {
					inTriviaDisplay = false;
					allTrials[currTrialN].rsp = e.key;
					allTrials[currTrialN].C_SWK = swkKeys[e.key];
					allTrials[currTrialN].C_SWK_rt = t2 - allTrials[currTrialN]['C_QPresent'];
					drawConfirmationDisplay();
				}
			} else if (inRateAnswerDisplay && rateAnswerResponseKeys.indexOf(e.key) > -1) {
				allTrials[currTrialN].C_Worth = e.key;
				allTrials[currTrialN].C_Worth_rt = t2 - allTrials[currTrialN]['C_WorthPresent'];
				drawConfirmationDisplay();
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
	allTrials[currTrialN].C_TrialEnd = performance.now();
	//confirmationRect.removeRect();
	currTrialN+=1; // iterate to next trial
	inConfirmation = false;
	// double check performance.now()
	if (endExperiment || performance.now() > maxExperimentDuration || currTrialN >= expVariables.length) {
		clearTimeout(experimentTimer);
		instructions.removeText();

		var strExpResults = JSON.stringify(allTrials);
		document.getElementById('experimentResults').value = strExpResults;

		drawLoadingText();

		document.getElementById('exp').submit()
	} else { // experiment has not ended 
		drawTriviaDisplay(expVariables[currTrialN]);
	} 
}

/*
var inWaitDisplay = false;
var drawWaitDisplay = function(payTime) {
	removeTriviaDisplay();
	var questionText = document.getElementById('html_text'); 
	questionText.innerHTML = "...";
	questionText.style.fontSize = "xxx-large";
	questionText.style.paddingTop = (canvas.height/2 - canvas.height/8).toString() + "px";
	if (inWaitDisplay == false) {
		inWaitDisplay = true;
		payTime = expVariables[currTrialN]['C_Wait']*1000;
		allTrials[currTrialN].C_WaitStart = performance.now();
		payPeriodTimer = setTimeout( function() {
			drawAnswerDisplay();
		},payTime);
	}
}
*/

var inAnswerDisplay = false;
var drawAnswerDisplay = function() {
	removeTriviaDisplay();
	var questionText = document.getElementById('html_text'); 
	questionText.innerHTML = expVariables[currTrialN]['Answer']; 
	questionText.style.paddingTop = (canvas.height/2 - canvas.height/8).toString() + "px";
	if (inAnswerDisplay == false) {
		inAnswerDisplay = true;
		//inWaitDisplay = false;
		allTrials[currTrialN].C_AnswerPresent = performance.now();
		payPeriodTimer = setTimeout( function() {
			drawRateAnswerDisplay();
		},answerDisplayTime);
	}
}

var one, two, three, four, five;
var oneBox, twoBox, threeBox, fourBox, fiveBox;
var numbers = [one, two, three, four, five];
var numberBoxes = [oneBox, twoBox, threeBox, fourBox, fiveBox];
var drawNumbers = function() {
	for (var i=0;i<numbers.length;i++) {
		var fontSize = canvas.width * 0.08;
		if (numberBoxes[i] == null) {
			numberBoxes[i] = new rect(numberBoxes[i], canvas.width * 0.02);
		} else {
			numberBoxes[i].removeRect();
		}
		numberBoxes[i].showRect(canvas.width/2 - canvas.width/4 + canvas.width/8*i, canvas.height/2 + canvas.height/8, WHITE, fontSize, fontSize);

		if (numbers[i] == null) {
			numbers[i] = new textBox(numbers[i], (i+1).toString(), canvas.width * 0.04, BLACK);
		} else {
			numbers[i].removeText();
		}
		numbers[i].showText(0 - canvas.width/4 + canvas.width/8*i, canvas.height/2 + canvas.height/8 + fontSize - fontSize*0.1, fontSize);
		numbers[i].textObj.setAttribute("font-family","Gill Sans");
	}
}

var removeRateAnswerDisplay = function() {
	for (var i=0;i<numbers.length;i++) {
		number = numbers[i];
		numberBox = numberBoxes[i];
		if (number!=null) {
			number.removeText();
		}
		if (numberBox!=null) {
			numberBox.removeRect();
		}
	}
	removeQuestionText();
	if (extremelyText!=null) {
		extremelyText.removeText();
	}
	if (notAtAllText!=null) {
		notAtAllText.removeText();
	}
}

var rateAnswerDisplayTimer;
var extremelyText;
var notAtAllText;
var inRateAnswerDisplay = false;
var drawRateAnswerDisplay = function() {
	var questionText = document.getElementById('html_text'); 
	payAmount = expVariables[currTrialN]['C_Pay'];
	questionText.innerHTML = "Was the answer worth "+payAmount.toString()+" cents?";
	var fontSize = canvas.width * 0.03;
	questionText.style.paddingTop = (canvas.height/2 - canvas.height/4).toString() + "px";
	drawNumbers();

	if (notAtAllText == null) {
		notAtAllText = new textBox(notAtAllText, "Not at all", canvas.width * 0.04, BLACK);
	} else {
		notAtAllText.removeText();
	}
	notAtAllText.showText(0 - canvas.width/4 + canvas.width/8*-1, canvas.height/2 + canvas.height/8 + fontSize + fontSize*.5, fontSize);
	notAtAllText.textObj.setAttribute("font-family","Gill Sans");

	if (extremelyText == null) {
		extremelyText = new textBox(extremelyText, "Extremely", canvas.width * 0.04, BLACK);
	} else {
		extremelyText.removeText();
	}
	extremelyText.showText(0 - canvas.width/4 + canvas.width/8*5, canvas.height/2 + canvas.height/8 + fontSize + fontSize*.5, fontSize);
	extremelyText.textObj.setAttribute("font-family","Gill Sans");
	
	if (inRateAnswerDisplay == false) {
		inRateAnswerDisplay = true;
		inAnswerDisplay = false;
		allTrials[currTrialN].C_WorthPresent = performance.now();
		rateAnswerDisplayTimer = setTimeout(function() {
			inRateAnswerDisplay = false;
			drawTooSlowDisplay();
		},maxWorthDuration);
	}
}

var inTooSlowScreen = false;
var drawTooSlowDisplay = function() {
	removeTriviaDisplay();
	removeRateAnswerDisplay();
	var fontSize = canvas.width * 0.03;
	var questionText = document.getElementById('html_text'); 
	questionText.innerHTML = "TOO SLOW";
	questionText.style.paddingTop = (canvas.height/2 - canvas.height/8).toString() + "px";
	questionText.style.fontFamily = "Gill Sans";
	questionText.style.fontSize = "xxx-large";

	if (inTooSlowScreen == false) {
		inTooSlowScreen = true;
		confirmTimer = setTimeout(function() {
			inTooSlowScreen = false;
			nextTrial();
		},tooSlowTime);
	}
}

var horzCross;
var vertCross;
var drawFixationDisplay = function() {
	removeTriviaDisplay();
	removeRateAnswerDisplay();
	if (horzCross == null) {
		horzCross = new rect(horzCross, canvas.width * 0.02);
	} else {
		horzCross.removeRect();
	}
	horzCross.showRect(canvas.width/2, canvas.height/2, BLACK, canvas.width * 0.03, canvas.width * 0.005);

	if (vertCross == null) {
		vertCross = new rect(vertCross, canvas.width * 0.02);
	} else {
		vertCross.removeRect();
	}
	vertCross.showRect(canvas.width/2, canvas.height/2 - canvas.width * 0.03/2 + canvas.width * 0.005/2, BLACK, canvas.width * 0.005, canvas.width * 0.03);
	confirmTimer = setTimeout(function() {
		horzCross.removeRect();
		vertCross.removeRect();
		nextTrial();
	},expVariables[currTrialN]['jitter']*1000);
}

/*
  * Does all clean up for trial
  * Clears trialTimer
  * Get trial duration / reaction time
  * Changes color of confirmation box
  * Sets timer for confirmation and iterates to next trial at the end of confirmation
*/
var drawConfirmationDisplay = function() {
	t2 = performance.now();
	clearTimeout(trialTimer);
	var color;
	if (inTriviaDisplay && t2 - t1 > maxStimDuration) { // did not respond
		drawNextTrial = true;
	} else {
		color = LIGHTBLUE;
	}
	inTriviaDisplay = false;
	//inWaitDisplay = false;
	inAnswerDisplay = false;
	inRateAnswerDisplay = false;
	inTooSlowScreen = false;

	drawFixation = true;
	drawConfirmation = true;
	if (rateAnswerResponseKeys.indexOf(allTrials[currTrialN].C_Worth) > -1) {
		numberBoxes[parseInt(allTrials[currTrialN].C_Worth) - 1].setColor(color);
	} else if (allTrials[currTrialN].rsp == 'q') {
		skipRect.setColor(color);
	} else if (allTrials[currTrialN].rsp == 'p') {
		payRect.setColor(color);
		drawFixation = false;
	} else {
		drawFixation = false; 
		drawConfirmation = false;
		drawTooSlowDisplay();
	}
	if (drawConfirmation && drawFixation) {
		confirmTimer = setTimeout(function() {
			inConfirmation = false;
			drawFixationDisplay();
		},confirmationTime);
	} else if (drawConfirmation) {
		confirmTimer = setTimeout(function() {
			inConfirmation = false;
			callNextDisplay();
		},confirmationTime);
	}
}

var callNextDisplay = function() {
	clearTimeout(confirmTimer);
	inConfirmation = false;
	if ('C_Worth' in allTrials[currTrialN] && rateAnswerResponseKeys.indexOf(allTrials[currTrialN].C_Worth) > -1) {
		removeRateAnswerDisplay();
		nextTrial();
	} else if (allTrials[currTrialN].rsp == 'q') {
		nextTrial();
	} else if (allTrials[currTrialN].rsp == 'p') {
	    decisionTimer = setTimeout(function() {
			drawAnswerDisplay();
		},postDecisionDelay);
	}  else {
		drawTooSlowDisplay();
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
	svg.setAttribute("width", (winWidth).toString());
	svg.setAttribute("height", (winHeight).toString());
	if (svg.contains(blankScreenCover)) {
		svg.removeChild(blankScreenCover);
	}
	if (svg.contains(alertText)) {
		svg.removeChild(alertText);
	}
	if (inTriviaDisplay) {
		drawTriviaDisplay(expVariables[currTrialN]);
	//} else if (inWaitDisplay) {
	//	drawWaitDisplay();
	} else if (inAnswerDisplay) {
		drawAnswerDisplay();
	} else if (inRateAnswerDisplay) {
		drawRateAnswerDisplay();
	}
}

window.onresize = function() {
	resizeWindow();
}
window.addEventListener("keypress", checkKeyPress);
window.addEventListener("keyup", setKeyUp);


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
