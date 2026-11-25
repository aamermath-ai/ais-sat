/* Worksheets AIS catalogue: grade → term → module → worksheet.
   Used by worksheets.html (the list students see) and teacher.html (the "Assign" picker).
   To add a worksheet: put its HTML file in source/worksheets/, add an item here, then run python3 source/build.py.
   "ws" must match the id in the worksheet's window.AISWS, so teachers can assign it to a class. */
const GRADES=[
  {id:"6",name:"Grade 6",course:"Mathematics",terms:[]},
  {id:"7",name:"Grade 7",course:"Mathematics",terms:[]},
  {id:"8",name:"Grade 8",course:"Mathematics",terms:[]},
  {id:"9",name:"Grade 9",course:"Algebra 1",terms:[
    {name:"Term 1",modules:[
      {name:"Module 3",topic:"Linear Equations",items:[
        {code:"3.1",ws:"g9-algebra-3-1",title:"Linear Equations in Standard Form",sub:"Quiz · Eid Al Etihad edition · 14 questions with hints and worked steps",file:"worksheets/g9-algebra-3-1-linear-equations-standard-form.html"}]}]}]},
  {id:"10",name:"Grade 10",course:"Geometry",terms:[
    {name:"Term 1",modules:[
      {name:"Module 13",topic:"Trigonometry with Right Triangles",items:[
        {code:"13.1",ws:"g10-geometry-13-1",title:"Tangent Ratio",sub:"Eid Al Etihad edition · 14 interactive questions with hints and worked steps",file:"worksheets/g10-geometry-13-1-tangent-ratio.html"}]}]}]}
];
