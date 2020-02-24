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
var updated_users = new Array();

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
        imageCapture.takePhoto()
        .then(blob => {
            socketio.emit('frame_available',{'frame':blob});
        })
        .catch(error);
    };

    getMediaStream();
    
    socketio.on('connect', function() {
            user_name = $("#current_user").text();
            var user_name = user_name.substring(user_name.lastIndexOf("<")+1,user_name.lastIndexOf(">")).substring(5,user_name.length);  
            // video_content = "<div class='polaroid'><img  id='" +user_name+"'></div>";
            // video_content += "<div class='container'>";
            // video_content += "<p><b>"+ user_name +"</b><b></p></div></div>";
            // $('#video_stream').append(video_content);
            socketio.emit('connected',{current_user:user_name});
            activeChat = 'group';
    });


    // The active chat will firstly be the group chat
    // join a room
    $('#join').click(function(event){
        event.preventDefault();
        user_name = $("#current_user").text();
        user_name = user_name.substring(user_name.lastIndexOf("<")+1,user_name.lastIndexOf(">"));
        active_users.push(user_name.substring(5,user_name.length));
        keys.push(user_name);
        img = document.querySelector('#'+user_name.substring(5,user_name.length));
        setInterval(function(){takePhoto(img);},200);
        socketio.emit('joined',{user:user_name});
        return false;
    });

    socketio.on("update_users",function(data){
        usr = data['users'];
        active_users = usr;

        var content = "<div id='sidebar-user-box'><span class='collection-item' id='slider-username'>public chat</span></div><br>";
        var i;
        
        for(i=0;i<usr.length;i++){
            content += "<div id='sidebar-user-box'><span class='collection-item' id='slider-username'>"
            + "<div class = 'chip'>"
            + "<img src='https://img.icons8.com/color/48/000000/online.png'>" // Avatar 
            +usr[i] + "</div>"
            +'</span></div><br>';     
            if(!(updated_users.includes(usr[i]))){
                video_content = "";
                video_content += "<div class='polaroid'><img  id='" +usr[i]+"'></div>";
                video_content += "<div class='container'>";
                video_content += "<p><b>"+ usr[i] +"</b><b></p></div></div>";
                updated_users.push(usr[i]);
                $('#video_stream').append(video_content);
                video_stream_html = $('#video_stream').html();
            }
        }

        
        $(document).on('click', '#sidebar-user-box', function (e) {
            e.preventDefault();
            activeChat = e.target.innerText;
            if(activeChat == 'public chat'){
                activeChat = 'group';
            }
            user_namet = $("#current_user").text();
            user_name = user_namet.substring(user_namet.lastIndexOf("<")+1,user_namet.lastIndexOf(">")).substring(5,user_namet.length);
            socketio.emit('update_chat',{destination:activeChat,origin:user_name});
            });
            $('#origins-list').html(content); 
            // $('#video_stream').append(video_content);       
    });

    $(document).on('click', '#sidebar-user-box', function (e) {
        e.preventDefault();
        activeChat = e.target.innerText;
    });

    socketio.on('join',function(){
    });

    $("#send").click(function(event){
        event.preventDefault();
        var msg = $("#message").val();
        $('#message').val('');
        user_name = $("#current_user").text();
        user_name = user_name.substring(user_name.lastIndexOf("<")+1,user_name.lastIndexOf(">")).substring(5,user_name.length);
        socketio.emit("add_message",{origin:user_name,message:msg,destination:activeChat});
    });

    socketio.on('frame_available',function(data){
        frame = data['frame'];
        var blob = new Blob( [new Uint8Array(frame)],{ type: "image/jpeg" } );
        var urlCreator = window.URL || window.webkitURL;
        var imageUrl = urlCreator.createObjectURL(blob);
        var uname = data['user'];
    
        video_dict[uname] = frame;

        if(active_users.includes(uname)){

            var img1 = document.querySelector('#'+uname);
            img1.src = imageUrl;
            keys.push(uname);
            
        }
        video_stream_html = $('#video_stream').html();
    });

    socketio.on('update_messages',function(data){
        msgs = data['messages'];
        var i;
        var content = '';
        user_name = $("#current_user").text();
        user_name = user_name.substring(user_name.lastIndexOf("<")+1,user_name.lastIndexOf(">")).substring(5,user_name.length);

        for(i=0;i<msgs.length;i++){
        var tmpMsg = '<div class="chip">'+ msgs[i]['origin'] + ': </div>';
        var sentiment = msgs[i]['sentiment'];
        
        
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

        $('#chat-messages').html(content);
        var element = document.getElementById('chat-messages');
        element.scrollTop = element.scrollHeight;
    });
});