var socketio;
var activeChat;
var sentiments = {
    "positive" : "😄",
    "negative" : "🙁",
    "neutral" : "😐"
}
var video_dict = {};
var keys = new Array();
var active_users = new Array();
var stream, imageCapture; 


$(document).ready(function(){
    (function(){
        document.documentElement.className = document.documentElement.className.replace(/(^|\s)no-js(\s|$)/, '$1$2') + (' js '); 
    })();

    namespace = '';
    socketio = io.connect();

    // var stream, imageCapture; 

    function getMediaStream()
    { 
        window.navigator.mediaDevices.getUserMedia({video: true})
        .then(function(mediaStream)
        { 
            stream = mediaStream; 
            let mediaStreamTrack = mediaStream.getVideoTracks()[0];
            imageCapture = new ImageCapture(mediaStreamTrack);
            // console.log(imageCapture);
        })
        .catch(error);
    }

    function error(error)
    { 
        console.error('error:', error); 
    }

    function asyncPhoto(){
        setTimeout(takePhoto,0);
    }
    function takePhoto(img)
    { 
        // const img = img || document.querySelector('img');
        // user_name = $("#current_user").text();
        // user_name = user_name.substring(user_name.lastIndexOf("<")+1,user_name.lastIndexOf(">")).substring(5,user_name.length);
        // var img1 = document.querySelector('#'+user_name);
        // while(true){
        imageCapture.takePhoto()
        .then(blob => {

            // console.log('printing blob inside takePhoto');
            // console.log(blob);
            socketio.emit('frame_available',{'frame':blob});
            // let url = window.URL.createObjectURL(blob);
            // console.log('printing url inside takePhoto');
            // console.log(url);
            // img.src = url;
            // window.URL.revokeObjectURL(url); 
        })
        .catch(error);
            // await new Promise(r=> setTimeout(r, 30));
        // }
    };

    getMediaStream();
    
    // Functions for handling socket events
    socketio.on('connect', function() {
            // console.log('new socket connected');
            user_name = $("#current_user").text();
            var user_name = user_name.substring(user_name.lastIndexOf("<")+1,user_name.lastIndexOf(">")).substring(5,user_name.length);  
            // video_content = "<div class='polaroid'><video preload='auto' id='" +user_name+"'></video></div>";
            video_content = "<div class='polaroid'><img  id='" +user_name+"'></div>";
            // video_content += "<div class='container'>";
            // video_content += "<p><b>"+ user_name +"</b><b></p></div></div>";
            $('#video_stream').append(video_content);
            socketio.emit('connected',{current_user:user_name});
            keys.push(user_name);
            activeChat = 'group';
    });


    // The active chat will firstly be the group chat
    // join a room
    $('#join').click(function(event){
        event.preventDefault();
        // console.log("join event called")
        user_namet = $("#current_user").text();
        user_name = user_namet.substring(user_namet.lastIndexOf("<")+1,user_namet.lastIndexOf(">"));
        // console.log('user_name = '+user_name);
        active_users.push(user_name.substring(5,user_name.length));
        keys.push(user_name);
        img = document.querySelector('#'+user_name.substring(5,user_name.length));
        console.log(user_name.substring(5,user_name.length));
        setInterval(function(){takePhoto(img);},200);
        // asyncPhoto();
        socketio.emit('joined',{user:user_name});
        return false;
    });

    socketio.on("update_users",function(data){
        // console.log('update_users called');
        // console.log(data);
        usr = data['users'];
        active_users = usr;
        // console.log('active_users1 = '+active_users);

        var content = "<div id='sidebar-user-box'><span class='collection-item' id='slider-username'>public chat</span></div><br>";
        video_content = "";
        var i;
        
        for(i=0;i<usr.length;i++){
        // content += '<p>'+usr[i]+'</p>';
            content += "<div id='sidebar-user-box'><span class='collection-item' id='slider-username'>"
            + "<div class = 'chip'>"
            + "<img src='https://img.icons8.com/color/48/000000/online.png'>" // Avatar 
            +usr[i] + "</div>"
            +'</span></div><br>';            
        }

        $(document).on('click', '#sidebar-user-box', function (e) {
            e.preventDefault();
            // console.log(e.target.innerText);
            // console.log('onclick event invoked');
            e.preventDefault();
            activeChat = e.target.innerText;
            // console.log('activeChat = '+activeChat);
            if(activeChat == 'public chat'){
                // console.log('Inside if');
                activeChat = 'group';
            }
            user_namet = $("#current_user").text();
            user_name = user_namet.substring(user_namet.lastIndexOf("<")+1,user_namet.lastIndexOf(">")).substring(5,user_namet.length);
            socketio.emit('update_chat',{destination:activeChat,origin:user_name});
            });
            // console.log('content = '+content);
            $('#origins-list').html(content); 
    });

    $(document).on('click', '#sidebar-user-box', function (e) {
        e.preventDefault();
        // console.log(e.target.innerText);
        // console.log('onclick event invoked');
        e.preventDefault();
        activeChat = e.target.innerText;
    });

    socketio.on('join',function(){
        // console.log('Caught join event');
    });

    $("#send").click(function(event){
        event.preventDefault();
        // console.log('message button clicked')
        // console.log('active chat = '+activeChat);
        var msg = $("#message").val();
        $('#message').val('');
        // console.log('msg = ' + msg);
        user_name = $("#current_user").text();
        user_name = user_name.substring(user_name.lastIndexOf("<")+1,user_name.lastIndexOf(">")).substring(5,user_name.length);
        // $('#chat-messages').append("<p>"+user_name+":"+msg+"</p> \n");
        socketio.emit("add_message",{origin:user_name,message:msg,destination:activeChat});
    });

    socketio.on('frame_available',function(data){
        // console.log('caught frame_available event');
        // console.log('username = ' + data['user']);
        //frame is received as a blob
        frame = data['frame'];
        var blob = new Blob( [new Uint8Array(frame)],{ type: "image/jpeg" } );
        // console.log('frame in frame_available = ');
        // console.log(frame);
        var urlCreator = window.URL || window.webkitURL;
        var imageUrl = urlCreator.createObjectURL(blob);
        var uname = data['user'];
    
        video_dict[uname] = frame;

        if(active_users.includes(uname)){

            var img1 = document.querySelector('#'+uname);
            img1.src = imageUrl;
            keys.push(uname);
            
        }
        // console.log('video_stream html');
        video_stream_html = $('#video_stream').html();
        // console.log(video_stream_html);
    });
    socketio.on('update_video',function(data){
        // console.log('Invoked update video event');
        // console.log(data);
    });

    socketio.on('update_messages',function(data){
        msgs = data['messages'];
        var i;
        var content = '';
        user_name = $("#current_user").text();
        user_name = user_name.substring(user_name.lastIndexOf("<")+1,user_name.lastIndexOf(">")).substring(5,user_name.length);

        for(i=0;i<msgs.length;i++){
        // console.log('printing message');
        // console.log(msgs[i])
        var tmpMsg = '<div class="chip">'+ msgs[i]['origin'] + ': </div>';
        var sentiment = msgs[i]['sentiment'];
        
        // console.log('printing message = ');
        // console.log(emojione.toImage(msgs[i]['message']));
        
        if(user_name == msgs[i]['origin']){
            content += '<div style="float:right;clear:both;display:table;">'
            + tmpMsg + msgs[i]['message'] + '</div>';
            content += '<div style="float:left;">'+sentiments[sentiment]+'</div><br/>';
            }

        else{
            content += '<div style="float:left;display:table;clear:both;">'+tmpMsg + msgs[i]['message'] +'</div>';
            content += '<div style="float:right;">'+sentiments[sentiment]+'</div><br/>'
        }
        }

        // console.log('content = '+content);

        $('#chat-messages').html(content);
        var element = document.getElementById('chat-messages');
        element.scrollTop = element.scrollHeight;
    });
});