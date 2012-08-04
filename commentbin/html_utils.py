class htmlToken(object):
  def __init__(self):
    self.tagname = None
    self.data = {}
    self.html = ""
    
  def _readuntilchar(self,char,html,pos):
    epos = html.find(char,pos)
    return (html[pos:epos+1],epos)
    
  def _readquotes(self,html,pos):
    """ 
    reads a double or single quoted substring of html with the starting quote 
    at pos. Returns (quote,quoted string,position of the ending quote +1)
    """
    ret = pos
    endquote = html[pos]
    quoted_string = ''
    quoted_string += endqute
    ret += 1
    while html[ret] != endquote:
      ret += 1
      quoted_string += html[ret]
      if html[ret] == "\\":
	ret += 1
	quoted_string += html[ret]
	ret += 1
    return (endquote, quoted_string, ret+1) 
    
  def read(self,html,pos):
    """ Unfinished """
    html_pos = pos
    html_len = len(html)
    if html[html_pos] == '&':
      self.tagname,html_pos
    if html[html_pos] == "<":
      self.tagname,html_pos = self._readuntilchar(' ',html,html_pos+1)
      self.html + '<'+self.tagname
    
    
