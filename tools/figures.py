"""Attach labeled figures to geometry questions by reading the numbers in their stems (no randomness, ids unchanged)."""
import re
def _m(p,s): return re.search(p,s)
def figure_for(q):
    if q.get("section")!="math" or q.get("domain")!="Geometry and Trigonometry": return None
    s=q["stem"]
    if m:=_m(r"right triangle has legs of length (\d+) and (\d+)\.",s): return {"t":"rtri","a":m[1],"b":m[2],"c":"?"}
    if m:=_m(r"hypotenuse of length (\d+) and one leg of length (\d+)",s): return {"t":"rtri","a":m[2],"b":"?","c":m[1]}
    if m:=_m(r"side opposite angle θ has length (\d+) and the hypotenuse has length (\d+)",s): return {"t":"rtri","a":m[1],"b":"","c":m[2],"th":"θ"}
    if _m(r"angle C is the right angle and sin A",s): return {"t":"rtri","a":"","b":"","c":"","letters":1}
    if m:=_m(r"30°-60°-90° triangle, the shorter leg has length (\d+)",s): return {"t":"s30","short":m[1],"long":"?","hyp":"?"}
    if m:=_m(r"45°-45°-90° triangle has legs of length (\d+)",s): return {"t":"s45","leg":m[1],"leg2":m[1],"hyp":"?"}
    if m:=_m(r"vertex angle of an isosceles triangle measures (\d+)°",s): return {"t":"iso","v":m[1]+"°","b":"?"}
    if m:=_m(r"Two (corresponding|alternate interior) angles measure \((.+?)\)° and \((.+?)\)°",s): return {"t":"parallel","kind":m[1],"p":"("+m[2]+")°","q":"("+m[3]+")°"}
    if _m(r"Two parallel lines are cut by a transversal\. Two corresponding angles measure \((.+?)\)° and \((.+?)\)°",s):
        m=_m(r"measure \((.+?)\)° and \((.+?)\)°",s); return {"t":"parallel","kind":"corresponding","p":"("+m[1]+")°","q":"("+m[2]+")°"}
    if m:=_m(r"AB = (\d+), DE = (\d+), and BC = (\d+)",s): return {"t":"similar","ab":m[1],"de":m[2],"bc":m[3],"ef":"?","letters":1}
    if m:=_m(r"angle P is \((.+?)\)°, the measure of angle Q is \((.+?)\)°, and the measure of angle R is \((.+?)\)°",s): return {"t":"tri3","A":"("+m[1]+")°","B":"("+m[2]+")°","C":"("+m[3]+")°","letters":["P","Q","R"]}
    if m:=_m(r"Two angles of a triangle measure (\d+)° and (\d+)°",s): return {"t":"tri3","A":m[1]+"°","B":m[2]+"°","C":"?"}
    if m:=_m(r"radius of (\d+)\. What is the length of an arc of the circle formed by a central angle of (\d+)°",s): return {"t":"arc","r":m[1],"th":m[2],"thl":m[2]+"°","s":"?"}
    if m:=_m(r"radius of (\d+)\. What is the area of a sector of the circle with a central angle of (\d+)°",s): return {"t":"sector","r":m[1],"th":m[2],"thl":m[2]+"°"}
    if m:=_m(r"Cylinder A has a radius of (\d+) and a height of (\d+)\. Cylinder B has a radius of (\d+) and a height of (\d+)",s): return {"t":"cyl2","r1":m[1],"h1":m[2],"r2":m[3],"h2":m[4]}
    if m:=_m(r"triangle has a base of (\d+) units and a height of (\d+) units",s): return {"t":"tribh","b":m[1],"h":m[2]}
    if m:=_m(r"cube with an edge length of (\d+)",s): return {"t":"box","l":m[1],"w":m[1],"h":m[1],"cube":1}
    if m:=_m(r"rectangle has an area of (\d+) square units and a length of (\d+)",s): return {"t":"rect","l":m[2],"w":"?"}
    if m:=_m(r"rectangle has a length of (\d+) and a width of (\d+)\. What is the length of a diagonal",s): return {"t":"rect","l":m[1],"w":m[2],"d":"?"}
    if m:=_m(r"circle with a diameter of (\d+)",s): return {"t":"circle","d":m[1]}
    if m:=_m(r"circle has an area of (\d+)π",s): return {"t":"circle","r":"?"}
    if m:=_m(r"circle has a circumference of (\d+)π",s): return {"t":"circle","r":"?"}
    if m:=_m(r"Two angles are supplementary\. One angle measures (\d+)°",s): return {"t":"supp","a":m[1]+"°","b":"?"}
    return None
