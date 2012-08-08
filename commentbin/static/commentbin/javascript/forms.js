var formElements = Array();

function textInputClick(inputElement) {
  inputElement.oldValue=inputElement.value;
  inputElement.value="";
}

function findElement( id ) {
  if ( ! id ) return -1;
  var i = 0 ;
  for( i = 0; i < formElements.length; i++ ) { 
    if ( formElements[i].id == id ) { 
      return i;
    };
  };
  return -1;
}

function textInputLeave(inputElement) {
  var val = inputElement.value;
  if ( val.length == 0 ) {
    inputElement.value=inputElement.oldValue;
  } else {
    var pos = findElement(inputElement.id)
    $('.'+formElements[pos].related).each( function() { 
      this.value=val;
      this.size = val.length;
    });
  }	
}
