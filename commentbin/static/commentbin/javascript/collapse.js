function collapsible( main, sidebar, toggle, width ) { 
  // Create the collapse handle
  var handle = document.createElement('img');

  handle.src=static_url+'commentbin/images/play.png';
  $(handle).addClass('collapse-handle');
  $(handle).addClass('icon');
  $(handle).addClass('clickable');
  $(handle).attr('onClick','toggleCollapse(this);');
  handle.title='Collapse the sidebar.';

  handle.collapse_data = { collapsed:false, 
                      width:width,
		      main:main,
		      sidebar:sidebar,
                     };
  toggle.appendChild(handle);
}

function toggleCollapse( element ) {
  if (element.collapse_data.collapsed) {
    element.collapse_data.collapsed = false;
    element.collapse_data.main.style.width=element.collapse_data.width;
    element.collapse_data.sidebar.style.display='block';
    $(element).removeClass('flip-horizontal');
    element.title='Collapse the sidebar.'
  } else {
    element.collapse_data.collapsed = true;
    element.collapse_data.main.style.width='auto';
    element.collapse_data.sidebar.style.display='none';
    $(element).addClass('flip-horizontal');
    element.title='Expand the sidebar.'
  }
}
  
  
