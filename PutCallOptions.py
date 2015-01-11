from math import exp, log, sqrt
from Fonctions import répartition_normale, densité_normale

def d_j(j, S, K, r, v, T):
    return (log(S/K) + (r + ((-1)**(j-1))*0.5*v*v)*T)/(v*(T**0.5))

def vanilla_call_price(S, K, r, v, T):
    """Valeur de l'obligation européenne où:
S: prix de l'action sous-jacente
K: Prix auquel on peut acheter l'obligation
r: taux d'interet sans risque
v: volatilité.
T: temps de maturité."""
    return S*répartition_normale(d_j(1, S, K, r, v, T))-K*exp(-r*T) * répartition_normale(d_j(2, S, K, r, v, T))

def vanilla_put_price(S, K, r, v, T):
    """Valeur de l'obligation européenne où:
S: prix de l'action sous-jacente
K: Prix auquel on peut vendre l'obligation
r: taux d'interet sans risque
v: volatilité.
T: temps de maturité."""
    return -S*répartition_normale(-d_j(1, S, K, r, v, T))+K*exp(-r*T) * répartition_normale(-d_j(2, S, K, r, v, T))

print(vanilla_call_price(57.58,60,0.01,0.1,1))
