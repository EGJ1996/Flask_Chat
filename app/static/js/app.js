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
$(document).ready(function(){
    namespace = '';
    socketio = io.connect();

    socketio.on('connect', function() {
            console.log('socket connected');
            user_name = $("#current_user").text();
            user_name = user_name.substring(user_name.lastIndexOf("<")+1,user_name.lastIndexOf(">")).substring(5,user_name.length);
            console.log('username = '+user_name);
            socketio.emit('connected',{current_user:user_name});
            activeChat = 'group';
    });

    // The active chat will firstly be the group chat

    // join a room
    $('#join').click(function(event){
        console.log("join event called")
        user_name = $("#current_user").text();
        user_name = user_name.substring(user_name.lastIndexOf("<")+1,user_name.lastIndexOf(">"));
        console.log('user_name = '+user_name);  
        active_users.push(user_name.substring(5,user_name.length));
        socketio.emit('joined',{user:user_name});
        return false;
    });

    socketio.on("update_users",function(data){
        console.log('update_users called');
        console.log(data);
        usr = data['users'];
        active_users = usr;
        console.log('active_users1 = '+active_users);
        var content = "<div id='sidebar-user-box'><span class='collection-item' id='slider-username'>public chat</span></div><br>";
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
        console.log(e.target.innerText);
        console.log('onclick event invoked');
        e.preventDefault();
        activeChat = e.target.innerText;
        console.log('activeChat = '+activeChat);
        if(activeChat == 'public chat'){
            console.log('Inside if');
            activeChat = 'group';
        }
        user_name = $("#current_user").text();
        user_name = user_name.substring(user_name.lastIndexOf("<")+1,user_name.lastIndexOf(">")).substring(5,user_name.length);
        socketio.emit('update_chat',{destination:activeChat,origin:user_name});
        });
        console.log('content = '+content);
        $('#origins-list').html(content);
        
    });

    $(document).on('click', '#sidebar-user-box', function (e) {
        console.log(e.target.innerText);
        console.log('onclick event invoked');
        e.preventDefault();
        activeChat = e.target.innerText;
    });

    socketio.on('join',function(){
        console.log('Caught join event');
    });

    $("#send").click(function(event){
        console.log('message button clicked')
        console.log('active chat = '+activeChat);
        var msg = $("#message").val();
        $('#message').val('');
        console.log('msg = ' + msg);
        user_name = $("#current_user").text();
        user_name = user_name.substring(user_name.lastIndexOf("<")+1,user_name.lastIndexOf(">")).substring(5,user_name.length);
        // $('#chat-messages').append("<p>"+user_name+":"+msg+"</p> \n");
        socketio.emit("add_message",{origin:user_name,message:msg,destination:activeChat});
    });

    socketio.on('video_frame',function(data){
        console.log('Inside video_frame handler');
        console.log('username = ' + data['user']);
        frame = data['frame'];
        console.log('frame = '+frame);
        var arrayBufferView = new Uint8Array(frame);
        var blob = new Blob( [ arrayBufferView ], { type: "image/jpeg" } );
        var urlCreator = window.URL || window.webkitURL;
        var imageUrl = urlCreator.createObjectURL(blob);
        console.log('imageUrl = '+imageUrl);
        var uname = data['user'];
        video_dict[uname] = imageUrl;
        console.log('checking if user is active, user = '+uname);
        console.log('length of active_users = '+active_users.length);
        for(var i=0;i<active_users.length;i++){
            console.log(active_users[i]);
        }

        if(active_users.includes(uname)){
            if(keys.includes(uname)){
                $('#'+uname).attr('src',imageUrl);
            }
            else{
                video_content = "";
                video_content += "<div class='polaroid'><img src='" +imageUrl + "' id='" +uname+"'>";
                video_content+= "<div class='container'>";
                video_content+="<p><b>"+ uname +"</b><b></p></div></div>";
                console.log('video_content = ');
                console.log(video_content);
                $('#video_stream').append(video_content);
                keys.push(uname);
            }
        }
    });

    socketio.on('update_video',function(data){
        console.log('Invoked update video event');
        console.log(data);
    });

    socketio.on('update_messages',function(data){
        msgs = data['messages'];
        var i;
        var content = '';
        user_name = $("#current_user").text();
        user_name = user_name.substring(user_name.lastIndexOf("<")+1,user_name.lastIndexOf(">")).substring(5,user_name.length);

        for(i=0;i<msgs.length;i++){
        console.log('printing message');
        console.log(msgs[i])
        var tmpMsg = '<div class="chip">'+ msgs[i]['origin'] + ': </div>';
        var sentiment = msgs[i]['sentiment'];
        
        console.log('printing message = ');
        console.log(emojione.toImage(msgs[i]['message']));
        
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

        console.log('content = '+content);

        $('#chat-messages').html(content);
        var element = document.getElementById('chat-messages');
        element.scrollTop = element.scrollHeight;
    });
});