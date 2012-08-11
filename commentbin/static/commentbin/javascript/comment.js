/* This field holds the comments present at the server at the time
 * of the page load */
var initialServerComments = new Array();

/* This field holds all currently hilighted comments. */
var hilightedComments = new Array();

/* The last time a list of comments was retrieved from the server,
 * (number of seconds from Jan 1 1970, the format is considered an 
 *  implementation and should not be relied upon)
 */
var lastRetrieved;

/* Unsaved comments on the client side.*/
var unsavedComments = new Array();

/* The first available ID for a new client-side comment */
var lastID = -1

/* The current selection when displaying the comment forn */
var current_selection = {}

var nick = '';

/*
 * Each comment is an object with the following fields:
 * 
 *   id 	... the id of the comment
 *   start 	... the start position in the code
 *   end	... the end position in the code
 *   text	... the actual comment
 */

/* Hilights the respective code and adds a tooltip with the comment text to it */
function hilightComment(comment) {
  
  var code_block = $('.code');
  var range = rangy.createRange();
  var commentClass = 'comment'+comment.id;
  var options = {
    elementTagName: "a",
    elementProperties: {
      href: 'javascript:clickComment('+comment.id+');',
      rel:  'tooltip'
    },
    normalize:true
  };
  var applier = rangy.createCssClassApplier("hilight "+commentClass, options);
  
  range.selectCharacters(code_block[0],comment.start,comment.end);  
  applier.applyToRange(range);
  $('.'+commentClass).attr('data-original-title',comment.text);
  $('.'+commentClass).tooltip({
    live: true
  });
  
}


function unHilightComment(commentID) { 
    $('.comment'+commentID).each( function( index ) {
    var annot = $(this).html()
    $(this).tooltip('hide')
    $(this).after(annot)
    $(this).remove()
  })
}

function deserializeComment( jsonSerializedComment ) { 
  var comment =  {
    id:jsonSerializedComment.pk,
    text:jsonSerializedComment.fields.text,
    start:jsonSerializedComment.fields.start,
    end:jsonSerializedComment.fields.end,
    nick:jsonSerializedComment.fields.nick,
    user:jsonSerializedComment.fields.user,
  };
  return(comment)
}


function isHilighted(c) {
  for( var i = 0; i < hilightedComments.length; i++ ) { 
    if ( hilightedComments[i].id == c.id ) return i;
  }
  return -1;
}

function equals(commentA, commentB) { 
  return ( commentA.id == commentB.id && commentA.start == commentB.start && commentA.end == commentB.end && commentA.text === commentB.text );
}

function hilightSerializedComments( arrayOfComments ) { 
  for( var i = 0; i < arrayOfComments.length; i++ ) {
    var c = deserializeComment(arrayOfComments[i])
    var pos = isHilighted(c);
    if ( pos > -1 ) {
      if ( equals(hilightedComments[pos],c) ) continue;
      hilightedComments[pos] = c;
      unHilightComment(c.id);
    } else {
      hilightedComments.push(c)
    }
    hilightComment( c );
  }
}

function getOtherCommentTag(comment) { 
  var block_quote = document.createElement('blockquote');
  block_quote.innerHTML=comment.text+'<small>Posted by '+comment.nick+' on '+comment.date+'</small>';
  return block_quote;
}

function postOtherComment() { 
  var comment = {
    start:0,
    end:0,
    text:$('#other_comment_text_field')[0].value,
    nick:$('#header_nick')[0].value,
    id:lastID--,
    inlinecomment:false,
  };
  $.ajax({
    url:'comments/',
    data:comment,
    type:'POST',
    success: function(data) {
      com = getOtherCommentTag( deserializeComment(eval(data.comment)[0]) );
      $('#othercommentslist')[0].appendChild(com);
      $('#other_comment_text_field')[0].value='';
    },
    error: error
  });
}

function saveComment(comment) {
  var comment = {
    start:current_selection.start,
    end:current_selection.end,
    text:$('#comment_field')[0].value,
    nick:$('#nick_field')[0].value,
    id:lastID--
  };
  hilightComment(comment);
  hilightedComments.push(comment);
  hideCommentForm();

  $.ajax({
    url:'comments/',
    data:comment,
    type:'POST',
    success: function(data) {
      var c = { id:data.clientid };
      var pos = isHilighted(c);
      /* This should not happen */
      if (pos == -1) return;
      unHilightComment(data.clientid);
      hilightedComments[pos] = deserializeComment(eval(data.comment)[0]);
      hilightComment(hilightedComments[pos])
    },
    error: function( jqXHR ) { 
      error(jqXHR);
      unsavedComments.push(comment);
    }
  });
}

function error(jqXHR) {
  $('#error')[0].innerHTML = "<div class='alert alert-error'>"+jqXHR.statusText + " ("+jqXHR.status+") <a class='close' data-dismiss='alert' href='#'>×</a></div>"
  //$('#error')[0].innerHTML = jqXHR.responseText;
}



function retrieveNewComments() { 
  $.ajax({
    url:'comments/',
    dataType:'json',
    data:{
      created_after:lastRetrieved
    },
    success:function(data) {
      lastRetrieved = data.timestamp;
      hilightSerializedComments(eval(data.comments));
    }
  });
}

function clickComment(commentID) {
  var comment = {
    id:commentID
  }
  var pos = isHilighted(comment);
  /* This should not happen! */
  if ( pos == -1 ) return;
  comment = hilightedComments[pos];
  $('#comment_edit_field')[0].value=comment.text;
  $('#commentid_edit_field')[0].value=comment.id;
  if ( comment.user && ! (comment.user === '') ) $('#comment_edit_nick')[0].innerHTML=comment.user;
  else $('#comment_edit_nick')[0].innerHTML=comment.nick;
  showCommentEditForm();
}

function showCommentEditForm() {
  $('#edit_comment_form').modal('show');
  $('#comment_edit_field')[0].focus();
}

function hideCommentEditForm() { 
  $('#edit_comment_form').modal('hide');
}

function editComment() { 
  var commentID = $('#commentid_edit_field')[0].value;
  var comment = {
    id:commentID
  }
  var pos = isHilighted(comment);
  /* This should not happen! */
  if ( pos == -1 ) return;
  var commentField = $('#comment_edit_field')[0];
  var newText = commentField.value;
  if ( ! (newText === hilightedComments[pos].text) ) {
    /* Something has really changed */
    unHilightComment(comment.id);
    hilightedComments[pos].text = newText;
    hilightComment(hilightedComments[pos]);
    
    $.ajax({
      url:'comments/'+comment.id,
      data:hilightedComments[pos],
      type:'PUT',
      success: function(data) {
      },
      error: function( jqXHR ) { 
	error(jqXHR);
        unsavedComments.push(comment);
      }
    });    
  }
  
  hideCommentEditForm();
}

function deleteComment() { 
  var commentID = $('#commentid_edit_field')[0].value;
  var pos = isHilighted({id:commentID})
  /* This should not happen */
  if ( pos == -1 ) return;
  comment = hilightedComments[pos]
  
  $.ajax({
    url:'comments/'+comment.id,
    data:comment,
    type:'DELETE',
    success: function(data) {
      var pos = isHilighted({id:data.deletedID})
      /* this should not happen */
      if ( pos == -1 ) return;
      unHilightComment(data.deletedID)
      hilightedComments.splice(pos,pos)
    },
    error: function( jqXHR ) { 
      error(jqXHR);
    }
  });
  hideCommentEditForm();
}

function deleteSnippet() {
  $.ajax({
    url:window.location.href,
    data:{},
    type:'DELETE',
    success: function(data) {
      window.location.replace(data.redirect);
    },
    error: function( jqXHR ) { 
      error(jqXHR);
    }
  });
}

function showCommentForm() {
  var sel = rangy.getSelection();
  var range = sel.getAllRanges()[0];
  if (range == undefined) return;
  var charRange = range.toCharacterRange($('.code')[0]);
  current_selection = {
    start:charRange.start,
    end:charRange.end
  }
  $('#add_comment_form').modal('show');
  $('#comment_field')[0].focus();
}

function hideCommentForm() {
  $('#add_comment_form').modal('hide');
  $('#comment_field')[0].value='';
}

function commentInit() { 
  rangy.init();
  cssClassApplierModule = rangy.modules.CssClassApplier;
  hilightSerializedComments( initialServerComments );
  $(document).bind('keyup','alt+ctrl+m',showCommentForm);
  setInterval(retrieveNewComments,10000);
  
  $('.mytooltip').tooltip();
  
  // Add collapse control to the code block
  var td = document.createElement('td');
  $('.highlighttable').find('tr')[0].appendChild(td);
  collapsible( $('div.code')[0], $('.othercomments')[0], td, '50%');
}