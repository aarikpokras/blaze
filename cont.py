RED_PERCEP = 0.2126
GRN_PERCEP = 0.7152
BLU_PERCEP = 0.0722
GAMMA_CCT_TH = 0.03928
GAMMA_CCT_BL_TH_DIV = 12.92
GAMMA_CCT_AB_TH_POW = 2.4
CONT_RAT_NUDGE = 0.05

def normalize(x):
  return x/255

def gammacorrect(x): # needs normalized values
  if (x <= GAMMA_CCT_TH):
    return x / GAMMA_CCT_BL_TH_DIV
  else:
    return x ** GAMMA_CCT_AB_TH_POW

def luminance(gcr, gcg, gcb): # needs gamma-corrected values
  return (RED_PERCEP * gcr) + (GRN_PERCEP * gcg) + (BLU_PERCEP * gcb)

def contrastratio(l1, l2): # l1 should be the greater luminance (must be spec by caller)
  return (l1 + CONT_RAT_NUDGE) / (l2 + CONT_RAT_NUDGE)

def retcr(c1, c2):
  if (isinstance(c1, list) and isinstance(c2, list)):
    c1n = [ normalize(c1[0]), normalize(c1[1]), normalize(c1[2]) ]
    c2n = [ normalize(c2[0]), normalize(c2[1]), normalize(c2[2]) ]

    c1g = [ gammacorrect(c1n[0]), gammacorrect(c1n[1]), gammacorrect(c1n[2]) ]
    c2g = [ gammacorrect(c2n[0]), gammacorrect(c2n[1]), gammacorrect(c2n[2]) ]

    c1l = luminance(c1g[0], c1g[1], c1g[2])
    c2l = luminance(c2g[0], c2g[1], c2g[2])

    fcr = -1

    if (c1l > c2l):
      fcr = contrastratio(c1l, c2l)
    else:
      fcr = contrastratio(c2l, c1l)

    return fcr
  else:
    raise Exception("Both arguments need to be lists")
