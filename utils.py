def load_settings( host, settings, g ):
  if host not in settings:
    return
  for (key,value) in settings[host].items():
    g[key]=value
    print key, value
  return