var checkout = {};

$(document).ready(function() {
  var $messages = $('.messages-content'),
    d, h, m,
    i = 0;

  $(window).load(function() {
    $messages.mCustomScrollbar();
    insertResponseMessage('Hi there, I\'m your personal Concierge. How can I help?');
  });

  function updateScrollbar() {
    $messages.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
      scrollInertia: 10,
      timeout: 0
    });
  }

  function setDate() {
    d = new Date()
    if (m != d.getMinutes()) {
      m = d.getMinutes();
      $('<div class="timestamp">' + d.getHours() + ':' + m + '</div>').appendTo($('.message:last'));
    }
  }

  function callChatbotApi(message) {
    // params, body, additionalParams
    return sdk.chatbotPost({}, {
      messages: [{
        type: 'unstructured',
        unstructured: {
          text: message
        }
      }]
    }, {});
  }

  function insertMessage() {
    msg = $('.message-input').val();
    if ($.trim(msg) == '') {
      return false;
    }
    $('<div class="message message-personal">' + msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
    setDate();
    $('.message-input').val(null);
    updateScrollbar();

    callChatbotApi(msg)
      .then((response) => {
        console.log(response);
        var data = response.data;

        if (data.messages && data.messages.length > 0) {
          

          console.log('received ' + data.messages.length + ' messages');

          var messages = data.messages;
          console.log("=== messages ===", messages);

          for (var message of messages) {
            if (message.type === 'unstructured') {
              console.log("=== here in unstructured ===");
              insertResponseMessage(message.unstructured.text);
              if(message.unstructured.text.includes("Looking for")){
                console.log("=== here in if loop  ===");

                //todo
                //trigger searchdb api 
                //respond with result
                console.log("REQUEST BODY ",message.unstructured.text);
                //Looking for chinese options around nyc at 10:00 for 3 people.
                const pattern = /\s+/; // Split the string at one or more spaces
                const substringsArray = message.unstructured.text.split(pattern);
                const cuisine = "";
                const loc = "";
                for (let i = 0; i < substringsArray.length; i++) {
                  if(substringsArray[i] == ("for")){
                      i++;
                    while(substringsArray[i] == ("options")){
                      cuisine = cuisine +substringsArray[i];
                      i++;
                    }
                  }
                  if(substringsArray[i] == ("around")){
                    i++;
                  while(substringsArray[i] == ("at")){
                    loc = loc +substringsArray[i];
                    i++;
                  }
                }
                console.log("REQUEST BODY " + cuisine + loc);
                }
              }
            } else if (message.type === 'structured' && message.structured.type === 'product') {
              var html = '';

              insertResponseMessage(message.structured.text);

              setTimeout(function() {
                html = '<img src="' + message.structured.payload.imageUrl + '" witdth="200" height="240" class="thumbnail" /><b>' +
                  message.structured.payload.name + '<br>$' +
                  message.structured.payload.price +
                  '</b><br><a href="#" onclick="' + message.structured.payload.clickAction + '()">' +
                  message.structured.payload.buttonLabel + '</a>';
                insertResponseMessage(html);
              }, 1100);
            } else {
              console.log('not implemented');
            }
          }
        } else {
          console.log("=== here in oops ===");
          insertResponseMessage('Oops, something went wrong. Please try again.');
        }
      })
      .catch((error) => {
        console.log('an error occurred', error);
        insertResponseMessage('Oops, something went wrong. Please try again.');
      });
  }

  $('.message-submit').click(function() {
    insertMessage();
  });

  $(window).on('keydown', function(e) {
    if (e.which == 13) {
      insertMessage();
      return false;
    }
  })

  function insertResponseMessage(content) {
    $('<div class="message loading new"><figure class="avatar"><img src="https://media.tenor.com/images/4c347ea7198af12fd0a66790515f958f/tenor.gif" /></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();
    if(content.includes("Looking for")){
      //todo
      //trigger searchdb api 
      //respond with result
      console.log("REQUEST BODY ",content);
      //Looking for chinese options around nyc at 10:00 for 3 people.
      const pattern = /\s+/; // Split the string at one or more spaces
      const substringsArray = content.split(pattern);
      const cuisine = "";
      const loc = "";
      for (let i = 0; i < substringsArray.length; i++) {
        if(substringsArray[i] == ("for")){
            i++;
          while(substringsArray[i] == ("options")){
            cuisine = cuisine +substringsArray[i];
            i++;
          }
        }
        if(substringsArray[i] == ("around")){
          i++;
        while(substringsArray[i] == ("at")){
          loc = loc +substringsArray[i];
          i++;
        }
      }
      console.log("REQUEST BODY " + cuisine + loc);
      }


    }
    setTimeout(function() {
      $('.message.loading').remove();
      $('<div class="message new"><figure class="avatar"><img src="https://media.tenor.com/images/4c347ea7198af12fd0a66790515f958f/tenor.gif" /></figure>' + content + '</div>').appendTo($('.mCSB_container')).addClass('new');
      setDate();
      updateScrollbar();
      i++;
    }, 500);
  }

});
