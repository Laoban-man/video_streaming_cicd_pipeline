$(document).ready(function(){
                    
    // **** Connect SocketIO ******    
    // start up a SocketIO connection to the server 
    var socket = io.connect('https://' + document.domain + ':' + location.port);
    // Event handler for new connections.
    // The callback function is invoked when a connection with the server is established.
    socket.on('connect', function() {

        // Successful connection message
        socket.emit('connection_msg', {data: 'I\'m connected!'});
    });
    socket.on("my_response",(arg) => {
	const resultsText = document.querySelector('h1#results');
	console.log(arg["data"]);
	resultsText.textContent = arg["data"];
    });
    
    // **** Camera Image Settings ****
let mediaRecorder;
let recordedBlobs;
const codecPreferences = document.querySelector('#codecPreferences');
const errorMsgElement = document.querySelector('span#errorMsg');
const recordedVideo = document.querySelector('video#recorded');
const recordButton = document.querySelector('button#record');
recordButton.addEventListener('click', () => {
  if (recordButton.textContent === 'Start Recording') {
    startRecording();
  } else {
    stopRecording();
    recordButton.textContent = 'Start Recording';
    playButton.disabled = false;
    trainButton.disabled = false;
    classifyButton.disabled = false;
    codecPreferences.disabled = false;
  }
});

const playButton = document.querySelector('button#play');
playButton.addEventListener('click', () => {
  const mimeType = codecPreferences.options[codecPreferences.selectedIndex].value.split(';', 1)[0];
  const superBuffer = new Blob(recordedBlobs, {type: mimeType});
  recordedVideo.src = null;
  recordedVideo.srcObject = null;
  recordedVideo.src = window.URL.createObjectURL(superBuffer);
  recordedVideo.controls = true;
  recordedVideo.play();
});

const trainButton = document.querySelector('button#train');
trainButton.addEventListener('click', () => {
  const blob = new Blob(recordedBlobs, {type: 'video/webm'});
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  send_data1(blob);
});
	
const classifyButton = document.querySelector('button#classify');
classifyButton.addEventListener('click', () => {
  const blob = new Blob(recordedBlobs, {type: 'video/webm'});
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  send_data2(blob);
});

function handleDataAvailable(event) {
  console.log('handleDataAvailable', event);
  if (event.data && event.data.size > 0) {
    recordedBlobs.push(event.data);
  }
}

function getSupportedMimeTypes() {
  const possibleTypes = [
    'video/webm;codecs=vp9,opus',
    'video/webm;codecs=vp8,opus',
    'video/webm;codecs=h264,opus',
    'video/mp4;codecs=h264,aac',
  ];
  return possibleTypes.filter(mimeType => {
    return MediaRecorder.isTypeSupported(mimeType);
  });
}

function startRecording() {
  recordedBlobs = [];
  const mimeType = codecPreferences.options[codecPreferences.selectedIndex].value;
  const options = {mimeType};

  try {
    mediaRecorder = new MediaRecorder(window.stream, options);
  } catch (e) {
    console.error('Exception while creating MediaRecorder:', e);
    errorMsgElement.innerHTML = `Exception while creating MediaRecorder: ${JSON.stringify(e)}`;
    return;
  }

  console.log('Created MediaRecorder', mediaRecorder, 'with options', options);
  recordButton.textContent = 'Stop Recording';
  playButton.disabled = true;
  trainButton.disabled = true;
  classifyButton.disabled = true;
  codecPreferences.disabled = true;
  mediaRecorder.onstop = (event) => {
    console.log('Recorder stopped: ', event);
    console.log('Recorded Blobs: ', recordedBlobs);
  };
  mediaRecorder.ondataavailable = handleDataAvailable;
  mediaRecorder.start();
  console.log('MediaRecorder started', mediaRecorder);
}

function stopRecording() {
  mediaRecorder.stop();
}

function handleSuccess(stream) {
  recordButton.disabled = false;
  console.log('getUserMedia() got stream:', stream);
  window.stream = stream;

  const gumVideo = document.querySelector('video#gum');
  gumVideo.srcObject = stream;

  getSupportedMimeTypes().forEach(mimeType => {
    const option = document.createElement('option');
    option.value = mimeType;
    option.innerText = option.value;
    codecPreferences.appendChild(option);
  });
  codecPreferences.disabled = false;
}

async function init(constraints) {
  try {
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    handleSuccess(stream);
  } catch (e) {
    console.error('navigator.getUserMedia error:', e);
    errorMsgElement.innerHTML = `navigator.getUserMedia error:${e.toString()}`;
  }
}

document.querySelector('button#start').addEventListener('click', async () => {
  document.querySelector('button#start').disabled = true;
  const hasEchoCancellation = document.querySelector('#echoCancellation').checked;
  const constraints = {
    audio: {
      echoCancellation: {exact: hasEchoCancellation}
    },
    video: {
      width: 1280, height: 720
    }
  };
  console.log('Using media constraints:', constraints);
  await init(constraints);
});
function send_data1(mlType,img){         
        console.log([mlType,img]);
	console.log("emitting");
	socket.emit('train_img', {data:[mlType,img]});
};
function send_data2(mlType,img){
        console.log([mlType,img]);
        console.log("emitting");
        socket.emit('classify_img', {data:[mlType,img]});
};
    //captureButton.addEventListener('click', () => {  
      //  var drawImage = context.drawImage(player, 0, 0, canvas.width, canvas.height);
        //var imgData = context.getImageData(0, 0, canvas.width, canvas.width);
        //console.log(imgData);
        //var img = canvas.toDataURL("image/png");
        // console.log(img);
        //$('#canvas2').html(imgData);           
        // *** SocketIO - send image to server side with event 'send_img' ***
        //send_data(mlType,img);
        //socket.emit('send_img', {data: img});
        // Stop all video streams.
        //player.srcObject.getVideoTracks().forEach(track => track.stop()); 
    //});
    
    navigator.mediaDevices.getUserMedia(constraints)
    .then((stream) => {
    	    // Attach the video stream to the video element and autoplay.
        player.srcObject = stream;
    });
    
    socket.on('my_response', function(msg) {
        console.log(arr);
        $('#data').html(arr);         
    });

});         // end of document ready function
